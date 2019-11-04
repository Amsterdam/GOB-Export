from datetime import date
import dateutil.parser as dt_parser

from gobexport.exporter.config import bag
from gobexport.exporter.uva2 import uva2_exporter

from gobexport.filters.notempty_filter import NotEmptyFilter

UVA2_DATE_FORMAT = '%Y%m%d'
UVA2_STATUS_CODES = {
    'ligplaatsen': {
        '1': '33',
        '2': '34',
    },
    'nummeraanduidingen': {
        '1': '16',
        '2': '17',
    },
    'openbareruimtes': {
        '1': '35',
        '2': '36',
    },
    'standplaatsen': {
        '1': '37',
        '2': '38',
    },
}


def add_uva2_products():
    _add_woonplaatsen_uva2_config()
    _add_openbareruimtes_uva2_config()
    _add_nummeraanduidingen_uva2_config()
    _add_ligplaatsen_uva2_config()
    _add_standplaatsen_uva2_config()


def format_uva2_date(datetimestr):
    if not datetimestr:
        # Input variable may be empty
        return None

    try:
        dt = dt_parser.parse(datetimestr)
        return dt.strftime(UVA2_DATE_FORMAT)
    except ValueError:
        # If invalid datetimestr, just return the original string so that no data is lost
        return datetimestr


def format_uva2_status(value, entity_name=None):
    # Status could be an int or string
    value = str(value)
    assert entity_name and entity_name in UVA2_STATUS_CODES, "A valid entity name is required"
    assert value in UVA2_STATUS_CODES[entity_name], "A valid status code is required"

    return UVA2_STATUS_CODES[entity_name][value]


def format_uva2_buurt(value):
    # Strip the first character (Stadsdeelcode)
    return value[1:]


def get_uva2_filename(abbreviation):
    assert abbreviation, "UVA2 requires an abbreviation"

    publish_date = date.today().strftime(UVA2_DATE_FORMAT)
    return f"UVA2_Actueel/{abbreviation}_{publish_date}_N_{publish_date}_{publish_date}.UVA2"


def _add_woonplaatsen_uva2_config():
    uva2_query = """
{
  bagWoonplaatsen {
    edges {
      node {
        amsterdamseSleutel
        identificatie
        naam
        documentdatum
        documentnummer
        beginGeldigheid
        eindGeldigheid
        ligtInGemeente {
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
"""

    bag.WoonplaatsenExportConfig.products['uva2'] = {
        'api_type': 'graphql_streaming',
        'exporter': uva2_exporter,
        'entity_filters': [
            NotEmptyFilter('amsterdamseSleutel'),
        ],
        'filename': lambda: get_uva2_filename("WPL"),
        'mime_type': 'plain/text',
        'format': {
            'sleutelVerzendend': 'amsterdamseSleutel',
            'Woonplaatsidentificatie': 'identificatie',
            'Woonplaatsnaam': 'naam',
            'DocumentdatumMutatieWoonplaats': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'documentdatum',
            },
            'DocumentnummerMutatieWoonplaats': 'documentnummer',
            'WoonplaatsPTTSchrijfwijze': '',
            'Mutatie-gebruiker': '',
            'Indicatie-vervallen': '',
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
            'WPLGME/GME/sleutelVerzendend': {
                'action': 'fill',
                'length': 14,
                'character': '0',
                'value': 'ligtInGemeente.[0].identificatie',
                'fill_type': 'ljust'
            },
            'WPLGME/GME/Gemeentecode': 'ligtInGemeente.[0].identificatie',
            'WPLGME/TijdvakRelatie/begindatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheid',
            },
            'WPLGME/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheid',
            }
        },
        'query': uva2_query
    }


