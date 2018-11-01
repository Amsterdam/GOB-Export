"""Implementation of Objectstore input connectors

The following connectors are implemented in this module:
    Objectstore - Connects to Objectstore using connection details

"""
from objectstore.objectstore import get_connection

from gobexport.connector.config import OBJECTSTORE_CONFIG


def connect_to_objectstore():
    """Connect to the objectstore

    The Amsterdam/objectstore library is used to connect to the objectstore

    :return: a connection to the given objectstore
    """
    return get_connection(OBJECTSTORE_CONFIG)
