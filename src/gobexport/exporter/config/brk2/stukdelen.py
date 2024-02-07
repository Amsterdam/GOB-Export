from gobexport.exporter.config.brk2.utils import brk2_filename
from gobexport.exporter.csv import csv_exporter
from gobexport.exporter.shared.brk import format_timestamp
from gobexport.filters.notempty_filter import NotEmptyFilter


class StukdelenExportConfig:

    def format_bedrag(self, value):
        return str(round(float(value)))

    format = {
        'BRK_SDL_ID': 'identificatie',
        'SDL_AARD_STUKDEEL_CODE': 'aard.code',
        'SDL_AARD_STUKDEEL_OMS': 'aard.omschrijving',
        'SDL_KOOPSOM': {
            "action": "format",
            "value": "bedragTransactie.bedrag",
            "formatter": format_bedrag,
        },
        'SDL_KOOPSOM_VALUTA': 'bedragTransactie.valuta',
        'BRK_STK_ID': 'stukidentificatie',
        'STK_AKR_PORTEFEUILLENR': 'portefeuillenummerAkr',
        'STK_TIJDSTIP_AANBIEDING': {
            'action': 'format',
            'formatter': format_timestamp,
            'value': 'tijdstipAanbiedingStuk',
        },
        'STK_REEKS_CODE': 'reeks.code',
        'STK_VOLGNUMMER': 'volgnummerStuk',
        'STK_REGISTERCODE_CODE': 'registercodeStuk.code',
        'STK_REGISTERCODE_OMS': 'registercodeStuk.omschrijving',
        'STK_SOORTREGISTER_CODE': 'soortRegisterStuk.code',
        'STK_SOORTREGISTER_OMS': 'soortRegisterStuk.omschrijving',
        'STK_DEEL_SOORT': 'deelSoortStuk',
        'BRK_TNG_ID': 'isBronVoorBrkTenaamstelling.[0].identificatie',
        'BRK_ATG_ID': {
            'condition': 'isempty',
            'reference': 'isBronVoorBrkAantekeningRecht.[0].identificatie',
            'negate': True,
            # Either one or the other is set, or none, but never both
            'trueval': 'isBronVoorBrkAantekeningRecht.[0].identificatie',
            'falseval': 'isBronVoorBrkAantekeningKadastraalObject.[0].identificatie'
        },
        'BRK_ASG_VVE': 'isBronVoorBrkZakelijkRecht.[0].vveIdentificatieOntstaanUit.[0].identificatie'
    }

    query_tng = '''
{
  brk2Stukdelen {
    edges {
      node {
        identificatie
        aard
        bedragTransactie
        stukidentificatie
        portefeuillenummerAkr
        tijdstipAanbiedingStuk
        reeks
        volgnummerStuk
        registercodeStuk
        soortRegisterStuk
        deelSoortStuk
        isBronVoorBrkTenaamstelling {
          edges {
            node {
              identificatie
            }
          }
        }
      }
    }
  }
}
'''

    query_art = '''
{
  brk2Stukdelen {
    edges {
      node {
        identificatie
        aard
        bedragTransactie
        stukidentificatie
        portefeuillenummerAkr
        tijdstipAanbiedingStuk
        reeks
        volgnummerStuk
        registercodeStuk
        soortRegisterStuk
        deelSoortStuk
        isBronVoorBrkAantekeningRecht {
          edges {
            node {
              identificatie
            }
          }
        }
      }
    }
  }
}
'''

    query_akt = '''
{
  brk2Stukdelen {
    edges {
      node {
        identificatie
        aard
        bedragTransactie
        stukidentificatie
        portefeuillenummerAkr
        tijdstipAanbiedingStuk
        reeks
        volgnummerStuk
        registercodeStuk
        soortRegisterStuk
        deelSoortStuk
        isBronVoorBrkAantekeningKadastraalObject {
          edges {
            node {
              identificatie
            }
          }
        }
      }
    }
  }
}

    '''

    query_zrt = '''
{
  brk2Stukdelen {
    edges {
      node {
        identificatie
        aard
        bedragTransactie
        stukidentificatie
        portefeuillenummerAkr
        tijdstipAanbiedingStuk
        reeks
        volgnummerStuk
        registercodeStuk
        soortRegisterStuk
        deelSoortStuk
        isBronVoorBrkZakelijkRecht(active: false) {
          edges {
            node {
              vveIdentificatieOntstaanUit {
                edges {
                  node {
                    identificatie
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

    products = {
        'csv_tng': {
            'exporter': csv_exporter,
            'api_type': 'graphql_streaming',
            'secure_user': 'gob',
            'batch_size': 10000,
            'unfold': True,
            'query': query_tng,
            'filename': lambda: brk2_filename('stukdeel', use_sensitive_dir=True),
            'mime_type': 'text/csv',
            'format': format,
            'entity_filters': [
                NotEmptyFilter('isBronVoorBrkTenaamstelling.[0].identificatie'),
            ],
        },
        'csv_art': {
            'exporter': csv_exporter,
            'api_type': 'graphql_streaming',
            'secure_user': 'gob',
            'batch_size': 10000,
            'unfold': True,
            'query': query_art,
            'append': True,
            'filename': lambda: brk2_filename('stukdeel', use_sensitive_dir=True),
            'mime_type': 'text/csv',
            'format': format,
            'entity_filters': [
                NotEmptyFilter(
                    'isBronVoorBrkAantekeningRecht.[0].identificatie',
                ),
            ],
        },
        'csv_akt': {
            'exporter': csv_exporter,
            'api_type': 'graphql_streaming',
            'secure_user': 'gob',
            'batch_size': 10000,
            'unfold': True,
            'query': query_akt,
            'append': True,
            'filename': lambda: brk2_filename('stukdeel', use_sensitive_dir=True),
            'mime_type': 'text/csv',
            'format': format,
            'entity_filters': [
                NotEmptyFilter(
                    'isBronVoorBrkAantekeningKadastraalObject.[0].identificatie',
                ),
            ],
        },
        'csv_zrt': {
            'exporter': csv_exporter,
            'api_type': 'graphql_streaming',
            'secure_user': 'gob',
            'batch_size': 10000,
            'unfold': True,
            'append': True,
            'query': query_zrt,
            'filename': lambda: brk2_filename('stukdeel', use_sensitive_dir=True),
            'mime_type': 'text/csv',
            'format': format,
            'entity_filters': [
                NotEmptyFilter('isBronVoorBrkZakelijkRecht.[0].vveIdentificatieOntstaanUit.[0].identificatie')
            ],
        }
    }
