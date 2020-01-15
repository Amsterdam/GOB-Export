from gobexport.exporter.esri import esri_exporter
from gobexport.exporter.config.brk.utils import brk_directory


class KadastraleGemeentecodesExportConfig:
    query = '''
{
  brkKadastralegemeentecodes {
    edges {
      node {
        identificatie
        geometrie
        isOnderdeelVanKadastralegemeente {
          edges {
            node {
              identificatie

              ligtInGemeente {
                edges {
                  node {
                    naam
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
'''

    filename = 'BRK_KAD_GEMEENTE'
    line_filename = 'BRK_KAD_GEMEENTE_L'
    products = {
        'shape': {
            'exporter': esri_exporter,
            'api_type': 'graphql_streaming',
            'secure': True,
            'filename': f'{brk_directory("shp")}/{filename}.shp',
            'mime_type': 'application/octet-stream',
            'format': {
                'GEMEENTE': 'ligtInGemeente.[0].naam',
                'KADGEMCODE': 'identificatie',
                'KADGEM': 'isOnderdeelVanKadastralegemeente.[0].identificatie',
            },
            'extra_files': [
                {
                    'filename': f'{brk_directory("dbf")}/{filename}.dbf',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': f'{brk_directory("shx")}/{filename}.shx',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': f'{brk_directory("prj")}/{filename}.prj',
                    'mime_type': 'application/octet-stream'
                },
            ],
            'query': query
        },
        'lineshape': {
            'exporter': esri_exporter,
            'endpoint': '/gob/secure/brk/kadastralegemeentecodes/?view=linegeometry&ndjson=true',
            'filename': f'{brk_directory("shp")}/{line_filename}.shp',
            'mime_type': 'application/octet-stream',
            'format': {
                'GEMEENTE': 'gemeente',
                'KADGEMCODE': 'kadastraleGemeentecode',
                'KADGEM': 'kadastraleGemeente',
            },
            'extra_files': [
                {
                    'filename': f'{brk_directory("dbf")}/{line_filename}.dbf',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': f'{brk_directory("shx")}/{line_filename}.shx',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': f'{brk_directory("prj")}/{line_filename}.prj',
                    'mime_type': 'application/octet-stream'
                },
            ]
        }
    }
