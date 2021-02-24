from gobexport.exporter.csv import csv_exporter
from gobexport.filters.notempty_filter import NotEmptyFilter
from gobexport.exporter.config.brk.utils import brk_filename, format_timestamp


class AantekeningenrechtenExportConfig:
    art_query = '''
{
  brkAantekeningenrechten {
    edges {
      node {
        identificatie
        aard
        omschrijving
        einddatum
        heeftBetrokkenPersoon {
          edges {
            node {
              identificatie
            }
          }
        }
        betrokkenTenaamstelling {
          edges {
            node {
              identificatie
              vanZakelijkrecht {
                edges {
                  node {
                    aardZakelijkRecht
                    rustOpKadastraalobject {
                      edges {
                        node {
                          identificatie
                          perceelnummer
                          indexletter
                          indexnummer
                          aangeduidDoorKadastralegemeentecode {
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

    art_format = {
        'BRK_ATG_ID': 'identificatie',
        'ATG_AARDAANTEKENING_CODE': 'aard.code',
        'ATG_AARDAANTEKENING_OMS': 'aard.omschrijving',
        'ATG_OMSCHRIJVING': 'omschrijving',
        'ATG_EINDDATUM': {
            'action': 'format',
            'formatter': format_timestamp,
            'value': 'einddatum',
        },
        'ATG_TYPE': {
            'action': 'literal',
            'value': 'Aantekening Zakelijk Recht (R)'
        },
        'BRK_KOT_ID': 'rustOpKadastraalobject.[0].identificatie',
        'KOT_KADASTRALEGEMCODE_CODE':
            'aangeduidDoorKadastralegemeentecode.[0].broninfo.omschrijving',
        'KOT_SECTIE': 'aangeduidDoorKadastralesectie.[0].code',
        'KOT_PERCEELNUMMER': 'rustOpKadastraalobject.[0].perceelnummer',
        'KOT_INDEX_LETTER': 'rustOpKadastraalobject.[0].indexletter',
        'KOT_INDEX_NUMMER': 'rustOpKadastraalobject.[0].indexnummer',
        'BRK_TNG_ID': 'betrokkenTenaamstelling.[0].identificatie',
        'ZRT_AARD_ZAKELIJKRECHT_CODE': 'vanZakelijkrecht.[0].aardZakelijkRecht.code',
        'ZRT_AARD_ZAKELIJKRECHT_OMS': 'vanZakelijkrecht.[0].aardZakelijkRecht.omschrijving',
        'BRK_SJT_ID': 'heeftBetrokkenPersoon.[0].identificatie',
    }

    akt_query = '''
{
  brkAantekeningenkadastraleobjecten {
    edges {
      node {
        identificatie
        aard
        omschrijving
        einddatum,
        heeftBetrokkenPersoon {
          edges {
            node {
              identificatie
            }
          }
        }
        heeftBetrekkingOpKadastraalObject {
          edges {
            node {
              identificatie
              perceelnummer
              indexletter
              indexnummer
              aangeduidDoorKadastralegemeentecode {
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
            }
          }
        }
      }
    }
  }
}
'''

    akt_format = {
        'BRK_ATG_ID': 'identificatie',
        'ATG_AARDAANTEKENING_CODE': 'aard.code',
        'ATG_AARDAANTEKENING_OMS': 'aard.omschrijving',
        'ATG_OMSCHRIJVING': 'omschrijving',
        'ATG_EINDDATUM': {
            'action': 'format',
            'formatter': format_timestamp,
            'value': 'einddatum',
        },
        'ATG_TYPE': {
            'action': 'literal',
            'value': 'Aantekening Kadastraal object (O)'
        },
        'BRK_KOT_ID': 'heeftBetrekkingOpKadastraalObject.[0].identificatie',
        'KOT_KADASTRALEGEMCODE_CODE':
            'aangeduidDoorKadastralegemeentecode.[0].broninfo.omschrijving',
        'KOT_SECTIE': 'aangeduidDoorKadastralesectie.[0].code',
        'KOT_PERCEELNUMMER': 'heeftBetrekkingOpKadastraalObject.[0].perceelnummer',
        'KOT_INDEX_LETTER': 'heeftBetrekkingOpKadastraalObject.[0].indexletter',
        'KOT_INDEX_NUMMER': 'heeftBetrekkingOpKadastraalObject.[0].indexnummer',
        'BRK_TNG_ID': '',
        'ZRT_AARD_ZAKELIJKRECHT_CODE': '',
        'ZRT_AARD_ZAKELIJKRECHT_OMS': '',
        'BRK_SJT_ID': 'heeftBetrokkenPersoon.[0].identificatie',
    }

    products = {
        'csv_art': {
            'api_type': 'graphql_streaming',
            'secure_user': 'gob',
            'unfold': True,
            'cross_relations': True,
            'entity_filters': [
                NotEmptyFilter('betrokkenTenaamstelling.[0].identificatie'),
                NotEmptyFilter('rustOpKadastraalobject.[0].identificatie'),
            ],
            'exporter': csv_exporter,
            'query': art_query,
            'filename': lambda: brk_filename("aantekening", is_sensitive=True),
            'mime_type': 'plain/text',
            'format': art_format,
        },
        'csv_akt': {
            'api_type': 'graphql_streaming',
            'secure_user': 'gob',
            'unfold': True,
            'entity_filters': [
                NotEmptyFilter('heeftBetrekkingOpKadastraalObject.[0].identificatie'),
            ],
            'exporter': csv_exporter,
            'query': akt_query,
            'filename': lambda: brk_filename("aantekening", is_sensitive=True),
            'mime_type': 'plain/text',
            'format': akt_format,
            'append': True,
        }
    }
