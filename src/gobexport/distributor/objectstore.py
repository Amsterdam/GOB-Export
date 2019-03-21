import os
import swiftclient

from gobcore.exceptions import GOBException

from objectstore.objectstore import put_object


def distribute_to_objectstore(connection, container, object_name, contents, content_type):
    """Distribute to the objectstore

    The Amsterdam/objectstore library is used to connect to the container
    :param connection
    :param container: The name of the container
    :param object_name: The filename of the object on the objectstore
    :param contents:
    :param content_type:
    :return:
    """
    proxy = os.getenv('HTTPS_PROXY')
    try:
        put_object(connection, container, object_name, contents=contents, content_type=content_type, proxy=proxy)
    except swiftclient.exceptions.ClientException as e:
        raise GOBException(e)
