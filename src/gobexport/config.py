"""Config

Export configuration

The API HOST is retrieved from the environment.
A default value is available for local development.

The collection and file are retrieved from the command line arguments

"""
import os


def _getenv(varname, default_value=None, is_optional=False):
    """
    Returns the value of the environment variable "varname"
    or the default value if the environment variable is not set

    :param varname: name of the environment variable
    :param default_value: value to return if variable is not set
    :raises AssertionError: if variable not set or value is empty
    :return: the value of the given variable
    """
    value = os.getenv(varname, default_value)
    assert is_optional or value, f"Environment variable '{varname}' not set or empty"
    return value


_DEFAULT_API_HOST = 'http://localhost:8141'
CONTAINER_BASE = os.getenv('CONTAINER_BASE', 'development')

# Let export write products to tmp folder within the container base
EXPORT_DIR = "_tmp"

OIDC_TOKEN_ENDPOINT = os.getenv("OIDC_TOKEN_ENDPOINT")

# Definition of URLs for public and secure endpoints
PUBLIC_URL = '/gob/public'
SECURE_URL = '/gob'

GOB_OBJECTSTORE = 'GOBObjectstore'
BASISINFORMATIE_OBJECTSTORE = 'Basisinformatie'

GOB_EXPORT_API_PORT = os.getenv('GOB_EXPORT_API_PORT', 8168)
API_BASE_PATH = os.getenv("BASE_PATH", default="")

# Logging for the API.
# Logging for services is configured in services.py
API_LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "default"
        },
    },
    "loggers": {
        "tests": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
        "gobexport": {
            "handlers": ["console"],
            "level": "INFO",
        },
    }
}


def get_host():
    """API Host

    :return: The API host to get the collection from
    """
    return os.getenv('API_HOST', _DEFAULT_API_HOST)


def get_oidc_client(client_name):
    """Get the OIDC client id and secret

    :return:
    """
    client_name = client_name.upper()
    return {
        'id': _getenv(f'OIDC_CLIENT_ID_{client_name}'),
        'secret': _getenv(f'OIDC_CLIENT_SECRET_{client_name}'),
    }


def get_public_key(key_name):
    """Public SSH key

    :return: The public ssh key to encrypt a file
    """
    return _getenv(f'PUBLIC_KEY_{key_name.upper()}')
