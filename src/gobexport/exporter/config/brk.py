import datetime

from gobexport.exporter.csv import csv_exporter


def brk_filename(name):
    now = datetime.datetime.now()
    datestr = now.strftime('%Y%m%d')
    return f'BRK_{name}_{datestr}.csv'


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

        show_when_bsn_condition = self.show_when_field_notempty_condition(bsn_field)
        show_when_not_bsn_condition = self.show_when_field_empty_condition(bsn_field)

        sjt_np_attrs = self._add_condition_to_attrs(show_when_bsn_condition, sjt_np_attrs)
        sjt_kad_attrs = self._add_condition_to_attrs(show_when_not_bsn_condition, sjt_kad_attrs)
        bsn_only_attrs = self._add_condition_to_attrs(show_when_bsn_condition, bsn_only_attrs)

        return {
            'SJT_BSN': bsn_field,
            **bsn_only_attrs,
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
        return {
            'BRK_SJT_ID': 'identificatie',
            'SJT_TYPE': 'typeSubject',
            'SJT_BESCHIKKINGSBEVOEGDH_CODE': 'beschikkingsbevoegdheid.code',
            'SJT_BESCHIKKINGSBEVOEGDH_OMS': 'beschikkingsbevoegdheid.omschrijving',
            **self._get_person_attrs(),
            **self._get_kvk_attrs(),
            **self._get_address_attrs(),
        }


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
        aardZakelijkRecht
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
        'ATG_TYPE': '',
        'BRK_KOT_ID': '',
        'KOT_KADASTRALEGEMCODE_CODE': '',
        'KOT_SECTIE': '',
        'KOT_PERCEELNUMMER': '',
        'KOT_INDEX_LETTER': '',
        'KOT_INDEX_NUMMER': '',
        'BRK_TNG_ID': 'betrokkenTenaamstelling.identificatie',
        'ZRT_AARD_ZAKELIJKRECHT_CODE': 'aardZakelijkRecht.code',
        'ZRT_AARD_ZAKELIJKRECHT_OMS': 'aardZakelijkRecht.omschrijving',
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
        'ATG_TYPE': '',
        'BRK_KOT_ID': 'heeftBetrekkingOpKadastraalObject.identificatie',
        'KOT_KADASTRALEGEMCODE_CODE': '',
        'KOT_SECTIE': '',
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
            'api_type': 'graphql',
            'exporter': csv_exporter,
            'query': art_query,
            'collection': 'aantekeningenrechten',
            'filename': filename,
            'mime_type': 'plain/text',
            'format': art_format,
        },
        'csv_akt': {
            'api_type': 'graphql',
            'exporter': csv_exporter,
            'query': akt_query,
            'collection': 'aantekeningenkadastraleobjecten',
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
            'SJT_NNP_RSIN': '',
            'SJT_NNP_KVKNUMMER': '',
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
                        'value': ','
                    },
                    'rustOpKadastraalobject.aangeduidDoorKadastralesectie.bronwaarde',
                    {
                        'action': 'literal',
                        'value': ','
                    },
                    'rustOpKadastraalobject.perceelnummer',
                    {
                        'action': 'literal',
                        'value': ','
                    },
                    'rustOpKadastraalobject.indexletter',
                    {
                        'action': 'literal',
                        'value': ','
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
                            'value': ',('
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
    filename = brk_filename("ZakelijkRecht")
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
            'api_type': 'graphql',
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
