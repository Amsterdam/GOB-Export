"""Meetbouten export

This module contains the export entries for the meetbouten catalog

"""
import datetime
import os
from pathlib import Path
import tempfile

from gobcore.exceptions import GOBException
from gobcore.log import get_logger

from gobexport.config import get_host, CONTAINER_BASE
from gobexport.connector.objectstore import connect_to_objectstore
from gobexport.distributor.objectstore import distribute_to_objectstore
from gobexport.exporter import export_to_file


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


def _export_collection(host, catalogue, collection, filename, destination):
    """Export a collection from a catalog

    :param host: The API host to retrieve the catalog and collection from
    :param catalog: The name of the catalog
    :param collection: The name of the collection
    :param file_name: The file to write the export results to
    :return:
    """

    # Extra variables for logging, generate them since we do not get them from workflow yet
    global extra_log_kwargs
    start_timestamp = int(datetime.datetime.now().replace(microsecond=0).timestamp())
    process_id = f"{start_timestamp}.{destination}.{collection}"
    extra_log_kwargs = {
        'process_id': process_id,
        'destination': destination,
        'entity': collection
    }

    logger.info(f"Export {catalogue}:{collection} to {destination} started.", extra=extra_log_kwargs)

    # Get name of local file to write results to
    results_file = _get_filename(filename) if destination == "Objectstore" else filename

    row_count = export_to_file(catalogue, collection, host, results_file)
    logger.info(f"{row_count} records exported to local file.", extra=extra_log_kwargs)

    if destination == "Objectstore":
        # Get objectstore connection
        connection, user = connect_to_objectstore()

        logger.info(f"Connection to {destination} {user} has been made.", extra=extra_log_kwargs)

        # Distribute to final location
        container = f'{CONTAINER_BASE}/{catalogue}/'
        with open(results_file, 'rb') as fp:
            try:
                distribute_to_objectstore(connection,
                                          container,
                                          filename,
                                          fp,
                                          'text/plain')
            except GOBException as e:
                logger.error(f'Failed to distribute to {destination} on location: {container}{filename}. Error: {e}',
                             extra=extra_log_kwargs)
                return False

        logger.info(f"File distributed to {destination} on location: {container}{filename}.", extra=extra_log_kwargs)

        # Delete temp file
        os.remove(results_file)
    elif destination == "File":
        logger.info(f"Export is written to {results_file}.", extra=extra_log_kwargs)


def export(catalogue, collection, filename, destination):
    host = get_host()
    _export_collection(host=host,
                       catalogue=catalogue,
                       collection=collection,
                       filename=filename,
                       destination=destination)
