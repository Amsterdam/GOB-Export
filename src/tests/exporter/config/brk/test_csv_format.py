from unittest import TestCase

from gobexport.exporter.config.brk.csv_format import BrkCsvFormat


class TestBrkCsvFormat(TestCase):

    def setUp(self) -> None:
        self.format = BrkCsvFormat()

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

