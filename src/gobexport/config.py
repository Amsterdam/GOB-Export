"""Config

Export configuration

The API HOST is retrieved from the environment.
A default value is available for local development.

The collection and file are retrieved from the command line arguments

"""
import os

from gobcore.exceptions import GOBException


_DEFAULT_API_HOST = 'http://localhost:8141'
CONTAINER_BASE = os.getenv('CONTAINER_BASE', 'development')

OIDC_TOKEN_ENDPOINT = os.getenv("OIDC_TOKEN_ENDPOINT")
OIDC_CLIENT_ID = os.getenv("OIDC_CLIENT_ID")
OIDC_CLIENT_SECRET = os.getenv("OIDC_CLIENT_SECRET")

# Definition of URLs for public and secure endpoints
PUBLIC_URL = '/gob'
SECURE_URL = '/gob/secure'

OBJECTSTORE_CONFIGS = {
    'Basisinformatie': {
        "VERSION": '2.0',
        "AUTHURL": 'https://identity.stack.cloudvps.com/v2.0',
        "TENANT_NAME": os.getenv("BASISINFORMATIE_OBJECTSTORE_TENANT_NAME"),
        "TENANT_ID": os.getenv("BASISINFORMATIE_OBJECTSTORE_TENANT_ID"),
        "USER": os.getenv("BASISINFORMATIE_OBJECTSTORE_USER"),
        "PASSWORD": os.getenv("BASISINFORMATIE_OBJECTSTORE_PASSWORD"),
        "REGION_NAME": 'NL'
    }
}


def get_objectstore_config(name: str):
    try:
        config = OBJECTSTORE_CONFIGS[name]
    except KeyError:
        raise GOBException(f"Objectstore config for source {name} not found.")

    config['name'] = name
    return config


def get_host():
    """API Host

    :return: The API host to get the collection from
    """
    return os.getenv('API_HOST', _DEFAULT_API_HOST)
