from gobexport.api import API
from gobexport.exporter.config import bag, brk, gebieden, meetbouten, nap, test
from gobexport.graphql import GraphQL

CONFIG_MAPPING = {
    'test_catalogue': {
        'test_entity': test.TestEntityExportConfig
    },
    'meetbouten': {
        'meetbouten': meetbouten.MeetboutExportConfig,
        'metingen': meetbouten.MetingenExportConfig,
        'referentiepunten': meetbouten.ReferentiepuntenExportConfig,
        'rollagen': meetbouten.RollagenExportConfig,
    },
    'nap': {
        'peilmerken': nap.PeilmerkenExportConfig,
    },
    'gebieden': {
        'bouwblokken': gebieden.BouwblokkenExportConfig,
        'buurten': gebieden.BuurtenExportConfig,
        'wijken': gebieden.WijkenExportConfig,
        'ggwgebieden': gebieden.GGWGebiedenExportConfig,
        'ggpgebieden': gebieden.GGPGebiedenExportConfig,
        'stadsdelen': gebieden.StadsdelenExportConfig,
    },
    'bag': {
        'woonplaatsen': bag.WoonplaatsenExportConfig,
        'openbareruimtes': bag.OpenbareruimtesExportConfig,
        'nummeraanduidingen': bag.NummeraanduidingenExportConfig,
        'verblijfsobjecten': bag.VerblijfsobjectenExportConfig,
        'ligplaatsen': bag.LigplaatsenExportConfig,
        'standplaatsen': bag.StandplaatsenExportConfig,
        'panden': bag.PandenExportConfig,
        'brondocumenten': bag.BrondocumentenExportConfig,
    },
    'brk': {
        'kadastralesubjecten': brk.KadastralesubjectenExportConfig,
        'aantekeningen': brk.AantekeningenExportConfig,
        'zakelijkerechten': brk.ZakelijkerechtenExportConfig,
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

    row_count = exporter(api, file, format, append=product.get('append', False))

    return row_count
