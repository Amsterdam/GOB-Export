from gobexport.api import API
from gobexport.exporter.config import bag, brk, gebieden, meetbouten, nap, test
from gobexport.graphql import GraphQL
from gobexport.graphql_streaming import GraphQLStreaming
from gobexport.buffered_iterable import BufferedIterable
from gobexport.filters.group_filter import GroupFilter

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
        'aardzakelijkerechten': brk.AardzakelijkerechtenExportConfig,
        'brkbag': brk.BrkBagExportConfig,
        'stukdelen': brk.StukdelenExportConfig,
        'kadastraleobjecten': brk.KadastraleobjectenExportConfig,
        'gemeentes': brk.GemeentesExportConfig,
        'bijpijling': brk.BijpijlingExportConfig,
    }
}


def product_source(product):
    return product.get('endpoint', product.get('query'))


def export_to_file(host, product, file, catalogue, collection, buffer_items=False):
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
    unfold = product.get('unfold', False)

    if product.get('api_type') == 'graphql':
        # Use GraphQL
        query = product['query']
        expand_history = product.get('expand_history')
        sort = product.get('sort')
        api = GraphQL(host, query, catalogue, collection, expand_history, sort, unfold=unfold)
    elif product.get('api_type') == 'graphql_streaming':
        query = product['query']
        api = GraphQLStreaming(host, query, unfold)
    else:
        # Use the REST API
        endpoint = product.get('endpoint')
        api = API(host=host, path=endpoint)

    exporter = product.get('exporter')
    format = product.get('format')

    buffered_api = BufferedIterable(api, product_source(product), buffer_items=buffer_items)

    kwargs = {}

    if product.get('entity_filters'):
        kwargs['filter'] = GroupFilter(product['entity_filters'])

    row_count = exporter(buffered_api, file, format, append=product.get('append', False), **kwargs)

    return row_count
