import dateutil.parser as dt_parser
import copy

from fractions import Fraction
from operator import itemgetter
from typing import Optional

from gobexport import requests
from gobexport.config import get_host

from gobexport.exporter.csv import csv_exporter
from gobexport.exporter.esri import esri_exporter
from gobexport.exporter.utils import convert_format, get_entity_value

from gobexport.filters.notempty_filter import NotEmptyFilter
from gobexport.filters.entity_filter import EntityFilter

from gobexport.formatter.geometry import format_geometry

FILE_TYPE_MAPPING = {
    'csv': {
        'dir': 'CSV_Actueel',
        'extension': 'csv'
    },
    'shp': {
        'dir': 'SHP_Actueel',
        'extension': 'shp'
    },
    'dbf': {
        'dir': 'SHP_Actueel',
        'extension': 'dbf'
    },
    'shx': {
        'dir': 'SHP_Actueel',
        'extension': 'shx'
    },
    'prj': {
        'dir': 'SHP_Actueel',
        'extension': 'prj'
    },
}


def _get_filename_date():
    meta = requests.get(f"{get_host()}/gob/brk/meta/1").json()
    return dt_parser.parse(meta.get('kennisgevingsdatum'))


def brk_directory(type='csv'):
    type_dir, _ = itemgetter('dir', 'extension')(FILE_TYPE_MAPPING[type])
    return f"AmsterdamRegio/{type_dir}"


def brk_filename(name, type='csv', append_date=True):
    assert type in FILE_TYPE_MAPPING.keys(), "Invalid file type"
    _, extension = itemgetter('dir', 'extension')(FILE_TYPE_MAPPING[type])
    date = _get_filename_date()
    datestr = f"_{date.strftime('%Y%m%d')}" if append_date else ""
    return f'{brk_directory(type)}/BRK_{name}{datestr}.{extension}'


def sort_attributes(attrs: dict, ordering: list):
    assert len(attrs.keys()) == len(ordering), "Number of attributes does not match the number of items to sort"
    assert set(attrs.keys()) == set(ordering), "Attribute keys don't match the items to sort"

    return {k: attrs[k] for k in ordering}


def format_timestamp(datetimestr: str, format: str = '%Y%m%d%H%M%S') -> Optional[str]:
    """Transforms the datetimestr from ISO-format to the format used in the BRK exports: yyyymmddhhmmss

    :param datetimestr:
    :return:
    """
    if not datetimestr:
        # Input variable may be empty
        return None

    try:
        dt = dt_parser.parse(datetimestr)
        return dt.strftime(format)
    except ValueError:
        # If invalid datetimestr, just return the original string so that no data is lost
        return datetimestr


class BrkCsvFormat:
    def _prefix_dict(self, dct: dict, key_prefix: str, val_prefix: str):
        return {f"{key_prefix}{key}": f"{val_prefix}{val}" for key, val in dct.items()}

    def _add_condition_to_attrs(self, condition: dict, attrs: dict):
        return {k: {**condition, 'trueval': v} for k, v in attrs.items()}

    def show_when_field_notempty_condition(self, fieldref: str):
        return {
            "condition": "isempty",
            "reference": fieldref,
            "negate": True,
        }

    def show_when_field_empty_condition(self, fieldref: str):
        return {
            "condition": "isempty",
            "reference": fieldref,
        }


