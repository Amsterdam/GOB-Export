import datetime

from fractions import Fraction
from operator import itemgetter

from gobexport.exporter.csv import csv_exporter
from gobexport.exporter.esri import esri_exporter

from gobexport.filters.notempty_filter import NotEmptyFilter


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


def brk_filename(name, type='csv'):
    assert type in FILE_TYPE_MAPPING.keys(), "Invalid file type"
    type_dir, extension = itemgetter('dir', 'extension')(FILE_TYPE_MAPPING[type])
    now = datetime.datetime.now()
    datestr = now.strftime('%Y%m%d')
    return f'AmsterdamRegio/{type_dir}/BRK_{name}_{datestr}.{extension}'


def sort_attributes(attrs: dict, ordering: list):
    assert len(attrs.keys()) == len(ordering), "Number of attributes does not match the number of items to sort"
    assert set(attrs.keys()) == set(ordering), "Attribute keys don't match the items to sort"

    return {k: attrs[k] for k in ordering}


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
        bsn_field = "_embedded.heeftBsnVoor.bronwaarde"

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
        kvk_field = "_embedded.heeftKvknummerVoor.bronwaarde"

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
            'SJT_NNP_RSIN': '_embedded.heeftRsinVoor.bronwaarde',
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
    filename = brk_filename("KadastraalSubject")

    products = {
        'csv': {
            'exporter': csv_exporter,
            'endpoint': '/gob/brk/kadastralesubjecten',
            'filename': filename,
            'mime_type': 'plain/text',
            'format': format.get_format(),
        }
    }


