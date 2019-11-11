import re

from datetime import date
import dateutil.parser as dt_parser

from gobexport.exporter.config import bag
from gobexport.exporter.uva2 import uva2_exporter

from gobexport.filters.notempty_filter import NotEmptyFilter

UVA2_DATE_FORMAT = '%Y%m%d'
UVA2_MAPPING = {
    'ligplaatsen_status': {
        '1': '33',
        '2': '34',
    },
    'nummeraanduidingen_status': {
        '1': '16',
        '2': '17',
    },
    'openbareruimtes_status': {
        '1': '35',
        '2': '36',
    },
    'standplaatsen_status': {
        '1': '37',
        '2': '38',
    },
    'panden_status': {
        '1': '24',
        '2': '25',
        '3': '26',
        '7': '27',
        '10': '30',
        '11': '31',
        '12': '32',
    },
    'verblijfsobjecten_status': {
        '1': '18',
        '2': '19',
        '3': '20',
        '4': '21',
        '5': '22',
        '6': '23',
    },
    'verblijfsobjecten_type_woonobject_code': {
        'Meerdere woningen': 'M',
        'Eén woning': 'E',
        'Onbekend': 'O',
    },
    'verblijfsobjecten_type_woonobject_omschrijving': {
        'Meerdere woningen': 'Meergezinswoning',
        'Eén woning': 'Eengezinswoning',
        'Onbekend': 'Onbekend',
    },
    'verblijfsobjecten_gebruiksdoel_domein': {
        'sportfunctie': '600',
        'onderwijsfunctie': '700',
        'winkelfunctie': '800',
        'overige gebruiksfunctie': '900',
        'woonfunctie': '1000',
        'Gemengde panden': '1020',
        'Complex met eenheden': '1040',
        'Bijzondere woongebouwen': '1050',
        'Internaat': '1054',
        'bijeenkomstfunctie': '1100',
        'celfunctie': '1200',
        'gezondheidszorgfunctie': '1300',
        'woonfunctie verpleeghuis': '1310',
        'Inrichting': '1320',
        'industriefunctie': '1400',
        'kantoorfunctie': '1500',
        'logiesfunctie': '1600',
        'Seniorenwoning': '2060',
        'Rolstoeltoegankelijke woning': '2061',
        'Studentenwoning': '2070',
        'Complex, onzelfst. studentenwoonruimten': '2081',
        'Complex, onzelfst. seniorenwoonruimten': '2082',
        'Complex, onzelfst. gehandicaptenwoonruimten': '2083',
        'Complex, onzelfst. woonruimten': '2085',
        'gezondheidszorgfunctie verpleeghuis': '2310',
        'Complex,onzelfst. woonruimten met begeleiding': '2330',
    },
    'verblijfsobjecten_gebruiksdoel_omschrijving': {
        'sportfunctie': 'BEST-sportfunctie',
        'onderwijsfunctie': 'BEST-onderwijsfunctie',
        'winkelfunctie': 'BEST-winkelfunctie',
        'overige gebruiksfunctie': 'BEST-overige gebruiksfunctie',
        'woonfunctie': 'BEST-woonfunctie',
        'Gemengde panden': 'BEST-gemengde panden',
        'Complex met eenheden': 'BEST-complex met eenheden',
        'Bijzondere woongebouwen': 'BEST-bijzondere woongebouwen',
        'Internaat': 'BEST-internaat',
        'bijeenkomstfunctie': 'BEST-bijeenkomstfunctie',
        'celfunctie': 'BEST-celfunctie',
        'gezondheidszorgfunctie': 'BEST-gezondheidszorgfunctie',
        'woonfunctie verpleeghuis': 'BEST-verpleeghuis',
        'Inrichting': 'BEST-inrichting',
        'industriefunctie': 'BEST-industriefunctie',
        'kantoorfunctie': 'BEST-kantoorfunctie',
        'logiesfunctie': 'BEST-logiesfunctie',
        'Seniorenwoning': '2060 Seniorenwoning',
        'Rolstoeltoegankelijke woning': '2061 Rolstoeltoegankelijke woning',
        'Studentenwoning': '2070 Studentenwoning',
        'Complex, onzelfst. studentenwoonruimten': '2081 Complex, onzelfst. studentenwoonruimten',
        'Complex, onzelfst. seniorenwoonruimten': '2082 Complex, onzelfst. seniorenwoonruimten',
        'Complex, onzelfst. gehandicaptenwoonruimten': '2083 Complex, onzelfst. gehandicaptenwoonruimten',
        'Complex, onzelfst. woonruimten': '2085 Complex, onzelfst. woonruimten',
        'gezondheidszorgfunctie verpleeghuis': '2310 Verpleeghuis',
        'Complex,onzelfst. woonruimten met begeleiding': '2330 Complex,onzelfst. woonruimten met begeleiding',
    }
}


