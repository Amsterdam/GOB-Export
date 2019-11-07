"""Meetbouten export

This module contains the export entries for the meetbouten catalog

"""
import os
import tempfile
import time
import sys
import traceback

from gobcore.exceptions import GOBException
from gobcore.logging.logger import logger

from gobexport.config import get_host, CONTAINER_BASE
from gobexport.connector.objectstore import connect_to_objectstore
from gobexport.distributor.objectstore import distribute_to_objectstore
from gobexport.exporter import CONFIG_MAPPING, export_to_file, product_source
from gobexport.buffered_iterable import with_buffered_iterable
from gobexport.utils import resolve_config_filenames

_MAX_TRIES = 3          # Default number of times to try the export
_RETRY_TIMEOUT = 300    # Default seconds between consecutive retries


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


def _with_retries(method, max_tries=_MAX_TRIES, retry_timeout=_RETRY_TIMEOUT, exc=Exception):
    """
    Run method, retry n_tries times if any exception is raised

    :param method: any method to execute
    :param max_tries: number of tries, if <=0 method will not be executed and None is returned
    :param exc: Exception class to catch (eg KeyError)
    :raises: exc if method fails n_tries time
    :return: result of method()
    """
    while max_tries > 0:
        max_tries -= 1
        try:
            return method()
        except exc as e:
            if max_tries == 0:
                logger.warning(f"Operation failed, no retries left")
                raise e

            print("Caught exception:")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)

            logger.warning(f"Operation failed: {str(e)}, retry in {retry_timeout} seconds. Retries left: {max_tries}")
            time.sleep(retry_timeout)


@with_buffered_iterable  # noqa: C901
def _export_collection(host, catalogue, collection, product_name, destination):
    """Export a collection from a catalog

    :param host: The API host to retrieve the catalog and collection from
    :param catalog: The name of the catalog
    :param collection: The name of the collection
    :param product_name: The name of the product to export
    :param destination: The destination of the resulting output file(s)
    :return:
    """
    logger.info(f"Export {catalogue}:{collection} to {destination} started.")

    # Get the configuration for this collection
    config = CONFIG_MAPPING[catalogue][collection]
    resolve_config_filenames(config)

    files = []

    # If a product has been supplied, export only that product
    products = {product_name: config.products[product_name]} if product_name else config.products

    # Start exporting each product
    for name, product in products.items():
        logger.info(f"Export to file '{name}' started, API type: {product.get('api_type', 'REST')}")

        # Get name of local file to write results to
        results_file = _get_filename(product['filename']) if destination == "Objectstore" else product['filename']

        # Buffer items if they are used multiple times. This prevents calling API multiple times for same data
        source = product_source(product)
        buffer_items = len(list(filter(lambda p: product_source(p) == source, config.products.values()))) > 1

        logger.info(f"Buffering API output {'enabled' if buffer_items else 'disabled'}")
        try:
            row_count = _with_retries(lambda: export_to_file(
                host,
                product,
                results_file,
                catalogue,
                product.get('collection', collection),
                buffer_items=buffer_items))
        except Exception as e:
            logger.error(f"Export to local file {name} failed: {str(e)}.")
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


def export(catalogue, collection, product, destination):
    host = get_host()
    _export_collection(host=host,
                       catalogue=catalogue,
                       collection=collection,
                       product_name=product,
                       destination=destination)
