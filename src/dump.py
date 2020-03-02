"""
Simple utility to be able to start exports to the analysis database from Jenkins

"""
import logging
import os
import json
import requests
import argparse
import re
import time

from gobexport.config import SECURE_URL
from gobexport.keycloak import get_secure_header
from gobexport.requests import get

config = {
    "ANALYSE_DATABASE_USER": None,
    "ANALYSE_DATABASE_PASSWORD": None,
    "ANALYSE_DATABASE_HOST_OVERRIDE": None,
    "ANALYSE_DATABASE_PORT_OVERRIDE": None,
}

RETRY_TIMEOUT = 300

for variable in config.keys():
    value = os.getenv(variable)
    if value is None:
        logging.error(f"Environment variable {variable} not set")
    else:
        config[variable] = value
assert None not in [config[variable] for variable in config.keys()], "Missing environment variables"


def update_headers(url, headers=None):
    headers = headers or {}
    if SECURE_URL in url:
        headers.update(get_secure_header())
    return headers


def get_catalog_collections(dump_api, catalog_name):
    url = f"{dump_api}/{catalog_name}/"
    result = get(url).json()
    catalog = {key: value for key, value in result.items() if key not in ['_links', '_embedded']}
    collections = result['_embedded']['collections']
    return catalog, collections


def get_relations(dump_api, catalog, collection):
    url = f"{dump_api}/rel/"
    result = get(url).json()
    abbreviation = f"{catalog['abbreviation']}_{collection['abbreviation']}".lower()
    relations = result['_embedded']['collections']
    return [collection for collection in relations if collection['name'].startswith(abbreviation)]


def dump_catalog(dump_api, catalog_name, collection_name):
    catalog, collections = get_catalog_collections(dump_api, catalog_name)
    if collection_name:
        collections = [collection for collection in collections if collection['name'] == collection_name]

    schema = catalog_name
    for collection in collections:
        dump_collection(dump_api, schema, catalog_name, collection['name'])
        for relation in get_relations(dump_api, catalog, collection):
            dump_collection(dump_api, schema, "rel", relation['name'])


def dump_collection(dump_api, schema, catalog_name, collection_name):
    MAX_TRIES = 3
    tries = 0
    while tries < MAX_TRIES:
        tries += 1
        print(f"Try {tries}: dump {catalog_name} - {collection_name}")
        if try_dump_collection(dump_api, schema, catalog_name, collection_name):
            return
        # Wait a little before next try
        time.sleep(RETRY_TIMEOUT)


def try_dump_collection(dump_api, schema, catalog_name, collection_name):
    url = f"{dump_api}/dump/{catalog_name}/{collection_name}/"
    data = json.dumps({
        "db": {
            "drivername": "postgres",
            "username": config['ANALYSE_DATABASE_USER'],
            "password": config['ANALYSE_DATABASE_PASSWORD'],
            "host": config['ANALYSE_DATABASE_HOST_OVERRIDE'],
            "port": config['ANALYSE_DATABASE_PORT_OVERRIDE']
        },
        "schema": schema,
        "include_relations": False
    })
    headers = {
        "Content-Type": "application/json"
    }

    print(f"Dump {catalog_name} - {collection_name} (schema: {schema})")
    start_request = time.time()
    success = False
    try:
        result = requests.post(url=url, json=None, data=data, headers=update_headers(url, headers), stream=True)

        lastline = ""
        start_line = time.time()
        for line in result.iter_lines(chunk_size=1):
            lastline = line.decode()
            end_line = time.time()
            print(f"{lastline} ({(end_line - start_line):.2f} / {(end_line - start_request):.2f} secs)")
            start_line = time.time()
    except Exception as e:
        print(f'ERROR: Export {catalog_name}-{collection_name} failed: {str(e)}')
    else:
        success = re.match(r'Export completed', lastline)
        if not success:
            print(f'ERROR: Export {catalog_name}-{collection_name} completed with errors')
    finally:
        end_request = time.time()
        print(f"Elapsed time: {(end_request - start_request):.2f} secs")
    return success


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Dump GOB collection via API to the analysis database'
    )
    parser.add_argument('dump_api', type=str, help='e.g. https://acc.api.data.amsterdam.nl/gob/secure')
    parser.add_argument('catalog', type=str, help='e.g. nap')
    parser.add_argument('collection', type=str, nargs="?", default="", help='e.g. peilmerken')
    args = parser.parse_args()

    # Compatibility fix
    DUMP_API = "/gob/dump"
    dump_api = args.dump_api.replace(DUMP_API, "/gob")

    dump_catalog(dump_api=dump_api, catalog_name=args.catalog, collection_name=args.collection)
