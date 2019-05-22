import datetime

from gobexport.exporter.csv import csv_exporter


class KadastralesubjectenCsvFormat:

    def _prefix_dict(self, dct: dict, key_prefix: str, val_prefix: str):
        return {f"{key_prefix}{key}": f"{val_prefix}{val}" for key, val in dct.items()}

    def _add_condition_to_attrs(self, condition: dict, attrs: dict):
        return {k: {**condition, 'value': v} for k, v in attrs.items()}

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

    now = datetime.datetime.now()
    datestr = now.strftime('%Y%m%d')
    filename = f'BRK_KadastraalSubject_{datestr}.csv'

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
    now = datetime.datetime.now()
    datestr = now.strftime('%Y%m%d')
    filename = f'BRK_Aantekening_{datestr}.csv'

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
