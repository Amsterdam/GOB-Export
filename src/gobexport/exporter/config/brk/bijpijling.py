from gobexport.exporter.esri import esri_exporter
from gobexport.filters.notempty_filter import NotEmptyFilter
from gobexport.formatter.geometry import format_geometry
from gobexport.exporter.config.brk.utils import brk_filename


class BijpijlingExportConfig:
    query = '''
{
  brkKadastraleobjecten(indexletter: "G") {
    edges {
      node {
        identificatie
        aangeduidDoorGemeente {
          edges {
            node {
              naam
            }
          }
        }
        aangeduidDoorKadastralegemeentecode {
          edges {
            node {
              broninfo
            }
          }
        }
        aangeduidDoorKadastralegemeente {
          edges {
            node {
              broninfo
            }
          }
        }
        aangeduidDoorKadastralesectie {
          edges {
            node {
              code
            }
          }
        }
        perceelnummer
        indexletter
        indexnummer
        bijpijlingGeometrie
      }
    }
  }
}
'''

    products = {
        'shape': {
            'exporter': esri_exporter,
            'api_type': 'graphql_streaming',
            'secure': True,
            'filename': lambda: brk_filename('bijpijling', type='shp', append_date=False),
            'entity_filters': [
                NotEmptyFilter('bijpijlingGeometrie'),
            ],
            'mime_type': 'application/octet-stream',
            'format': {
                'BRK_KOT_ID': 'identificatie',
                'GEMEENTE': 'aangeduidDoorGemeente.naam',
                'KADGEMCODE': 'aangeduidDoorKadastralegemeentecode.[0].broninfo.omschrijving',
                'KADGEM': 'aangeduidDoorKadastralegemeente.[0].broninfo.omschrijving',
                'SECTIE': 'aangeduidDoorKadastralesectie.[0].code',
                'PERCEELNR': 'perceelnummer',
                'INDEXLTR': 'indexletter',
                'INDEXNR': 'indexnummer',
                'geometrie': {
                    'action': 'format',
                    'formatter': format_geometry,
                    'value': 'bijpijlingGeometrie'
                },
            },
            'extra_files': [
                {
                    'filename': lambda: brk_filename('bijpijling', type='dbf', append_date=False),
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': lambda: brk_filename('bijpijling', type='shx', append_date=False),
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': lambda: brk_filename('bijpijling', type='prj', append_date=False),
                    'mime_type': 'application/octet-stream'
                },
            ],
            'query': query
        }
    }