def add_uva2_products():
    _add_woonplaatsen_uva2_config()
    _add_openbareruimtes_uva2_config()
    _add_nummeraanduidingen_uva2_config()
    _add_ligplaatsen_uva2_config()
    _add_standplaatsen_uva2_config()
    _add_verblijfsobjecten_uva2_config()
    _add_panden_uva2_config()


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


def format_uva2_mapping(value, mapping_name=None):
    # Value could be an int or string
    value = str(value)
    assert mapping_name and mapping_name in UVA2_MAPPING, "A valid mapping name is required"
    return UVA2_MAPPING[mapping_name].get(value, '')


def format_uva2_buurt(value):
    # Strip the first character (Stadsdeelcode)
    return value[1:]


def format_uva2_coordinate(value, coordinate=None):
    assert coordinate in ('x', 'y'), "A valid coordinate (x or y) should be provided"

    index = 1 if coordinate == 'x' else 2

    match = re.match(r'^POINT\(([0-9\.]+) ([0-9\.]+)\)$', value)
    if match:
        return int(round(float(match.group(index))))
    else:
        return ''


def row_formatter_verblijfsobjecten(row):
    """
    Format rows for UVA2 with the following rules:
    GebruiksdoelVerblijfsobjectDomein, and OmschrijvingGebruiksdoelVerblijfsobjectDomein:
        1. Get the value from gebruiksdoel
        2. If there's a value in gebruiksdoelWoonfunctie use this value
        3. If gebruiksdoel is 'Woonfunctie' and gebruiksdoelWoonfunctie use '2075 Woning'
        4. If there's a value in gebruiksdoelGezondheidszorgfunctie use this value
        5. If there are multiple gebruiksdoel and no gebruiksdoelWoonfunctie use the first value
    """
    node = row['node']
    # Get the first gebruiksdoel
    gebruiksdoel = node['gebruiksdoel'][0]['omschrijving']

    # Overwrite if we have a woonfunctie or gezondheidszorgfunctie
    if node['gebruiksdoelWoonfunctie']:
        gebruiksdoel = node['gebruiksdoelWoonfunctie']['omschrijving']
        gebruiksdoel = 'woonfunctie verpleeghuis' if gebruiksdoel == 'Verpleeghuis' else gebruiksdoel

    if node['gebruiksdoelGezondheidszorgfunctie']:
        gebruiksdoel = node['gebruiksdoelGezondheidszorgfunctie']['omschrijving']
        gebruiksdoel = 'gezondheidszorgfunctie verpleeghuis' if gebruiksdoel == 'Verpleeghuis' else gebruiksdoel

    if gebruiksdoel == 'woonfunctie':
        node['GebruiksdoelVerblijfsobjectDomein'] = '2075'
        node['OmschrijvingGebruiksdoelVerblijfsobjectDomein'] = '2075 Woning'
    else:
        node['GebruiksdoelVerblijfsobjectDomein'] = format_uva2_mapping(
                                                        gebruiksdoel,
                                                        'verblijfsobjecten_gebruiksdoel_domein')
        node['OmschrijvingGebruiksdoelVerblijfsobjectDomein'] = format_uva2_mapping(
                                                        gebruiksdoel,
                                                        'verblijfsobjecten_gebruiksdoel_omschrijving')
    return row


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
                'formatter': format_uva2_mapping,
                'value': 'status.code',
                'kwargs': {'mapping_name': 'openbareruimtes_status'},
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
                'formatter': format_uva2_mapping,
                'value': 'status.code',
                'kwargs': {'mapping_name': 'nummeraanduidingen_status'},
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

    uva2_numlighfd_query = """
{
  bagLigplaatsen {
    edges {
      node {
        amsterdamseSleutel
        beginGeldigheid
        eindGeldigheid
        heeftHoofdadres {
          edges {
            node {
              amsterdamseSleutel
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

    uva2_numlignvn_query = """
{
  bagLigplaatsen {
    edges {
      node {
        amsterdamseSleutel
        beginGeldigheid
        eindGeldigheid
        heeftNevenadres {
          edges {
            node {
              amsterdamseSleutel
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
                'formatter': format_uva2_mapping,
                'value': 'status.code',
                'kwargs': {'mapping_name': 'ligplaatsen_status'},
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

    # NUMLIGHFD
    bag.LigplaatsenExportConfig.products['uva2_numlighfd'] = {
        'api_type': 'graphql_streaming',
        'exporter': uva2_exporter,
        'entity_filters': [
            NotEmptyFilter('amsterdamseSleutel'),
            NotEmptyFilter('heeftHoofdadres.[0].amsterdamseSleutel'),
        ],
        'filename': lambda: get_uva2_filename("NUMLIGHFD"),
        'mime_type': 'plain/text',
        'format': {
            'sleutelVerzendend': 'heeftHoofdadres.[0].amsterdamseSleutel',
            'IdentificatiecodeNummeraanduiding': 'heeftHoofdadres.[0].amsterdamseSleutel',
            'TijdvakGeldigheid/begindatumTijdvakGeldigheid': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'heeftHoofdadres.[0].beginGeldigheid',
            },
            'TijdvakGeldigheid/einddatumTijdvakGeldigheid': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'heeftHoofdadres.[0].eindGeldigheid',
            },
            'NUMLIGHFD/LIG/sleutelVerzendend': 'amsterdamseSleutel',
            'NUMLIGHFD/LIG/Ligplaatsidentificatie': 'amsterdamseSleutel',
            'NUMLIGHFD/TijdvakRelatie/begindatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'heeftHoofdadres.[0].beginGeldigheid',
            },
            'NUMLIGHFD/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'heeftHoofdadres.[0].eindGeldigheid',
            }
        },
        'query': uva2_numlighfd_query
    }

    # NUMLIGNVN
    bag.LigplaatsenExportConfig.products['uva2_numlignvn'] = {
        'api_type': 'graphql_streaming',
        'exporter': uva2_exporter,
        'entity_filters': [
            NotEmptyFilter('amsterdamseSleutel'),
            NotEmptyFilter('heeftNevenadres.[0].amsterdamseSleutel'),
        ],
        'unfold': True,
        'filename': lambda: get_uva2_filename("NUMLIGNVN"),
        'mime_type': 'plain/text',
        'format': {
            'sleutelVerzendend': 'heeftNevenadres.[0].amsterdamseSleutel',
            'IdentificatiecodeNummeraanduiding': 'heeftNevenadres.[0].amsterdamseSleutel',
            'TijdvakGeldigheid/begindatumTijdvakGeldigheid': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'heeftNevenadres.[0].beginGeldigheid',
            },
            'TijdvakGeldigheid/einddatumTijdvakGeldigheid': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'heeftNevenadres.[0].eindGeldigheid',
            },
            'NUMLIGNVN/LIG/sleutelVerzendend': 'amsterdamseSleutel',
            'NUMLIGNVN/LIG/Ligplaatsidentificatie': 'amsterdamseSleutel',
            'NUMLIGNVN/TijdvakRelatie/begindatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'heeftNevenadres.[0].beginGeldigheid',
            },
            'NUMLIGNVN/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'heeftNevenadres.[0].eindGeldigheid',
            }
        },
        'query': uva2_numlignvn_query
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

    uva2_numstahfd_query = """
{
  bagStandplaatsen {
    edges {
      node {
        amsterdamseSleutel
        beginGeldigheid
        eindGeldigheid
        heeftHoofdadres {
          edges {
            node {
              amsterdamseSleutel
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

    uva2_numstanvn_query = """
{
  bagStandplaatsen {
    edges {
      node {
        amsterdamseSleutel
        beginGeldigheid
        eindGeldigheid
        heeftNevenadres {
          edges {
            node {
              amsterdamseSleutel
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
                'formatter': format_uva2_mapping,
                'value': 'status.code',
                'kwargs': {'mapping_name': 'standplaatsen_status'},
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

    # NUMSTAHFD
    bag.StandplaatsenExportConfig.products['uva2_numstahfd'] = {
        'api_type': 'graphql_streaming',
        'exporter': uva2_exporter,
        'entity_filters': [
            NotEmptyFilter('amsterdamseSleutel'),
            NotEmptyFilter('heeftHoofdadres.[0].amsterdamseSleutel'),
        ],
        'filename': lambda: get_uva2_filename("NUMSTAHFD"),
        'mime_type': 'plain/text',
        'format': {
            'sleutelVerzendend': 'heeftHoofdadres.[0].amsterdamseSleutel',
            'IdentificatiecodeNummeraanduiding': 'heeftHoofdadres.[0].amsterdamseSleutel',
            'TijdvakGeldigheid/begindatumTijdvakGeldigheid': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'heeftHoofdadres.[0].beginGeldigheid',
            },
            'TijdvakGeldigheid/einddatumTijdvakGeldigheid': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'heeftHoofdadres.[0].eindGeldigheid',
            },
            'NUMSTAHFD/STA/sleutelVerzendend': 'amsterdamseSleutel',
            'NUMSTAHFD/STA/Standplaatsidentificatie': 'amsterdamseSleutel',
            'NUMSTAHFD/TijdvakRelatie/begindatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'heeftHoofdadres.[0].beginGeldigheid',
            },
            'NUMSTAHFD/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'heeftHoofdadres.[0].eindGeldigheid',
            }
        },
        'query': uva2_numstahfd_query
    }

    # NUMSTANVN
    bag.StandplaatsenExportConfig.products['uva2_numstanvn'] = {
        'api_type': 'graphql_streaming',
        'exporter': uva2_exporter,
        'entity_filters': [
            NotEmptyFilter('amsterdamseSleutel'),
            NotEmptyFilter('heeftNevenadres.[0].amsterdamseSleutel'),
        ],
        'unfold': True,
        'filename': lambda: get_uva2_filename("NUMSTANVN"),
        'mime_type': 'plain/text',
        'format': {
            'sleutelVerzendend': 'heeftNevenadres.[0].amsterdamseSleutel',
            'IdentificatiecodeNummeraanduiding': 'heeftNevenadres.[0].amsterdamseSleutel',
            'TijdvakGeldigheid/begindatumTijdvakGeldigheid': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'heeftNevenadres.[0].beginGeldigheid',
            },
            'TijdvakGeldigheid/einddatumTijdvakGeldigheid': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'heeftNevenadres.[0].eindGeldigheid',
            },
            'NUMSTANVN/STA/sleutelVerzendend': 'amsterdamseSleutel',
            'NUMSTANVN/STA/Standplaatsidentificatie': 'amsterdamseSleutel',
            'NUMSTANVN/TijdvakRelatie/begindatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'heeftNevenadres.[0].beginGeldigheid',
            },
            'NUMSTANVN/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'heeftNevenadres.[0].eindGeldigheid',
            }
        },
        'query': uva2_numstanvn_query
    }