class KadastralesubjectenCsvFormat(BrkCsvFormat):
    ordering = [
        'BRK_SJT_ID',
        'SJT_TYPE',
        'SJT_BESCHIKKINGSBEVOEGDH_CODE',
        'SJT_BESCHIKKINGSBEVOEGDH_OMS',
        'SJT_BSN',
        'SJT_NP_VOORNAMEN',
        'SJT_NP_VOORVOEGSELSGESLSNAAM',
        'SJT_NAAM',
        'SJT_NP_GESLACHTSCODE',
        'SJT_NP_GESLACHTSCODE_OMS',
        'SJT_NP_AANDUIDINGNAAMGEBR_CODE',
        'SJT_NP_AANDUIDINGNAAMGEBR_OMS',
        'SJT_NP_GEBOORTEDATUM',
        'SJT_NP_GEBOORTEPLAATS',
        'SJT_NP_GEBOORTELAND_CODE',
        'SJT_NP_GEBOORTELAND_OMS',
        'SJT_NP_DATUMOVERLIJDEN',
        'SJT_NP_VOORNAMEN_PARTNER',
        'SJT_NP_VOORVOEGSEL_PARTNER',
        'SJT_NP_GESLACHTSNAAM_PARTNER',
        'SJT_NP_LANDWAARNAARVERTR_CODE',
        'SJT_NP_LANDWAARNAARVERTR_OMS',
        'SJT_KAD_GESLACHTSCODE',
        'SJT_KAD_GESLACHTSCODE_OMS',
        'SJT_KAD_VOORNAMEN',
        'SJT_KAD_VOORVOEGSELSGESLSNAAM',
        'SJT_KAD_GESLACHTSNAAM',
        'SJT_KAD_GEBOORTEDATUM',
        'SJT_KAD_GEBOORTEPLAATS',
        'SJT_KAD_GEBOORTELAND_CODE',
        'SJT_KAD_GEBOORTELAND_OMS',
        'SJT_KAD_INDICATIEOVERLEDEN',
        'SJT_KAD_DATUMOVERLIJDEN',
        'SJT_NNP_RSIN',
        'SJT_NNP_KVKNUMMER',
        'SJT_NNP_RECHTSVORM_CODE',
        'SJT_NNP_RECHTSVORM_OMS',
        'SJT_NNP_STATUTAIRE_NAAM',
        'SJT_NNP_STATUTAIRE_ZETEL',
        'SJT_KAD_STATUTAIRE_NAAM',
        'SJT_KAD_RECHTSVORM_CODE',
        'SJT_KAD_RECHTSVORM_OMS',
        'SJT_KAD_STATUTAIRE_ZETEL',
        'SWS_OPENBARERUIMTENAAM',
        'SWS_HUISNUMMER',
        'SWS_HUISLETTER',
        'SWS_HUISNUMMERTOEVOEGING',
        'SWS_POSTCODE',
        'SWS_WOONPLAATSNAAM',
        'SWS_BUITENLAND_ADRES',
        'SWS_BUITENLAND_WOONPLAATS',
        'SWS_BUITENLAND_REGIO',
        'SWS_BUITENLAND_NAAM',
        'SWS_BUITENLAND_CODE',
        'SWS_BUITENLAND_OMS',
        'SPS_POSTBUSNUMMER',
        'SPS_POSTBUS_POSTCODE',
        'SPS_POSTBUS_WOONPLAATSNAAM',
        'SPS_OPENBARERUIMTENAAM',
        'SPS_HUISNUMMER',
        'SPS_HUISLETTER',
        'SPS_HUISNUMMERTOEVOEGING',
        'SPS_POSTCODE',
        'SPS_WOONPLAATSNAAM',
        'SPS_BUITENLAND_ADRES',
        'SPS_BUITENLAND_WOONPLAATS',
        'SPS_BUITENLAND_REGIO',
        'SPS_BUITENLAND_NAAM',
        'SPS_BUITENLAND_CODE',
        'SPS_BUITENLAND_OMS'
    ]

    def _get_person_attrs(self):
        bsn_field = "heeftBsnVoor.bronwaarde"

        # Are prefixed with SJT_NP_ and SJT_KAD_ . Only one of the sets will be set, depending on the value of BSN
        generic_attrs = {
            'VOORNAMEN': 'voornamen',
            'VOORVOEGSELSGESLSNAAM': 'voorvoegsels',
            'GESLACHTSCODE': 'geslacht.code',
            'GESLACHTSCODE_OMS': 'geslacht.omschrijving',
            'GEBOORTEDATUM': 'geboortedatum',
            'GEBOORTEPLAATS': 'geboorteplaats',
            'GEBOORTELAND_CODE': 'geboorteland.code',
            'GEBOORTELAND_OMS': 'geboorteland.omschrijving',
            'DATUMOVERLIJDEN': 'datumOverlijden',
        }
        sjt_np_attrs = self._prefix_dict(generic_attrs, 'SJT_NP_', '')
        sjt_kad_attrs = self._prefix_dict(generic_attrs, 'SJT_KAD_', '')
        bsn_only_attrs = {
            'SJT_NAAM': 'geslachtsnaam',
        }
        non_bsn_attrs = {
            'SJT_KAD_GESLACHTSNAAM': 'geslachtsnaam'
        }

        show_when_bsn_condition = self.show_when_field_notempty_condition(bsn_field)
        show_when_not_bsn_condition = self.show_when_field_empty_condition(bsn_field)

        sjt_np_attrs = self._add_condition_to_attrs(show_when_bsn_condition, sjt_np_attrs)
        sjt_kad_attrs = self._add_condition_to_attrs(show_when_not_bsn_condition, sjt_kad_attrs)
        bsn_only_attrs = self._add_condition_to_attrs(show_when_bsn_condition, bsn_only_attrs)
        non_bsn_attrs = self._add_condition_to_attrs(show_when_not_bsn_condition, non_bsn_attrs)

        return {
            'SJT_BSN': '',
            **bsn_only_attrs,
            **non_bsn_attrs,
            **sjt_np_attrs,
            'SJT_NP_AANDUIDINGNAAMGEBR_CODE': 'naamGebruik.code',
            'SJT_NP_AANDUIDINGNAAMGEBR_OMS': 'naamGebruik.omschrijving',
            'SJT_NP_VOORNAMEN_PARTNER': 'voornamenPartner',
            'SJT_NP_VOORVOEGSEL_PARTNER': 'voorVoegselsPartner',
            'SJT_NP_GESLACHTSNAAM_PARTNER': 'geslachtsnaamPartner',
            'SJT_NP_LANDWAARNAARVERTR_CODE': 'landWaarnaarVertrokken.code',
            'SJT_NP_LANDWAARNAARVERTR_OMS': 'landWaarnaarVertrokken.omschrijving',
            **sjt_kad_attrs,
            'SJT_KAD_INDICATIEOVERLEDEN': 'indicatieOverleden',
        }

    def _get_kvk_attrs(self):
        # Are prefixed with either SJT_NNP_ or SJT_KAD_
        # If SJT_NNP_KVKNUMMER is available, SJT_NNP_ attrs should be set, otherwise SJT_KAD_
        kvk_field = "heeftKvknummerVoor.bronwaarde"

        generic_attrs = {
            'RECHTSVORM_CODE': 'rechtsvorm.code',
            'RECHTSVORM_OMS': 'rechtsvorm.omschrijving',
            'STATUTAIRE_NAAM': 'statutaireNaam',
            'STATUTAIRE_ZETEL': 'statutaireZetel',
        }

        sjt_nnp_attrs = self._prefix_dict(generic_attrs, 'SJT_NNP_', '')
        sjt_kad_attrs = self._prefix_dict(generic_attrs, 'SJT_KAD_', '')

        show_when_kvk_condition = self.show_when_field_notempty_condition(kvk_field)
        show_when_not_kvk_condition = self.show_when_field_empty_condition(kvk_field)
        sjt_nnp_attrs = self._add_condition_to_attrs(show_when_kvk_condition, sjt_nnp_attrs)
        sjt_kad_attrs = self._add_condition_to_attrs(show_when_not_kvk_condition, sjt_kad_attrs)

        return {
            'SJT_NNP_RSIN': 'heeftRsinVoor.bronwaarde',
            'SJT_NNP_KVKNUMMER': kvk_field,
            **sjt_nnp_attrs,
            **sjt_kad_attrs,
        }

    def _get_address_attrs(self):
        nl_address_format = {
            'OPENBARERUIMTENAAM': 'openbare_ruimte',
            'HUISNUMMER': 'huisnummer',
            'HUISLETTER': 'huisletter',
            'HUISNUMMERTOEVOEGING': 'huisnummer_toevoeging',
            'POSTCODE': 'postcode',
            'WOONPLAATSNAAM': 'woonplaats',
        }

        foreign_address_format = {
            'BUITENLAND_ADRES': 'adres',
            'BUITENLAND_WOONPLAATS': 'woonplaats',
            'BUITENLAND_REGIO': 'regio',
            'BUITENLAND_NAAM': 'naam',
            'BUITENLAND_CODE': 'code',
            'BUITENLAND_OMS': 'omschrijving',
        }

        postbus_format = {
            'POSTBUSNUMMER': 'nummer',
            'POSTBUS_POSTCODE': 'postcode',
            'POSTBUS_WOONPLAATSNAAM': 'woonplaatsnaam',
        }

        return {
            **self._prefix_dict(nl_address_format, 'SWS_', 'woonadres.'),
            **self._prefix_dict(foreign_address_format, 'SWS_', 'woonadresBuitenland.'),
            **self._prefix_dict(postbus_format, 'SPS_', 'postadresPostbus.'),
            **self._prefix_dict(nl_address_format, 'SPS_', 'postadres.'),
            **self._prefix_dict(foreign_address_format, 'SPS_', 'postadresBuitenland.'),
        }

    def get_format(self):
        return sort_attributes({
            'BRK_SJT_ID': 'identificatie',
            'SJT_TYPE': 'typeSubject',
            'SJT_BESCHIKKINGSBEVOEGDH_CODE': 'beschikkingsbevoegdheid.code',
            'SJT_BESCHIKKINGSBEVOEGDH_OMS': 'beschikkingsbevoegdheid.omschrijving',
            **self._get_person_attrs(),
            **self._get_kvk_attrs(),
            **self._get_address_attrs(),
        }, self.ordering)


class KadastralesubjectenExportConfig:
    format = KadastralesubjectenCsvFormat()

    products = {
        'csv': {
            'endpoint': '/gob/brk/kadastralesubjecten/?view=enhanced&ndjson=true',
            'exporter': csv_exporter,
            'filename': lambda: brk_filename("kadastraal_subject"),
            'mime_type': 'plain/text',
            'format': format.get_format(),
        }
    }


class AantekeningenExportConfig:
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
            'unfold': True,
            'cross_relations': True,
            'entity_filters': [
                NotEmptyFilter('betrokkenTenaamstelling.[0].identificatie'),
                NotEmptyFilter('rustOpKadastraalobject.[0].identificatie'),
            ],
            'exporter': csv_exporter,
            'query': art_query,
            'filename': lambda: brk_filename("aantekening"),
            'mime_type': 'plain/text',
            'format': art_format,
        },
        'csv_akt': {
            'api_type': 'graphql_streaming',
            'unfold': True,
            'entity_filters': [
                NotEmptyFilter('heeftBetrekkingOpKadastraalObject.[0].identificatie'),
            ],
            'exporter': csv_exporter,
            'query': akt_query,
            'filename': lambda: brk_filename("aantekening"),
            'mime_type': 'plain/text',
            'format': akt_format,
            'append': True,
        }
    }


