"""Config

Export configuration

The API HOST is retrieved from the environment.
A default value is available for local development.

The collection and file are retrieved from the command line arguments

"""
import os


_DEFAULT_API_HOST = 'http://localhost:5000'
CONTAINER_BASE = os.getenv('CONTAINER_BASE', 'distributie')


def get_host():
    """API Host

    :return: The API host to get the collection from
    """
    return os.getenv('API_HOST', _DEFAULT_API_HOST)
