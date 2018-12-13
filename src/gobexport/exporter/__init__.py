from gobexport.api import API
from gobexport.exporter.config.gebieden import StadsdelenExportConfig, WijkenExportConfig, \
                                    BuurtenExportConfig, BouwblokkenExportConfig
from gobexport.exporter.config.meetbouten import MeetboutExportConfig, MetingenExportConfig, \
                                     ReferentiepuntenExportConfig, RollagenExportConfig
from gobexport.exporter.config.nap import PeilmerkenExportConfig
from gobexport.exporter.config.test import TestEntityExportConfig


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
        'stadsdelen': StadsdelenExportConfig,
    }
}


def export_to_file(host, endpoint, exporter, file, format):
    """Export a collection from a catalog a file.

    The entities that are exposed by the specified API host are retrieved, converted and written to
    the specified output file

    :param host: The API host
    :param endpoint: The API endpoint
    :param exporter: The function used to write to file
    :param file: The name of the file to write the ouput
    :return: The number of exported rows
    """
    api = API(host=host, path=endpoint)

    row_count = exporter(api, file, format)

    return row_count
