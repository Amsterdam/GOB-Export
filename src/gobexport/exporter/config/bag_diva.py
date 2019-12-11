import re

from datetime import date
import dateutil.parser as dt_parser

from gobexport.exporter.config import bag
from gobexport.exporter.csv import csv_exporter
from gobexport.exporter.dat import dat_exporter
from gobexport.exporter.uva2 import uva2_exporter
from gobexport.exporter.esri import get_x, get_y, get_longitude, get_latitude

from gobexport.filters.unique_filter import UniqueFilter
from gobexport.filters.notempty_filter import NotEmptyFilter

UVA2_DATE_FORMAT = '%Y%m%d'
UVA2_MAPPING = {
    'ligplaatsen_status_code': {
        '1': '33',
        '2': '34',
    },
    'ligplaatsen_status_vervallen': {
        '1': 'N',
        '2': 'J',
    },
    'nummeraanduidingen_status_code': {
        '1': '16',
        '2': '17',
    },
    'nummeraanduidingen_status_vervallen': {
        '1': 'N',
        '2': 'J',
    },
    'openbareruimtes_status': {
        '1': '35',
        '2': '36',
    },
    'standplaatsen_status_code': {
        '1': '37',
        '2': '38',
    },
    'standplaatsen_status_vervallen': {
        '1': 'N',
        '2': 'J',
    },
    'panden_status_code': {
        '1': '24',
        '2': '25',
        '3': '26',
        '7': '27',
        '8': '28',
        '9': '29',
        '10': '30',
        '11': '31',
        '12': '32',
        '13': '50',
        '14': '51',
    },
    'panden_status_vervallen': {
        '1': 'N',
        '2': 'N',
        '3': 'N',
        '7': 'N',
        '8': 'J',
        '9': 'J',
        '10': 'N',
        '11': 'N',
        '12': 'N',
        '13': 'N',
        '14': 'J',
    },
    'verblijfsobjecten_status': {
        '1': '18',
        '2': '19',
        '3': '20',
        '4': '21',
        '5': '22',
        '6': '23',
        '7': '40',
        '8': '41',
    },
    'verblijfsobjecten_status_vervallen': {
        '1': 'N',
        '2': 'J',
        '3': 'N',
        '4': 'N',
        '5': 'J',
        '6': 'N',
        '7': 'N',
        '8': 'J',
    },
    'verblijfsobjecten_status_coordinaat_domein': {
        '1': 'TMP',
        '2': '',
        '3': 'TMP',
        '4': 'DEF',
        '5': 'DEF',
        '6': 'DEF',
    },
    'verblijfsobjecten_status_coordinaat_omschrijving': {
        '1': 'Tijdelijk punt',
        '2': '',
        '3': 'Tijdelijk punt',
        '4': 'Definitief punt',
        '5': 'Definitief punt',
        '6': 'Definitief punt',
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
        'Recreatiewoningen': '1610',
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
        'overige gebruiksfunctie': 'BEST-overige gebruiksfunctie ',
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
        'Recreatiewoningen': 'BEST-recreatiewoningen',
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


def add_bag_diva_products():
    _add_woonplaatsen_diva_config()
    _add_openbareruimtes_diva_config()
    _add_nummeraanduidingen_diva_config()
    _add_ligplaatsen_diva_config()
    _add_standplaatsen_diva_config()
    _add_verblijfsobjecten_diva_config()
    _add_panden_diva_config()


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


def format_uva2_mapping(value, mapping_name):
    # Value could be an int or string
    value = str(value)
    assert mapping_name in UVA2_MAPPING, "A valid mapping name is required"
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


def show_date_when_reference_filled(reference_name, date_field):
    return {
        'condition': 'isempty',
        'reference': reference_name,
        'falseval': {
            'action': 'format',
            'formatter': format_uva2_date,
            'value': date_field,
        },
        'trueval': {
            'action': 'literal',
            'value': ''
        }
    }


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
    if 'node' in row:
        node = row['node']  # export via graphql/graphql_streaming
    else:
        node = row  # export via enhanced views

    # Get the first gebruiksdoel, sorted by code
    sorted_gebruiksdoel = sorted(node['gebruiksdoel'], key=lambda i: int(i['code']))
    gebruiksdoel = sorted_gebruiksdoel[0]['omschrijving']

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


def row_formatter_geometrie(row):
    """
    Format rows for DAT geometrie export with the following rules:
    1. Remove the leading 0 from the amsterdamseSleutel
    2. Format the WKT string to include a space
    """
    row['node']['amsterdamseSleutel'] = row['node']['amsterdamseSleutel'][1:]

    row['node']['geometrie'] = re.sub(r'([A-Z]+)(\(.+\))', r'\1 \2', row['node']['geometrie']) \
        if row['node']['geometrie'] else ''

    return row


def get_uva2_filename(abbreviation):
    assert abbreviation, "UVA2 requires an abbreviation"

    publish_date = date.today().strftime(UVA2_DATE_FORMAT)
    return f"UVA2_Actueel/{abbreviation}_{publish_date}_N_{publish_date}_{publish_date}.UVA2"


def get_uva2_adresobject_filename(abbreviation):
    assert abbreviation, "UVA2 ADRESOBJECT requires an abbreviation"

    publish_date = date.today().strftime(UVA2_DATE_FORMAT)
    return f"UVA2_ADRESOBJECT/ADRESOBJECT_{abbreviation}_{publish_date}.UVA2"


def get_dat_landelijke_sleutel_filename(catalogue_name, abbreviation):
    assert catalogue_name and abbreviation, "DAT Landelijke Sleutel requires a catalogue_name and an abbreviation"

    publish_date = date.today().strftime(UVA2_DATE_FORMAT)
    return f"{catalogue_name}_LandelijkeSleutel/{abbreviation}_{publish_date}.dat"


def get_dat_geometrie_filename(catalogue_name, collection_name):
    assert catalogue_name and collection_name, "DAT Geometrie requires a catalogue_name and a collection_name"

    return f"{catalogue_name}_Geometrie/{catalogue_name}_{collection_name}_GEOMETRIE.dat"


def _add_woonplaatsen_diva_config():
    uva2_query = """
{
  bagWoonplaatsen {
    edges {
      node {
        amsterdamseSleutel
        identificatie
        naam
        woonplaatsPtt
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

    dat_landelijke_sleutel_query = """
{
  bagWoonplaatsen(active: false) {
    edges {
      node {
        amsterdamseSleutel
        identificatie
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
            'WoonplaatsPTTSchrijfwijze': 'woonplaatsPtt',
            'Mutatie-gebruiker': {
                'action': 'literal',
                'value': 'DBI',
            },
            'Indicatie-vervallen': {
                'action': 'literal',
                'value': 'N',
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

    # Landelijke sleutel
    bag.WoonplaatsenExportConfig.products['dat_landelijke_sleutel'] = {
        'api_type': 'graphql_streaming',
        'exporter': csv_exporter,
        'entity_filters': [
            NotEmptyFilter('amsterdamseSleutel'),
            NotEmptyFilter('identificatie'),
            UniqueFilter('identificatie')
        ],
        'filename': lambda: get_dat_landelijke_sleutel_filename("BAG", "WPL"),
        'mime_type': 'plain/text',
        'format': {
            'asd_woonplaatscode': 'amsterdamseSleutel',
            'bag_woonplaatscode': 'identificatie',
            'ind_authentiek': {
                'action': 'literal',
                'value': 'J',
            },
            'objectklasse': {
                'action': 'literal',
                'value': 'WPL',
            },
        },
        'query': dat_landelijke_sleutel_query
    }


def _add_openbareruimtes_diva_config():
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
        straatnaamPtt
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

    dat_landelijke_sleutel_query = """
{
  bagOpenbareruimtes(active: false, sort: eind_geldigheid_desc) {
    edges {
      node {
        amsterdamseSleutel
        identificatie
        straatcode
      }
    }
  }
}
"""

    dat_geometrie_query = """
{
  bagOpenbareruimtes {
    edges {
      node {
        amsterdamseSleutel
        geometrie
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
            'StraatnaamPTTSchrijfwijze': 'straatnaamPtt',
            'Mutatie-gebruiker': {
                'action': 'literal',
                'value': 'DBI'
            },
            'Indicatie-vervallen': {
                'action': 'literal',
                'value': 'N'
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

    # Landelijke sleutel
    bag.OpenbareruimtesExportConfig.products['dat_landelijke_sleutel'] = {
        'api_type': 'graphql',
        'exporter': csv_exporter,
        'entity_filters': [
            NotEmptyFilter('amsterdamseSleutel'),
            NotEmptyFilter('identificatie'),
            UniqueFilter('identificatie')
        ],
        'filename': lambda: get_dat_landelijke_sleutel_filename("BAG", "OPR"),
        'mime_type': 'plain/text',
        'format': {
            'asd_openbare-ruimtecode': 'amsterdamseSleutel',
            'bag_openbare-ruimtecode': 'identificatie',
            'ind_authentiek': {
                'action': 'literal',
                'value': 'J',
            },
            'objectklasse': {
                'action': 'literal',
                'value': 'OPR',
            },
            'straatcode': 'straatcode'
        },
        'query': dat_landelijke_sleutel_query
    }

    # Geometrie
    bag.OpenbareruimtesExportConfig.products['dat_geometrie'] = {
        'api_type': 'graphql_streaming',
        'exporter': dat_exporter,
        'entity_filters': [
            NotEmptyFilter('amsterdamseSleutel'),
        ],
        'row_formatter': row_formatter_geometrie,
        'filename': lambda: get_dat_geometrie_filename("BAG", "OPENBARERUIMTE"),
        'mime_type': 'plain/text',
        'format': 'amsterdamseSleutel:num|geometrie:plain',
        'query': dat_geometrie_query
    }


def _add_nummeraanduidingen_diva_config():
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

    dat_landelijke_sleutel_query = """
{
  bagNummeraanduidingen(active: false) {
    edges {
      node {
        amsterdamseSleutel
        identificatie
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
            'Mutatie-gebruiker': {
                'action': 'literal',
                'value': 'DBI',
            },
            'Indicatie-vervallen': {
                'action': 'format',
                'formatter': format_uva2_mapping,
                'value': 'status.code',
                'kwargs': {'mapping_name': 'nummeraanduidingen_status_vervallen'},
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
            'NUMBRN/BRN/Code': '',
            'NUMBRN/TijdvakRelatie/begindatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheid',
            },
            'NUMBRN/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheid',
            },
            'NUMSTS/STS/Code': {
                'action': 'format',
                'formatter': format_uva2_mapping,
                'value': 'status.code',
                'kwargs': {'mapping_name': 'nummeraanduidingen_status_code'},
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

    # Landelijke sleutel
    bag.NummeraanduidingenExportConfig.products['dat_landelijke_sleutel'] = {
        'api_type': 'graphql_streaming',
        'exporter': csv_exporter,
        'entity_filters': [
            NotEmptyFilter('amsterdamseSleutel'),
            NotEmptyFilter('identificatie'),
            UniqueFilter('identificatie')
        ],
        'filename': lambda: get_dat_landelijke_sleutel_filename("BAG", "NUM"),
        'mime_type': 'plain/text',
        'format': {
            'asd_adrescode': 'amsterdamseSleutel',
            'bag_adrescode': 'identificatie',
            'ind_authentiek': {
                'action': 'literal',
                'value': 'J',
            },
            'objectklasse': {
                'action': 'literal',
                'value': 'NUM',
            },
        },
        'query': dat_landelijke_sleutel_query
    }


def _add_ligplaatsen_diva_config():
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
        heeftHoofdadres {
          edges {
            node {
              amsterdamseSleutel
              beginGeldigheid
              eindGeldigheid
              beginGeldigheidRelatie
              eindGeldigheidRelatie
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
        heeftNevenadres {
          edges {
            node {
              amsterdamseSleutel
              beginGeldigheid
              eindGeldigheid
              beginGeldigheidRelatie
              eindGeldigheidRelatie
            }
          }
        }
      }
    }
  }
}
"""

    dat_landelijke_sleutel_query = """
{
  bagLigplaatsen(active: false) {
    edges {
      node {
        amsterdamseSleutel
        identificatie
      }
    }
  }
}
"""

    dat_geometrie_query = """
{
  bagLigplaatsen {
    edges {
      node {
        amsterdamseSleutel
        geometrie
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
            'Mutatie-gebruiker': {
                'action': 'literal',
                'value': 'DBI',
            },
            'Indicatie-vervallen': {
                'action': 'format',
                'formatter': format_uva2_mapping,
                'value': 'status.code',
                'kwargs': {'mapping_name': 'ligplaatsen_status_vervallen'},
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
            'LIGBRN/BRN/Code': '',
            'LIGBRN/TijdvakRelatie/begindatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheid',
            },
            'LIGBRN/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheid',
            },
            'LIGSTS/STS/Code': {
                'action': 'format',
                'formatter': format_uva2_mapping,
                'value': 'status.code',
                'kwargs': {'mapping_name': 'ligplaatsen_status_code'},
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
                'value': 'heeftHoofdadres.[0].beginGeldigheidRelatie',
            },
            'NUMLIGHFD/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'heeftHoofdadres.[0].eindGeldigheidRelatie',
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
                'value': 'heeftNevenadres.[0].beginGeldigheidRelatie',
            },
            'NUMLIGNVN/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'heeftNevenadres.[0].eindGeldigheidRelatie',
            }
        },
        'query': uva2_numlignvn_query
    }

    # ADRESOBJECT
    bag.LigplaatsenExportConfig.products['uva2_adresobject'] = {
        'endpoint': '/gob/bag/ligplaatsen/?view=enhanced_uva2&ndjson=true',
        'exporter': uva2_exporter,
        'entity_filters': [
            NotEmptyFilter('amsterdamseSleutel'),
        ],
        'filename': lambda: get_uva2_adresobject_filename("LPS"),
        'mime_type': 'plain/text',
        'format': {
            'Identificerende sleutel ligplaats': 'amsterdamseSleutel',
            'Datum begin geldigheid mutatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheid',
            },
            'Datum einde geldigheid mutatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheid',
            },
            'Identificerende sleutel nummeraanduiding hoofdadres': 'heeftHoofdadres.amsterdamseSleutel',
            'Huisnummer hoofdadres': 'heeftHoofdadres.huisnummer',
            'Huisletter hoofdadres': 'heeftHoofdadres.huisletter',
            'Huisnummertoevoeging hoofdadres': 'heeftHoofdadres.huisnummertoevoeging',
            'Postcode hoofdadres': 'heeftHoofdadres.postcode',
            'Straatcode hoofdadres': 'ligtAanOpenbareruimte.straatcode',
            'Naam openbare ruimte hoofdadres': 'ligtAanOpenbareruimte.naam',
            'Straatnaam NEN hoofdadres': 'ligtAanOpenbareruimte.naamNen',
            'Straatnaam TPG hoofdadres': 'ligtAanOpenbareruimte.straatnaamPtt',
            'Woonplaatscode hoofdadres': 'ligtInWoonplaats.amsterdamseSleutel',
            'Woonplaatsnaam hoofdadres': 'ligtInWoonplaats.naam',
            'Datum begin geldigheid ligplaats': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheidObject',
            },
            'Datum einde geldigheid ligplaats': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheidObject',
            },
            'Stadsdeelcode': 'ligtInStadsdeel.code',
            'Stadsdeelnaam': 'ligtInStadsdeel.naam',
            'Buurtcode': {
                'action': 'format',
                'formatter': format_uva2_buurt,
                'value': 'ligtInBuurt.code',
            },
            'Buurtnaam': 'ligtInBuurt.naam',
            'Xcoordinaat(RD)': {
                'action': 'format',
                'formatter': get_x,
                'value': 'geometrie',
            },
            'Ycoordinaat(RD)': {
                'action': 'format',
                'formatter': get_y,
                'value': 'geometrie',
            },
            'Longitude(WGS84)': {
                'action': 'format',
                'formatter': get_longitude,
                'value': 'geometrie',
            },
            'Latitude(WGS84)': {
                'action': 'format',
                'formatter': get_latitude,
                'value': 'geometrie',
            },
            'Oppervlakte ligplaats': '',  # empty
            'Documentdatum mutatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'documentdatum',
            },
            'Documentnummer mutatie': 'documentnummer',
            'Broncode': '',  # empty
            'Broncode omschrijving': '',  # empty
            'Statuscode': {
                'action': 'format',
                'formatter': format_uva2_mapping,
                'value': 'status.code',
                'kwargs': {'mapping_name': 'ligplaatsen_status_code'},
            },
            'Statuscode omschrijving': 'status.omschrijving',
        }
    }

    # Landelijke sleutel
    bag.LigplaatsenExportConfig.products['dat_landelijke_sleutel'] = {
        'api_type': 'graphql_streaming',
        'exporter': csv_exporter,
        'entity_filters': [
            NotEmptyFilter('amsterdamseSleutel'),
            NotEmptyFilter('identificatie'),
            UniqueFilter('identificatie')
        ],
        'filename': lambda: get_dat_landelijke_sleutel_filename("BAG", "LIG"),
        'mime_type': 'plain/text',
        'format': {
            'asd_ligplaatscode': 'amsterdamseSleutel',
            'bag_ligplaatscode': 'identificatie',
            'ind_authentiek': {
                'action': 'literal',
                'value': 'J',
            },
            'objectklasse': {
                'action': 'literal',
                'value': 'LIG',
            },
        },
        'query': dat_landelijke_sleutel_query
    }

    # Geometrie
    bag.LigplaatsenExportConfig.products['dat_geometrie'] = {
        'api_type': 'graphql_streaming',
        'exporter': dat_exporter,
        'entity_filters': [
            NotEmptyFilter('amsterdamseSleutel'),
        ],
        'row_formatter': row_formatter_geometrie,
        'filename': lambda: get_dat_geometrie_filename("BAG", "LIGPLAATS"),
        'mime_type': 'plain/text',
        'format': 'amsterdamseSleutel:num|geometrie:plain',
        'query': dat_geometrie_query
    }


def _add_standplaatsen_diva_config():
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
        heeftHoofdadres {
          edges {
            node {
              amsterdamseSleutel
              beginGeldigheid
              eindGeldigheid
              beginGeldigheidRelatie
              eindGeldigheidRelatie
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
        heeftNevenadres {
          edges {
            node {
              amsterdamseSleutel
              beginGeldigheid
              eindGeldigheid
              beginGeldigheidRelatie
              eindGeldigheidRelatie
            }
          }
        }
      }
    }
  }
}
"""

    dat_landelijke_sleutel_query = """
{
  bagStandplaatsen(active: false) {
    edges {
      node {
        amsterdamseSleutel
        identificatie
      }
    }
  }
}
"""

    dat_geometrie_query = """
{
  bagStandplaatsen {
    edges {
      node {
        amsterdamseSleutel
        geometrie
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
            'Mutatie-gebruiker': {
                'action': 'literal',
                'value': 'DBI',
            },
            'Indicatie-vervallen': {
                'action': 'format',
                'formatter': format_uva2_mapping,
                'value': 'status.code',
                'kwargs': {'mapping_name': 'standplaatsen_status_vervallen'},
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
            'STABRN/BRN/Code': '',
            'STABRN/TijdvakRelatie/begindatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheid',
            },
            'STABRN/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheid',
            },
            'STASTS/STS/Code': {
                'action': 'format',
                'formatter': format_uva2_mapping,
                'value': 'status.code',
                'kwargs': {'mapping_name': 'standplaatsen_status_code'},
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
                'value': 'heeftHoofdadres.[0].beginGeldigheidRelatie',
            },
            'NUMSTAHFD/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'heeftHoofdadres.[0].eindGeldigheidRelatie',
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
                'value': 'heeftNevenadres.[0].beginGeldigheidRelatie',
            },
            'NUMSTANVN/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'heeftNevenadres.[0].eindGeldigheidRelatie',
            }
        },
        'query': uva2_numstanvn_query
    }

    # ADRESOBJECT
    bag.StandplaatsenExportConfig.products['uva2_adresobject'] = {
        'endpoint': '/gob/bag/standplaatsen/?view=enhanced_uva2&ndjson=true',
        'exporter': uva2_exporter,
        'entity_filters': [
            NotEmptyFilter('amsterdamseSleutel'),
        ],
        'filename': lambda: get_uva2_adresobject_filename("SPS"),
        'mime_type': 'plain/text',
        'format': {
            'Identificerende sleutel standplaats': 'amsterdamseSleutel',
            'Datum begin geldigheid mutatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheid',
            },
            'Datum einde geldigheid mutatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheid',
            },
            'Identificerende sleutel nummeraanduiding hoofdadres': 'heeftHoofdadres.amsterdamseSleutel',
            'Huisnummer hoofdadres': 'heeftHoofdadres.huisnummer',
            'Huisletter hoofdadres': 'heeftHoofdadres.huisletter',
            'Huisnummertoevoeging hoofdadres': 'heeftHoofdadres.huisnummertoevoeging',
            'Postcode hoofdadres': 'heeftHoofdadres.postcode',
            'Straatcode hoofdadres': 'ligtAanOpenbareruimte.straatcode',
            'Naam openbare ruimte hoofdadres': 'ligtAanOpenbareruimte.naam',
            'Straatnaam NEN hoofdadres': 'ligtAanOpenbareruimte.naamNen',
            'Straatnaam TPG hoofdadres': 'ligtAanOpenbareruimte.straatnaamPtt',
            'Woonplaatscode hoofdadres': 'ligtInWoonplaats.amsterdamseSleutel',
            'Woonplaatsnaam hoofdadres': 'ligtInWoonplaats.naam',
            'Datum begin geldigheid standplaats': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheidObject',
            },
            'Datum einde geldigheid standplaats': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheidObject',
            },
            'Stadsdeelcode': 'ligtInStadsdeel.code',
            'Stadsdeelnaam': 'ligtInStadsdeel.naam',
            'Buurtcode': {
                'action': 'format',
                'formatter': format_uva2_buurt,
                'value': 'ligtInBuurt.code',
            },
            'Buurtnaam': 'ligtInBuurt.naam',
            'Xcoordinaat(RD)': {
                'action': 'format',
                'formatter': get_x,
                'value': 'geometrie',
            },
            'Ycoordinaat(RD)': {
                'action': 'format',
                'formatter': get_y,
                'value': 'geometrie',
            },
            'Longitude(WGS84)': {
                'action': 'format',
                'formatter': get_longitude,
                'value': 'geometrie',
            },
            'Latitude(WGS84)': {
                'action': 'format',
                'formatter': get_latitude,
                'value': 'geometrie',
            },
            'Oppervlakte standplaats': '',  # empty
            'Documentdatum mutatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'documentdatum',
            },
            'Documentnummer mutatie': 'documentnummer',
            'Broncode': '',  # empty
            'Broncode omschrijving': '',  # empty
            'Statuscode': {
                'action': 'format',
                'formatter': format_uva2_mapping,
                'value': 'status.code',
                'kwargs': {'mapping_name': 'standplaatsen_status_code'},
            },
            'Statuscode omschrijving': 'status.omschrijving',
        }
    }

    # Landelijke sleutel
    bag.StandplaatsenExportConfig.products['dat_landelijke_sleutel'] = {
        'api_type': 'graphql_streaming',
        'exporter': csv_exporter,
        'entity_filters': [
            NotEmptyFilter('amsterdamseSleutel'),
            NotEmptyFilter('identificatie'),
            UniqueFilter('identificatie')
        ],
        'filename': lambda: get_dat_landelijke_sleutel_filename("BAG", "STA"),
        'mime_type': 'plain/text',
        'format': {
            'asd_standplaatscode': 'amsterdamseSleutel',
            'bag_standplaatscode': 'identificatie',
            'ind_authentiek': {
                'action': 'literal',
                'value': 'J',
            },
            'objectklasse': {
                'action': 'literal',
                'value': 'STA',
            },
        },
        'query': dat_landelijke_sleutel_query
    }

    # Geometrie
    bag.StandplaatsenExportConfig.products['dat_geometrie'] = {
        'api_type': 'graphql_streaming',
        'exporter': dat_exporter,
        'entity_filters': [
            NotEmptyFilter('amsterdamseSleutel'),
        ],
        'row_formatter': row_formatter_geometrie,
        'filename': lambda: get_dat_geometrie_filename("BAG", "STANDPLAATS"),
        'mime_type': 'plain/text',
        'format': 'amsterdamseSleutel:num|geometrie:plain',
        'query': dat_geometrie_query
    }


