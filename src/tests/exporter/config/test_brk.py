from unittest import TestCase
from datetime import datetime

from gobexport.exporter.config.brk import KadastralesubjectenCsvFormat, brk_filename, sort_attributes, format_atg_timestamp


class TestBrkConfigHelpers(TestCase):

    def test_brk_filename(self):
        self.assertEqual(f"AmsterdamRegio/CSV_Actueel/BRK_FileName_{datetime.now().strftime('%Y%m%d')}.csv",
                         brk_filename('FileName'))

        self.assertEqual(f"AmsterdamRegio/SHP_Actueel/BRK_FileName_{datetime.now().strftime('%Y%m%d')}.shp",
                         brk_filename('FileName', 'shp'))

        # Assert undefined file type raises error
        with self.assertRaises(AssertionError):
            brk_filename('FileName', 'xxx')

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

    def test_atg_timestamp_format(self):
        inp = '2035-03-31T01:02:03.000000'
        outp = '20350331010203'
        self.assertEqual(outp, format_atg_timestamp(inp))

        for inp in ['invalid_str', None]:
            # These inputs should not change
            self.assertEqual(inp, format_atg_timestamp(inp))



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
