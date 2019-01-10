"""Meetbouten export

This module contains the export entries for the meetbouten catalog

"""
import datetime
import os
import tempfile

from gobcore.exceptions import GOBException
from gobcore.log import get_logger

from gobexport.config import get_host, CONTAINER_BASE
from gobexport.connector.objectstore import connect_to_objectstore
from gobexport.distributor.objectstore import distribute_to_objectstore
from gobexport.exporter import CONFIG_MAPPING, export_to_file


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
    temp_filename = os.path.join(dir, name)
    os.makedirs(os.path.dirname(temp_filename), exist_ok=True)
    return temp_filename


def _export_collection(host, catalogue, collection, destination):  # noqa: C901
    """Export a collection from a catalog

    :param host: The API host to retrieve the catalog and collection from
    :param catalog: The name of the catalog
    :param collection: The name of the collection
    :param destination: The destination of the resulting output file(s)
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

    # Get the configuration for this collection
    config = CONFIG_MAPPING[catalogue][collection]

    files = []

    # Start exporting each product
    for name, product in config.products.items():
        # Get name of local file to write results to
        results_file = _get_filename(product['filename']) if destination == "Objectstore" else product['filename']

        format = product.get('format')
        row_count = export_to_file(host, product['endpoint'], product['exporter'], results_file, format)

        logger.info(f"{row_count} records exported to local file {name}.", extra=extra_log_kwargs)

        files.append({
            'temp_location': results_file,
            'distribution': product['filename'],
            'mime_type': product['mime_type']})

        # Add extra result files (e.g. .prj file)
        extra_files = product.get('extra_files', [])
        files.extend([{'temp_location': _get_filename(file['filename']),
                       'distribution': file['filename'],
                       'mime_type': file['mime_type']} for file in extra_files])

    if destination == "Objectstore":
        # Get objectstore connection
        connection, user = connect_to_objectstore()
        logger.info(f"Connection to {destination} {user} has been made.", extra=extra_log_kwargs)

    # Start distribution of all resulting files
    for file in files:
        if destination == "Objectstore":
            # Distribute to final location
            container = f'{CONTAINER_BASE}/{catalogue}/'
            with open(file['temp_location'], 'rb') as fp:
                try:
                    distribute_to_objectstore(connection,
                                              container,
                                              file['distribution'],
                                              fp,
                                              file['mime_type'])
                except GOBException as e:
                    logger.error(f"Failed to distribute to {destination} on location: {container}{file['distribution']}. \
                                 Error: {e}",
                                 extra=extra_log_kwargs)
                    return False

            logger.info(f"File distributed to {destination} on location: {container}{file['distribution']}.",
                        extra=extra_log_kwargs)

            # Delete temp file
            os.remove(file['temp_location'])

        elif destination == "File":
            logger.info(f"Export is written to {file['distribution']}.", extra=extra_log_kwargs)


def export(catalogue, collection, destination):
    host = get_host()
    _export_collection(host=host,
                       catalogue=catalogue,
                       collection=collection,
                       destination=destination)
