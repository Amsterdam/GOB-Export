from gobexport.api import API
from gobexport.exporter.config.gebieden import StadsdelenExportConfig, GGWGebiedenExportConfig, \
                                    GGPGebiedenExportConfig, WijkenExportConfig, \
                                    BuurtenExportConfig, BouwblokkenExportConfig
from gobexport.exporter.config.meetbouten import MeetboutExportConfig, MetingenExportConfig, \
                                     ReferentiepuntenExportConfig, RollagenExportConfig
from gobexport.exporter.config.nap import PeilmerkenExportConfig
from gobexport.exporter.config.test import TestEntityExportConfig
from gobexport.graphql import GraphQL

CONFIG_MAPPING = {
    'test_catalogue': {
        'test_entity': TestEntityExportConfig
    },
    'meetbouten': {
        'meetbouten': MeetboutExportConfig,
        'metingen': MetingenExportConfig,
        'referentiepunten': ReferentiepuntenExportConfig,
        'rollagen': RollagenExportConfig,
    },
    'nap': {
        'peilmerken': PeilmerkenExportConfig,
    },
    'gebieden': {
        'bouwblokken': BouwblokkenExportConfig,
        'buurten': BuurtenExportConfig,
        'wijken': WijkenExportConfig,
        'ggwgebieden': GGWGebiedenExportConfig,
        'ggpgebieden': GGPGebiedenExportConfig,
        'stadsdelen': StadsdelenExportConfig,
    }
}


def export_to_file(host, product, file, catalogue, collection):
    """Export a collection from a catalog a file.

    The entities that are exposed by the specified API host are retrieved, converted and written to
    the specified output file

    :param host: The API host
    :param product: The product definition for this export type
    :param file: The name of the file to write the ouput
    :param catalogue: The catalogue to export
    :param collection: The collection to export
    :return: The number of exported rows
    """
    if product.get('api_type') == 'graphql':
        # Use GraphQL
        query = product['query']
        expand_history = product.get('expand_history')
        api = GraphQL(host, query, catalogue, collection, expand_history)
    else:
        # Use the REST API
        endpoint = product.get('endpoint')
        api = API(host=host, path=endpoint)

    exporter = product.get('exporter')
    format = product.get('format')

    row_count = exporter(api, file, format)

    return row_count
