from objectstore.objectstore import put_object


def distribute_to_objectstore(connection, catalog, object_name, contents, content_type):
    """Distribute to the objectstore

    The Amsterdam/objectstore library is used to connect to the container
    :param connection
    :param catalog: The name of the catalog
    :param object_name: The filename of the object on the objectstore
    :param contents:
    :param content_type:
    :return:
    """
    container = f'distributie/{catalog}/'
    put_object(connection, container, object_name, contents=contents, content_type=content_type)
