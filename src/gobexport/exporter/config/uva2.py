from datetime import date
import dateutil.parser as dt_parser

from gobexport.exporter.config.bag import WoonplaatsenExportConfig
from gobexport.exporter.uva2 import uva2_exporter

UVA2_DATE_FORMAT = '%Y%m%d'


def add_uva2_products():
    _add_woonplaatsen_uva2_config()


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

    WoonplaatsenExportConfig.products['uva2'] = {
        'api_type': 'graphql',
        'exporter': uva2_exporter,
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
