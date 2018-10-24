"""Meetbouten export

This module contains the export entries for the meetbouten catalog

"""
from export.meetbouten import export_meetbouten
from export.config import get_host, get_args


def export_collection(host, catalog, collection, file):
    """Export a collection from a catalog

    :param host: The API host to retrieve the catalog and collection from
    :param catalog: The name of the catalog
    :param collection: The name of the collection
    :param file: The file to write the export results to
    :return:
    """
    exporter = {
        'meetbouten': export_meetbouten
    }
    exporter[catalog](collection, host, file)


host = get_host()
args = get_args()

export_collection(host=host, catalog=args.catalog, collection=args.collection, file=args.file)
