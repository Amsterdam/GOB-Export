"""
Dumps GOB data to the analysis database

"""
import requests
import re
import time

from gobcore.logging.logger import logger
from gobconfig.datastore.config import get_datastore_config

from gobexport.config import PUBLIC_URL, SECURE_URL, get_host
from gobexport.keycloak import get_secure_header
from gobexport.requests import get

ANALYSE_DB_DATASTORE_ID = 'GOBAnalyse'
SECURE_USER = 'gob'


class Dumper:

    MAX_TRIES = 3
    RETRY_TIMEOUT = 300

    def __init__(self):
        self._init_config()

    def _init_config(self):
        """
        Initialize dumper configuration

        If localhost is used then use the public GOB url for all other case use the GOB secure url.
        Read the destination database properties from the environment

        :return:
        """
        api_host = get_host()
        api_url = PUBLIC_URL if any(host in api_host for host in ["localhost", "gobapi"]) else SECURE_URL
        self.dump_api = f"{api_host}{api_url}"
        self.db_config = get_datastore_config(ANALYSE_DB_DATASTORE_ID)

    def update_headers(self, url, headers=None):
        """
        Update the request headers with authorization parameters if the secure GOB url is used for a request

        :param url:
        :param headers:
        :return:
        """
        headers = headers or {}
        if SECURE_URL in url:
            headers.update(get_secure_header(SECURE_USER))
        return headers

    def get_catalog_collections(self, catalog_name):
        """
        Get all collections for a given catalog name

        :param catalog_name:
        :return:
        """
        url = f"{self.dump_api}/{catalog_name}/"
        result = get(url, secure_user=SECURE_USER).json()
        catalog = {key: value for key, value in result.items() if key not in ['_links', '_embedded']}
        collections = result['_embedded']['collections']
        return catalog, collections

    def get_relations(self, catalog, collection):
        """
        Get all releations for a given catalog collection

        :param catalog:
        :param collection:
        :return:
        """
        url = f"{self.dump_api}/rel/"
        result = get(url, secure_user=SECURE_USER).json()
        abbreviation = f"{catalog['abbreviation']}_{collection['abbreviation']}".lower()
        relations = result['_embedded']['collections']
        return [collection for collection in relations if collection['name'].startswith(abbreviation)]

    def dump_catalog(self, catalog_name, collection_name, include_relations=True, force_full=False):
        """
        Dump a catalog. If a collection is specified only dump the given catalog collection.

        The relations for the given catalog (and collection) are also dumped.

        :param catalog_name:
        :param collection_name:
        :return:
        """
        catalog, collections = self.get_catalog_collections(catalog_name)
        if collection_name:
            collections = [collection for collection in collections if collection['name'] == collection_name]

        schema = catalog_name
        for collection in collections:
            self.dump_collection(schema, catalog_name, collection['name'], force_full)
            if include_relations:
                for relation in self.get_relations(catalog, collection):
                    self.dump_collection(schema, "rel", relation['name'], force_full)

    def dump_collection(self, schema, catalog_name, collection_name, force_full=False):
        """
        Dump a catalog collection into a remote database in the given schema

        If the dump fails the operation is retried with a maximum of MAX_TRIES
        and a wait between each try of RETRY_TIMEOUT seconds
        :param schema:
        :param catalog_name:
        :param collection_name:
        :return:
        """
        tries = 0
        while tries < Dumper.MAX_TRIES:
            tries += 1
            logger.info(f"Try {tries}: dump {catalog_name} - {collection_name}")
            if self.try_dump_collection(schema, catalog_name, collection_name, force_full):
                # On Successful dump
                return
            # Wait RETRY_TIMEOUT seconds before next try
            time.sleep(self.RETRY_TIMEOUT)
        logger.error(f'Export {catalog_name}-{collection_name} failed after {Dumper.MAX_TRIES}')

    def try_dump_collection(self, schema, catalog_name, collection_name, force_full=False):
        """
        Try to dump the given catalog collection in the given schema

        The dump is performed by issuing an API POST request to the GOB API.

        :param schema:
        :param catalog_name:
        :param collection_name:
        :return:
        """
        url = f"{self.dump_api}/dump/{catalog_name}/{collection_name}/"
        data = {
            "db": self.db_config,
            "schema": schema,
            "include_relations": False,
            "force_full": force_full,
        }
        headers = {
            "Content-Type": "application/json"
        }

        logger.info(f"Dump {catalog_name} - {collection_name} (schema: {schema})")
        start_request = time.time()
        success = False
        try:
            result = requests.post(
                url=url,
                json=data,
                headers=self.update_headers(url, headers),
                stream=True
            )

            last_line = ""
            start_line = time.time()
            for line in result.iter_lines(chunk_size=1):
                last_line = line.decode()
                end_line = time.time()
                logger.info(f"{last_line} ({(end_line - start_line):.2f} / {(end_line - start_request):.2f} secs)")
                start_line = time.time()
        except Exception as e:
            logger.warning(f'Export {catalog_name}-{collection_name} failed: {str(e)}')
        else:
            success = re.match(r'Export completed', last_line) is not None
            if not success:
                logger.warning(f'Export {catalog_name}-{collection_name} completed with errors')
        finally:
            end_request = time.time()
            logger.info(f"Elapsed time: {(end_request - start_request):.2f} secs")
        return success
