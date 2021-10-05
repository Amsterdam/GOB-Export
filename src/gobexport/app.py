import datetime
import os
from threading import Thread

from gobcore.logging.logger import logger
from gobcore.message_broker.config import EXPORT, EXPORT_QUEUE, EXPORT_RESULT_KEY, EXPORT_TEST_QUEUE, \
    EXPORT_TEST_RESULT_KEY, WORKFLOW_EXCHANGE
from gobcore.message_broker.messagedriven_service import RUNS_IN_OWN_THREAD, messagedriven_service
from gobcore.message_broker.notifications import DumpNotification, add_notification, \
    get_notification, listen_to_notifications
from gobcore.workflow.start_workflow import start_workflow

from gobexport.config import GOB_EXPORT_API_PORT
from gobexport.dump import Dumper
from gobexport.export import export
from gobexport.flask_api import get_flask_app
from gobexport.test import test


def assert_message_attributes(msg, attrs):
    for attr in attrs:
        assert msg.get(attr), f"Missing attribute {attr}"


def handle_export_dump_msg(msg):
    header = msg['header']
    logger.configure(msg, "DUMP")
    Dumper().dump_catalog(catalog_name=header['catalogue'],
                          collection_name=header['collection'],
                          include_relations=header.get('include_relations', True),
                          force_full=header.get('full', False))

    add_notification(msg, DumpNotification(header['catalogue'], header['collection']))


def handle_export_file_msg(msg):
    header = msg['header']
    logger.configure(msg, "EXPORT")
    export(catalogue=header['catalogue'],
           collection=header['collection'],
           product=header['product'],
           destination=header['destination'])


def handle_export_msg(msg):
    header = msg.get('header', {})
    assert_message_attributes(header, ["catalogue", "collection", "destination"])

    catalogue = header['catalogue']
    collection = header['collection']
    product = header.get('product', None)
    destination = header['destination']
    application = header.get('application', "GOBExport")

    msg["header"].update({
        'destination': destination,
        'application': application,
        'catalogue': catalogue,
        'entity': collection,
        'product': product,
    })

    if destination == "Database":
        handle_export_dump_msg(msg)
    elif destination in ["Objectstore", "File"]:
        handle_export_file_msg(msg)
    else:
        logger.error(f"Unrecognized destination for export {catalogue} {collection}: {destination}")

    return {
        **msg,
        "header": msg.get("header"),
        "summary": logger.get_summary(),
        "contents": None
    }


def handle_export_test_msg(msg):
    header = msg.get('header', {})
    assert_message_attributes(header, ["catalogue"])

    catalogue = header['catalogue']

    start_timestamp = int(datetime.datetime.utcnow().replace(microsecond=0).timestamp())
    process_id = header.get('process_id', f"{start_timestamp}.export_test.{catalogue}")

    msg["header"].update({
        'process_id': process_id,
        'application': "GOBExportTest",
        'entity': catalogue
    })

    logger.configure(msg, "EXPORT_TEST")

    test(catalogue)

    summary = logger.get_summary()
    msg = {
        "header": msg.get("header"),
        "summary": summary,
        "contents": None
    }

    # To overcome distribute problems of locked files,
    # distribute is decoupled and starts at a certain
    # time triggered by in Jenkins.
    #
    # Send out a notification for a successfull export test
    #
    # if len(summary['errors']) == 0:
    #     add_notification(msg, ExportTestNotification(header['catalogue'],
    #                                                  header.get('collection'),
    #                                                  header.get('product')))
    return msg


def dump_on_new_events(msg):
    """
    On any creation of events, update the analysis database for the new changes

    :param msg:
    :return:
    """
    notification = get_notification(msg)

    # Start an export cat-col to db workflow to update the analysis database
    workflow = {
        'workflow_name': EXPORT
    }
    arguments = {
        'catalogue': notification.header.get('catalogue'),
        'collection': notification.header.get('collection'),
        'application': notification.header.get('application'),
        'process_id': notification.header.get('process_id'),
        'destination': 'Database',
        'include_relations': False,
        'retry_time': 10 * 60  # retry for max 10 minutes if already running
    }
    start_workflow(workflow, arguments)


SERVICEDEFINITION = {
    'export_request': {
        'queue': EXPORT_QUEUE,
        'handler': handle_export_msg,
        'report': {
            'exchange': WORKFLOW_EXCHANGE,
            'key': EXPORT_RESULT_KEY,
        }
    },
    'export_test': {
        'queue': EXPORT_TEST_QUEUE,
        'handler': handle_export_test_msg,
        'report': {
            'exchange': WORKFLOW_EXCHANGE,
            'key': EXPORT_TEST_RESULT_KEY,
        }
    },
    'dump': {
        'queue': lambda: listen_to_notifications("dump", 'events'),
        'handler': dump_on_new_events,
        RUNS_IN_OWN_THREAD: True
    }
}


def run_message_thread():
    try:
        messagedriven_service(SERVICEDEFINITION, "Export")
    except Exception as e:
        print("ERROR: no connection with GOB message broker, application is stopped")
        print(e)
    os._exit(os.EX_UNAVAILABLE)


def get_app():
    """Get app and start messagedriven_service in separate thread."""
    t = Thread(target=run_message_thread)
    t.start()

    return get_flask_app()


def run():
    """
    Get the Flask app and run it at the port as defined in config

    :return: None
    """
    app = get_app()
    app.run(port=GOB_EXPORT_API_PORT)
