from datetime import date
import dateutil.parser as dt_parser

from gobexport.exporter.config import bag
from gobexport.exporter.uva2 import uva2_exporter

from gobexport.filters.notempty_filter import NotEmptyFilter

UVA2_DATE_FORMAT = '%Y%m%d'
UVA2_STATUS_CODES = {
    'openbareruimtes': {
        '1': '35',
        '2': '36',
    }
}


def add_uva2_products():
    _add_woonplaatsen_uva2_config()
    _add_openbareruimtes_uva2_config()


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
        'api_type': 'graphql',
        'exporter': uva2_exporter,
        'entity_filters': [
            NotEmptyFilter('amsterdamseSleutel'),
        ],
        'filename': get_uva2_filename("WPL"),
        'mime_type': 'plain/text',
        'format': {
            'sleutelverzendend': 'amsterdamseSleutel',
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
        'api_type': 'graphql',
        'exporter': uva2_exporter,
        'entity_filters': [
            NotEmptyFilter('amsterdamseSleutel'),
            NotEmptyFilter('straatcode'),
        ],
        'filename': get_uva2_filename("OPR"),
        'mime_type': 'plain/text',
        'format': {
            'sleutelverzendend': 'amsterdamseSleutel',
            'TypeOpenbareRuimteDomein': 'type.code',
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
            'OPRBRN/TijdvakRelatie/begindatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheid',
            },
            'OPRBRN/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheid',
            },
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