def _add_openbareruimtes_uva2_config():
    uva2_query = """
{
  bagOpenbareruimtes {
    edges {
      node {
        amsterdamseSleutel
        type
        naam
        documentdatum
        documentnummer
        straatcode
        naamNen
        beginGeldigheid
        eindGeldigheid
        status
        ligtInWoonplaats {
          edges {
            node {
              amsterdamseSleutel
              identificatie
            }
          }
        }
      }
    }
  }
}
"""

    bag.OpenbareruimtesExportConfig.products['uva2'] = {
        'api_type': 'graphql_streaming',
        'exporter': uva2_exporter,
        'entity_filters': [
            NotEmptyFilter('amsterdamseSleutel'),
            NotEmptyFilter('straatcode'),
        ],
        'filename': lambda: get_uva2_filename("OPR"),
        'mime_type': 'plain/text',
        'format': {
            'sleutelVerzendend': 'amsterdamseSleutel',
            'TypeOpenbareRuimteDomein': {
                'action': 'fill',
                'length': 2,
                'character': '0',
                'value': 'type.code',
                'fill_type': 'rjust'
            },
            'OmschrijvingTypeOpenbareRuimteDomein': '',
            'NaamOpenbareRuimte': 'naam',
            'DocumentdatumMutatieOpenbareRuimte': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'documentdatum',
            },
            'DocumentnummerMutatieOpenbareRuimte': 'documentnummer',
            'Straatnummer': '',
            'Straatcode': 'straatcode',
            'StraatnaamNENSchrijfwijze': 'naamNen',
            'StraatnaamPTTSchrijfwijze': '',
            'Mutatie-gebruiker': '',
            'Indicatie-vervallen': '',
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
            'OPRBRN/BRN/Code': '',
            'OPRBRN/TijdvakRelatie/begindatumRelatie': '',
            'OPRBRN/TijdvakRelatie/einddatumRelatie': '',
            'OPRSTS/STS/Code': {
                'action': 'format',
                'formatter': format_uva2_status,
                'value': 'status.code',
                'kwargs': {'entity_name': 'openbareruimtes'},
            },
            'OPRSTS/TijdvakRelatie/begindatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheid',
            },
            'OPRSTS/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheid',
            },
            'OPRWPL/WPL/sleutelVerzendend': 'ligtInWoonplaats.[0].amsterdamseSleutel',
            'OPRWPL/WPL/Woonplaatsidentificatie': 'ligtInWoonplaats.[0].identificatie',
            'OPRWPL/TijdvakRelatie/begindatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheid',
            },
            'OPRWPL/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheid',
            }
        },
        'query': uva2_query
    }


def _add_nummeraanduidingen_uva2_config():
    uva2_query = """
{
  bagNummeraanduidingen {
    edges {
      node {
        amsterdamseSleutel
        huisnummer
        huisletter
        huisnummertoevoeging
        postcode
        documentdatum
        documentnummer
        typeAdresseerbaarObject
        beginGeldigheid
        eindGeldigheid
        status
        ligtAanOpenbareruimte {
          edges {
            node {
              amsterdamseSleutel
              straatcode
            }
          }
        }
      }
    }
  }
}
"""

    bag.NummeraanduidingenExportConfig.products['uva2'] = {
        'api_type': 'graphql_streaming',
        'exporter': uva2_exporter,
        'entity_filters': [
            NotEmptyFilter('amsterdamseSleutel'),
        ],
        'filename': lambda: get_uva2_filename("NUM"),
        'mime_type': 'plain/text',
        'format': {
            'sleutelVerzendend': 'amsterdamseSleutel',
            'IdentificatiecodeNummeraanduiding': 'amsterdamseSleutel',
            'Huisnummer': 'huisnummer',
            'Huisletter': 'huisletter',
            'Huisnummertoevoeging': 'huisnummertoevoeging',
            'Postcode': 'postcode',
            'DocumentdatumMutatieNummeraanduiding': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'documentdatum',
            },
            'DocumentnummerMutatieNummeraanduiding': 'documentnummer',
            'TypeAdresseerbaarObjectDomein': {
                'action': 'fill',
                'length': 2,
                'character': '0',
                'value': 'typeAdresseerbaarObject.code',
                'fill_type': 'rjust'
            },
            'OmschrijvingTypeAdresseerbaarObjectDomein': 'typeAdresseerbaarObject.omschrijving',
            'Adresnummer': '',
            'Mutatie-gebruiker': '',
            'Indicatie-vervallen': '',
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
            'NUMBRN/BRN/Code': '',
            'NUMBRN/TijdvakRelatie/begindatumRelatie': '',
            'NUMBRN/TijdvakRelatie/einddatumRelatie': '',
            'NUMSTS/STS/Code': {
                'action': 'format',
                'formatter': format_uva2_status,
                'value': 'status.code',
                'kwargs': {'entity_name': 'nummeraanduidingen'},
            },
            'NUMSTS/TijdvakRelatie/begindatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheid',
            },
            'NUMSTS/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheid',
            },
            'NUMOPR/OPR/sleutelVerzendend': 'ligtAanOpenbareruimte.[0].amsterdamseSleutel',
            'NUMOPR/OPR/Straatcode': 'ligtAanOpenbareruimte.[0].straatcode',
            'NUMOPR/TijdvakRelatie/begindatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheid',
            },
            'NUMOPR/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheid',
            }
        },
        'query': uva2_query
    }


