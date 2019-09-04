from unittest import TestCase
from unittest.mock import patch
from datetime import datetime

from gobexport.exporter.config.brk import KadastralesubjectenCsvFormat, brk_filename, sort_attributes, \
    format_timestamp, ZakelijkerechtenCsvFormat, PerceelnummerEsriFormat, _get_filename_date


class TestBrkConfigHelpers(TestCase):

    @patch("gobexport.exporter.config.brk._get_filename_date", datetime.now)
    def test_brk_filename(self):
        self.assertEqual(f"AmsterdamRegio/CSV_Actueel/BRK_FileName_{datetime.now().strftime('%Y%m%d')}.csv",
                         brk_filename('FileName'))

        self.assertEqual(f"AmsterdamRegio/SHP_Actueel/BRK_FileName_{datetime.now().strftime('%Y%m%d')}.shp",
                         brk_filename('FileName', type='shp'))

        self.assertEqual(f"AmsterdamRegio/SHP_Actueel/BRK_FileName.prj",
                         brk_filename('FileName', type='prj', append_date=False,))

        # Assert undefined file type raises error
        with self.assertRaises(AssertionError):
            brk_filename('FileName', type='xxx')

    def test_sort_attributes(self):
        attrs = {
            'b': {
                'some': {
                    'nested': 'dict'
                }
            },
            'a': [1, 2, 3],
            'c': 'stringval'
        }

        expected_result = {
            'c': 'stringval',
            'a': [1, 2, 3],
            'b': {
                'some': {
                    'nested': 'dict'
                },
            },
        }

        self.assertEqual(expected_result, sort_attributes(attrs, ['c', 'a', 'b']))

        with self.assertRaises(AssertionError):
            sort_attributes(attrs, ['d', 'a', 'b'])

        with self.assertRaises(AssertionError):
            sort_attributes(attrs, ['c', 'a', 'b', 'c'])

        del attrs['a']
        with self.assertRaises(AssertionError):
            sort_attributes(attrs, ['c' 'a', 'b'])

    def test_format_timestamp(self):
        inp = '2035-03-31T01:02:03.000000'
        outp = '20350331010203'
        self.assertEqual(outp, format_timestamp(inp))

        for inp in ['invalid_str', None]:
            # These inputs should not change
            self.assertEqual(inp, format_timestamp(inp))

    @patch("gobexport.exporter.config.brk.requests.get")
    def test_get_filename_date(self, mock_request_get):
        mock_request_get.return_value.json.return_value = {
            'id': 1,
            'kennisgevingsdatum': "2019-09-03T00:00:00",
        }

        expected_date = datetime(year=2019, month=9, day=3)
        self.assertEqual(expected_date, _get_filename_date())


class TestBrkCsvFormat(TestCase):

    def setUp(self) -> None:
        self.format = KadastralesubjectenCsvFormat()

    def test_prefix_dict(self):
        inp_dict = {"key": "val"}
        res = self.format._prefix_dict(inp_dict, "key_prefix_", "val_prefix_")
        self.assertEqual({"key_prefix_key": "val_prefix_val"}, res)

    def test_add_condition_to_attrs(self):
        condition = {
            "condition": "isempty",
            "reference": "field.ref",
        }
        attrs = {
            'KEY1': 'val1',
            'KEY2': 'val2',
        }

        expected = {
            'KEY1': {
                'condition': 'isempty',
                'reference': 'field.ref',
                'trueval': 'val1',
            },
            'KEY2': {
                'condition': 'isempty',
                'reference': 'field.ref',
                'trueval': 'val2',
            }
        }
        res = self.format._add_condition_to_attrs(condition, attrs)
        self.assertEqual(expected, res)

    def test_show_when_field_notempty_condition(self):
        expected = {
            'condition': 'isempty',
            'reference': 'FIELDREF',
            'negate': True,
        }

        self.assertEqual(expected, self.format.show_when_field_notempty_condition('FIELDREF'))

    def test_hide_when_field_isempty_condition(self):
        expected = {
            'condition': 'isempty',
            'reference': 'FIELDREF',
        }

        self.assertEqual(expected, self.format.show_when_field_empty_condition('FIELDREF'))


class TestBrkZakelijkerechtenCsvFormat(TestCase):

    def setUp(self) -> None:
        self.format = ZakelijkerechtenCsvFormat()

    def test_zrt_belast_met_azt_formatter(self):
        testcases = [
            ('A', '[A]'),
            ('A|B', '[A]+[B]'),
        ]

        for inp, outp in testcases:
            self.assertEqual(outp, self.format.zrt_belast_met_azt_formatter(inp))

        testcases = ['', None, 1]

        for testcase in testcases:
            with self.assertRaises(AssertionError):
                self.format.zrt_belast_met_azt_formatter(testcase)

    def test_zrt_belast_azt_formatter(self):
        self.assertEqual('[A]', self.format.zrt_belast_azt_formatter('A'))

        errors = ['', None, 1]

        for testcase in errors:
            with self.assertRaises(AssertionError):
                self.format.zrt_belast_azt_formatter(testcase)


class TestPerceelnummerEsriFormat(TestCase):

    def setUp(self) -> None:
        self.format = PerceelnummerEsriFormat()

    def test_format_rotatie(self):
        testcases = [
            (0, '0.000'),
            (-0.234435345, '-0.234'),
            (0.1299999999, '0.130'),
        ]

        for inp, outp in testcases:
            self.assertEqual(self.format.format_rotatie(inp), outp)

        invalid_testcases = [None, '']

        for testcase in invalid_testcases:
            with self.assertRaises(AssertionError):
                self.format.format_rotatie(testcase)