def _add_verblijfsobjecten_diva_config():
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
        cbsNummer
        aantalBouwlagen
        ligtInPanden {
          edges {
            node {
              typeWoonobject
              ligging
            }
          }
        }
        indicatieWoningvoorraad
        aantalKamers
        beginGeldigheid
        eindGeldigheid
        redenafvoer
        eigendomsverhouding
        financieringscode
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
        heeftHoofdadres {
          edges {
            node {
              amsterdamseSleutel
              beginGeldigheid
              eindGeldigheid
              beginGeldigheidRelatie
              eindGeldigheidRelatie
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
        heeftNevenadres {
          edges {
            node {
              amsterdamseSleutel
              beginGeldigheid
              eindGeldigheid
              beginGeldigheidRelatie
              eindGeldigheidRelatie
            }
          }
        }
      }
    }
  }
}
"""

    dat_landelijke_sleutel_query = """
{
  bagVerblijfsobjecten(active: false) {
    edges {
      node {
        amsterdamseSleutel
        identificatie
      }
    }
  }
}
"""

    dat_geometrie_query = """
{
  bagVerblijfsobjecten {
    edges {
      node {
        amsterdamseSleutel
        geometrie
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
            'GebruiksdoelVerblijfsobjectDomein': {
                'action': 'fill',
                'length': 4,
                'character': '0',
                'value': 'GebruiksdoelVerblijfsobjectDomein',
                'fill_type': 'rjust'
            },
            'OmschrijvingGebruiksdoelVerblijfsobjectDomein': 'OmschrijvingGebruiksdoelVerblijfsobjectDomein',
            'OppervlakteVerblijfsobject': 'oppervlakte',
            'DocumentdatumMutatieVerblijfsobject': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'documentdatum',
            },
            'DocumentnummerMutatieVerblijfsobject': 'documentnummer',
            'Bouwlaagtoegang': {
                'condition': 'isnone',
                'reference': 'verdiepingToegang',
                'trueval': {
                    'action': 'literal',
                    'value': '',
                },
                'falseval': {
                    'condition': 'isempty',
                    'reference': 'verdiepingToegang',
                    'trueval': {
                        'action': 'literal',
                        'value': '0',
                    },
                    'falseval': 'verdiepingToegang'
                }
            },
            'Frontbreedte': '',
            'VerblijfsobjectnummerGemeente': '',
            'StatusCoordinaatDomein': {
                'action': 'format',
                'formatter': format_uva2_mapping,
                'value': 'status.code',
                'kwargs': {'mapping_name': 'verblijfsobjecten_status_coordinaat_domein'}
            },
            'OmschrijvingCoordinaatDomein': {
                'action': 'format',
                'formatter': format_uva2_mapping,
                'value': 'status.code',
                'kwargs': {'mapping_name': 'verblijfsobjecten_status_coordinaat_omschrijving'}
            },
            'AantalVerhuurbareEenheden': 'aantalEenhedenComplex',
            'CBS-nummer': 'cbsNummer',
            'AantalBouwlagen': 'aantalBouwlagen',
            'TypeWoonobjectDomein': {
                'action': 'format',
                'formatter': format_uva2_mapping,
                'value': 'ligtInPanden.[0].typeWoonobject',
                'kwargs': {'mapping_name': 'verblijfsobjecten_type_woonobject_code'},
            },
            'OmschrijvingTypeWoonobjectDomein': {
                'action': 'format',
                'formatter': format_uva2_mapping,
                'value': 'ligtInPanden.[0].typeWoonobject',
                'kwargs': {'mapping_name': 'verblijfsobjecten_type_woonobject_omschrijving'},
            },
            'IndicatieWoningvoorraad': 'indicatieWoningvoorraad',
            'AantalKamers': {
                'condition': 'isnone',
                'reference': 'aantalKamers',
                'trueval': {
                    'action': 'literal',
                    'value': '',
                },
                'falseval': {
                    'condition': 'isempty',
                    'reference': 'aantalKamers',
                    'trueval': {
                        'action': 'literal',
                        'value': '0',
                    },
                    'falseval': 'aantalKamers'
                }
            },
            'Mutatie-gebruiker': {
                'action': 'literal',
                'value': 'DBI'
            },
            'Indicatie-vervallen': {
                'action': 'format',
                'formatter': format_uva2_mapping,
                'value': 'status.code',
                'kwargs': {'mapping_name': 'verblijfsobjecten_status_vervallen'}
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
            'VBOAVR/AVR/Code': 'redenafvoer.code',
            'VBOAVR/TijdvakRelatie/begindatumRelatie': show_date_when_reference_filled(
                'redenafvoer.code',
                'beginGeldigheid'
            ),
            'VBOAVR/TijdvakRelatie/einddatumRelatie': show_date_when_reference_filled(
                'redenafvoer.code',
                'eindGeldigheid'
            ),
            'VBOBRN/BRN/Code': '',
            'VBOBRN/TijdvakRelatie/begindatumRelatie': '',
            'VBOBRN/TijdvakRelatie/einddatumRelatie': '',
            'VBOEGM/EGM/Code': {
                'condition': 'isempty',
                'reference': 'eigendomsverhouding.code',
                'trueval': {
                    'action': 'literal',
                    'value': ''
                },
                'falseval': {
                    'action': 'fill',
                    'length': 2,
                    'character': '0',
                    'value': 'eigendomsverhouding.code',
                    'fill_type': 'rjust'
                }
            },
            'VBOEGM/TijdvakRelatie/begindatumRelatie': show_date_when_reference_filled(
                'eigendomsverhouding.code',
                'beginGeldigheid'
            ),
            'VBOEGM/TijdvakRelatie/einddatumRelatie': show_date_when_reference_filled(
                'eigendomsverhouding.code',
                'eindGeldigheid'
            ),
            'VBOFNG/FNG/Code': {
                'condition': 'isempty',
                'reference': 'financieringscode.code',
                'trueval': {
                    'action': 'literal',
                    'value': ''
                },
                'falseval': 'financieringscode.code'
            },
            'VBOFNG/TijdvakRelatie/begindatumRelatie': show_date_when_reference_filled(
                'financieringscode.code',
                'beginGeldigheid'
            ),
            'VBOFNG/TijdvakRelatie/einddatumRelatie': show_date_when_reference_filled(
                'financieringscode.code',
                'eindGeldigheid'
            ),
            'VBOGBK/GBK/Code': 'feitelijkGebruik.code',
            'VBOGBK/TijdvakRelatie/begindatumRelatie': show_date_when_reference_filled(
                'feitelijkGebruik.code',
                'beginGeldigheid'
            ),
            'VBOGBK/TijdvakRelatie/einddatumRelatie': show_date_when_reference_filled(
                'feitelijkGebruik.code',
                'eindGeldigheid'
            ),
            'VBOLOC/LOC/Code': '',
            'VBOLOC/TijdvakRelatie/begindatumRelatie': '',
            'VBOLOC/TijdvakRelatie/einddatumRelatie': '',
            'VBOLGG/LGG/Code': {
                'condition': 'isempty',
                'reference': 'ligtInPanden.[0].ligging.code',
                'trueval': {
                    'action': 'literal',
                    'value': '99'
                },
                'falseval': {
                    'action': 'fill',
                    'length': 2,
                    'character': '0',
                    'value': 'ligtInPanden.[0].ligging.code',
                    'fill_type': 'rjust'
                }
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
            'VBOTGG/TGG/Code': {
                'condition': 'isempty',
                'reference': 'toegang.[0].code',
                'trueval': {
                    'action': 'literal',
                    'value': ''
                },
                'falseval': {
                    'action': 'fill',
                    'length': 2,
                    'character': '0',
                    'value': 'toegang.[0].code',
                    'fill_type': 'rjust'
                }
            },
            'VBOTGG/TijdvakRelatie/begindatumRelatie': show_date_when_reference_filled(
                'toegang.[0].code',
                'beginGeldigheid'
            ),
            'VBOTGG/TijdvakRelatie/einddatumRelatie': show_date_when_reference_filled(
                'toegang.[0].code',
                'eindGeldigheid'
            ),
            'VBOOVR/OVR/Code': 'redenopvoer.code',
            'VBOOVR/TijdvakRelatie/begindatumRelatie': show_date_when_reference_filled(
                'redenopvoer.code',
                'beginGeldigheid'
            ),
            'VBOOVR/TijdvakRelatie/einddatumRelatie': show_date_when_reference_filled(
                'redenopvoer.code',
                'eindGeldigheid'
            ),
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
            'VBOBRT/BRT/Buurtcode': {
                'action': 'format',
                'formatter': format_uva2_buurt,
                'value': 'ligtInBuurt.[0].code',
            },
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
                'value': 'heeftHoofdadres.[0].beginGeldigheidRelatie',
            },
            'NUMVBOHFD/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'heeftHoofdadres.[0].eindGeldigheidRelatie',
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
                'value': 'heeftNevenadres.[0].beginGeldigheidRelatie',
            },
            'NUMVBONVN/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'heeftNevenadres.[0].eindGeldigheidRelatie',
            }
        },
        'query': uva2_numvbonvn_query
    }

    # ADRESOBJECT
    bag.VerblijfsobjectenExportConfig.products['uva2_adresobject'] = {
        'endpoint': '/gob/bag/verblijfsobjecten/?view=enhanced_uva2&ndjson=true',
        'exporter': uva2_exporter,
        'entity_filters': [
            NotEmptyFilter('amsterdamseSleutel'),
        ],
        'filename': lambda: get_uva2_adresobject_filename("VOT"),
        'row_formatter': row_formatter_verblijfsobjecten,
        'mime_type': 'plain/text',
        'format': {
            'Identificerende sleutel Verblijfsobject': 'amsterdamseSleutel',
            'Datum begin geldigheid mutatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheid',
            },
            'Datum einde geldigheid mutatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheid',
            },
            'Identificerende sleutel nummeraanduiding hoofdadres': 'heeftHoofdadres.amsterdamseSleutel',
            'Huisnummer hoofdadres': 'heeftHoofdadres.huisnummer',
            'Huisletter hoofdadres': 'heeftHoofdadres.huisletter',
            'Huisnummertoevoeging hoofdadres': 'heeftHoofdadres.huisnummertoevoeging',
            'Postcode hoofdadres': 'heeftHoofdadres.postcode',
            'Straatcode hoofdadres': 'ligtAanOpenbareruimte.straatcode',
            'Naam openbare ruimte hoofdadres': 'ligtAanOpenbareruimte.naam',
            'Straatnaam NEN hoofdadres': 'ligtAanOpenbareruimte.naamNen',
            'Straatnaam TPG hoofdadres': 'ligtAanOpenbareruimte.straatnaamPtt',
            'Woonplaatscode hoofdadres': 'ligtInWoonplaats.amsterdamseSleutel',
            'Woonplaatsnaam hoofdadres': 'ligtInWoonplaats.naam',
            'Datum begin geldigheid verblijfsobject': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheidObject',
            },
            'Datum einde geldigheid verblijfsobject': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheidObject',
            },
            'Stadsdeelcode': 'ligtInStadsdeel.code',
            'Stadsdeelnaam': 'ligtInStadsdeel.naam',
            'Buurtcode': {
                'action': 'format',
                'formatter': format_uva2_buurt,
                'value': 'ligtInBuurt.code',
            },
            'Buurtnaam': 'ligtInBuurt.naam',
            'Xcoordinaat(RD)': {
                'action': 'format',
                'formatter': get_x,
                'value': 'geometrie',
            },
            'Ycoordinaat(RD)': {
                'action': 'format',
                'formatter': get_y,
                'value': 'geometrie',
            },
            'Longitude(WGS84)': {
                'action': 'format',
                'formatter': get_longitude,
                'value': 'geometrie',
            },
            'Latitude(WGS84)': {
                'action': 'format',
                'formatter': get_latitude,
                'value': 'geometrie',
            },
            'Oppervlakte verblijfsobject': '',  # empty
            'Documentdatum mutatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'documentdatum',
            },
            'Documentnummer mutatie': 'documentnummer',
            'Broncode': '',  # empty
            'Broncode omschrijving': '',  # empty
            'Statuscode': {
                'action': 'format',
                'formatter': format_uva2_mapping,
                'value': 'status.code',
                'kwargs': {'mapping_name': 'verblijfsobjecten_status'},
            },
            'Statuscode omschrijving': 'status.omschrijving',
            'Status coordinaat domein': {
                'action': 'format',
                'formatter': format_uva2_mapping,
                'value': 'status.code',
                'kwargs': {'mapping_name': 'verblijfsobjecten_status_coordinaat_domein'}
            },
            'Omschrijving coordinaat domein': {
                'action': 'format',
                'formatter': format_uva2_mapping,
                'value': 'status.code',
                'kwargs': {'mapping_name': 'verblijfsobjecten_status_coordinaat_omschrijving'}
            },
            'Gebruiksdoel code': {
                'action': 'fill',
                'length': 4,
                'character': '0',
                'value': 'GebruiksdoelVerblijfsobjectDomein',
                'fill_type': 'rjust'
            },
            'Gebruiksdoel omschrijving': 'OmschrijvingGebruiksdoelVerblijfsobjectDomein',
            'Bouwlaag toegang': {
                'condition': 'isnone',
                'reference': 'verdiepingToegang',
                'trueval': {
                    'action': 'literal',
                    'value': '',
                },
                'falseval': {
                    'condition': 'isempty',
                    'reference': 'verdiepingToegang',
                    'trueval': {
                        'action': 'literal',
                        'value': '0',
                    },
                    'falseval': 'verdiepingToegang'
                }
            },
            'Aantal verhuurbare eenheden': 'aantalEenhedenComplex',
            'CBS-nummer': 'cbsNummer',
            'Aantal bouwlagen': 'aantalBouwlagen',
            'Type woonobject domein': {
                'action': 'format',
                'formatter': format_uva2_mapping,
                'value': 'ligtInPanden.typeWoonobject',
                'kwargs': {'mapping_name': 'verblijfsobjecten_type_woonobject_code'},
            },
            'Type woonobject omschrijving': {
                'action': 'format',
                'formatter': format_uva2_mapping,
                'value': 'ligtInPanden.typeWoonobject',
                'kwargs': {'mapping_name': 'verblijfsobjecten_type_woonobject_omschrijving'},
            },
            'Indicatie woningvoorraad': 'indicatieWoningvoorraad',
            'Gebruik code': 'feitelijkGebruik.code',
            'Gebruik omschrijving': 'feitelijkGebruik.omschrijving',
            'Locatie ingang code': '',  # empty
            'Locatie ingang omschrijving': '',  # empty
            'Ligging code': 'ligtInPanden.ligging.code',
            'Ligging omschrijving': 'ligtInPanden.ligging.omschrijving',
            'Financieringswijze code': 'financieringscode.code',
            'Financieringswijze omschrijving': 'financieringscode.omschrijving',
            'Eigendomsverhouding code': 'eigendomsverhouding.code',
            'Eigendomsverhouding omschrijving': 'eigendomsverhouding.omschrijving',
            'Toegang code': 'toegang.code',
            'Toegang omschrijving': 'toegang.omschrijving',
            'Bouwjaar': 'ligtInPanden.oorspronkelijkBouwjaar',
            'Bouwbloknummer': 'ligtInPanden.ligtInBouwblok.code',
        }
    }

    # Landelijke sleutel
    bag.VerblijfsobjectenExportConfig.products['dat_landelijke_sleutel'] = {
        'api_type': 'graphql_streaming',
        'exporter': csv_exporter,
        'entity_filters': [
            NotEmptyFilter('amsterdamseSleutel'),
            NotEmptyFilter('identificatie'),
            UniqueFilter('identificatie')
        ],
        'filename': lambda: get_dat_landelijke_sleutel_filename("BAG", "VBO"),
        'mime_type': 'plain/text',
        'format': {
            'asd_verblijfsobjectcode': 'amsterdamseSleutel',
            'bag_verblijfsobjectcode': 'identificatie',
            'ind_authentiek': {
                'action': 'literal',
                'value': 'J',
            },
            'objectklasse': {
                'action': 'literal',
                'value': 'VBO',
            },
        },
        'query': dat_landelijke_sleutel_query
    }

    # Geometrie
    bag.VerblijfsobjectenExportConfig.products['dat_geometrie'] = {
        'api_type': 'graphql_streaming',
        'exporter': dat_exporter,
        'entity_filters': [
            NotEmptyFilter('amsterdamseSleutel'),
        ],
        'row_formatter': row_formatter_geometrie,
        'filename': lambda: get_dat_geometrie_filename("BAG", "VERBLIJFSOBJECT"),
        'mime_type': 'plain/text',
        'format': 'amsterdamseSleutel:num|geometrie:plain',
        'query': dat_geometrie_query
    }


