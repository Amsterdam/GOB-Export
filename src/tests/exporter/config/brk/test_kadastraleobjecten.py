from unittest import TestCase
from unittest.mock import patch

from gobexport.exporter.config.brk.kadastraleobjecten import (
    KadastraleobjectenEsriFormat,
    KadastraleobjectenCsvFormat,
    aandeel_sort
)


class TestKadastraleobjectenCsvFormat(TestCase):

    def setUp(self) -> None:
        self.format = KadastraleobjectenCsvFormat()

    def test_comma_concatter(self):
        testcases = [
            ('A|B', 'A, B'),
            ('A', 'A'),
        ]

        for inp, outp in testcases:
            self.assertEqual(outp, self.format.comma_concatter(inp))

    def test_comma_no_space_concatter(self):
        testcases = [
            ('A|B', 'A,B'),
            ('A', 'A'),
        ]

        for inp, outp in testcases:
            self.assertEqual(outp, self.format.comma_no_space_concatter(inp))

    def test_concat_with_comma(self):

        self.assertEqual({
            'action': 'format',
            'value': 'the reference',
            'formatter': self.format.comma_concatter,
        }, self.format.concat_with_comma('the reference'))

        self.assertEqual({
            'action': 'format',
            'value': 'the reference',
            'formatter': self.format.comma_no_space_concatter,
        }, self.format.concat_with_comma('the reference', False))

    def test_format_kadgrootte(self):
        testcases = [
            ('1.0', '1'),
            ('10.0', '10'),
            ('0.1', '0.1'),
            ('10', '10'),
        ]

        for inp, outp in testcases:
            self.assertEqual(outp, self.format.format_kadgrootte(inp))

    def test_if_vve(self):
        expected = {
            'condition': 'isempty',
            'reference': 'betrokkenBijAppartementsrechtsplitsingVve.[0].identificatie',
            'negate': True,
            'trueval': {'true': 'val'},
            'falseval': 'FALSEVAL',
        }

        self.assertEqual(expected, self.format.if_vve({'true': 'val'}, 'FALSEVAL'))

    def test_if_sjt(self):
        expected = {
            'condition': 'isempty',
            'negate': True,
            'reference': 'vanKadastraalsubject.[0].identificatie',
            'trueval': 'the true val',
        }

        self.assertEqual(expected, self.format.if_sjt('the true val'))

        expected['falseval'] = 'the false val'

        self.assertEqual(expected, self.format.if_sjt('the true val', 'the false val'))

    def test_vve_or_subj(self):
        expected = {
            'condition': 'isempty',
            'reference': 'betrokkenBijAppartementsrechtsplitsingVve.[0].identificatie',
            'negate': True,
            'trueval': 'betrokkenBijAppartementsrechtsplitsingVve.[0].theAttribute',
            'falseval': 'vanKadastraalsubject.[0].theAttribute',
        }
        self.assertEqual(expected, self.format.vve_or_subj('theAttribute'))

    def test_row_formatter(self):
        row = {
            'node': {
                'isOntstaanUitGPerceel': {
                    'edges': [
                        {
                            'node': {
                                'identificatie': 'percA',
                            }
                        },
                        {
                            'node': {
                                'identificatie': 'percB',
                            }
                        }
                    ]
                }
            }
        }
        expected = {
            'node': {
                'isOntstaanUitGPerceel': {
                    'edges': [
                        {
                            'node': {
                                'identificatie': 'percA,percB',
                            }
                        },
                    ]
                }
            }
        }

        self.assertEqual(expected, self.format.row_formatter(row))


class TestKadastraleobjectenEsriFormat(TestCase):

    def setUp(self) -> None:
        self.format = KadastraleobjectenEsriFormat()

    @patch("gobexport.exporter.config.brk.kadastraleobjecten.KadastraleobjectenCsvFormat.get_format",
           return_value={"a": "A", "b": {"x": "X"}, "c": "C", "d": "D"})
    @patch("gobexport.exporter.config.brk.kadastraleobjecten.KadastraleobjectenEsriFormat.get_mapping",
           return_value={"A": "a", "B": "b", "C": {"y": "Y"}})
    def test_get_format(self, get_mapping_mock, get_format_mock):
        output = {"A": "A", "B": {"x": "X"}, "C": {"y": "Y"}}
        self.assertEqual(self.format.get_format(), output)


class TestKadastraleobjectenExportConfig(TestCase):

    def test_aandeel_sort(self):

        testcases = [
            (None, None, False),
            (None, {'noemer': 3, 'teller': 1}, False),
            ({'noemer': 2, 'teller': 1}, None, True),
            ({'noemer': 2, 'teller': 1}, {'noemer': None, 'teller': None}, True),
            ({'noemer': None, 'teller': None}, {'noemer': 3, 'teller': 1}, False),
            ({'noemer': None, 'teller': None}, {'noemer': None, 'teller': None}, False),
            ({'noemer': 2, 'teller': 1}, {'noemer': 3, 'teller': 1}, True),
            ({'noemer': 3, 'teller': 1}, {'noemer': 2, 'teller': 1}, False),
            ({'noemer': 2, 'teller': 1}, {'noemer': 2, 'teller': 1}, False),
        ]

        for a, b, result in testcases:
            self.assertEqual(result, aandeel_sort(a, b))
