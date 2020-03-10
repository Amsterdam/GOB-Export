"""Export

This component exports data sources
"""
import datetime

from gobcore.message_broker.config import WORKFLOW_EXCHANGE, EXPORT_QUEUE, EXPORT_TEST_QUEUE, EXPORT_RESULT_KEY, \
    EXPORT_TEST_RESULT_KEY
from gobcore.message_broker.messagedriven_service import messagedriven_service
from gobcore.logging.logger import logger

from gobexport.export import export
from gobexport.test import test
from gobexport.dump import Dumper


def assert_message_attributes(msg, attrs):
    for attr in attrs:
        assert msg.get(attr), f"Missing attribute {attr}"


def handle_export_dump_msg(msg):
    header = msg['header']
    logger.configure(msg, "DUMP")
    Dumper().dump_catalog(catalog_name=header['catalogue'],
                          collection_name=header['collection'])


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
    application = "GOBExport"

    start_timestamp = int(datetime.datetime.utcnow().replace(microsecond=0).timestamp())
    process_id = f"{start_timestamp}.{destination}.{collection}"

    msg["header"].update({
        'process_id': process_id,
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
        "header": msg.get("header"),
        "summary": {
            "warnings": logger.get_warnings(),
            "errors": logger.get_errors()
        },
        "contents": None
    }


def handle_export_test_msg(msg):
    header = msg.get('header', {})
    assert_message_attributes(header, ["catalogue"])

    catalogue = header['catalogue']

    start_timestamp = int(datetime.datetime.utcnow().replace(microsecond=0).timestamp())
    process_id = f"{start_timestamp}.export_test.{catalogue}"

    msg["header"].update({
        'process_id': process_id,
        'application': f"GOBExportTest",
        'entity': catalogue
    })

    logger.configure(msg, "EXPORT_TEST")

    test(catalogue)

    return {
        "header": msg.get("header"),
        "summary": {
            "warnings": logger.get_warnings(),
            "errors": logger.get_errors()
        },
        "contents": None
    }


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
    }
}

messagedriven_service(SERVICEDEFINITION, "Export")
