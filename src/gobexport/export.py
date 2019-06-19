"""Meetbouten export

This module contains the export entries for the meetbouten catalog

"""
import os
import tempfile

from gobcore.exceptions import GOBException
from gobcore.logging.logger import logger

from gobexport.config import get_host, CONTAINER_BASE
from gobexport.connector.objectstore import connect_to_objectstore
from gobexport.distributor.objectstore import distribute_to_objectstore
from gobexport.exporter import CONFIG_MAPPING, export_to_file


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
    logger.info(f"Export {catalogue}:{collection} to {destination} started.")

    # Get the configuration for this collection
    config = CONFIG_MAPPING[catalogue][collection]

    files = []

    # Start exporting each product
    for name, product in config.products.items():
        logger.info(f"Export to file '{name}' started.")

        # Get name of local file to write results to
        results_file = _get_filename(product['filename']) if destination == "Objectstore" else product['filename']
        try:
            row_count = export_to_file(host, product, results_file, catalogue, product.get('collection', collection))
        except Exception as e:
            logger.error(f"Exported to local file {name} failed: {str(e)}.")
        else:
            logger.info(f"{row_count} records exported to local file {name}.")

            if not product.get('append', False):
                # Do not add file to files again when appending
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
        logger.info(f"Connection to {destination} {user} has been made.")

    # Start distribution of all resulting files
    for file in files:
        logger.info(f"Write file '{file['distribution']}'.")
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
                                 Error: {e}")
                    return False

            logger.info(f"File distributed to {destination} on location: {container}{file['distribution']}.")

            # Delete temp file
            os.remove(file['temp_location'])

        elif destination == "File":
            logger.info(f"Export is written to {file['distribution']}.")

    logger.info("Export completed")


def export(catalogue, collection, destination):
    host = get_host()
    _export_collection(host=host,
                       catalogue=catalogue,
                       collection=collection,
                       destination=destination)
