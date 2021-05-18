"""Meetbouten export

This module contains the export entries for the meetbouten catalog

"""
import os
import tempfile
import time
import sys
import traceback
import re

from objectstore.objectstore import delete_object, get_full_container_list

from gobcore.exceptions import GOBException
from gobcore.logging.logger import logger
from gobcore.datastore.factory import DatastoreFactory
from gobcore.datastore.objectstore import ObjectDatastore
from gobconfig.datastore.config import get_datastore_config

from gobexport.config import get_host, CONTAINER_BASE, EXPORT_DIR, GOB_OBJECTSTORE
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
                logger.warning("Operation failed, no retries left")
                raise e

            print("Caught exception:")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)

            logger.warning(f"Operation failed: {str(e)}, retry in {retry_timeout} seconds. Retries left: {max_tries}")
            time.sleep(retry_timeout)


def _append_to_file(src_file: str, dst_file: str):
    """Appends src_file to dst_file

    :param src_file:
    :param dst_file:
    :return:
    """
    with open(dst_file, 'a') as dst, open(src_file, 'r') as src:
        dst.write(src.read())


@with_buffered_iterable
def _export_collection(host, catalogue, collection, product_name, destination):  # noqa: C901
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
    try:
        products = {product_name: config.products[product_name]} if product_name else config.products
    except KeyError:
        logger.error(f"Product '{product_name}' not found")
        return

    # Start exporting each product
    for name, product in products.items():
        logger.info(f"Export to file '{name}' started, API type: {product.get('api_type', 'REST')}")

        # Get name of local file to write results to
        results_file = _get_filename(product['filename']) if destination == "Objectstore" else product['filename']

        if product.get('append', False):
            # Add .to_append to avoid writing to the previously created file
            results_file = _get_filename(f"{product['filename']}.to_append")
            product['append_to_filename'] = _get_filename(product['filename']) \
                if destination == "Objectstore" \
                else product['filename']

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

            if product.get('append', False):
                # Append temporary file to existing file and cleanup temp file
                _append_to_file(results_file, product['append_to_filename'])
                os.remove(results_file)
            else:
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
        config = get_datastore_config(GOB_OBJECTSTORE)
        datastore = DatastoreFactory.get_datastore(config)
        datastore.connect()

        assert isinstance(datastore, ObjectDatastore)

        connection = datastore.connection
        logger.info(f"Connection to {destination} {datastore.user} has been made.")

    # Start distribution of all resulting files
    for file in files:
        logger.info(f"Write file '{file['distribution']}'.")
        if destination == "Objectstore":
            # Distribute to pre-final location
            container = f'{CONTAINER_BASE}/{EXPORT_DIR}/{catalogue}/'
            with open(file['temp_location'], 'rb') as fp:
                try:
                    distribute_to_objectstore(connection,
                                              container,
                                              file['distribution'],
                                              fp,
                                              file['mime_type'])
                except GOBException as e:
                    logger.error(f"Failed to copy to {destination} on location: {container}{file['distribution']}. \
                                 Error: {e}")
                    return False

            logger.info(f"File copied to {destination} on location: {container}{file['distribution']}.")

            cleanup_datefiles(connection, CONTAINER_BASE, f"{EXPORT_DIR}/{catalogue}/{file['distribution']}")

            # Delete temp file
            os.remove(file['temp_location'])

        elif destination == "File":
            logger.info(f"Export is written to {file['distribution']}.")

    logger.info("Export completed")


def cleanup_datefiles(connection, container, filename):
    """Delete previous files from ObjectStore.

    The file with filename is not deleted.
    """
    cleanup_pattern = get_cleanup_pattern(filename)
    if cleanup_pattern == filename:
        # No dates in filename, nothing to do
        return

    logger.info(f'Clean previous files for {filename}.')

    for item in get_full_container_list(connection, container):
        if re.match(cleanup_pattern, item['name']) and item['name'] != filename:
            delete_object(connection, container, item)
            logger.info(f'File {item["name"]} deleted.')


def get_cleanup_pattern(filename):
    """Detect dates and replace the date by it's regex."""
    return re.sub(r"\d{8}", r"\\d{8}", filename)


def export(catalogue, collection, product, destination):
    host = get_host()
    _export_collection(host=host,
                       catalogue=catalogue,
                       collection=collection,
                       product_name=product,
                       destination=destination)
