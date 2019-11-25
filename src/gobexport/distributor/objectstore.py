import swiftclient
from fnmatch import fnmatch

from objectstore.objectstore import (
    delete_object,
    get_full_container_list,
    put_object,
)

from gobcore.exceptions import GOBException
from gobcore.logging.logger import logger


def distribute_to_objectstore(connection, container, object_name, contents, content_type):
    """Distribute to the objectstore

    The Amsterdam/objectstore library is used to connect to the container
    :param connection: Objectstore connection
    :param container: The name of the container
    :param object_name: The filename of the object on the objectstore
    :param contents:
    :param content_type:
    :return:
    """
    try:
        put_object(connection, container, object_name, contents=contents, content_type=content_type)
    except swiftclient.exceptions.ClientException as e:
        raise GOBException(e)


def cleanup_objectstore(connection, container, catalogue, cleanup_mask, object_name=None):
    """Delete objects from the objectstore

    The Amsterdam/objectstore library is used to connect to the container
    :param connection: Objectstore connection
    :param container: The name of the container
    :param cleanup_mask: The filename mask to delete objects from the objectstore
    :param object_name: The filename of the object on the objectstore to preserve
    :return:

    Notes:
    - cleanup_mask should contain fnmatch pattern.
    (see https://docs.python.org/3/library/fnmatch.html)
    """
    # Do nothing if no cleanup_mask provided
    if not cleanup_mask:
        return

    deleted_files_count = 0
    try:
        for item in get_full_container_list(connection, container):
            # preserve object if its full path matches object_name
            if object_name and item["name"] == f"{catalogue}/{object_name}":
                continue
            # delete object if its full path matches cleanup_mask
            if fnmatch(item["name"], f"{catalogue}/{cleanup_mask}"):
                delete_object(connection, container, item)
                logger.info(f'File {container}/{item["name"]} deleted.')
                deleted_files_count += 1
    except swiftclient.exceptions.ClientException as e:
        raise GOBException(e)

    return deleted_files_count
