from gobexport.exporter.csv import csv_exporter
from gobexport.exporter.esri import esri_exporter
from gobexport.formatter.geometry import format_geometry
from gobexport.exporter.config.brk.utils import brk_filename, brk_directory


class GemeentesExportConfig:
    query = '''
{
  brkGemeentes(sort:naam_asc) {
    edges {
      node {
        identificatie
        naam
        geometrie
      }
    }
  }
}
'''

    shp_filename = 'BRK_GEMEENTE'
    products = {
        'csv': {
            'exporter': csv_exporter,
            'api_type': 'graphql',
            'secure_user': 'gob',
            'query': query,
            'filename': lambda: brk_filename('Gemeente', type='csv', use_sensitive_dir=False),
            'mime_type': 'plain/text',
            'format': {
                'naam': 'naam',
                'identificatie': 'identificatie',
                'geometrie': {
                    'action': 'format',
                    'formatter': format_geometry,
                    'value': 'geometrie'
                },
            }
        },
        'shape': {
            'exporter': esri_exporter,
            'api_type': 'graphql',
            'secure_user': 'gob',
            'filename': f'{brk_directory("shp", use_sensitive_dir=False)}/{shp_filename}.shp',
            'mime_type': 'application/octet-stream',
            'format': {
                'GEMEENTE': 'naam',
            },
            'extra_files': [
                {
                    'filename': f'{brk_directory("dbf", use_sensitive_dir=False)}/{shp_filename}.dbf',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': f'{brk_directory("shx", use_sensitive_dir=False)}/{shp_filename}.shx',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': f'{brk_directory("prj", use_sensitive_dir=False)}/{shp_filename}.prj',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': f'{brk_directory("prj", use_sensitive_dir=False)}/{shp_filename}.cpg',
                    'mime_type': 'application/octet-stream'
                },
            ],
            'query': query
        }
    }