def _add_panden_diva_config():
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

    uva2_pndvbo_query = """
{
  bagVerblijfsobjecten {
    edges {
      node {
        amsterdamseSleutel
        beginGeldigheid
        eindGeldigheid
        ligtInPanden {
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

    dat_landelijke_sleutel_query = """
{
  bagPanden(active: false) {
    edges {
      node {
        amsterdamseSleutel
        identificatie
      }
    }
  }
}
"""

    dat_geometrie_query = """
{
  bagPanden {
    edges {
      node {
        amsterdamseSleutel
        geometrie
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
            'Mutatie-gebruiker': {
                'action': 'literal',
                'value': 'DBI',
            },
            'Indicatie-vervallen': {
                'action': 'format',
                'formatter': format_uva2_mapping,
                'value': 'status.code',
                'kwargs': {'mapping_name': 'panden_status_vervallen'},
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
            'PNDSTS/STS/Code': {
                'action': 'format',
                'formatter': format_uva2_mapping,
                'value': 'status.code',
                'kwargs': {'mapping_name': 'panden_status_code'},
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

    bag.PandenExportConfig.products['uva2_pndvbo'] = {
        'api_type': 'graphql_streaming',
        'exporter': uva2_exporter,
        'entity_filters': [
            NotEmptyFilter('amsterdamseSleutel'),
            NotEmptyFilter('ligtInPanden.[0].amsterdamseSleutel'),
        ],
        'filename': lambda: get_uva2_filename("PNDVBO"),
        'mime_type': 'plain/text',
        'unfold': True,
        'format': {
            'sleutelverzendend': 'ligtInPanden.[0].amsterdamseSleutel',
            'Pandidentificatie': 'ligtInPanden.[0].amsterdamseSleutel',
            'TijdvakGeldigheid/begindatumTijdvakGeldigheid': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'ligtInPanden.[0].beginGeldigheid',
            },
            'TijdvakGeldigheid/einddatumTijdvakGeldigheid': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'ligtInPanden.[0].eindGeldigheid',
            },
            'PNDVBO/VBO/sleutelVerzendend': 'amsterdamseSleutel',
            'PNDVBO/VBO/Verblijfsobjectidentificatie': 'amsterdamseSleutel',
            'PNDVBO/TijdvakRelatie/begindatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'beginGeldigheid',
            },
            'PNDVBO/TijdvakRelatie/einddatumRelatie': {
                'action': 'format',
                'formatter': format_uva2_date,
                'value': 'eindGeldigheid',
            }
        },
        'query': uva2_pndvbo_query
    }

    # Landelijke sleutel
    bag.PandenExportConfig.products['dat_landelijke_sleutel'] = {
        'api_type': 'graphql_streaming',
        'exporter': csv_exporter,
        'entity_filters': [
            NotEmptyFilter('amsterdamseSleutel'),
            NotEmptyFilter('identificatie'),
            UniqueFilter('identificatie')
        ],
        'filename': lambda: get_dat_landelijke_sleutel_filename("BAG", "PND"),
        'mime_type': 'plain/text',
        'format': {
            'asd_pandcode': 'amsterdamseSleutel',
            'bag_pandcode': 'identificatie',
            'ind_authentiek': {
                'action': 'literal',
                'value': 'J',
            },
            'objectklasse': {
                'action': 'literal',
                'value': 'PND',
            },
        },
        'query': dat_landelijke_sleutel_query
    }

    # Geometrie
    bag.PandenExportConfig.products['dat_geometrie'] = {
        'api_type': 'graphql_streaming',
        'exporter': dat_exporter,
        'entity_filters': [
            NotEmptyFilter('amsterdamseSleutel'),
        ],
        'row_formatter': row_formatter_geometrie,
        'filename': lambda: get_dat_geometrie_filename("BAG", "PAND"),
        'mime_type': 'plain/text',
        'format': 'amsterdamseSleutel:num|geometrie:plain',
        'query': dat_geometrie_query
    }
