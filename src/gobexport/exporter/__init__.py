"""Exporter init and mapping."""


from gobexport.api import API
from gobexport.buffered_iterable import BufferedIterable
from gobexport.exporter.config import bag, bgt, brk, brk2, gebieden, meetbouten, nap, test, wkpb
from gobexport.exporter.encryption import encrypt_file
from gobexport.filters.group_filter import GroupFilter
from gobexport.graphql import GraphQL
from gobexport.graphql_streaming import GraphQLStreaming
from gobexport.merged_api import MergedApi
from gobexport.objectstore import ObjectstoreFile

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
        'onderzoeken': bag.OnderzoekenExportConfig,
    },
    'brk': {
        'kadastralesubjecten': brk.KadastralesubjectenExportConfig,
        'aantekeningenrechten': brk.AantekeningenrechtenExportConfig,
        'zakelijkerechten': brk.ZakelijkerechtenExportConfig,
        'aardzakelijkerechten': brk.AardzakelijkerechtenExportConfig,
        'stukdelen': brk.StukdelenExportConfig,
        'kadastraleobjecten': brk.KadastraleobjectenExportConfig,
        'gemeentes': brk.GemeentesExportConfig,
        'kadastralegemeentecodes': brk.KadastraleGemeentecodesExportConfig,
        'kadastralesecties': brk.KadastralesectiesExportConfig,
    },
    'brk2': {
        'kadastraleobjecten': brk2.KadastraleobjectenExportConfig,
        'gemeentes': brk2.GemeentesExportConfig,
        'kadastralegemeentecodes': brk2.KadastralegemeentecodesExportConfig,
        'kadastralesecties': brk2.KadastralesectiesExportConfig,
        'aantekeningen': brk2.AantekeningenExportConfig,
        'zakelijkerechten': brk2.ZakelijkerechtenExportConfig,
        'stukdelen': brk2.StukdelenExportConfig
    },
    'bgt': {
        'onderbouw': bgt.OnderbouwExportConfig,
        'overbouw': bgt.OverbouwExportConfig,
    },
    'wkpb': {
        'beperkingen': wkpb.BeperkingenExportConfig,
        'brondocumenten': wkpb.BrondocumentenExportConfig,
    }
}


def product_source(product):
    return product.get('endpoint', product.get('query', product.get('filename')))


def _init_api(product: dict, host: str, catalogue: str, collection: str):
    unfold = product.get('unfold', False)
    secure_user = product.get('secure_user')

    if product.get('api_type') == 'graphql':
        # Use GraphQL
        query = product['query']
        expand_history = product.get('expand_history')
        sort = product.get('sort')
        api = GraphQL(host, query, catalogue, collection, expand_history, sort=sort, unfold=unfold,
                      secure_user=secure_user, row_formatter=product.get('row_formatter'),
                      cross_relations=product.get('cross_relations', False))
    elif product.get('api_type') == 'graphql_streaming':
        query = product['query']
        api = GraphQLStreaming(host, query, unfold=unfold, sort=product.get('sort'), secure_user=secure_user,
                               row_formatter=product.get('row_formatter'),
                               cross_relations=product.get('cross_relations', False),
                               batch_size=product.get('batch_size'))
    elif product.get('api_type') == 'objectstore':
        config = product['config']
        api = ObjectstoreFile(config, row_formatter=product.get('row_formatter'))
    else:
        # Use the REST API
        endpoint = product.get('endpoint')
        api = API(host=host, path=endpoint, row_formatter=product.get('row_formatter'), secure_user=secure_user)

    if product.get('merge_result'):
        # A secondary API is defined. Return a new MergedAPI object that combines the results from both API's.
        api2_product = product.get('merge_result')
        api2 = _init_api(api2_product, host, catalogue, collection)
        api = MergedApi(api, api2, api2_product['match_attributes'], api2_product['attributes'])

    return api


def export_to_file(host, product, file_path, catalogue, collection, buffer_items=False):
    """Export a collection from a catalog to a file.

    The entities that are exposed by the specified API host are retrieved, converted and written to
    the specified output file.

    :param host: The API host
    :param product: The product definition for this export type
    :param file_path: The path of the file to write the output to
    :param catalogue: The catalogue to export
    :param collection: The collection to export
    :return: The number of exported rows
    """
    api = _init_api(product, host, catalogue, collection)

    exporter = product.get('exporter')
    format = product.get('format')

    buffered_api = BufferedIterable(api, product_source(product), buffer_items=buffer_items)

    kwargs = {}

    filter = GroupFilter(product['entity_filters']) if product.get('entity_filters') else None
    kwargs['filter'] = filter

    row_count = exporter(buffered_api, file_path, format,
                         append=product.get('append', False) and product['append_to_filename'],
                         **kwargs)

    if product.get('encryption_key'):
        encrypt_file(file_path, product.get('encryption_key'))

    # Reset the entity filter(s)
    if filter:
        filter.reset()

    return row_count
