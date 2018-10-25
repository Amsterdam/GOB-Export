"""Implementation of Objectstore input connectors

The following connectors are implemented in this module:
    Objectstore - Connects to Objectstore using connection details

"""
from objectstore.objectstore import get_connection

from export.connector.config import OBJECTSTORE_CONFIG


def connect_to_objectstore():
    """Connect to the objectstore

    The Amsterdam/objectstore library is used to connect to the objectstore

    :return: a connection to the given objectstore
    """
    OBJECTSTORE = OBJECTSTORE_CONFIG

    try:
        connection = get_connection(OBJECTSTORE)
    except Exception as e:
        raise
    else:
        return connection
