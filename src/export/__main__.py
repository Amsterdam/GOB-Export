"""Meetbouten export

This module contains the export entries for the meetbouten catalog

"""
import os
from pathlib import Path
import tempfile
import time

from export.config import get_host, get_args
from export.connector.objectstore import connect_to_objectstore
from export.distributor.objectstore import distribute_to_objectstore
from export.meetbouten import export_meetbouten


# TODO: Should be fetched from GOBCore in next iterations
VALID_CATALOGS = [
    'meetbouten',
]


def _get_filename(name):
    """Gets the full filename given a the name of a file

    :param name:
    :return:
    """
    dir = tempfile.gettempdir()
    # Create the path if the path not yet exists
    path = Path(dir)
    path.mkdir(exist_ok=True)
    return os.path.join(dir, name)


def export_collection(host, catalog, collection, file_name):
    """Export a collection from a catalog

    :param host: The API host to retrieve the catalog and collection from
    :param catalog: The name of the catalog
    :param collection: The name of the collection
    :param file_name: The file to write the export results to
    :return:
    """
    exporter = {
        'meetbouten': export_meetbouten
    }

    # Get temp file name
    temporary_file = _get_filename(file_name)

    exporter[catalog](collection, host, temporary_file)

    # Get objectstore connection
    connection = connect_to_objectstore()

    # Distribute to final location
    with open(temporary_file, 'rb') as fp:
        distribute_to_objectstore(connection,
                                  catalog,
                                  file_name,
                                  fp,
                                  'text/plain')

    # Delete temp file
    os.remove(temporary_file)


host = get_host()
args = get_args()

keep_alive = True

if args.catalog:
    # If we receive a catalog as an argument, start exporting
    export_collection(host=host, catalog=args.catalog, collection=args.collection, file_name=args.file_name)
else:
    # Run indefinite to have a docker container available for exports
    while keep_alive:
        print('.')
        time.sleep(60)
