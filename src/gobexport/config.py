"""Config

Export configuration

The API HOST is retrieved from the environment.
A default value is available for local development.

The collection and file are retrieved from the command line arguments

"""
import os


_DEFAULT_API_HOST = 'http://localhost:8141'
CONTAINER_BASE = os.getenv('CONTAINER_BASE', 'development')

OIDC_TOKEN_ENDPOINT = os.getenv("OIDC_TOKEN_ENDPOINT")
OIDC_CLIENT_ID = os.getenv("OIDC_CLIENT_ID")
OIDC_CLIENT_SECRET = os.getenv("OIDC_CLIENT_SECRET")

# Definition of URLs for public and secure endpoints
PUBLIC_URL = '/gob'
SECURE_URL = '/gob/secure'


def get_host():
    """API Host

    :return: The API host to get the collection from
    """
    return os.getenv('API_HOST', _DEFAULT_API_HOST)