class ZakelijkerechtenCsvFormat(BrkCsvFormat):

    def if_vve(self, trueval, falseval):
        return {
            'condition': 'isempty',
            'reference': 'betrokkenBijAppartementsrechtsplitsingVve.[0].identificatie',
            'negate': True,
            'trueval': trueval,
            'falseval': falseval,
        }

    def zrt_belast_met_azt_valuebuilder(self, entity: dict):
        take = [
            ('belastMetZrt1', 'akrAardZakelijkRecht'),
            ('belastMetZrt2', 'akrAardZakelijkRecht'),
            ('belastMetZrt3', 'akrAardZakelijkRecht'),
            ('belastMetZrt4', 'akrAardZakelijkRecht'),
        ]

        values = self._take_nested(take, entity)
        return self._format_azt_values(values)

    def zrt_belast_azt_valuebuilder(self, entity: dict):
        take = [
            ('belastZrt1', 'akrAardZakelijkRecht'),
            ('belastZrt2', 'akrAardZakelijkRecht'),
            ('belastZrt3', 'akrAardZakelijkRecht'),
        ]
        values = self._take_nested(take, entity)
        return self._format_azt_values(values)

    def _take_nested(self, take, entity, depth=0):
        """Takes values from nested structure with relations. Serves as input for _format_azt_values

        Take is a list of 2-tuples (relation, fieldname). The list follows the relations hierarchy and the name of the
        field to extract from that level.

        Returns a structure of values as they appear in the take list, as a list of lists. In each list the first item
        is the value of the requested field. The subsequent items are lists for each next nested relation as requested
        in take.

        Example:

        entity = {
            relA: [{
              'fieldA': 'valA',
              'relB': [
                {
                    'fieldB': 'valB1',
                    'relC': [
                        {'fieldC': 'valC1'
                    ]
                },
                {
                    'fieldB': 'valB2'
                }
              ]
            }]
        }

        take = [
            ('relA', 'fieldA'),
            ('relB', 'fieldB'),
            ('relC', 'fieldC'),
        ]

        result = [
            ['valA', ['valB1', ['valC1']], ['valB2']]
        ]

        :param take:
        :param entity:
        :param depth:
        :return:
        """
        result = []
        node = entity.get('node')

        if depth > 0:
            # Add value of requested field to result
            field = take[depth - 1][1]
            value = node.get(field)
            result = [value] if value else []

        if depth < len(take):
            relation = take[depth][0]

            if relation in node and len(node[relation]['edges']) > 0:
                # Add any nested relations as list to result
                result += [self._take_nested(take, e, depth + 1) for e in node[relation]['edges']]

        return result

    def _flatten_list(self, l: list):
        flatlist = []

        for item in l:
            if isinstance(item, list):
                flatlist.extend(self._flatten_list(item))
            else:
                flatlist.append(item)
        return flatlist

    def _is_complex_branch(self, branch: list):
        """A branch is considered complex if it contains any further branches

        For example:

        branch = ['valA', ['valB1', ['valC1']], ['valB2']]

        is considered complex, as at the outermost list is of length 3; there are two branches, one with valB1 and one
        with valB2.

        branch = ['valA', ['valB1', ['valC1', ['valD1']]]]

        is not considered complex, as each item in the branch has only one child.

        :param branch:
        :return:
        """
        return len(branch) > 2 or any(
            self._is_complex_branch(subbranch) for subbranch in branch if isinstance(subbranch, list)
        )

    def _format_branch(self, branch: list):
        """Formats a branch. Nested items in the branch are separated by a "-". If at some level the branch branches
        again, this branch is considered "complex". For a complex branch an "*" is added.

        :param branch:
        :return:
        """
        return f'[{"* " if self._is_complex_branch(branch) else ""}{"-".join(self._flatten_list(branch))}]'

    def _format_azt_values(self, values: list):
        """Separates branches bij the "+" character.

        :param values:
        :return:
        """
        return "+".join([self._format_branch(branch) for branch in values])

    def _get_np_attrs(self):
        attrs = {
            'SJT_NP_GEBOORTEDATUM': 'vanKadastraalsubject.[0].geboortedatum',
            'SJT_NP_GEBOORTEPLAATS': 'vanKadastraalsubject.[0].geboorteplaats',
            'SJT_NP_GEBOORTELAND_CODE': 'vanKadastraalsubject.[0].geboorteland.code',
            'SJT_NP_GEBOORTELAND_OMS': 'vanKadastraalsubject.[0].geboorteland.omschrijving',
            'SJT_NP_DATUMOVERLIJDEN': 'vanKadastraalsubject.[0].datumOverlijden',
        }

        return self._add_condition_to_attrs(
            self.show_when_field_empty_condition("vanKadastraalsubject.[0].statutaireNaam"),
            attrs,
        )

    def _get_nnp_attrs(self):

        attrs = {
            'SJT_NNP_RSIN': self.if_vve(
                trueval='betrokkenBijAppartementsrechtsplitsingVve.[0].heeftRsinVoor.bronwaarde',
                falseval='vanKadastraalsubject.[0].heeftRsinVoor.bronwaarde'
            ),
            'SJT_NNP_KVKNUMMER': self.if_vve(
                trueval='betrokkenBijAppartementsrechtsplitsingVve.[0].heeftKvknummerVoor.bronwaarde',
                falseval='vanKadastraalsubject.[0].heeftKvknummerVoor.bronwaarde'
            ),
            'SJT_NNP_RECHTSVORM_CODE': self.if_vve(
                trueval='betrokkenBijAppartementsrechtsplitsingVve.[0].rechtsvorm.code',
                falseval='vanKadastraalsubject.[0].rechtsvorm.code'
            ),
            'SJT_NNP_RECHTSVORM_OMS': self.if_vve(
                trueval='betrokkenBijAppartementsrechtsplitsingVve.[0].rechtsvorm.omschrijving',
                falseval='vanKadastraalsubject.[0].rechtsvorm.omschrijving'
            ),
            'SJT_NNP_STATUTAIRE_NAAM': self.if_vve(
                trueval='betrokkenBijAppartementsrechtsplitsingVve.[0].statutaireNaam',
                falseval='vanKadastraalsubject.[0].statutaireNaam'
            ),
            'SJT_NNP_STATUTAIRE_ZETEL': self.if_vve(
                trueval='betrokkenBijAppartementsrechtsplitsingVve.[0].statutaireZetel',
                falseval='vanKadastraalsubject.[0].statutaireZetel'
            )
        }

        return attrs

    def row_formatter(self, row):
        """Performs actions:
        1. Creates belastMet and belast keys in row from belastMetZrtN and belastZrtN relations.
        2. Creates betrokkenBij key
        3. Creates separate rows for TNG relations and VVE relations (so that TNG data is not linked with VVE data in
        the export)

        :param row:
        :return:
        """
        row['node']['belastMetAzt'] = self.zrt_belast_met_azt_valuebuilder(row)
        row['node']['belastAzt'] = self.zrt_belast_azt_valuebuilder(row)

        if 'belastMetZrt1' in row['node']:
            del row['node']['belastMetZrt1']

        if 'belastZrt1' in row['node']:
            del row['node']['belastZrt1']

        asg_vve_key = 'betrokkenBijAppartementsrechtsplitsingVve'
        tng_key = 'invVanZakelijkrechtBrkTenaamstellingen'

        # Set betrokkenBij
        if asg_vve_key in row['node'] and len(row['node'][asg_vve_key]['edges']):
            row['node']['betrokkenBij'] = row['node'][asg_vve_key]['edges'][0]['node']['identificatie']
        else:
            row['node']['betrokkenBij'] = None

        if asg_vve_key in row['node'] and tng_key in row['node'] and \
                len(row['node'][asg_vve_key]['edges']) and len(row['node'][tng_key]['edges']):
            # Both relations asg_vve_key and tng_key exist in row. Split row into two rows, with in one row only the
            # asg objects and the other row with only the tng objects.
            asg_row = copy.deepcopy(row)
            asg_row['node'][asg_vve_key]['edges'] = []

            row['node'][tng_key]['edges'] = []

            return [row, asg_row]

        return row

    def get_format(self):

        return {
            'BRK_ZRT_ID': 'identificatie',
            'ZRT_AARDZAKELIJKRECHT_CODE': 'aardZakelijkRecht.code',
            'ZRT_AARDZAKELIJKRECHT_OMS': 'aardZakelijkRecht.omschrijving',
            'ZRT_AARDZAKELIJKRECHT_AKR_CODE': 'akrAardZakelijkRecht',
            'ZRT_BELAST_AZT': 'belastAzt',
            'ZRT_BELAST_MET_AZT': 'belastMetAzt',
            'ZRT_ONTSTAAN_UIT': 'ontstaanUitAppartementsrechtsplitsingVve.[0].identificatie',
            'ZRT_BETROKKEN_BIJ': 'betrokkenBij',
            'ZRT_ISBEPERKT_TOT_TNG': 'isBeperktTot',
            'ZRT_BETREKKING_OP_KOT': {
                'action': 'concat',
                'fields': [
                    'aangeduidDoorKadastralegemeentecode.[0].broninfo.omschrijving',
                    {
                        'action': 'literal',
                        'value': '-'
                    },
                    'aangeduidDoorKadastralesectie.[0].code',
                    {
                        'action': 'literal',
                        'value': '-'
                    },
                    {
                        'action': 'fill',
                        'length': 5,
                        'character': '0',
                        'value': 'rustOpKadastraalobject.[0].perceelnummer',
                        'fill_type': 'rjust',
                    },
                    {
                        'action': 'literal',
                        'value': '-'
                    },
                    'rustOpKadastraalobject.[0].indexletter',
                    {
                        'action': 'literal',
                        'value': '-'
                    },
                    {
                        'action': 'fill',
                        'length': 4,
                        'character': '0',
                        'value': 'rustOpKadastraalobject.[0].indexnummer',
                        'fill_type': 'rjust',
                    }
                ]
            },
            'BRK_KOT_ID': 'rustOpKadastraalobject.[0].identificatie',
            'KOT_STATUS_CODE': 'rustOpKadastraalobject.[0].status',
            'KOT_MODIFICATION': '',
            'BRK_TNG_ID': 'invVanZakelijkrechtBrkTenaamstellingen.[0].identificatie',
            'TNG_AANDEEL_TELLER': 'invVanZakelijkrechtBrkTenaamstellingen.[0].aandeel.teller',
            'TNG_AANDEEL_NOEMER': 'invVanZakelijkrechtBrkTenaamstellingen.[0].aandeel.noemer',
            'TNG_EINDDATUM': {
                'action': 'format',
                'formatter': format_timestamp,
                'value': 'invVanZakelijkrechtBrkTenaamstellingen.[0].eindGeldigheid',
            },
            'TNG_ACTUEEL': {
                'condition': 'isempty',
                'reference': 'invVanZakelijkrechtBrkTenaamstellingen.[0].identificatie',
                'negate': True,
                'trueval': {
                    'action': 'literal',
                    'value': 'TRUE',
                },
            },
            'ASG_APP_RECHTSPLITSTYPE_CODE': 'appartementsrechtsplitsingtype.code',
            'ASG_APP_RECHTSPLITSTYPE_OMS': 'appartementsrechtsplitsingtype.omschrijving',
            'ASG_EINDDATUM': 'einddatumAppartementsrechtsplitsing',
            'ASG_ACTUEEL': 'indicatieActueelAppartementsrechtsplitsing',
            'BRK_SJT_ID': self.if_vve(
                trueval='betrokkenBijAppartementsrechtsplitsingVve.[0].identificatie',
                falseval='vanKadastraalsubject.[0].identificatie',
            ),
            'SJT_BSN': '',
            'SJT_BESCHIKKINGSBEVOEGDH_CODE': self.if_vve(
                trueval='betrokkenBijAppartementsrechtsplitsingVve.[0].beschikkingsbevoegdheid.code',
                falseval='vanKadastraalsubject.[0].beschikkingsbevoegdheid.code',
            ),
            'SJT_BESCHIKKINGSBEVOEGDH_OMS': self.if_vve(
                trueval='betrokkenBijAppartementsrechtsplitsingVve.[0].beschikkingsbevoegdheid.omschrijving',
                falseval='vanKadastraalsubject.[0].beschikkingsbevoegdheid.omschrijving',
            ),
            'SJT_NAAM': self.if_vve(
                trueval='betrokkenBijAppartementsrechtsplitsingVve.[0].statutaireNaam',
                falseval={
                    'condition': 'isempty',
                    'reference': 'vanKadastraalsubject.[0].statutaireNaam',
                    'trueval': {
                        'action': 'concat',
                        'fields': [
                            'vanKadastraalsubject.[0].geslachtsnaam',
                            {
                                'action': 'literal',
                                'value': ','
                            },
                            'vanKadastraalsubject.[0].voornamen',
                            {
                                'action': 'literal',
                                'value': ','
                            },
                            'vanKadastraalsubject.[0].voorvoegsels',
                            {
                                'action': 'literal',
                                'value': ' ('
                            },
                            'vanKadastraalsubject.[0].geslacht.code',
                            {
                                'action': 'literal',
                                'value': ')'
                            },
                        ]
                    },
                    'falseval': 'vanKadastraalsubject.[0].statutaireNaam'
                }
            ),
            **self._get_np_attrs(),
            **self._get_nnp_attrs(),
        }