class AantekeningenExportConfig:
    filename = brk_filename("Aantekening")

    art_query = '''
{
  aantekeningenrechten {
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
                aardZakelijkRecht
                edges {
                  node {
                    rustOpKadastraalobject {
                      edges {
                        node {
                          identificatie
                          perceelnummer
                          indexletter
                          indexnummer
                          aangeduidDoorKadastralegemeentecode
                          aangeduidDoorKadastralesectie
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
        isGebaseerdOpStukdeel {
          edges {
            node {
              identificatie
              id
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
        'ATG_EINDDATUM': 'einddatum',
        'ATG_TYPE': {
            'action': 'literal',
            'value': 'Aantekening Zakelijk Recht (R)'
        },
        'BRK_KOT_ID': 'rustOpKadastraalobject.identificatie',
        'KOT_KADASTRALEGEMCODE_CODE': 'rustOpKadastraalobject.aangeduidDoorKadastralegemeentecode.bronwaarde',
        'KOT_SECTIE': 'rustOpKadastraalobject.aangeduidDoorKadastralesectie.bronwaarde',
        'KOT_PERCEELNUMMER': 'rustOpKadastraalobject.perceelnummer',
        'KOT_INDEX_LETTER': 'rustOpKadastraalobject.indexletter',
        'KOT_INDEX_NUMMER': 'rustOpKadastraalobject.indexnummer',
        'BRK_TNG_ID': 'betrokkenTenaamstelling.identificatie',
        'ZRT_AARD_ZAKELIJKRECHT_CODE': 'vanZakelijkRecht.aardZakelijkRecht.code',
        'ZRT_AARD_ZAKELIJKRECHT_OMS': 'vanZakelijkRecht.aardZakelijkRecht.omschrijving',
        'BRK_SJT_ID': 'heeftBetrokkenPersoon.identificatie',
    }

    akt_query = '''
{
  aantekeningenkadastraleobjecten {
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
              aangeduidDoorKadastralegemeentecode
              aangeduidDoorKadastralesectie
            }
          }
        }
        isGebaseerdOpStukdeel {
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

    akt_format = {
        'BRK_ATG_ID': 'identificatie',
        'ATG_AARDAANTEKENING_CODE': 'aard.code',
        'ATG_AARDAANTEKENING_OMS': 'aard.omschrijving',
        'ATG_OMSCHRIJVING': 'omschrijving',
        'ATG_EINDDATUM': 'einddatum',
        'ATG_TYPE': {
            'action': 'literal',
            'value': 'Aantekening Kadastraal object (O)'
        },
        'BRK_KOT_ID': 'heeftBetrekkingOpKadastraalObject.identificatie',
        'KOT_KADASTRALEGEMCODE_CODE':
            'heeftBetrekkingOpKadastraalObject.aangeduidDoorKadastralegemeentecode.bronwaarde',
        'KOT_SECTIE': 'heeftBetrekkingOpKadastraalObject.aangeduidDoorKadastralesectie.bronwaarde',
        'KOT_PERCEELNUMMER': 'heeftBetrekkingOpKadastraalObject.perceelnummer',
        'KOT_INDEX_LETTER': 'heeftBetrekkingOpKadastraalObject.indexletter',
        'KOT_INDEX_NUMMER': 'heeftBetrekkingOpKadastraalObject.indexnummer',
        'BRK_TNG_ID': '',
        'ZRT_AARD_ZAKELIJKRECHT_CODE': '',
        'ZRT_AARD_ZAKELIJKRECHT_OMS': '',
        'BRK_SJT_ID': 'heeftBetrokkenPersoon.identificatie',
    }

    products = {
        'csv_art': {
            'api_type': 'graphql_streaming',
            'unfold': True,
            'exporter': csv_exporter,
            'query': art_query,
            'filename': filename,
            'mime_type': 'plain/text',
            'format': art_format,
        },
        'csv_akt': {
            'api_type': 'graphql_streaming',
            'unfold': True,
            'exporter': csv_exporter,
            'query': akt_query,
            'filename': filename,
            'mime_type': 'plain/text',
            'format': akt_format,
            'append': True,
        }
    }


class ZakelijkerechtenCsvFormat(BrkCsvFormat):

    def _get_np_attrs(self):
        bsn_field = "vanKadastraalsubject.heeftBsnVoor.bronwaarde"

        attrs = {
            'SJT_NP_GEBOORTEDATUM': 'vanKadastraalsubject'
                                    '.geboortedatum',
            'SJT_NP_GEBOORTEPLAATS': 'vanKadastraalsubject'
                                     '.geboorteplaats',
            'SJT_NP_GEBOORTELAND_CODE': 'vanKadastraalsubject'
                                        '.geboorteland.code',
            'SJT_NP_GEBOORTELAND_OMS': 'vanKadastraalsubject'
                                       '.geboorteland.omschrijving',
            'SJT_NP_DATUMOVERLIJDEN': 'vanKadastraalsubject'
                                      '.datumOverlijden',
        }

        return self._add_condition_to_attrs(
            self.show_when_field_notempty_condition(bsn_field),
            attrs,
        )

    def _get_nnp_attrs(self):
        kvk_field = 'vanKadastraalsubject.heeftKvknummerVoor.bronwaarde'

        attrs = {
            'SJT_NNP_RSIN': 'heeftRsinVoor.bronwaarde',
            'SJT_NNP_KVKNUMMER': 'heeftKvknummerVoor.bronwaarde',
            'SJT_NNP_RECHTSVORM_CODE': 'vanKadastraalsubject'
                                       '.rechtsvorm.code',
            'SJT_NNP_RECHTSVORM_OMS': 'vanKadastraalsubject'
                                      '.rechtsvorm.omschrijving',
            'SJT_NNP_STATUTAIRE_NAAM': 'vanKadastraalsubject'
                                       '.statutaireNaam',
            'SJT_NNP_STATUTAIRE_ZETEL': 'vanKadastraalsubject'
                                        '.statutaireZetel'
        }

        return self._add_condition_to_attrs(
            self.show_when_field_notempty_condition(kvk_field),
            attrs,
        )

    def get_format(self):
        return {
            'BRK_ZRT_ID': 'identificatie',
            'ZRT_AARDZAKELIJKRECHT_CODE': 'aardZakelijkRecht.code',
            'ZRT_AARDZAKELIJKRECHT_OMS': 'aardZakelijkRecht.omschrijving',
            'ZRT_AARDZAKELIJKRECHT_AKR_CODE': 'akrAardZakelijkRecht',
            'ZRT_BELAST_AZT': 'belastZakelijkeRechten.akrAardZakelijkRecht',
            'ZRT_BELAST_MET_AZT': 'belastMetZakelijkeRechten.akrAardZakelijkRecht',
            'ZRT_ONTSTAAN_UIT': 'ontstaanUitAppartementsrechtsplitsing',
            'ZRT_BETROKKEN_BIJ': 'betrokkenBijAppartementsrechtsplitsing',
            'ZRT_ISBEPERKT_TOT_TNG': 'isBeperktTot',
            'ZRT_BETREKKING_OP_KOT': {
                'action': 'concat',
                'fields': [
                    'rustOpKadastraalobject.aangeduidDoorKadastralegemeentecode.bronwaarde',
                    {
                        'action': 'literal',
                        'value': '-'
                    },
                    'rustOpKadastraalobject.aangeduidDoorKadastralesectie.bronwaarde',
                    {
                        'action': 'literal',
                        'value': '-'
                    },
                    'rustOpKadastraalobject.perceelnummer',
                    {
                        'action': 'literal',
                        'value': '-'
                    },
                    'rustOpKadastraalobject.indexletter',
                    {
                        'action': 'literal',
                        'value': '-'
                    },
                    'rustOpKadastraalobject.indexnummer',
                ]
            },
            'BRK_KOT_ID': 'rustOpKadastraalobject.identificatie',
            'KOT_STATUS_CODE': 'rustOpKadastraalobject.status',
            'KOT_MODIFICATION': 'rustOpKadastraalobject.wijzigingsdatum',
            'BRK_TNG_ID': 'invVanZakelijkrechtBrkTenaamstellingen.identificatie',
            'TNG_AANDEEL_TELLER': 'invVanZakelijkrechtBrkTenaamstellingen.aandeel.teller',
            'TNG_AANDEEL_NOEMER': 'invVanZakelijkrechtBrkTenaamstellingen.aandeel.noemer',
            'TNG_EINDDATUM': 'invVanZakelijkrechtBrkTenaamstellingen.eindGeldigheid',
            'TNG_ACTUEEL': {
                'condition': 'isempty',
                'reference': 'invVanZakelijkrechtBrkTenaamstellingen.eindGeldigheid',
                'trueval': {
                    'action': 'literal',
                    'value': 'TRUE',
                },
                'falseval': {
                    'action': 'literal',
                    'value': 'FALSE',
                }
            },
            'ASG_APP_RECHTSPLITSTYPE_CODE': 'appartementsrechtsplitsingtype.code',
            'ASG_APP_RECHTSPLITSTYPE_OMS': 'appartementsrechtsplitsingtype.omschrijving',
            'ASG_EINDDATUM': 'einddatumAppartementsrechtsplitsing',
            'ASG_ACTUEEL': 'indicatieActueelAppartementsrechtsplitsing',
            'BRK_SJT_ID': 'vanKadastraalsubject.identificatie',
            'SJT_BSN': 'vanKadastraalsubject.heeftBsnVoor.bronwaarde',
            'SJT_BESCHIKKINGSBEVOEGDH_CODE': 'vanKadastraalsubject'
                                             '.beschikkingsbevoegdheid.code',
            'SJT_BESCHIKKINGSBEVOEGDH_OMS': 'vanKadastraalsubject'
                                            '.beschikkingsbevoegdheid.omschrijving',
            'SJT_NAAM': {
                'condition': 'isempty',
                'reference': 'vanKadastraalsubject.heeftBsnVoor.bronwaarde',
                'negate': True,
                'trueval': {
                    'action': 'concat',
                    'fields': [
                        'vanKadastraalsubject.geslachtsnaam',
                        {
                            'action': 'literal',
                            'value': ','
                        },
                        'vanKadastraalsubject.voornamen',
                        {
                            'action': 'literal',
                            'value': ','
                        },
                        'vanKadastraalsubject.voorvoegsels',
                        {
                            'action': 'literal',
                            'value': ' ('
                        },
                        'vanKadastraalsubject.geslacht.code',
                        {
                            'action': 'literal',
                            'value': ')'
                        },
                    ]
                },
                'falseval': 'vanKadastraalsubject.statutaireNaam'
            },
            **self._get_np_attrs(),
            **self._get_nnp_attrs(),
        }


class ZakelijkerechtenExportConfig:
    filename = brk_filename("zakelijk_recht")
    format = ZakelijkerechtenCsvFormat()

    query = '''
{
  zakelijkerechten {
    edges {
      node {
        identificatie
        aardZakelijkRecht
        akrAardZakelijkRecht
        belastZakelijkerechten {
          edges {
            node {
              akrAardZakelijkRecht
            }
          }
        }
        belastMetZakelijkerechten {
          edges {
            node {
              akrAardZakelijkRecht
            }
          }
        }
        ontstaanUitAppartementsrechtsplitsing
        betrokkenBijAppartementsrechtsplitsing
        isBeperktTot
        rustOpKadastraalobject {
          edges {
            node {
              perceelnummer
              indexletter
              indexnummer
              identificatie
              status
              wijzigingsdatum
              aangeduidDoorKadastralegemeentecode
              aangeduidDoorKadastralesectie
            }
          }
        }
        appartementsrechtsplitsingtype,
        einddatumAppartementsrechtsplitsing,
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
            'query': query,
            'filename': filename,
            'mime_type': 'plain/text',
            'format': format.get_format(),
        }
    }


class AardzakelijkerechtenExportConfig:
    filename = brk_filename("CAardZakelijkRecht")
    format = {
        'AZT_CODE': 'code',
        'AZT_OMSCHRIJVING': 'waarde',
        'AZT_AARDZAKELIJKRECHT_AKR_CODE': 'akrCode',
    }

    query = '''
{
  aardzakelijkerechten(sort:code_asc) {
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
            'filename': filename,
            'mime_type': 'plain/text',
            'format': format,
        }
    }


class BrkBagExportConfig:
    filename = brk_filename("BRK_BAG")
    format = {
        'BRK_KOT_ID': 'identificatie',
        'KOT_AKRKADGEMEENTECODE_CODE': '',  # TODO when gemeentecode is imported
        'KOT_AKRKADGEMEENTECODE_OMS': 'aangeduidDoorKadastralegemeentecode.bronwaarde',
        'KOT_SECTIE': 'aangeduidDoorKadastralesectie.bronwaarde',
        'KOT_PERCEELNUMMER': 'perceelnummer',
        'KOT_INDEX_LETTER': 'indexletter',
        'KOT_INDEX_NUMMER': 'indexnummer',
        'KOT_STATUS_CODE': 'status',
        'KOT_MODIFICATION': 'wijzigingsdatum',
        'BAG_VOT_ID': 'heeftEenRelatieMetVerblijfsobject.identificatie',
        'DIVA_VOT_ID': '',
        'AOT_OPENBARERUIMTENAAM': 'ligtAanOpenbareruimte.naam',
        'AOT_HUISNUMMER': 'heeftHoofdadres.huisnummer',
        'AOT_HUISLETTER': 'heeftHoofdadres.huisletter',
        'AOT_HUISNUMMERTOEVOEGING': 'heeftHoofdadres.huisnummertoevoeging',
        'AOT_POSTCODE': 'heeftHoofdadres.postcode',
        'AOT_WOONPLAATSNAAM': 'ligtInWoonplaats.naam',
        'BRON_RELATIE': {
            'action': 'literal',
            'value': 'BRK'
        }
    }

    query = '''
{
  kadastraleobjecten {
    edges {
      node {
        identificatie
        aangeduidDoorKadastralegemeente
        aangeduidDoorKadastralegemeentecode
        aangeduidDoorKadastralesectie
        perceelnummer
        indexletter
        indexnummer
        status
        wijzigingsdatum
        heeftEenRelatieMetVerblijfsobject {
          edges {
            node {
              identificatie
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

    products = {
        'csv': {
            'exporter': csv_exporter,
            'entity_filters': [
                NotEmptyFilter('heeftEenRelatieMetVerblijfsobject.identificatie'),
            ],
            'api_type': 'graphql_streaming',
            'unfold': True,
            'query': query,
            'filename': filename,
            'mime_type': 'plain/text',
            'format': format,
        }
    }


class StukdelenExportConfig:
    filename = brk_filename('Stukdeel')
    format = {
        'BRK_SDL_ID': 'identificatie',
        'SDL_AARDSTUKDEEL_CODE': 'aard.code',
        'SDL_AARDSTUKDEEL_OMS': 'aard.omschrijving',
        'SDL_KOOPSOM': 'bedragTransactie.bedrag',
        'SDL_KOOPSOM_VALUTA': 'bedragTransactie.valuta',
        'BRK_STK_ID': 'stukidentificatie',
        'STK_AKRPORTEFEUILLENR': 'portefeuillenummerAkr',
        'STK_TIJDSTIP_AANBIEDING': 'tijdstipAanbiedingStuk',
        'STK_REEKS_CODE': 'reeks',
        'STK_VOLGNUMMER': 'volgnummerStuk',
        'STK_REGISTERCODE_CODE': 'registercodeStuk.code',
        'STK_REGISTERCODE_OMS': 'registercodeStuk.omschrijving',
        'STK_SOORTREGISTER_CODE': 'soortRegisterStuk.code',
        'STK_SOORTREGISTER_OMS': 'soortRegisterStuk.omschrijving',
        'STK_DEEL_SOORT': 'deelSoortStuk',
        'BRK_TNG_ID': 'isBronVoorTenaamstelling.identificatie',
        'BRK_ATG_ID': {
            'condition': 'isempty',
            'reference': 'isBronVoorAantekeningRecht.identificatie',
            'negate': True,
            # Either one or the other is set, or none, but never both
            'trueval': 'isBronVoorAantekeningRecht.identificatie',
            'elseval': 'isBronVoorAantekeningKadastraalObject.identificatie'
        },
        'BRK_ASG_VVE': 'isBronVoorZakelijkRecht.appartementsrechtsplitsingidentificatie'
    }

    query = '''
{
  stukdelen {
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
        isBronVoorAantekeningRecht {
          edges {
            node {
              identificatie
            }
          }
        }
        isBronVoorAantekeningKadastraalObject {
          edges {
            node {
              identificatie
            }
          }
        }
        isBronVoorZakelijkRecht {
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
        'csv': {
            'exporter': csv_exporter,
            'api_type': 'graphql_streaming',
            'query': query,
            'filename': filename,
            'mime_type': 'plain/text',
            'format': format,
        }
    }


class KadastraleobjectenExportConfig:
    filename = brk_filename('KadastraalObject')
    format = {
        'BRK_KOT_ID': 'identificatie',
        # TODO Gemeente codes etc after correct import of gemeentes
        'KOT_GEMEENTENAAM': 'gemeente',
        'KOT_AKRKADGEMCODE_CODE': 'aangeduidDoorKadastralegemeentecode.bronwaarde',
        'KOT_KADASTRALEGEMEENTE_CODE': 'aangeduidDoorKadastralegemeentecode.bronwaarde',
        'KOT_KAD_GEMEENTECODE': 'aangeduidDoorKadastralegemeente.bronwaarde',
        'KOT_KAD_GEMEENTE_OMS': '',
        'KOT_SECTIE': 'aangeduidDoorKadastralesectie.bronwaarde',
        'KOT_PERCEELNUMMER': 'perceelnummer',
        'KOT_INDEX_LETTER': 'indexletter',
        'KOT_INDEX_NUMMER': 'indexnummer',
        'KOT_SOORTGROOTTE_CODE': 'soortGrootte.code',
        'KOT_SOORTGROOTTE_OMS': 'soortGrootte.omschrijving',
        'KOT_KADGROOTTE': 'grootte',
        'KOT_RELATIE_G_PERCEEL': 'isOntstaanUitGPerceel.identificatie',
        'KOT_KOOPSOM': 'koopsom',
        'KOT_KOOPSOM_VALUTA': 'koopsomValutacode',
        'KOT_KOOPJAAR': 'koopjaar',
        'KOT_INDICATIE_MEER_OBJECTEN': 'indicatieMeerObjecten',
        'KOT_CULTUURCODEONBEBOUWD_CODE': 'soortCultuurOnbebouwd.code',
        'KOT_CULTUURCODEONBEBOUWD_OMS': 'soortCultuurOnbebouwd.omschrijving',
        'KOT_CULTUURCODEBEBOUWD_CODE': 'soortCultuurBebouwd.code',
        'KOT_CULTUURCODEBEBOUWD_OMS': 'soortCultuurBebouwd.omschrijving',
        'KOT_AKRREGISTER9TEKST': '',
        'KOT_STATUS_CODE': 'status',
        'KOT_TOESTANDSDATUM': 'toestandsdatum',
        'KOT_IND_VOORLOPIGE_KADGRENS': 'indicatieVoorlopigeGeometrie',
        'BRK_SJT_ID': 'vanKadastraalsubject.identificatie',
        'SJT_NAAM': {
            'condition': 'isempty',
            'reference': 'vanKadastraalsubject.heeftBsnVoor.bronwaarde',
            'negate': True,
            'trueval': {
                'action': 'concat',
                'fields': [
                    'vanKadastraalsubject.geslachtsnaam',
                    {
                        'action': 'literal',
                        'value': ','
                    },
                    'vanKadastraalsubject.voornamen',
                    {
                        'action': 'literal',
                        'value': ','
                    },
                    'vanKadastraalsubject.voorvoegsels',
                    {
                        'action': 'literal',
                        'value': ' ('
                    },
                    'vanKadastraalsubject.geslacht.code',
                    {
                        'action': 'literal',
                        'value': ')'
                    },
                ]
            },
            'falseval': 'vanKadastraalsubject.statutaireNaam'
        },
        'SJT_TYPE': 'vanKadastraalsubject.typeSubject',
        'SJT_NP_GEBOORTEDATUM': 'vanKadastraalsubject.geboortedatum',
        'SJT_NP_GEBOORTEPLAATS': 'vanKadastraalsubject.geboorteplaats',
        'SJT_NP_GEBOORTELAND_CODE': 'vanKadastraalsubject.geboorteland.code',
        'SJT_NP_GEBOORTELAND_OMS': 'vanKadastraalsubject.geboorteland.omschrijving',
        'SJT_NP_DATUMOVERLIJDEN': 'vanKadastraalsubject.datumOverlijden',
        'SJT_NNP_RSIN': 'vanKadastraalsubject.heeftRsinVoor.bronwaarde',
        'SJT_NNP_KVKNUMMER': 'vanKadastraalsubject.heeftKvknummerVoor.bronwaarde',
        'SJT_NNP_RECHTSVORM_CODE': 'vanKadastraalsubject.rechtsvorm.code',
        'SJT_NNP_RECHTSVORM_OMS': 'vanKadastraalsubject.rechtsvorm.omschrijving',
        'SJT_NNP_STATUTAIRE_NAAM': 'vanKadastraalsubject.statutaireNaam',
        'SJT_NNP_STATUTAIRE_ZETEL': 'vanKadastraalsubject.statutaireZetel',
        'SJT_ZRT': 'invRustOpKadastraalobjectBrkZakelijkerechten.aardZakelijkRecht.code',
        'SJT_AANDEEL': {
            'condition': 'isempty',
            'reference': 'invVanZakelijkrechtBrkTenaamstellingen.aandeel.teller',
            'negate': True,
            'trueval': {
                'action': 'concat',
                'fields': [
                    'invVanZakelijkrechtBrkTenaamstellingen.aandeel.teller',
                    {
                        'action': 'literal',
                        'value': '/',
                    },
                    'invVanZakelijkrechtBrkTenaamstellingen.aandeel.noemer'
                ]
            },
        },
        'SJT_VVE_SJT_ID': '',
        'SJT_VVE_UIT_EIGENDOM': '',
        'KOT_INONDERZOEK': 'inOnderzoek',
        'KOT_MODIFICATION': 'wijzigingsdatum',
        'GEOMETRIE': 'geometrie'
    }

    query = '''
{
  kadastraleobjecten {
    edges {
      node {
        identificatie
        volgnummer
        gemeente
        aangeduidDoorGemeente
        aangeduidDoorKadastralegemeentecode
        aangeduidDoorKadastralegemeente
        aangeduidDoorKadastralesectie
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
        wijzigingsdatum
        geometrie
        invRustOpKadastraalobjectBrkZakelijkerechten(akrAardZakelijkRecht:"VE") {
          edges {
            node {
              identificatie
              aardZakelijkRecht
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
    """
    Tenaamstellingen/Subject: Return the tenaamstelling with the largest aandeel (teller/noemer). When multiple
    tenaamstellingen have an even aandeel, sort the tenaamstellingen by its subject's geslachtsnaam.
    """
    products = {
        'csv': {
            'exporter': csv_exporter,
            'api_type': 'graphql',
            'query': query,
            'filename': filename,
            'mime_type': 'plain/text',
            'format': format,
            'sort': {
                'invRustOpKadastraalobjectBrkZakelijkerechten'
                '.invVanZakelijkrechtBrkTenaamstellingen'
                '.aandeel':
                    lambda x, y: Fraction(x['teller'], x['noemer']) > Fraction(y['teller'], y['noemer']),
                'invRustOpKadastraalobjectBrkZakelijkerechten'
                '.invVanZakelijkrechtBrkTenaamstellingen'
                '.vanKadastraalsubject'
                '.geslachtsnaam':
                    lambda x, y: str(x).lower() > str(y).lower(),
            }
        }
    }


class GemeentesExportConfig:
    csv_format = {
        'AZT_CODE': 'code',
        'AZT_OMSCHRIJVING': 'waarde',
        'AZT_AARDZAKELIJKRECHT_AKR_CODE': 'akrCode',
    }

    query = '''
{
  gemeentes(sort:naam_asc) {
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

    products = {
        'csv': {
            'exporter': csv_exporter,
            'api_type': 'graphql',
            'query': query,
            'filename': brk_filename('Gemeente', 'csv'),
            'mime_type': 'plain/text',
            'format': {
                'naam': 'naam',
                'identificatie': 'identificatie',
                'geometrie': 'geometrie'
            }
        },
        'shape': {
            'exporter': esri_exporter,
            'api_type': 'graphql',
            'filename': brk_filename('Gemeente', 'shp'),
            'mime_type': 'application/octet-stream',
            'format': {
                'GEMEENTE': 'naam',
                'GME_ID': 'identificatie'
            },
            'extra_files': [
                {
                    'filename': brk_filename('Gemeente', 'dbf'),
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': brk_filename('Gemeente', 'shx'),
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': brk_filename('Gemeente', 'prj'),
                    'mime_type': 'application/octet-stream'
                },
            ],
            'query': query
        }
    }
