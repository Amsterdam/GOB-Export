"""BRK2 kadastraleobjecten export tests."""


from unittest import TestCase
from unittest.mock import Mock, patch

from gobexport.filters.notempty_filter import NotEmptyFilter
from gobexport.exporter.config.brk2.kadastraleobjecten import (
    Brk2BagCsvFormat,
    aandeel_sort,
    KadastraleobjectenExportConfig,
)


class TestBrk2ExportConfig(TestCase):
    """BRK2 Kadastraleobjecten export tests."""

    def test_aandeel_sort(self):
        """aandeel_sort test."""

        testcases = [
            (None, None, False),
            (None, {"noemer": 3, "teller": 1}, False),
            ({"noemer": 2, "teller": 1}, None, True),
            ({"noemer": 2, "teller": 1}, {"noemer": None, "teller": None}, True),
            ({"noemer": None, "teller": None}, {"noemer": 3, "teller": 1}, False),
            ({"noemer": None, "teller": None}, {"noemer": None, "teller": None}, False),
            ({"noemer": 2, "teller": 1}, {"noemer": 3, "teller": 1}, True),
            ({"noemer": 3, "teller": 1}, {"noemer": 2, "teller": 1}, False),
            ({"noemer": 2, "teller": 1}, {"noemer": 2, "teller": 1}, False),
        ]

        for a, b, result in testcases:
            self.assertEqual(result, aandeel_sort(a, b))

    @patch(
        "gobexport.exporter.config.brk2.kadastraleobjecten.NotEmptyFilter",
        Mock(spec_set=NotEmptyFilter),
    )
    @patch(
        "gobexport.exporter.config.brk2.kadastraleobjecten.Brk2BagCsvFormat",
        Mock(spec_set=Brk2BagCsvFormat),
    )
    @patch(
        "gobexport.exporter.config.brk2.kadastraleobjecten.get_entity_value",
        lambda entity, field: entity[field],
    )
    def test_vot_filter(self):
        """VotFilter tests."""
        vot_filter = KadastraleobjectenExportConfig().VotFilter()

        entity = {
            "heeftEenRelatieMetBagVerblijfsobject.[0].identificatie": None,
            "heeftEenRelatieMetBagVerblijfsobject.[0].broninfo.woonplaatsnaam": "not Amsterdam",
        }
        self.assertTrue(
            vot_filter.filter(entity),
            "Should return True when no VOT identification set and not 'Amsterdam'",
        )

        entity = {
            "heeftEenRelatieMetBagVerblijfsobject.[0].identificatie": None,
            "heeftEenRelatieMetBagVerblijfsobject.[0].broninfo.woonplaatsnaam": "Amsterdam",
        }
        self.assertFalse(
            vot_filter.filter(entity),
            "Should return False when VOT identification not set and 'Amsterdam'",
        )

        entity = {
            "heeftEenRelatieMetBagVerblijfsobject.[0].identificatie": None,
            "heeftEenRelatieMetBagVerblijfsobject.[0].broninfo.woonplaatsnaam": None,
        }
        self.assertTrue(
            vot_filter.filter(entity),
            "Should return True when VOT identification not set and city not set",
        )
