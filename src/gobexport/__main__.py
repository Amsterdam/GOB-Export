"""Export

This component exports data sources
"""
from gobcore.message_broker.config import WORKFLOW_EXCHANGE, EXPORT_QUEUE
from gobcore.message_broker.messagedriven_service import messagedriven_service
from gobexport.export import export


def handle_export_msg(msg):
    attrs = ["catalogue", "collection", "destination"]

    for attr in attrs:
        assert msg.get(attr), f"Missing attribute {attr}"

    export(**{attr: value for attr, value in msg.items() if attr in attrs})


SERVICEDEFINITION = {
    'export_request': {
        'exchange': WORKFLOW_EXCHANGE,
        'queue': EXPORT_QUEUE,
        'key': "export.start",
        'handler': handle_export_msg
    }
}

messagedriven_service(SERVICEDEFINITION, "Export")
