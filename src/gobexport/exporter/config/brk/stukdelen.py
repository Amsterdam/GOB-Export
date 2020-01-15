from gobexport.exporter.csv import csv_exporter
from gobexport.filters.notempty_filter import NotEmptyFilter
from gobexport.exporter.config.brk.utils import brk_filename, format_timestamp


class StukdelenExportConfig:
    format = {
        'BRK_SDL_ID': 'identificatie',
        'SDL_AARD_STUKDEEL_CODE': 'aard.code',
        'SDL_AARD_STUKDEEL_OMS': 'aard.omschrijving',
        'SDL_KOOPSOM': 'bedragTransactie.bedrag',
        'SDL_KOOPSOM_VALUTA': 'bedragTransactie.valuta',
        'BRK_STK_ID': 'stukidentificatie',
        'STK_AKR_PORTEFEUILLENR': 'portefeuillenummerAkr',
        'STK_TIJDSTIP_AANBIEDING': {
            'action': 'format',
            'formatter': format_timestamp,
            'value': 'tijdstipAanbiedingStuk',
        },
        'STK_REEKS_CODE': 'reeks',
        'STK_VOLGNUMMER': 'volgnummerStuk',
        'STK_REGISTERCODE_CODE': 'registercodeStuk.code',
        'STK_REGISTERCODE_OMS': 'registercodeStuk.omschrijving',
        'STK_SOORTREGISTER_CODE': 'soortRegisterStuk.code',
        'STK_SOORTREGISTER_OMS': 'soortRegisterStuk.omschrijving',
        'STK_DEEL_SOORT': 'deelSoortStuk',
        'BRK_TNG_ID': 'isBronVoorTenaamstelling.[0].identificatie',
        'BRK_ATG_ID': {
            'condition': 'isempty',
            'reference': 'isBronVoorAantekeningRecht.[0].identificatie',
            'negate': True,
            # Either one or the other is set, or none, but never both
            'trueval': 'isBronVoorAantekeningRecht.[0].identificatie',
            'falseval': 'isBronVoorAantekeningKadastraalObject.[0].identificatie'
        },
        'BRK_ASG_VVE': 'isBronVoorZakelijkRecht.[0].appartementsrechtsplitsingidentificatie'
    }

    query_tng = '''
{
  brkStukdelen {
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
        isBronVoorTenaamstelling {
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
  brkStukdelen {
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
        isBronVoorAantekeningRecht {
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
      brkStukdelen {
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
            isBronVoorAantekeningKadastraalObject {
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
  brkStukdelen {
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
        isBronVoorZakelijkRecht(active: false) {
          edges {
            node {
              appartementsrechtsplitsingidentificatie
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
            'secure': True,
            'batch_size': 10000,
            'unfold': True,
            'query': query_tng,
            'filename': lambda: brk_filename('stukdeel'),
            'mime_type': 'plain/text',
            'format': format,
            'entity_filters': [
                NotEmptyFilter('isBronVoorTenaamstelling.[0].identificatie'),
            ],
        },
        'csv_art': {
            'exporter': csv_exporter,
            'api_type': 'graphql_streaming',
            'secure': True,
            'batch_size': 10000,
            'unfold': True,
            'query': query_art,
            'append': True,
            'filename': lambda: brk_filename('stukdeel'),
            'mime_type': 'plain/text',
            'format': format,
            'entity_filters': [
                NotEmptyFilter(
                    'isBronVoorAantekeningRecht.[0].identificatie',
                ),
            ],
        },
        'csv_akt': {
            'exporter': csv_exporter,
            'api_type': 'graphql_streaming',
            'secure': True,
            'batch_size': 10000,
            'unfold': True,
            'query': query_akt,
            'append': True,
            'filename': lambda: brk_filename('stukdeel'),
            'mime_type': 'plain/text',
            'format': format,
            'entity_filters': [
                NotEmptyFilter(
                    'isBronVoorAantekeningKadastraalObject.[0].identificatie',
                ),
            ],
        },
        'csv_zrt': {
            'exporter': csv_exporter,
            'api_type': 'graphql_streaming',
            'secure': True,
            'batch_size': 10000,
            'unfold': True,
            'append': True,
            'query': query_zrt,
            'filename': lambda: brk_filename('stukdeel'),
            'mime_type': 'plain/text',
            'format': format,
            'entity_filters': [
                NotEmptyFilter('isBronVoorZakelijkRecht.[0].appartementsrechtsplitsingidentificatie')
            ],
        }
    }
