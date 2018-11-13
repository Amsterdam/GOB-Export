"""Meetbouten export

This module contains the export entries for the meetbouten catalog

"""
import datetime
import os
from pathlib import Path
import tempfile
import time

from gobcore.exceptions import GOBException
from gobcore.log import get_logger

from gobexport.config import get_host, get_args, CONTAINER_BASE
from gobexport.connector.objectstore import connect_to_objectstore
from gobexport.distributor.objectstore import distribute_to_objectstore
from gobexport.meetbouten import export_meetbouten


logger = get_logger(name="EXPORT")
extra_log_kwargs = {}


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
    # Extra variables for logging, generate them since we do not get them from workflow yet
    global extra_log_kwargs
    start_timestamp = int(datetime.datetime.now().replace(microsecond=0).timestamp())
    destination = 'GOB Objectstore'
    process_id = f"{start_timestamp}.{destination}.{collection}"
    extra_log_kwargs = {
        'process_id': process_id,
        'destination': destination,
        'entity': collection
    }

    logger.info(f"Export {catalog}:{collection} to {destination} started.", extra=extra_log_kwargs)

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

    row_count = exporter[catalog](collection, host, temporary_file)
    logger.info(f"{row_count} records exported to local file.", extra=extra_log_kwargs)

    # Get objectstore connection
    connection, user = connect_to_objectstore()

    logger.info(f"Connection to {destination} {user} has been made.", extra=extra_log_kwargs)

    # Distribute to final location
    container = f'{CONTAINER_BASE}/{catalog}/'
    with open(temporary_file, 'rb') as fp:
        try:
            distribute_to_objectstore(connection,
                                      container,
                                      file_name,
                                      fp,
                                      'text/plain')
        except GOBException as e:
            logger.error(f'Failed to distribute to {destination} on location: {container}{file_name}. Error: {e}',
                         extra=extra_log_kwargs)
            return False

    logger.info(f"File distributed to {destination} on location: {container}{file_name}.", extra=extra_log_kwargs)

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