class ZakelijkerechtenExportConfig:
    format = ZakelijkerechtenCsvFormat()

    query = '''
{
  brkZakelijkerechten {
    edges {
      node {
        identificatie
        aardZakelijkRecht
        akrAardZakelijkRecht
        belastZrt1: belastZakelijkerechten {
          edges {
            node {
              akrAardZakelijkRecht
              belastZrt2: belastZakelijkerechten {
                edges {
                  node {
                    akrAardZakelijkRecht
                    belastZrt3: belastZakelijkerechten {
                      edges {
                        node {
                          akrAardZakelijkRecht
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
        belastMetZrt1: belastMetZakelijkerechten {
          edges {
            node {
              akrAardZakelijkRecht
              belastMetZrt2: belastMetZakelijkerechten {
                edges {
                  node {
                    akrAardZakelijkRecht
                    belastMetZrt3: belastMetZakelijkerechten {
                      edges {
                        node {
                          akrAardZakelijkRecht
                          belastMetZrt4: belastMetZakelijkerechten {
                            edges {
                              node {
                                akrAardZakelijkRecht
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
        ontstaanUitAppartementsrechtsplitsingVve {
          edges {
            node {
              identificatie
            }
          }
        }
        betrokkenBijAppartementsrechtsplitsingVve {
          edges {
            node {
              identificatie
              rechtsvorm
              statutaireNaam
              statutaireZetel
              heeftKvknummerVoor
              heeftRsinVoor
              beschikkingsbevoegdheid
            }
          }
        }
        isBeperktTot
        rustOpKadastraalobject {
          edges {
            node {
              perceelnummer
              indexletter
              indexnummer
              identificatie
              status
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
        appartementsrechtsplitsingtype
        einddatumAppartementsrechtsplitsing
        indicatieActueelAppartementsrechtsplitsing
        invVanZakelijkrechtBrkTenaamstellingen {
          edges {
            node {
              identificatie
              aandeel
              eindGeldigheid
              vanKadastraalsubject {
                edges {
                  node {
                    identificatie
                    beschikkingsbevoegdheid
                    geslachtsnaam
                    voornamen
                    geslacht
                    voorvoegsels
                    geboortedatum
                    geboorteplaats
                    geboorteland
                    datumOverlijden
                    rechtsvorm
                    statutaireNaam
                    statutaireZetel
                    heeftBsnVoor
                    heeftKvknummerVoor
                    heeftRsinVoor
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
        'csv': {
            'exporter': csv_exporter,
            'api_type': 'graphql_streaming',
            'unfold': True,
            'row_formatter': format.row_formatter,
            'entity_filters': [
                NotEmptyFilter('invVanZakelijkrechtBrkTenaamstellingen.[0].identificatie',
                               'betrokkenBijAppartementsrechtsplitsingVve.[0].identificatie'),
            ],
            'query': query,
            'filename': lambda: brk_filename("zakelijk_recht"),
            'mime_type': 'plain/text',
            'format': format.get_format(),
        }
    }


class AardzakelijkerechtenExportConfig:
    format = {
        'AZT_CODE': 'code',
        'AZT_OMSCHRIJVING': 'waarde',
        'AZT_AARDZAKELIJKRECHT_AKR_CODE': 'akrCode',
    }

    query = '''
{
  brkAardzakelijkerechten(sort:code_asc) {
    edges {
      node {
        code
        waarde
        akrCode
      }
    }
  }
}
'''

    products = {
        'csv': {
            'exporter': csv_exporter,
            'api_type': 'graphql',
            'query': query,
            'filename': lambda: brk_filename("c_aard_zakelijkrecht"),
            'mime_type': 'plain/text',
            'format': format,
        }
    }


class BrkBagCsvFormat:

    def if_vot_relation(self, trueval: str, falseval: str):
        return {
            'condition': 'isempty',
            'reference': 'heeftEenRelatieMetVerblijfsobject.[0].identificatie',
            'negate': True,
            'trueval': trueval,
            'falseval': falseval,
        }

    def get_format(self):
        return {
            'BRK_KOT_ID': 'identificatie',
            'KOT_AKRKADGEMEENTECODE_CODE': 'aangeduidDoorKadastralegemeentecode.[0].broninfo.code',
            'KOT_AKRKADGEMEENTECODE_OMS': 'aangeduidDoorKadastralegemeentecode.[0].broninfo.omschrijving',
            'KOT_SECTIE': 'aangeduidDoorKadastralesectie.[0].code',
            'KOT_PERCEELNUMMER': 'perceelnummer',
            'KOT_INDEX_LETTER': 'indexletter',
            'KOT_INDEX_NUMMER': 'indexnummer',
            'KOT_STATUS_CODE': 'status',
            'KOT_MODIFICATION': '',
            'BAG_VOT_ID': 'heeftEenRelatieMetVerblijfsobject.[0].bronwaarde',
            'DIVA_VOT_ID': '',
            'AOT_OPENBARERUIMTENAAM': self.if_vot_relation(
                trueval='ligtAanOpenbareruimte.naam',
                falseval='heeftEenRelatieMetVerblijfsobject.[0].broninfo.openbareruimtenaam'
            ),
            'AOT_HUISNUMMER': self.if_vot_relation(
                trueval='heeftHoofdadres.huisnummer',
                falseval='heeftEenRelatieMetVerblijfsobject.[0].broninfo.huisnummer'
            ),
            'AOT_HUISLETTER': self.if_vot_relation(
                trueval='heeftHoofdadres.huisletter',
                falseval='heeftEenRelatieMetVerblijfsobject.[0].broninfo.huisletter'
            ),
            'AOT_HUISNUMMERTOEVOEGING': self.if_vot_relation(
                trueval='heeftHoofdadres.huisnummertoevoeging',
                falseval='heeftEenRelatieMetVerblijfsobject.[0].broninfo.huisnummertoevoeging'
            ),
            'AOT_POSTCODE': self.if_vot_relation(
                trueval='heeftHoofdadres.postcode',
                falseval='heeftEenRelatieMetVerblijfsobject.[0].broninfo.postcode'
            ),
            'AOT_WOONPLAATSNAAM': self.if_vot_relation(
                trueval='ligtInWoonplaats.naam',
                falseval='heeftEenRelatieMetVerblijfsobject.[0].broninfo.woonplaatsnaam'
            ),
            'BRON_RELATIE': {
                'action': 'literal',
                'value': 'BRK'
            }
        }


class BrkBagExportConfig:
    format = BrkBagCsvFormat()

    query = '''
{
  brkKadastraleobjecten {
    edges {
      node {
        identificatie
        aangeduidDoorKadastralegemeente {
          edges {
            node {
              broninfo
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
        status
        heeftEenRelatieMetVerblijfsobject {
          edges {
            node {
              identificatie
              bronwaarde
              status
              broninfo
                heeftHoofdadres {
                edges {
                  node {
                    identificatie
                    ligtAanOpenbareruimte {
                      edges {
                        node {
                          naam
                        }
                      }
                    }
                    huisnummer
                    huisletter
                    huisnummertoevoeging
                    postcode
                    ligtInWoonplaats {
                      edges {
                        node {
                          naam
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

    class VotFilter(EntityFilter):
        """Only include rows with VOT statuses, for VOT's where status is defined:
        2   Niet gerealiseerd verblijfsobject
        3   Verblijfsobject in gebruik (niet ingemeten)
        4   Verblijfsobject in gebruik
        6   Verblijfsobject buiten gebruik

        """
        valid_status_codes = [2, 3, 4, 6]
        vot_identificatie = 'heeftEenRelatieMetVerblijfsobject.[0].identificatie'
        status_code = 'heeftEenRelatieMetVerblijfsobject.[0].status.code'
        city = 'heeftEenRelatieMetVerblijfsobject.[0].broninfo.woonplaatsnaam'

        def filter(self, entity: dict):
            if get_entity_value(entity, self.vot_identificatie):
                status_code = get_entity_value(entity, self.status_code)
                return status_code and int(status_code) in self.valid_status_codes
            elif get_entity_value(entity, self.city):
                return not get_entity_value(entity, self.city).lower().startswith('amsterdam')

            return True

    products = {
        'csv': {
            'exporter': csv_exporter,
            'entity_filters': [
                NotEmptyFilter('heeftEenRelatieMetVerblijfsobject.[0].bronwaarde'),
                VotFilter(),
            ],
            'api_type': 'graphql_streaming',
            'unfold': True,
            'query': query,
            'filename': lambda: brk_filename("BRK_BAG"),
            'mime_type': 'plain/text',
            'format': format.get_format(),
        }
    }


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
            'batch_size': 10000,
            'unfold': True,
            'query': query_tng,
            'filename': lambda: brk_filename('stukdeel'),
            'mime_type': 'plain/text',
            'format': format,
            'entity_filters': [
                NotEmptyFilter('isBronVoorTenaamstelling.[0].identificatie'),
            ]
        },
        'csv_art': {
            'exporter': csv_exporter,
            'api_type': 'graphql_streaming',
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
            ]
        },
        'csv_akt': {
            'exporter': csv_exporter,
            'api_type': 'graphql_streaming',
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
            ]
        },
        'csv_zrt': {
            'exporter': csv_exporter,
            'api_type': 'graphql_streaming',
            'batch_size': 10000,
            'unfold': True,
            'append': True,
            'query': query_zrt,
            'filename': lambda: brk_filename('stukdeel'),
            'mime_type': 'plain/text',
            'format': format,
            'entity_filters': [
                NotEmptyFilter('isBronVoorZakelijkRecht.[0].appartementsrechtsplitsingidentificatie')
            ]
        }
    }


class KadastraleobjectenCsvFormat:

    def if_vve(self, trueval, falseval):
        return {
            'condition': 'isempty',
            'reference': 'betrokkenBijAppartementsrechtsplitsingVve.[0].identificatie',
            'negate': True,
            'trueval': trueval,
            'falseval': falseval,
        }

    def if_sjt(self, trueval, falseval=None):
        val = {
            'condition': 'isempty',
            'reference': 'vanKadastraalsubject.[0].identificatie',
            'negate': True,
            'trueval': trueval,
        }

        if falseval:
            val['falseval'] = falseval

        return val

    def if_empty_geenWaarde(self, reference):
        return {
            'condition': 'isempty',
            'reference': reference,
            'negate': True,
            'trueval': reference,
            'falseval': {
                'action': 'literal',
                'value': 'geenWaarde'
            }
        }

    def comma_concatter(self, value):
        return value.replace('|', ', ')

    def comma_no_space_concatter(self, value):
        return value.replace('|', ',')

    def concat_with_comma(self, reference, with_space=True):
        return {
            'action': 'format',
            'value': reference,
            'formatter': self.comma_concatter if with_space else self.comma_no_space_concatter
        }

    def format_kadgrootte(self, value):
        floatval = float(value)

        if floatval < 1:
            return str(floatval)
        else:
            return str(int(floatval))

    def vve_or_subj(self, attribute):
        return self.if_vve(
            trueval=f"betrokkenBijAppartementsrechtsplitsingVve.[0].{attribute}",
            falseval=f"vanKadastraalsubject.[0].{attribute}",
        )

    def get_format(self):
        return {
            'BRK_KOT_ID': 'identificatie',
            'KOT_GEMEENTENAAM': 'aangeduidDoorGemeente.naam',
            'KOT_AKRKADGEMCODE_CODE': 'aangeduidDoorKadastralegemeentecode.[0].broninfo.code',
            'KOT_KADASTRALEGEMEENTE_CODE': 'aangeduidDoorKadastralegemeentecode.[0].broninfo.omschrijving',
            'KOT_KAD_GEMEENTECODE': 'aangeduidDoorKadastralegemeente.[0].broninfo.code',
            'KOT_KAD_GEMEENTE_OMS': 'aangeduidDoorKadastralegemeente.[0].broninfo.omschrijving',
            'KOT_SECTIE': 'aangeduidDoorKadastralesectie.[0].code',
            'KOT_PERCEELNUMMER': 'perceelnummer',
            'KOT_INDEX_LETTER': 'indexletter',
            'KOT_INDEX_NUMMER': 'indexnummer',
            'KOT_SOORTGROOTTE_CODE': 'soortGrootte.code',
            'KOT_SOORTGROOTTE_OMS': 'soortGrootte.omschrijving',
            'KOT_KADGROOTTE': {
                'action': 'format',
                'value': 'grootte',
                'formatter': self.format_kadgrootte,
            },
            'KOT_RELATIE_G_PERCEEL': self.concat_with_comma('isOntstaanUitGPerceel.identificatie', False),
            'KOT_KOOPSOM': 'koopsom',
            'KOT_KOOPSOM_VALUTA': 'koopsomValutacode',
            'KOT_KOOPJAAR': 'koopjaar',
            'KOT_INDICATIE_MEER_OBJECTEN': 'indicatieMeerObjecten',
            'KOT_CULTUURCODEONBEBOUWD_CODE': 'soortCultuurOnbebouwd.code',
            'KOT_CULTUURCODEONBEBOUWD_OMS': 'soortCultuurOnbebouwd.omschrijving',
            'KOT_CULTUURCODEBEBOUWD_CODE': self.if_empty_geenWaarde(
                self.concat_with_comma('soortCultuurBebouwd.code')
            ),
            'KOT_CULTUURCODEBEBOUWD_OMS': self.if_empty_geenWaarde(
                self.concat_with_comma('soortCultuurBebouwd.omschrijving')
            ),
            'KOT_AKRREGISTER9TEKST': '',
            'KOT_STATUS_CODE': 'status',
            'KOT_TOESTANDSDATUM': {
                'action': 'format',
                'formatter': format_timestamp,
                'value': 'toestandsdatum',
            },
            'KOT_IND_VOORLOPIGE_KADGRENS': {
                'reference': 'indicatieVoorlopigeGeometrie',
                'action': 'case',
                'values': {
                    'J': 'Voorlopige grens',
                    'N': 'Definitieve grens',
                },
            },
            'BRK_SJT_ID': self.vve_or_subj('identificatie'),
            'SJT_NAAM': self.if_vve(
                trueval='betrokkenBijAppartementsrechtsplitsingVve.[0].statutaireNaam',
                falseval=self.if_sjt(
                    trueval={
                        'condition': 'isempty',
                        'reference': 'vanKadastraalsubject.[0].statutaireNaam',
                        'trueval': {
                            'action': 'concat',
                            'fields': [
                                'vanKadastraalsubject.[0].geslachtsnaam',
                                {
                                    'action': 'literal',
                                    'value': ','
                                },
                                'vanKadastraalsubject.[0].voornamen',
                                {
                                    'action': 'literal',
                                    'value': ','
                                },
                                'vanKadastraalsubject.[0].voorvoegsels',
                                {
                                    'action': 'literal',
                                    'value': ' ('
                                },
                                'vanKadastraalsubject.[0].geslacht.code',
                                {
                                    'action': 'literal',
                                    'value': ')'
                                },
                            ]
                        },
                        'falseval': 'vanKadastraalsubject.[0].statutaireNaam'
                    }
                )
            ),
            'SJT_TYPE': self.vve_or_subj('typeSubject'),
            'SJT_NP_GEBOORTEDATUM': 'vanKadastraalsubject.[0].geboortedatum',
            'SJT_NP_GEBOORTEPLAATS': 'vanKadastraalsubject.[0].geboorteplaats',
            'SJT_NP_GEBOORTELAND_CODE': 'vanKadastraalsubject.[0].geboorteland.code',
            'SJT_NP_GEBOORTELAND_OMS': 'vanKadastraalsubject.[0].geboorteland.omschrijving',
            'SJT_NP_DATUMOVERLIJDEN': 'vanKadastraalsubject.[0].datumOverlijden',
            'SJT_NNP_RSIN': self.vve_or_subj('heeftRsinVoor.bronwaarde'),
            'SJT_NNP_KVKNUMMER': self.vve_or_subj('heeftKvknummerVoor.bronwaarde'),
            'SJT_NNP_RECHTSVORM_CODE': self.vve_or_subj('rechtsvorm.code'),
            'SJT_NNP_RECHTSVORM_OMS': self.vve_or_subj('rechtsvorm.omschrijving'),
            'SJT_NNP_STATUTAIRE_NAAM': self.vve_or_subj('statutaireNaam'),
            'SJT_NNP_STATUTAIRE_ZETEL': self.vve_or_subj('statutaireZetel'),
            'SJT_ZRT': 'invRustOpKadastraalobjectBrkZakelijkerechten.[0].aardZakelijkRecht.omschrijving',
            'SJT_AANDEEL': self.if_vve(
                trueval={
                    'action': 'literal',
                    'value': '1/1'
                },
                falseval={
                    'condition': 'isempty',
                    'reference': 'invVanZakelijkrechtBrkTenaamstellingen.[0].aandeel.teller',
                    'negate': True,
                    'trueval': {
                        'action': 'concat',
                        'fields': [
                            'invVanZakelijkrechtBrkTenaamstellingen.[0].aandeel.teller',
                            {
                                'action': 'literal',
                                'value': '/',
                            },
                            'invVanZakelijkrechtBrkTenaamstellingen.[0].aandeel.noemer'
                        ]
                    },
                    'falseval': {
                        'action': 'literal',
                        'value': 'ONBEKEND',
                    }
                }
            ),
            'SJT_VVE_SJT_ID': 'betrokkenBijAppartementsrechtsplitsingVve.[0].identificatie',
            'SJT_VVE_UIT_EIGENDOM': 'betrokkenBijAppartementsrechtsplitsingVve.[0].statutaireNaam',
            'KOT_INONDERZOEK': 'inOnderzoek',
            'KOT_MODIFICATION': '',
            'GEOMETRIE': {
                'action': 'format',
                'formatter': format_geometry,
                'value': 'geometrie'
            },
        }


class KadastraleobjectenEsriFormat(KadastraleobjectenCsvFormat):
    inonderzk = {
        'condition': 'isempty',
        'reference': 'inOnderzoek',
        'trueval': {
            'action': 'literal',
            'value': 'N',
        },
        'falseval': {
            'action': 'literal',
            'value': 'J',
        }
    }

    toestd_dat = {
        'action': 'format',
        'formatter': format_timestamp,
        'value': 'toestandsdatum',
        'kwargs': {'format': '%Y-%m-%d'},
    }

    def get_mapping(self):
        return {
            'BRK_KOT_ID': 'BRK_KOT_ID',
            'GEMEENTE': 'KOT_GEMEENTENAAM',
            'KADGEMCODE': 'KOT_KADASTRALEGEMEENTE_CODE',
            'KADGEM': 'KOT_KAD_GEMEENTE_OMS',
            'SECTIE': 'KOT_SECTIE',
            'PERCEELNR': 'KOT_PERCEELNUMMER',
            'INDEXLTR': 'KOT_INDEX_LETTER',
            'INDEXNR': 'KOT_INDEX_NUMMER',
            'SOORTGCOD': 'KOT_SOORTGROOTTE_CODE',
            'SOORTGOMS': 'KOT_SOORTGROOTTE_OMS',
            'KADGROOTTE': 'KOT_KADGROOTTE',
            'REL_GPCL': 'KOT_RELATIE_G_PERCEEL',
            'KOOPSOM': 'KOT_KOOPSOM',
            'KOOPSOMVAL': 'KOT_KOOPSOM_VALUTA',
            'KOOPJAAR': 'KOT_KOOPJAAR',
            'MEEROB_IND': 'KOT_INDICATIE_MEER_OBJECTEN',
            'CULTONBCOD': 'KOT_CULTUURCODEONBEBOUWD_CODE',
            'CULTONBOMS': 'KOT_CULTUURCODEONBEBOUWD_OMS',
            'CULTBCOD': 'KOT_CULTUURCODEBEBOUWD_CODE',
            'CULTBOMS': 'KOT_CULTUURCODEBEBOUWD_OMS',
            'AKRREG9T': 'KOT_AKRREGISTER9TEKST',
            'STATUSCOD': 'KOT_STATUS_CODE',
            'TOESTD_DAT': self.toestd_dat,
            'VL_KGR_IND': 'KOT_IND_VOORLOPIGE_KADGRENS',
            'BRK_SJT_ID': 'BRK_SJT_ID',
            'VVE_SJT_ID': 'SJT_VVE_SJT_ID',
            'SJT_NAAM': 'SJT_NAAM',
            'SJT_TYPE': 'SJT_TYPE',
            'RSIN': 'SJT_NNP_RSIN',
            'KVKNUMMER': 'SJT_NNP_KVKNUMMER',
            'RECHTSVCOD': 'SJT_NNP_RECHTSVORM_CODE',
            'RECHTSVOMS': 'SJT_NNP_RECHTSVORM_OMS',
            'STAT_NAAM': 'SJT_NNP_STATUTAIRE_NAAM',
            'STAT_ZETEL': 'SJT_NNP_STATUTAIRE_ZETEL',
            'SJT_ZRT': 'SJT_ZRT',
            # SJT_AANDEE is not a typo. Will be truncated by GDAL, which breaks the mapping.
            'SJT_AANDEE': 'SJT_AANDEEL',
            'INONDERZK': self.inonderzk,
        }

    def get_format(self):
        csv_format = super().get_format()
        return convert_format(csv_format, self.get_mapping())


class KadastraleobjectenEsriNoSubjectsFormat(KadastraleobjectenEsriFormat):
    def get_mapping(self):
        return {
            'BRK_KOT_ID': 'BRK_KOT_ID',
            'GEMEENTE': 'KOT_GEMEENTENAAM',
            'KADGEMCODE': 'KOT_KADASTRALEGEMEENTE_CODE',
            'KADGEM': 'KOT_KAD_GEMEENTE_OMS',
            'SECTIE': 'KOT_SECTIE',
            'PERCEELNR': 'KOT_PERCEELNUMMER',
            'INDEXLTR': 'KOT_INDEX_LETTER',
            'INDEXNR': 'KOT_INDEX_NUMMER',
            'SOORTGCOD': 'KOT_SOORTGROOTTE_CODE',
            'SOORTGOMS': 'KOT_SOORTGROOTTE_OMS',
            'KADGROOTTE': 'KOT_KADGROOTTE',
            'REL_GPCL': 'KOT_RELATIE_G_PERCEEL',
            'KOOPSOM': 'KOT_KOOPSOM',
            'KOOPSOMVAL': 'KOT_KOOPSOM_VALUTA',
            'KOOPJAAR': 'KOT_KOOPJAAR',
            'MEEROB_IND': 'KOT_INDICATIE_MEER_OBJECTEN',
            'CULTONBCOD': 'KOT_CULTUURCODEONBEBOUWD_CODE',
            'CULTONBOMS': 'KOT_CULTUURCODEONBEBOUWD_OMS',
            'CULTBCOD': 'KOT_CULTUURCODEBEBOUWD_CODE',
            'CULTBOMS': 'KOT_CULTUURCODEBEBOUWD_OMS',
            'AKRREG9T': 'KOT_AKRREGISTER9TEKST',
            'STATUSCOD': 'KOT_STATUS_CODE',
            'TOESTD_DAT': self.toestd_dat,
            'VL_KGR_IND': 'KOT_IND_VOORLOPIGE_KADGRENS',
            'INONDERZK': self.inonderzk,
        }


def aandeel_sort(a: dict, b: dict):
    """Returns True if a takes preference over b

    :param a:
    :param b:
    :return:
    """
    def is_valid(aandeel: dict):
        return aandeel is not None and isinstance(aandeel, dict) and aandeel.get('teller') is not None \
               and aandeel.get('noemer') is not None

    if not is_valid(a):
        return False

    if not is_valid(b):
        return True

    return Fraction(a['teller'], a['noemer']) > Fraction(b['teller'], b['noemer'])


class KadastraleobjectenExportConfig:
    csv_format = KadastraleobjectenCsvFormat()
    esri_format = KadastraleobjectenEsriFormat()
    esri_format_no_subjects = KadastraleobjectenEsriNoSubjectsFormat()

    csv_query = '''
{
  brkKadastraleobjecten {
    edges {
      node {
        identificatie
        volgnummer
        gemeente
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
        soortGrootte
        grootte
        isOntstaanUitGPerceel {
          edges {
            node {
              identificatie
            }
          }
        }
        koopsom
        koopsomValutacode
        koopjaar
        indicatieMeerObjecten
        soortCultuurOnbebouwd
        soortCultuurBebouwd
        status
        toestandsdatum
        indicatieVoorlopigeGeometrie
        inOnderzoek
        geometrie
        invRustOpKadastraalobjectBrkZakelijkerechten(akrAardZakelijkRecht:"VE") {
          edges {
            node {
              identificatie
              aardZakelijkRecht
              betrokkenBijAppartementsrechtsplitsingVve {
                edges {
                  node {
                    identificatie
                    statutaireNaam
                    typeSubject
                    heeftRsinVoor
                    heeftKvknummerVoor
                    heeftBsnVoor
                    rechtsvorm
                    statutaireNaam
                    statutaireZetel
                  }
                }
              }
              invVanZakelijkrechtBrkTenaamstellingen {
                edges {
                  node {
                    aandeel
                    vanKadastraalsubject {
                      edges {
                        node {
                          identificatie
                          voornamen
                          voorvoegsels
                          geslachtsnaam
                          geslacht
                          statutaireNaam
                          typeSubject
                          geboortedatum
                          geboorteplaats
                          geboorteland
                          datumOverlijden
                          heeftRsinVoor
                          heeftKvknummerVoor
                          heeftBsnVoor
                          rechtsvorm
                          statutaireNaam
                          statutaireZetel
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

    esri_query = '''
{
  brkKadastraleobjecten(indexletter:"G") {
    edges {
      node {
        identificatie
        volgnummer
        gemeente
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
        soortGrootte
        grootte
        isOntstaanUitGPerceel {
          edges {
            node {
              identificatie
            }
          }
        }
        koopsom
        koopsomValutacode
        koopjaar
        indicatieMeerObjecten
        soortCultuurOnbebouwd
        soortCultuurBebouwd
        status
        toestandsdatum
        indicatieVoorlopigeGeometrie
        inOnderzoek
        geometrie
        invRustOpKadastraalobjectBrkZakelijkerechten(akrAardZakelijkRecht:"VE") {
          edges {
            node {
              identificatie
              aardZakelijkRecht
              betrokkenBijAppartementsrechtsplitsingVve {
                edges {
                  node {
                    identificatie
                    statutaireNaam
                    typeSubject
                    heeftRsinVoor
                    heeftKvknummerVoor
                    heeftBsnVoor
                    rechtsvorm
                    statutaireNaam
                    statutaireZetel
                  }
                }
              }
              invVanZakelijkrechtBrkTenaamstellingen {
                edges {
                  node {
                    aandeel
                    vanKadastraalsubject {
                      edges {
                        node {
                          identificatie
                          voornamen
                          voorvoegsels
                          geslachtsnaam
                          geslacht
                          statutaireNaam
                          typeSubject
                          geboortedatum
                          geboorteplaats
                          geboorteland
                          datumOverlijden
                          heeftRsinVoor
                          heeftKvknummerVoor
                          heeftBsnVoor
                          rechtsvorm
                          statutaireNaam
                          statutaireZetel
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

    sort = {
        'invRustOpKadastraalobjectBrkZakelijkerechten'
        '.invVanZakelijkrechtBrkTenaamstellingen'
        '.aandeel': aandeel_sort,
        'invRustOpKadastraalobjectBrkZakelijkerechten'
        '.invVanZakelijkrechtBrkTenaamstellingen'
        '.vanKadastraalsubject'
        '.identificatie':
        # Take subject ID with highest number (which is the last part of the . separated string)
            lambda x, y: int(x.split('.')[-1]) > int(y.split('.')[-1])
    }

    """
    Tenaamstellingen/Subject: Return the tenaamstelling with the largest aandeel (teller/noemer). When multiple
    tenaamstellingen have an even aandeel, sort the tenaamstellingen by its subject's geslachtsnaam.
    """
    products = {
        'csv': {
            'exporter': csv_exporter,
            'api_type': 'graphql_streaming',
            'query': csv_query,
            'filename': lambda: brk_filename('kadastraal_object'),
            'mime_type': 'plain/text',
            'format': csv_format.get_format(),
            'sort': sort,
        },
        'esri_actueel': {
            'api_type': 'graphql_streaming',
            'exporter': esri_exporter,
            'filename': 'AmsterdamRegio/SHP_Actueel/BRK_Adam_totaal_G.shp',
            'mime_type': 'application/octet-stream',
            'format': esri_format.get_format(),
            'sort': sort,
            'extra_files': [
                {
                    'filename': 'AmsterdamRegio/SHP_Actueel/BRK_Adam_totaal_G.dbf',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'AmsterdamRegio/SHP_Actueel/BRK_Adam_totaal_G.shx',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'AmsterdamRegio/SHP_Actueel/BRK_Adam_totaal_G.prj',
                    'mime_type': 'application/octet-stream'
                },
            ],
            'query': esri_query
        },
        'esri_actueel_no_subjects': {
            'api_type': 'graphql_streaming',
            'exporter': esri_exporter,
            'filename': 'AmsterdamRegio/SHP_Actueel/BRK_Adam_totaal_G_zonderSubjecten.shp',
            'mime_type': 'application/octet-stream',
            'format': esri_format_no_subjects.get_format(),
            'extra_files': [
                {
                    'filename': 'AmsterdamRegio/SHP_Actueel/BRK_Adam_totaal_G_zonderSubjecten.dbf',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'AmsterdamRegio/SHP_Actueel/BRK_Adam_totaal_G_zonderSubjecten.shx',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'AmsterdamRegio/SHP_Actueel/BRK_Adam_totaal_G_zonderSubjecten.prj',
                    'mime_type': 'application/octet-stream'
                },
            ],
            'query': esri_query
        }
    }


class GemeentesExportConfig:
    query = '''
{
  brkGemeentes(sort:naam_asc) {
    edges {
      node {
        identificatie
        naam
        geometrie
      }
    }
  }
}
'''

    shp_filename = 'BRK_GEMEENTE'
    products = {
        'csv': {
            'exporter': csv_exporter,
            'api_type': 'graphql',
            'query': query,
            'filename': lambda: brk_filename('Gemeente', type='csv'),
            'mime_type': 'plain/text',
            'format': {
                'naam': 'naam',
                'identificatie': 'identificatie',
                'geometrie': {
                    'action': 'format',
                    'formatter': format_geometry,
                    'value': 'geometrie'
                },
            }
        },
        'shape': {
            'exporter': esri_exporter,
            'api_type': 'graphql',
            'filename': f'{brk_directory("shp")}/{shp_filename}.shp',
            'mime_type': 'application/octet-stream',
            'format': {
                'GEMEENTE': 'naam',
            },
            'extra_files': [
                {
                    'filename': f'{brk_directory("dbf")}/{shp_filename}.dbf',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': f'{brk_directory("shx")}/{shp_filename}.shx',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': f'{brk_directory("prj")}/{shp_filename}.prj',
                    'mime_type': 'application/octet-stream'
                },
            ],
            'query': query
        }
    }


class KadastraleGemeentecodesExportConfig:
    query = '''
{
  brkKadastralegemeentecodes {
    edges {
      node {
        identificatie
        geometrie
        isOnderdeelVanKadastralegemeente {
          edges {
            node {
              identificatie

              ligtInGemeente {
                edges {
                  node {
                    naam
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

    filename = 'BRK_KAD_GEMEENTE'
    line_filename = 'BRK_KAD_GEMEENTE_L'
    products = {
        'shape': {
            'exporter': esri_exporter,
            'api_type': 'graphql_streaming',
            'filename': f'{brk_directory("shp")}/{filename}.shp',
            'mime_type': 'application/octet-stream',
            'format': {
                'GEMEENTE': 'ligtInGemeente.[0].naam',
                'KADGEMCODE': 'identificatie',
                'KADGEM': 'isOnderdeelVanKadastralegemeente.[0].identificatie',
            },
            'extra_files': [
                {
                    'filename': f'{brk_directory("dbf")}/{filename}.dbf',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': f'{brk_directory("shx")}/{filename}.shx',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': f'{brk_directory("prj")}/{filename}.prj',
                    'mime_type': 'application/octet-stream'
                },
            ],
            'query': query
        },
        'lineshape': {
            'exporter': esri_exporter,
            'endpoint': '/gob/brk/kadastralegemeentecodes/?view=linegeometry&ndjson=true',
            'filename': f'{brk_directory("shp")}/{line_filename}.shp',
            'mime_type': 'application/octet-stream',
            'format': {
                'GEMEENTE': 'gemeente',
                'KADGEMCODE': 'kadastraleGemeentecode',
                'KADGEM': 'kadastraleGemeente',
            },
            'extra_files': [
                {
                    'filename': f'{brk_directory("dbf")}/{line_filename}.dbf',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': f'{brk_directory("shx")}/{line_filename}.shx',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': f'{brk_directory("prj")}/{line_filename}.prj',
                    'mime_type': 'application/octet-stream'
                },
            ]
        }
    }


class KadastralesectiesExportConfig:
    query = '''
{
  brkKadastralesecties {
    edges {
      node {
        code
        geometrie
        isOnderdeelVanKadastralegemeentecode {
          edges {
            node {
              identificatie
              isOnderdeelVanKadastralegemeente {
                edges {
                  node {
                    identificatie
                    ligtInGemeente {
                      edges {
                        node {
                          naam
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

    filename = 'BRK_KAD_SECTIE'
    line_filename = 'BRK_KAD_SECTIE_L'
    products = {
        'shape': {
            'exporter': esri_exporter,
            'api_type': 'graphql_streaming',
            'filename': f'{brk_directory("shp")}/{filename}.shp',
            'mime_type': 'application/octet-stream',
            'format': {
                'GEMEENTE': 'ligtInGemeente.[0].naam',
                'KADGEMCODE': 'isOnderdeelVanKadastralegemeentecode.[0].identificatie',
                'KADGEM': 'isOnderdeelVanKadastralegemeente.[0].identificatie',
                'SECTIE': 'code',
            },
            'extra_files': [
                {
                    'filename': f'{brk_directory("dbf")}/{filename}.dbf',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': f'{brk_directory("shx")}/{filename}.shx',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': f'{brk_directory("prj")}/{filename}.prj',
                    'mime_type': 'application/octet-stream'
                },
            ],
            'query': query
        },
        'lineshape': {
            'exporter': esri_exporter,
            'endpoint': '/gob/brk/kadastralesecties/?view=linegeometry&ndjson=true',
            'filename': f'{brk_directory("shp")}/{line_filename}.shp',
            'mime_type': 'application/octet-stream',
            'format': {
                'GEMEENTE': 'gemeente',
                'KADGEMCODE': 'kadastraleGemeentecode',
                'KADGEM': 'kadastraleGemeente',
                'SECTIE': 'kadastraleSectieCode'
            },
            'extra_files': [
                {
                    'filename': f'{brk_directory("dbf")}/{line_filename}.dbf',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': f'{brk_directory("shx")}/{line_filename}.shx',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': f'{brk_directory("prj")}/{line_filename}.prj',
                    'mime_type': 'application/octet-stream'
                },
            ]
        }
    }


class BijpijlingExportConfig:
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
        bijpijlingGeometrie
      }
    }
  }
}
'''

    products = {
        'shape': {
            'exporter': esri_exporter,
            'api_type': 'graphql_streaming',
            'filename': lambda: brk_filename('bijpijling', type='shp', append_date=False),
            'entity_filters': [
                NotEmptyFilter('bijpijlingGeometrie'),
            ],
            'mime_type': 'application/octet-stream',
            'format': {
                'BRK_KOT_ID': 'identificatie',
                'GEMEENTE': 'aangeduidDoorGemeente.naam',
                'KADGEMCODE': 'aangeduidDoorKadastralegemeentecode.[0].broninfo.omschrijving',
                'KADGEM': 'aangeduidDoorKadastralegemeente.[0].broninfo.omschrijving',
                'SECTIE': 'aangeduidDoorKadastralesectie.[0].code',
                'PERCEELNR': 'perceelnummer',
                'INDEXLTR': 'indexletter',
                'INDEXNR': 'indexnummer',
                'geometrie': {
                    'action': 'format',
                    'formatter': format_geometry,
                    'value': 'bijpijlingGeometrie'
                },
            },
            'extra_files': [
                {
                    'filename': lambda: brk_filename('bijpijling', type='dbf', append_date=False),
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': lambda: brk_filename('bijpijling', type='shx', append_date=False),
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': lambda: brk_filename('bijpijling', type='prj', append_date=False),
                    'mime_type': 'application/octet-stream'
                },
            ],
            'query': query
        }
    }


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
