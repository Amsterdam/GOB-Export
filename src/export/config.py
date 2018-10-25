"""Config

Export configuration

The API HOST is retrieved from the environment.
A default value is available for local development.

The collection and file are retrieved from the command line arguments

"""
import os
import argparse

_DEFAULT_API_HOST = 'http://localhost:5000'


def get_host():
    """API Host

    :return: The API host to get the collection from
    """
    return os.getenv('API_HOST', _DEFAULT_API_HOST)


def get_args():
    """Arguments

    Retrieved the commanad line arguments:
        collection: The collection to export
        file: The name of the file to write the results to

    :return: A dictionary containing the collection and file names
    """
    parser = argparse.ArgumentParser(description='Export data collection')
    parser.add_argument('catalog', type=str,
                        help='the name of the data catalog (example: "meetbouten"')
    parser.add_argument('collection', type=str,
                        help='the name of the data collection (example: "meetbouten"')
    parser.add_argument('file_name', type=str,
                        help='the name of the file to write the output to (example: "/tmp/MBT_MEETBOUT.dat")')
    return parser.parse_args()
