"""Meetbouten export

This module contains the export entries for the meetbouten catalog

"""

from export.meetbouten.meetbout import export_meetbouten
from export.config import get_host, get_args


def export_collection(host, collection, file):
    """Export a collection

    :param host: The API host to retrieve the collection from
    :param collection: The name of the collection
    :param file: The file to write the export results to
    :return:
    """
    exporter = {
        'meetbouten': export_meetbouten
    }
    exporter[collection](host, file)


host = get_host()
args = get_args()

export_collection(host=host, collection=args.collection, file=args.file)