def _add_ligplaatsen_uva2_config():
    uva2_query = """
{
  bagLigplaatsen {
    edges {
      node {
        amsterdamseSleutel
        documentdatum
        documentnummer
        beginGeldigheid
        eindGeldigheid
        status
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

    bag.LigplaatsenExportConfig.products['uva2'] = {
        'api_type': 'graphql_streaming',
        'exporter': uva2_exporter,
        'entity_filters': [
            NotEmptyFilter('amsterdamseSleutel'),
        ],
        'filename': lambda: get_uva2_filename("LIG"),
        'mime_type': 'plain/text',
        'format': {
            'sleutelVerzendend': 'amsterdamseSleutel',
            'Ligplaatsidentificatie': 'amsterdamseSleutel',
            'Ligplaatsgeometrie': '',
            'DocumentdatumMutatieLigplaats': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'documentdatum',
            },
            'DocumentnummerMutatieLigplaats': 'documentnummer',
            'LigplaatsnummerGemeente': '',
            'Mutatie-gebruiker': '',
            'Indicatie-vervallen': '',
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
            'LIGBRN/BRN/Code': '',
            'LIGBRN/TijdvakRelatie/begindatumRelatie': '',
            'LIGBRN/TijdvakRelatie/einddatumRelatie': '',
            'LIGSTS/STS/Code': {
                'action': 'format',
                'formatter': format_uva2_status,
                'value': 'status.code',
                'kwargs': {'entity_name': 'ligplaatsen'},
            },
            'LIGSTS/TijdvakRelatie/begindatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheid',
            },
            'LIGSTS/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheid',
            },
            'LIGBRT/BRT/sleutelVerzendend': {
                'action': 'fill',
                'length': 14,
                'character': '0',
                'value': 'ligtInBuurt.[0].identificatie',
                'fill_type': 'ljust'
            },
            'LIGBRT/BRT/Buurtcode': {
                'action': 'format',
                'formatter': format_uva2_buurt,
                'value': 'ligtInBuurt.[0].code',
            },
            'LIGBRT/TijdvakRelatie/begindatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheid',
            },
            'LIGBRT/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheid',
            }
        },
        'query': uva2_query
    }


def _add_standplaatsen_uva2_config():
    uva2_query = """
{
  bagStandplaatsen {
    edges {
      node {
        amsterdamseSleutel
        documentdatum
        documentnummer
        beginGeldigheid
        eindGeldigheid
        status
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

    bag.StandplaatsenExportConfig.products['uva2'] = {
        'api_type': 'graphql_streaming',
        'exporter': uva2_exporter,
        'entity_filters': [
            NotEmptyFilter('amsterdamseSleutel'),
        ],
        'filename': lambda: get_uva2_filename("STA"),
        'mime_type': 'plain/text',
        'format': {
            'sleutelVerzendend': 'amsterdamseSleutel',
            'Standplaatsidentificatie': 'amsterdamseSleutel',
            'Standplaatsgeometrie': '',
            'DocumentdatumMutatieStandplaats': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'documentdatum',
            },
            'DocumentnummerMutatieStandplaats': 'documentnummer',
            'StandplaatsnummerGemeente': '',
            'Mutatie-gebruiker': '',
            'Indicatie-vervallen': '',
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
            'STABRN/BRN/Code': '',
            'STABRN/TijdvakRelatie/begindatumRelatie': '',
            'STABRN/TijdvakRelatie/einddatumRelatie': '',
            'STASTS/STS/Code': {
                'action': 'format',
                'formatter': format_uva2_status,
                'value': 'status.code',
                'kwargs': {'entity_name': 'standplaatsen'},
            },
            'STASTS/TijdvakRelatie/begindatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheid',
            },
            'STASTS/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheid',
            },
            'STABRT/BRT/sleutelVerzendend': {
                'action': 'fill',
                'length': 14,
                'character': '0',
                'value': 'ligtInBuurt.[0].identificatie',
                'fill_type': 'ljust'
            },
            'STABRT/BRT/Buurtcode': {
                'action': 'format',
                'formatter': format_uva2_buurt,
                'value': 'ligtInBuurt.[0].code',
            },
            'STABRT/TijdvakRelatie/begindatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheid',
            },
            'STABRT/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheid',
            }
        },
        'query': uva2_query
    }