def _add_verblijfsobjecten_uva2_config():
    uva2_query = """
{
  bagVerblijfsobjecten {
    edges {
      node {
        amsterdamseSleutel
        gebruiksdoel
        gebruiksdoelWoonfunctie
        gebruiksdoelGezondheidszorgfunctie
        oppervlakte
        documentdatum
        documentnummer
        verdiepingToegang
        aantalEenhedenComplex
        aantalBouwlagen
        ligtInPanden {
          edges {
            node {
              typeWoonobject
              ligging
            }
          }
        }
        aantalKamers
        beginGeldigheid
        eindGeldigheid
        redenafvoer
        eigendomsverhouding
        feitelijkGebruik
        toegang
        redenopvoer
        status
        ligtInBuurt {
          edges {
            node {
              identificatie
              code
            }
          }
        }
        geometrie
      }
    }
  }
}
"""

    uva2_numvbohfd_query = """
{
  bagVerblijfsobjecten {
    edges {
      node {
        amsterdamseSleutel
        beginGeldigheid
        eindGeldigheid
        heeftHoofdadres {
          edges {
            node {
              amsterdamseSleutel
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

    uva2_numvbonvn_query = """
{
  bagVerblijfsobjecten {
    edges {
      node {
        amsterdamseSleutel
        beginGeldigheid
        eindGeldigheid
        heeftNevenadres {
          edges {
            node {
              amsterdamseSleutel
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

    bag.VerblijfsobjectenExportConfig.products['uva2'] = {
        'api_type': 'graphql_streaming',
        'exporter': uva2_exporter,
        'entity_filters': [
            NotEmptyFilter('amsterdamseSleutel'),
        ],
        'filename': lambda: get_uva2_filename("VBO"),
        'row_formatter': row_formatter_verblijfsobjecten,
        'mime_type': 'plain/text',
        'format': {
            'sleutelverzendend': 'amsterdamseSleutel',
            'Verblijfsobjectidentificatie': 'amsterdamseSleutel',
            'Verblijfsobjectgeometrie': '',
            'X-Coordinaat': {
                'action': 'format',
                'formatter': format_uva2_coordinate,
                'value': 'geometrie',
                'kwargs': {
                    'coordinate': 'x'
                }
            },
            'Y-Coordinaat': {
                'action': 'format',
                'formatter': format_uva2_coordinate,
                'value': 'geometrie',
                'kwargs': {
                    'coordinate': 'y'
                }
            },
            'GebruiksdoelVerblijfsobjectDomein': 'GebruiksdoelVerblijfsobjectDomein',
            'OmschrijvingGebruiksdoelVerblijfsobjectDomein': 'OmschrijvingGebruiksdoelVerblijfsobjectDomein',
            'OppervlakteVerblijfsobject': 'oppervlakte',
            'DocumentdatumMutatieVerblijfsobject': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'documentdatum',
            },
            'DocumentnummerMutatieVerblijfsobject': 'documentnummer',
            'Bouwlaagtoegang': 'verdiepingToegang',
            'Frontbreedte': '',
            'VerblijfsobjectnummerGemeente': '',
            'StatusCoordinaatDomein': '',
            'OmschrijvingCoordinaatDomein': '',
            'AantalVerhuurbareEenheden': 'aantalEenhedenComplex',
            'CBS-nummer': '',
            'AantalBouwlagen': 'aantalBouwlagen',
            'TypeWoonobjectDomein': {
                'action': 'format',
                'formatter': format_uva2_mapping,
                'value': 'ligtInPanden.[0].typeWoonobject.code',
                'kwargs': {'mapping_name': 'verblijfsobjecten_type_woonobject_code'},
            },
            'OmschrijvingTypeWoonobjectDomein': {
                'action': 'format',
                'formatter': format_uva2_mapping,
                'value': 'ligtInPanden.[0].typeWoonobject.omschrijving',
                'kwargs': {'mapping_name': 'verblijfsobjecten_type_woonobject_omschrijving'},
            },
            'IndicatieWoningvoorraad': '',
            'AantalKamers': 'aantalKamers',
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
            'VBOAVR/AVR/Code': 'redenafvoer.code',
            'VBOAVR/TijdvakRelatie/begindatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheid',
            },
            'VBOAVR/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheid',
            },
            'VBOBRN/BRN/Code': '',
            'VBOBRN/TijdvakRelatie/begindatumRelatie': '',
            'VBOBRN/TijdvakRelatie/einddatumRelatie': '',
            'VBOEGM/EGM/Code': {
                'action': 'fill',
                'length': 2,
                'character': '0',
                'value': 'eigendomsverhouding.code',
                'fill_type': 'rjust'
            },
            'VBOEGM/TijdvakRelatie/begindatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheid',
            },
            'VBOEGM/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheid',
            },
            'VBOFNG/FNG/Code': '',
            'VBOFNG/TijdvakRelatie/begindatumRelatie': '',
            'VBOFNG/TijdvakRelatie/einddatumRelatie': '',
            'VBOGBK/GBK/Code': 'feitelijkGebruik.code',
            'VBOGBK/TijdvakRelatie/begindatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheid',
            },
            'VBOGBK/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheid',
            },
            'VBOLOC/LOC/Code': '',
            'VBOLOC/TijdvakRelatie/begindatumRelatie': '',
            'VBOLOC/TijdvakRelatie/einddatumRelatie': '',
            'VBOLGG/LGG/Code': {
                'action': 'fill',
                'length': 2,
                'character': '0',
                'value': 'ligtInPanden.[0].ligging.code',
                'fill_type': 'rjust'
            },
            'VBOLGG/TijdvakRelatie/begindatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheid',
            },
            'VBOLGG/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheid',
            },
            'VBOMNT/MNT/Code': '',
            'VBOMNT/TijdvakRelatie/begindatumRelatie': '',
            'VBOMNT/TijdvakRelatie/einddatumRelatie': '',
            'VBOTGG/TGG/Code': 'toegang.[0].code',
            'VBOTGG/TijdvakRelatie/begindatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheid',
            },
            'VBOTGG/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheid',
            },
            'VBOOVR/OVR/Code': 'redenopvoer.code',
            'VBOOVR/TijdvakRelatie/begindatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheid',
            },
            'VBOOVR/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheid',
            },
            'VBOSTS/STS/Code': {
                'action': 'format',
                'formatter': format_uva2_mapping,
                'value': 'status.code',
                'kwargs': {'mapping_name': 'verblijfsobjecten_status'},
            },
            'VBOSTS/TijdvakRelatie/begindatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheid',
            },
            'VBOSTS/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheid',
            },
            'VBOBRT/BRT/sleutelVerzendend': 'ligtInBuurt.[0].identificatie',
            'VBOBRT/BRT/Buurtcode': 'ligtInBuurt.[0].code',
            'VBOBRT/TijdvakRelatie/begindatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheid',
            },
            'VBOBRT/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheid',
            }
        },
        'query': uva2_query
    }

    # NUMVBOHFD
    bag.VerblijfsobjectenExportConfig.products['uva2_numvbohfd'] = {
        'api_type': 'graphql_streaming',
        'exporter': uva2_exporter,
        'entity_filters': [
            NotEmptyFilter('amsterdamseSleutel'),
            NotEmptyFilter('heeftHoofdadres.[0].amsterdamseSleutel'),
        ],
        'filename': lambda: get_uva2_filename("NUMVBOHFD"),
        'mime_type': 'plain/text',
        'format': {
            'sleutelVerzendend': 'heeftHoofdadres.[0].amsterdamseSleutel',
            'IdentificatiecodeNummeraanduiding': 'heeftHoofdadres.[0].amsterdamseSleutel',
            'TijdvakGeldigheid/begindatumTijdvakGeldigheid': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'heeftHoofdadres.[0].beginGeldigheid',
            },
            'TijdvakGeldigheid/einddatumTijdvakGeldigheid': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'heeftHoofdadres.[0].eindGeldigheid',
            },
            'NUMVBOHFD/VBO/sleutelVerzendend': 'amsterdamseSleutel',
            'NUMVBOHFD/VBO/Verblijfsobjectidentificatie': 'amsterdamseSleutel',
            'NUMVBOHFD/TijdvakRelatie/begindatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'heeftHoofdadres.[0].beginGeldigheid',
            },
            'NUMVBOHFD/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'heeftHoofdadres.[0].eindGeldigheid',
            }
        },
        'query': uva2_numvbohfd_query
    }

    # NUMVBONVN
    bag.VerblijfsobjectenExportConfig.products['uva2_numvbonvn'] = {
        'api_type': 'graphql_streaming',
        'exporter': uva2_exporter,
        'entity_filters': [
            NotEmptyFilter('amsterdamseSleutel'),
            NotEmptyFilter('heeftNevenadres.[0].amsterdamseSleutel'),
        ],
        'unfold': True,
        'filename': lambda: get_uva2_filename("NUMVBONVN"),
        'mime_type': 'plain/text',
        'format': {
            'sleutelVerzendend': 'heeftNevenadres.[0].amsterdamseSleutel',
            'IdentificatiecodeNummeraanduiding': 'heeftNevenadres.[0].amsterdamseSleutel',
            'TijdvakGeldigheid/begindatumTijdvakGeldigheid': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'heeftNevenadres.[0].beginGeldigheid',
            },
            'TijdvakGeldigheid/einddatumTijdvakGeldigheid': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'heeftNevenadres.[0].eindGeldigheid',
            },
            'NUMVBONVN/sleutelVerzendend': 'amsterdamseSleutel',
            'NUMVBONVN/VBO/Verblijfsobjectidentificatie': 'amsterdamseSleutel',
            'NUMVBONVN/TijdvakRelatie/begindatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'heeftNevenadres.[0].beginGeldigheid',
            },
            'NUMVBONVN/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'heeftNevenadres.[0].eindGeldigheid',
            }
        },
        'query': uva2_numvbonvn_query
    }


