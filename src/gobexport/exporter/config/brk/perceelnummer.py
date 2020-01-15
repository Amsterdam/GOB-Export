from gobexport.exporter.esri import esri_exporter
from gobexport.filters.notempty_filter import NotEmptyFilter
from gobexport.formatter.geometry import format_geometry
from gobexport.exporter.config.brk.utils import brk_filename


class PerceelnummerEsriFormat:

    def format_rotatie(self, value):
        assert not None and isinstance(value, (int, float))
        # Return rotatie with three decimal places
        return f'{value:.3f}'

    def get_format(self):
        return {
            'BRK_KOT_ID': 'identificatie',
            'GEMEENTE': 'aangeduidDoorGemeente.naam',
            'KADGEMCODE': 'aangeduidDoorKadastralegemeentecode.[0].broninfo.omschrijving',
            'KADGEM': 'aangeduidDoorKadastralegemeente.[0].broninfo.omschrijving',
            'SECTIE': 'aangeduidDoorKadastralesectie.[0].code',
            'PERCEELNR': 'perceelnummer',
            'INDEXLTR': 'indexletter',
            'INDEXNR': 'indexnummer',
            'ROTATIE': {
                'condition': 'isempty',
                'reference': 'perceelnummerRotatie',
                'falseval': {
                    'action': 'format',
                    'formatter': self.format_rotatie,
                    'value': 'perceelnummerRotatie',
                },
                'trueval': {
                    'action': 'literal',
                    'value': '0.000',
                }
            },
            'geometrie': {
                'action': 'format',
                'formatter': format_geometry,
                'value': 'plaatscoordinaten'
            },
        }


class PerceelnummerExportConfig:
    format = PerceelnummerEsriFormat()

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
        perceelnummerRotatie
        plaatscoordinaten
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
            'filename': lambda: brk_filename('perceelnummer', type='shp', append_date=False),
            'entity_filters': [
                NotEmptyFilter('plaatscoordinaten'),
            ],
            'mime_type': 'application/octet-stream',
            'format': format.get_format(),
            'extra_files': [
                {
                    'filename': lambda: brk_filename('perceelnummer', type='dbf', append_date=False),
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': lambda: brk_filename('perceelnummer', type='shx', append_date=False),
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': lambda: brk_filename('perceelnummer', type='prj', append_date=False),
                    'mime_type': 'application/octet-stream'
                },
            ],
            'query': query
        }
    }
