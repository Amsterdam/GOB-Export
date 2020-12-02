from gobexport.exporter.esri import esri_exporter
from gobexport.exporter.config.brk.utils import brk_directory


class KadastralesectiesExportConfig:
    query = '''
{
  brkKadastralesecties {
    edges {
      node {
        code
        geometrie
        isOnderdeelVanKadastralegemeentecode {
          edges {
            node {
              identificatie
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
    }
  }
}
'''

    filename = 'BRK_KAD_SECTIE'
    products = {
        'shape': {
            'exporter': esri_exporter,
            'api_type': 'graphql_streaming',
            'secure_user': 'gob',
            'filename': f'{brk_directory("shp")}/{filename}.shp',
            'mime_type': 'application/octet-stream',
            'format': {
                'GEMEENTE': 'ligtInGemeente.[0].naam',
                'KADGEMCODE': 'isOnderdeelVanKadastralegemeentecode.[0].identificatie',
                'KADGEM': 'isOnderdeelVanKadastralegemeente.[0].identificatie',
                'SECTIE': 'code',
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
    }
