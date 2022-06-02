from gobexport.exporter.csv import csv_exporter
from gobexport.exporter.config.brk.csv_format import BrkCsvFormat
from gobexport.exporter.config.brk.utils import sort_attributes, brk_filename


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
            'SJT_BSN': 'heeft_bsn_voor',
            **bsn_only_attrs,
            **non_bsn_attrs,
            **sjt_np_attrs,
            'SJT_NP_AANDUIDINGNAAMGEBR_CODE': 'naamGebruik.code',
            'SJT_NP_AANDUIDINGNAAMGEBR_OMS': 'naamGebruik.omschrijving',
            'SJT_NP_VOORNAMEN_PARTNER': 'voornamenPartner',
            'SJT_NP_VOORVOEGSEL_PARTNER': 'voorvoegselsPartner',
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
            'OPENBARERUIMTENAAM': 'openbareRuimte',
            'HUISNUMMER': 'huisnummer',
            'HUISLETTER': 'huisletter',
            'HUISNUMMERTOEVOEGING': 'huisnummerToevoeging',
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
            'secure_user': 'gob',
            'exporter': csv_exporter,
            'filename': lambda: brk_filename('kadastraal_subject', use_sensitive_dir=True),
            'mime_type': 'plain/text',
            'format': format.get_format(),
        }
    }
