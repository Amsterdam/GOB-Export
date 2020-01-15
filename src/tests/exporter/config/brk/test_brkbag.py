from unittest import TestCase
from unittest.mock import patch, MagicMock

from gobexport.exporter.config.brk.brkbag import BrkBagExportConfig


@patch("gobexport.exporter.config.brk.brkbag.NotEmptyFilter", MagicMock())
@patch("gobexport.exporter.config.brk.brkbag.BrkBagCsvFormat", MagicMock())
class TestBrkBagExportConfig(TestCase):

    @patch("gobexport.exporter.config.brk.brkbag.get_entity_value", lambda entity, field: entity[field])
    def test_vot_filter(self):
        config = BrkBagExportConfig()
        vot_filter = config.VotFilter()

        entity = {
            'heeftEenRelatieMetVerblijfsobject.[0].identificatie': None,
            'heeftEenRelatieMetVerblijfsobject.[0].status.code': 20,
            'heeftEenRelatieMetVerblijfsobject.[0].broninfo.woonplaatsnaam': 'not Amsterdam'
        }

        self.assertTrue(vot_filter.filter(entity), 'Should return True when no VOT identification set and not '
                                                   'Amsterdam')

        entity = {
            'heeftEenRelatieMetVerblijfsobject.[0].identificatie': None,
            'heeftEenRelatieMetVerblijfsobject.[0].status.code': 20,
            'heeftEenRelatieMetVerblijfsobject.[0].broninfo.woonplaatsnaam': 'Amsterdam'
        }

        self.assertFalse(vot_filter.filter(entity), 'Should return False when VOT identification not set '
                                                    'and Amsterdam')

        entity = {
            'heeftEenRelatieMetVerblijfsobject.[0].identificatie': 'some id',
            'heeftEenRelatieMetVerblijfsobject.[0].status.code': 20,
            'heeftEenRelatieMetVerblijfsobject.[0].broninfo.woonplaatsnaam': 'not Amsterdam'
        }

        self.assertFalse(vot_filter.filter(entity), 'Should return False when VOT identification set and status code '
                                                    'is not included in valid_status_codes')

        entity = {
            'heeftEenRelatieMetVerblijfsobject.[0].identificatie': None,
            'heeftEenRelatieMetVerblijfsobject.[0].status.code': 20,
            'heeftEenRelatieMetVerblijfsobject.[0].broninfo.woonplaatsnaam': None,
        }

        self.assertTrue(vot_filter.filter(entity), 'Should return True when VOT identification not set and city '
                                                   'not set')

        status_codes = [2, 3, 4, 6]

        for status_code in status_codes:
            entity = {
                'heeftEenRelatieMetVerblijfsobject.[0].identificatie': 'some id',
                'heeftEenRelatieMetVerblijfsobject.[0].status.code': status_code,
                'heeftEenRelatieMetVerblijfsobject.[0].broninfo.woonplaatsnaam': 'not Amsterdam'
            }

            self.assertTrue(vot_filter.filter(entity), 'Should return True when VOT identification set and code '
                                                       'incluced in valid_status_codes')
