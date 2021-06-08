from unittest import TestCase
from unittest.mock import patch, MagicMock

from gobexport.exporter.config.brk.kadastraleobjecten import KadastraleobjectenExportConfig


@patch("gobexport.exporter.config.brk.kadastraleobjecten.NotEmptyFilter", MagicMock())
@patch("gobexport.exporter.config.brk.kadastraleobjecten.BrkBagCsvFormat", MagicMock())
class TestBrkBagExportConfig(TestCase):

    @patch("gobexport.exporter.config.brk.kadastraleobjecten.get_entity_value", lambda entity, field: entity[field])
    def test_vot_filter(self):
        config = KadastraleobjectenExportConfig()
        vot_filter = config.VotFilter()

        entity = {
            'heeftEenRelatieMetVerblijfsobject.[0].identificatie': None,
            'heeftEenRelatieMetVerblijfsobject.[0].broninfo.woonplaatsnaam': 'not Amsterdam'
        }

        self.assertTrue(vot_filter.filter(entity), 'Should return True when no VOT identification set and not '
                                                   'Amsterdam')

        entity = {
            'heeftEenRelatieMetVerblijfsobject.[0].identificatie': None,
            'heeftEenRelatieMetVerblijfsobject.[0].broninfo.woonplaatsnaam': 'Amsterdam'
        }

        self.assertFalse(vot_filter.filter(entity), 'Should return False when VOT identification not set '
                                                    'and Amsterdam')

        entity = {
            'heeftEenRelatieMetVerblijfsobject.[0].identificatie': None,
            'heeftEenRelatieMetVerblijfsobject.[0].broninfo.woonplaatsnaam': None,
        }

        self.assertTrue(vot_filter.filter(entity), 'Should return True when VOT identification not set and city '
                                                   'not set')
