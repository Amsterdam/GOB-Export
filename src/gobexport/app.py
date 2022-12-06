import datetime
import os
from threading import Thread

from gobcore.logging.logger import logger, RequestsHandler, StdoutHandler
from gobcore.message_broker.config import EXPORT_QUEUE, EXPORT_RESULT_KEY, EXPORT_TEST_QUEUE, \
    EXPORT_TEST_RESULT_KEY, WORKFLOW_EXCHANGE
from gobcore.message_broker.messagedriven_service import messagedriven_service
from gobcore.message_broker.typing import ServiceDefinition

from gobexport.config import GOB_EXPORT_API_PORT
from gobexport.export import export
from gobexport.flask_api import get_flask_app
from gobexport.test import test


LOG_HANDLERS = [RequestsHandler(), StdoutHandler()]


def assert_message_attributes(msg, attrs):
    for attr in attrs:
        assert msg.get(attr), f"Missing attribute {attr}"


def handle_export_file_msg(msg):
    header = msg["header"]
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

    if destination in ["Objectstore", "File"]:
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


SERVICEDEFINITION: ServiceDefinition = {
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
