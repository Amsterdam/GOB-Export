"""
Simple utility to be able to start exports to the analysis database from Jenkins

"""
import logging
import os
import json
import requests
import re
import time

from gobcore.logging.logger import logger

from gobexport.config import PUBLIC_URL, SECURE_URL, get_host
from gobexport.keycloak import get_secure_header
from gobexport.requests import get


class Dumper():

    config = {}
    dump_api = None
    RETRY_TIMEOUT = 300

    def __init__(self):
        if not Dumper.config:
            self._init_config()

    def _init_config(self):
        api_host = get_host()
        api_url = PUBLIC_URL if "localhost" in api_host else SECURE_URL
        Dumper.dump_api = f"{api_host}{api_url}"
        variables = [
            "ANALYSE_DATABASE_USER",
            "ANALYSE_DATABASE_PASSWORD",
            "ANALYSE_DATABASE_HOST_OVERRIDE",
            "ANALYSE_DATABASE_PORT_OVERRIDE"
        ]
        for variable in variables:
            value = os.getenv(variable)
            if value is None:
                logging.error(f"Environment variable {variable} not set")
            else:
                Dumper.config[variable] = value

    def update_headers(self, url, headers=None):
        headers = headers or {}
        if SECURE_URL in url:
            headers.update(get_secure_header())
        return headers

    def get_catalog_collections(self, catalog_name):
        url = f"{self.dump_api}/{catalog_name}/"
        result = get(url).json()
        catalog = {key: value for key, value in result.items() if key not in ['_links', '_embedded']}
        collections = result['_embedded']['collections']
        return catalog, collections

    def get_relations(self, catalog, collection):
        url = f"{self.dump_api}/rel/"
        result = get(url).json()
        abbreviation = f"{catalog['abbreviation']}_{collection['abbreviation']}".lower()
        relations = result['_embedded']['collections']
        return [collection for collection in relations if collection['name'].startswith(abbreviation)]

    def dump_catalog(self, catalog_name, collection_name):
        catalog, collections = self.get_catalog_collections(catalog_name)
        if collection_name:
            collections = [collection for collection in collections if collection['name'] == collection_name]

        schema = catalog_name
        for collection in collections:
            self.dump_collection(schema, catalog_name, collection['name'])
            for relation in self.get_relations(catalog, collection):
                self.dump_collection(schema, "rel", relation['name'])

    def dump_collection(self, schema, catalog_name, collection_name):
        MAX_TRIES = 3
        tries = 0
        while tries < MAX_TRIES:
            tries += 1
            logger.info(f"Try {tries}: dump {catalog_name} - {collection_name}")
            if self.try_dump_collection(schema, catalog_name, collection_name):
                return
            # Wait a little before next try
            time.sleep(self.RETRY_TIMEOUT)

    def try_dump_collection(self, schema, catalog_name, collection_name):
        url = f"{self.dump_api}/dump/{catalog_name}/{collection_name}/"
        data = json.dumps({
            "db": {
                "drivername": "postgres",
                "username": self.config['ANALYSE_DATABASE_USER'],
                "password": self.config['ANALYSE_DATABASE_PASSWORD'],
                "host": self.config['ANALYSE_DATABASE_HOST_OVERRIDE'],
                "port": self.config['ANALYSE_DATABASE_PORT_OVERRIDE']
            },
            "schema": schema,
            "include_relations": False
        })
        headers = {
            "Content-Type": "application/json"
        }

        logger.info(f"Dump {catalog_name} - {collection_name} (schema: {schema})")
        start_request = time.time()
        success = False
        try:
            result = requests.post(
                url=url,
                json=None,
                data=data,
                headers=self.update_headers(url, headers),
                stream=True
            )

            lastline = ""
            start_line = time.time()
            for line in result.iter_lines(chunk_size=1):
                lastline = line.decode()
                end_line = time.time()
                logger.info(f"{lastline} ({(end_line - start_line):.2f} / {(end_line - start_request):.2f} secs)")
                start_line = time.time()
        except Exception as e:
            logger.error(f'Export {catalog_name}-{collection_name} failed: {str(e)}')
        else:
            success = re.match(r'Export completed', lastline)
            if not success:
                logger.error(f'Export {catalog_name}-{collection_name} completed with errors')
        finally:
            end_request = time.time()
            logger.info(f"Elapsed time: {(end_request - start_request):.2f} secs")
        return success
