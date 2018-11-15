import re

from gobexport.api import API
from gobexport.exporter.config.meetbouten import MeetboutExportConfig, MetingenExportConfig, \
                                     ReferentiepuntenExportConfig, RollagenExportConfig
from gobexport.exporter.config.nap import PeilmerkenExportConfig
from gobexport.exporter.types import type_convert


CONFIG_MAPPING = {
    'meetbouten': {
        'meetbouten': MeetboutExportConfig,
        'metingen': MetingenExportConfig,
        'referentiepunten': ReferentiepuntenExportConfig,
        'rollagen': RollagenExportConfig,
    },
    'nap': {
        'peilmerken': PeilmerkenExportConfig,
    }
}


def _export_entity(entity, format):
    """Exports a single entity

    Headers:       None
    Separator:     |
    String marker: $$


    The export format is a string containing the attributes and types to be converted.
    A declarative way of describing exports is used:
    The export format is used both to read the attributes and types and to write the correct output format.

    :param meetbout:
    :return:
    """
    pattern = re.compile('(\w+):(\w+):?(\w+)?\|?')
    export = []
    for (attr_name, attr_type, args) in re.findall(pattern, format):
        attr_value = type_convert(attr_type, entity.get(attr_name, None), args)
        export.append(attr_value)
    return '|'.join(export)


def export_to_file(catalog, collection, host, file):
    """Export a collection from a catalog to a file

    The entities that are exposed by the specified API host are retrieved, converted and written to
    the specified output file

    :param collection: The collection to export
    :param host: The API host
    :param file: The name of the file to write the ouput
    :return: None
    """
    config = CONFIG_MAPPING[catalog][collection]
    api = API(host=host, path=config.path)

    row_count = 0

    with open(file, 'w') as fp:
        for entity in api:
            row_count += 1
            fp.write(_export_entity(entity, config.format) + '\n')

    return row_count