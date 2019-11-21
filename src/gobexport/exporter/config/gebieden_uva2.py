from gobexport.exporter.config import gebieden
from gobexport.exporter.config.uva2 import get_uva2_filename
from gobexport.exporter.config.uva2 import format_uva2_date, format_uva2_buurt
from gobexport.exporter.uva2 import uva2_exporter

from gobexport.filters.notempty_filter import NotEmptyFilter


def add_gebieden_uva2_products():
    """
    Add UVA2 products that are related to gebieden
    :return:
    """
    _add_stadsdelen_uva2_config()
    _add_buurten_uva2_config()
    _add_bouwblokken_uva2_config()


def _add_stadsdelen_uva2_config():
    """
    Add UVA2 products that are related to stadsdelen

    A minor exception is gemeenten. This is related to gebieden but not a part of gebieden.
    The relation is by means of the gemeente as is referenced by stadsdelen

    :return:
    """
    uva2_gem_query = """
{
  gebiedenStadsdelen (naam: "Centrum") {
    edges {
      node {
      naam
        ligtInGemeente {
          edges {
            node {
              naam
              identificatie
            }
          }
        }
      }
    }
  }
}
"""

    gebieden.StadsdelenExportConfig.products['uva2_gem'] = {
        'api_type': 'graphql',
        'exporter': uva2_exporter,
        'entity_filters': [],
        'filename': lambda: get_uva2_filename("GME"),
        'mime_type': 'plain/text',
        'format': {
            'sleutelVerzendend': {
                'action': 'fill',
                'length': 14,
                'character': '0',
                'value': 'ligtInGemeente.[0].identificatie',
                'fill_type': 'ljust'
            },
            'Gemeentecode': 'ligtInGemeente.[0].identificatie',
            'Gemeentenaam': 'ligtInGemeente.[0].naam',
            'GemeenteWaarinOvergegaan': '',
            'IndicatieVerzorgingsgebied': {
                'action': 'literal',
                'value': "J",
            },
            'Geometrie': '',
            'Mutatie-gebruiker': {
                'action': 'literal',
                'value': "GVI",
            },
            'Indicatie-vervallen': {
                'action': 'literal',
                'value': "N",
            },
            'TijdvakGeldigheid/begindatumTijdvakGeldigheid': {
                'action': 'literal',
                'value': "19000101",
            },
            'TijdvakGeldigheid/einddatumTijdvakGeldigheid': ''
        },
        'query': uva2_gem_query
    }

    uva2_sdl_query = """
{
  gebiedenStadsdelen {
    edges {
      node {
        identificatie
        code
        naam
        documentnummer
        documentdatum
        beginGeldigheid
        eindGeldigheid
        ligtInGemeente {
          edges {
            node {
              identificatie
              beginGeldigheid
              eindGeldigheid
            }
          }
        }
      }
    }
  }
}
"""

    gebieden.StadsdelenExportConfig.products['uva2_sdl'] = {
        'api_type': 'graphql',
        'exporter': uva2_exporter,
        'entity_filters': [
            NotEmptyFilter('identificatie'),
        ],
        'filename': lambda: get_uva2_filename("SDL"),
        'mime_type': 'plain/text',
        'format': {
            'sleutelVerzendend': 'identificatie',
            'Stadsdeelcode': 'code',
            'Stadsdeelnaam': 'naam',
            'Brondocumentverwijzing': 'documentnummer',
            'Brondocumentdatum': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'documentdatum',
            },
            'Geometrie': '',
            'Mutatie-gebruiker': {
                'action': 'literal',
                'value': "DPG",
            },
            'Indicatie-vervallen': {
                'action': 'literal',
                'value': "N",
            },
            'TijdvakGeldigheid/begindatumTijdvakGeldigheid': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheid',
            },
            'TijdvakGeldigheid/einddatumTijdvakGeldigheid': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheid',
            },
            'SDLGME/GME/sleutelVerzendend': {
                'action': 'fill',
                'length': 14,
                'character': '0',
                'value': 'ligtInGemeente.[0].identificatie',
                'fill_type': 'ljust'
            },
            'SDLGME/GME/Gemeentecode': 'ligtInGemeente.[0].identificatie',
            'SDLGME/TijdvakRelatie/begindatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheid',
            },
            'SDLGME/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheid',
            }
        },
        'query': uva2_sdl_query
    }


