"""BRK2 kadastraleobjecten export tests."""


from unittest import TestCase
from unittest.mock import Mock, patch

from gobexport.filters.notempty_filter import NotEmptyFilter
from gobexport.exporter.config.brk2.kadastraleobjecten import (
    Brk2BagCsvFormat,
    aandeel_sort,
    KadastraleobjectenExportConfig,
    KadastraleobjectenCsvFormat,
    KadastraleobjectenEsriNoSubjectsFormat,
    PerceelnummerEsriFormat,
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
            "heeftEenRelatieMetVerblijfsobject.[0].identificatie": None,
            "heeftEenRelatieMetVerblijfsobject.[0].broninfo.woonplaatsnaam": "not Amsterdam",
        }
        self.assertTrue(
            vot_filter.filter(entity),
            "Should return True when no VOT identification set and not 'Amsterdam'",
        )

        entity = {
            "heeftEenRelatieMetVerblijfsobject.[0].identificatie": None,
            "heeftEenRelatieMetVerblijfsobject.[0].broninfo.woonplaatsnaam": "Amsterdam",
        }
        self.assertFalse(
            vot_filter.filter(entity),
            "Should return False when VOT identification not set and 'Amsterdam'",
        )

        entity = {
            "heeftEenRelatieMetVerblijfsobject.[0].identificatie": None,
            "heeftEenRelatieMetVerblijfsobject.[0].broninfo.woonplaatsnaam": None,
        }
        self.assertTrue(
            vot_filter.filter(entity),
            "Should return True when VOT identification not set and city not set",
        )


class TestKadastraleobjectenCsvFormat(TestCase):
    """Kadastraleobjecten CSV format tests."""

    def setUp(self) -> None:
        self.format = KadastraleobjectenCsvFormat()

    def test_comma_concatter(self):
        testcases = [
            ("A|B", "A, B"),
            ("A", "A"),
        ]

        for inp, outp in testcases:
            self.assertEqual(outp, self.format.comma_concatter(inp))

    def test_concat_with_comma(self):
        self.assertEqual(
            {
                "action": "format",
                "value": "the reference",
                "formatter": self.format.comma_concatter,
            },
            self.format.concat_with_comma("the reference"),
        )

    def test_format_kadgrootte(self):
        testcases = [
            ("1.0", "1"),
            ("10.0", "10"),
            ("0.1", "0.1"),
            ("10", "10"),
        ]

        for inp, outp in testcases:
            self.assertEqual(outp, self.format.format_kadgrootte(inp))

    def test_if_vve(self):
        expected = {
            "condition": "isempty",
            "reference": "betrokkenBijAppartementsrechtsplitsingVve.[0].identificatie",
            "negate": True,
            "trueval": {"true": "val"},
            "falseval": "FALSEVAL",
        }

        self.assertEqual(expected, self.format.if_vve({"true": "val"}, "FALSEVAL"))

    def test_if_sjt(self):
        expected = {
            "condition": "isempty",
            "negate": True,
            "reference": "vanKadastraalsubject.[0].identificatie",
            "trueval": "the true val",
        }

        self.assertEqual(expected, self.format.if_sjt("the true val"))

        expected["falseval"] = "the false val"

        self.assertEqual(expected, self.format.if_sjt("the true val", "the false val"))

    def test_vve_or_subj(self):
        expected = {
            "condition": "isempty",
            "reference": "betrokkenBijAppartementsrechtsplitsingVve.[0].identificatie",
            "negate": True,
            "trueval": "betrokkenBijAppartementsrechtsplitsingVve.[0].theAttribute",
            "falseval": "vanKadastraalsubject.[0].theAttribute",
        }
        self.assertEqual(expected, self.format.vve_or_subj("theAttribute"))

    def test_row_formatter(self):
        row = {
            "node": {
                "isOntstaanUitGPerceel": {
                    "edges": [
                        {
                            "node": {
                                "identificatie": "percA",
                            }
                        },
                        {
                            "node": {
                                "identificatie": "percB",
                            }
                        },
                    ]
                }
            }
        }
        expected = {
            "node": {
                "isOntstaanUitGPerceel": {
                    "edges": [
                        {
                            "node": {
                                "identificatie": "percA,percB",
                            }
                        },
                    ]
                }
            }
        }

        self.assertEqual(expected, self.format.row_formatter(row))


class TestKadastraleobjectenEsriNoSubjectsFormat(TestCase):
    """Kadastraleobjecten ESRI format test."""

    def setUp(self) -> None:
        self.format = KadastraleobjectenEsriNoSubjectsFormat()

    @patch(
        "gobexport.exporter.config.brk2.kadastraleobjecten.KadastraleobjectenCsvFormat.get_format",
        Mock(return_value={"a": "A", "b": {"x": "X"}, "c": "C", "d": "D"}),
    )
    @patch(
        "gobexport.exporter.config.brk2.kadastraleobjecten.KadastraleobjectenEsriNoSubjectsFormat.get_mapping",
        Mock(return_value={"A": "a", "B": "b", "C": {"y": "Y"}}),
    )
    def test_get_format(self):
        output = {"A": "A", "B": {"x": "X"}, "C": {"y": "Y"}}
        self.assertEqual(self.format.get_format(), output)


class TestPerceelnummerEsriFormat(TestCase):
    """Kadastraleobjecten Perceelnummer ESRI format test."""

    def setUp(self) -> None:
        self.format = PerceelnummerEsriFormat()

    def test_format_rotation(self):
        """Perceelnummer rotation test."""
        testcases = [
            (0, "0.000"),
            (-0.234435345, "-0.234"),
            (0.1299999999, "0.130"),
        ]

        for inp, outp in testcases:
            self.assertEqual(self.format.format_rotation(inp), outp)

        invalid_testcases = [None, ""]
        for testcase in invalid_testcases:
            with self.assertRaises(AssertionError):
                self.format.format_rotation(testcase)
