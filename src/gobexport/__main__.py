"""Export

This component exports data sources
"""
import datetime

from gobcore.message_broker.config import WORKFLOW_EXCHANGE, EXPORT_QUEUE, RESULT_QUEUE
from gobcore.message_broker.messagedriven_service import messagedriven_service
from gobcore.logging.logger import logger

from gobexport.export import export
from gobexport.test import test


def assert_message_attributes(msg, attrs):
    for attr in attrs:
        assert msg.get(attr), f"Missing attribute {attr}"


def handle_export_msg(msg):
    assert_message_attributes(msg, ["catalogue", "collection", "destination"])

    catalogue = msg['catalogue']
    collection = msg['collection']
    destination = msg['destination']
    application = "GOBExport"

    start_timestamp = int(datetime.datetime.utcnow().replace(microsecond=0).timestamp())
    process_id = f"{start_timestamp}.{destination}.{collection}"

    msg["header"].update({
        'process_id': process_id,
        'destination': destination,
        'application': application,
        'catalogue': catalogue,
        'entity': collection,
    })

    logger.configure(msg, "EXPORT")

    export(catalogue, collection, destination)

    return {
        "header": msg.get("header"),
        "summary": {
            "warnings": logger.get_warnings(),
            "errors": logger.get_errors()
        },
        "contents": None
    }


def handle_export_test_msg(msg):
    assert_message_attributes(msg, ["catalogue"])

    catalogue = msg['catalogue']

    start_timestamp = int(datetime.datetime.utcnow().replace(microsecond=0).timestamp())
    process_id = f"{start_timestamp}.export_test.{catalogue}"

    msg["header"].update({
        'process_id': process_id,
        'application': f"GOBExportTest",
        'catalogue': catalogue,
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
        'exchange': WORKFLOW_EXCHANGE,
        'queue': EXPORT_QUEUE,
        'key': "export.start",
        'handler': handle_export_msg,
        'report': {
            'exchange': WORKFLOW_EXCHANGE,
            'queue': RESULT_QUEUE,
            'key': 'export.result'
        }
    },
    'export_test': {
        'exchange': WORKFLOW_EXCHANGE,
        'queue': EXPORT_QUEUE,
        'key': "export_test.start",
        'handler': handle_export_test_msg,
        'report': {
            'exchange': WORKFLOW_EXCHANGE,
            'queue': RESULT_QUEUE,
            'key': 'export_test.result'
        }
    }
}

messagedriven_service(SERVICEDEFINITION, "Export")