def _add_buurten_uva2_config():

    uva2_query = """
{
  gebiedenBuurten {
    edges {
      node {
        identificatie
        code
        naam
        documentnummer
        documentdatum
        beginGeldigheid
        eindGeldigheid
        ligtInWijk {
          edges {
            node {
              ligtInStadsdeel {
                edges {
                  node {
                    identificatie
                    code
                    beginGeldigheid
                    eindGeldigheid
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
"""

    gebieden.BuurtenExportConfig.products['uva2'] = {
        'api_type': 'graphql',
        'exporter': uva2_exporter,
        'entity_filters': [
            NotEmptyFilter('identificatie'),
        ],
        'filename': lambda: get_uva2_filename("BRT"),
        'mime_type': 'plain/text',
        'format': {
            'sleutelVerzendend': 'identificatie',
            'Buurtcode': {
                'action': 'format',
                'formatter': format_uva2_buurt,
                'value': 'code',
            },
            'Buurtnaam': 'naam',
            'Brondocumentverwijzing': 'documentnummer',
            'Brondocumentdatum': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'documentdatum',
            },
            'Geometrie': '',
            'Mutatie-gebruiker': {
                'action': 'literal',
                'value': "DPG",
            },
            'Indicatie-vervallen': {
                'action': 'literal',
                'value': "N",
            },
            'TijdvakGeldigheid/begindatumTijdvakGeldigheid': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheid',
            },
            'TijdvakGeldigheid/einddatumTijdvakGeldigheid': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheid',
            },
            'BRTSDL/SDL/sleutelVerzendend': {
                'action': 'fill',
                'length': 14,
                'character': '0',
                'value': 'ligtInWijk.[0].ligtInStadsdeel.[0].identificatie',
                'fill_type': 'ljust'
            },
            'BRTSDL/SDL/Stadsdeelcode': 'ligtInWijk.[0].ligtInStadsdeel.[0].code',
            'BRTSDL/TijdvakRelatie/begindatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheid'
            },
            'BRTSDL/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'ligtInWijk.[0].ligtInStadsdeel.[0].eindGeldigheid',
            }
        },
        'query': uva2_query
    }


def _add_bouwblokken_uva2_config():

    uva2_query = """
{
  gebiedenBouwblokken {
    edges {
      node {
        identificatie
        code
        beginGeldigheid
        eindGeldigheid
        ligtInBuurt {
          edges {
            node {
              identificatie
              code
            }
          }
        }
      }
    }
  }
}
"""

    gebieden.BouwblokkenExportConfig.products['uva2'] = {
        'api_type': 'graphql',
        'exporter': uva2_exporter,
        'entity_filters': [
            NotEmptyFilter('identificatie'),
        ],
        'filename': lambda: get_uva2_filename("BBK"),
        'mime_type': 'plain/text',
        'format': {
            'sleutelVerzendend': 'identificatie',
            'Bouwbloknummer': 'code',
            'Geometrie': '',
            'TijdvakGeldigheid/begindatumTijdvakGeldigheid': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheid',
            },
            'TijdvakGeldigheid/einddatumTijdvakGeldigheid': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheid',
            },
            'BBKBRT/BRT/sleutelVerzendend': {
                'action': 'fill',
                'length': 14,
                'character': '0',
                'value': 'ligtInBuurt.[0].identificatie',
                'fill_type': 'ljust'
            },
            'BBKBRT/BRT/Buurtcode': 'ligtInBuurt.[0].code',
            'BBKBRT/TijdvakRelatie/begindatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheid'
            },
            'BBKBRT/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheid',
            }
        },
        'query': uva2_query
    }