def _add_panden_uva2_config():
    uva2_query = """
{
  bagPanden {
    edges {
      node {
        amsterdamseSleutel
        documentdatum
        documentnummer
        oorspronkelijkBouwjaar
        beginGeldigheid
        eindGeldigheid
        status
        ligtInBouwblok {
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

    bag.PandenExportConfig.products['uva2'] = {
        'api_type': 'graphql_streaming',
        'exporter': uva2_exporter,
        'entity_filters': [
            NotEmptyFilter('amsterdamseSleutel'),
        ],
        'filename': lambda: get_uva2_filename("PND"),
        'mime_type': 'plain/text',
        'format': {
            'sleutelverzendend': 'amsterdamseSleutel',
            'Pandidentificatie': 'amsterdamseSleutel',
            'Pandgeometrie': '',
            'DocumentdatumMutatiePand': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'documentdatum',
            },
            'DocumentnummerMutatiePand': 'documentnummer',
            'OorspronkelijkBouwjaarPand': 'oorspronkelijkBouwjaar',
            'LaagsteBouwlaag': '',
            'HoogsteBouwlaag': '',
            'Pandnummer': '',
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
            'PNDSTS/STS/Code': {
                'action': 'format',
                'formatter': format_uva2_mapping,
                'value': 'status.code',
                'kwargs': {'mapping_name': 'panden_status'},
            },
            'PNDSTS/TijdvakRelatie/begindatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheid',
            },
            'PNDSTS/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheid',
            },
            'PNDBBK/BBK/sleutelVerzendend': 'ligtInBouwblok.[0].identificatie',
            'PNDBBK/BBK/Bouwbloknummer': 'ligtInBouwblok.[0].code',
            'PNDBBK/TijdvakRelatie/begindatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheid',
            },
            'PNDBBK/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheid',
            }
        },
        'query': uva2_query
    }
