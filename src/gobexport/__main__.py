"""Export

This component exports data sources
"""
from gobcore.message_broker.config import WORKFLOW_EXCHANGE, EXPORT_QUEUE
from gobcore.message_broker.messagedriven_service import messagedriven_service
from gobexport.export import export


def handle_export_msg(msg):
    assert(msg.get("catalogue"))
    assert(msg.get("collection"))
    assert(msg.get("filename"))

    export(catalogue=msg["catalogue"], collection=msg["collection"], filename=msg["filename"])


SERVICEDEFINITION = {
    'export_request': {
        'exchange': WORKFLOW_EXCHANGE,
        'queue': EXPORT_QUEUE,
        'key': "export.start",
        'handler': handle_export_msg
    }
}

messagedriven_service(SERVICEDEFINITION, "Export")
