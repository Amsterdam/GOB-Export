import datetime
import unittest
from unittest.mock import patch

from gobcore.exceptions import GOBTypeException
from gobexport.converters import history


class TestHistory(unittest.TestCase):

    def setUp(self):
        pass

    def test_convert_to_history_rows(self):
        row = {
            'beginGeldigheid': '2010-01-01',
            'eindGeldigheid': '',
            'reference': [{
                'beginGeldigheid': '2012-01-01',
                'eindGeldigheid': ''
            }]
        }

        # Expect two rows with startTijdvak and eindTijdvak
        result = history.convert_to_history_rows(row)
        self.assertEqual(len(result), 2)
        expected_result = [
            {
                'beginGeldigheid': '2010-01-01',
                'eindGeldigheid': '',
                'reference': None,
                'beginTijdvak': '2010-01-01',
                'eindTijdvak': '2012-01-01'
            },
            {
                'beginGeldigheid': '2010-01-01',
                'eindGeldigheid': '',
                'reference': {
                    'beginGeldigheid': '2012-01-01',
                    'eindGeldigheid': ''
                },
                'beginTijdvak': '2012-01-01',
                'eindTijdvak': ''
            }
        ]
        self.assertEqual(result, expected_result)

    def test_row_with_reference_before_entity(self):
        row = {
            'beginGeldigheid': '2012-01-01',
            'eindGeldigheid': '',
            'reference': [{
                'beginGeldigheid': '2010-01-01',
                'eindGeldigheid': ''
            }]
        }

        # Expect two rows with startTijdvak and eindTijdvak
        result = history.convert_to_history_rows(row)
        self.assertEqual(len(result), 1)
        expected_result = [
            {
                'beginGeldigheid': '2012-01-01',
                'eindGeldigheid': '',
                'reference': {
                    'beginGeldigheid': '2010-01-01',
                    'eindGeldigheid': ''
                },
                'beginTijdvak': '2012-01-01',
                'eindTijdvak': ''
            }
        ]
        self.assertEqual(result, expected_result)

    def test_convert_to_date(self):
        self.assertEqual(datetime.date(2010, 1, 1), history._convert_to_date('2010-01-01'))
        self.assertEqual(datetime.datetime(2010, 1, 1, 12), history._convert_to_date('2010-01-01T12:00:00.000000'))
        self.assertEqual(None, history._convert_to_date('2010-AA-01'))

    def test_convert_date_to_string(self):
        self.assertEqual('2010-01-01', history._convert_date_to_string(datetime.date(2010, 1, 1)))
        self.assertEqual('2010-01-01T12:00:00.000000', history._convert_date_to_string(datetime.datetime(2010, 1, 1, 12)))

    def test_convert_to_snake_case(self):
        self.assertEqual('camel_case', history._convert_to_snake_case('camelCase'))
        self.assertEqual('_camel_case', history._convert_to_snake_case('CamelCase'))
        self.assertEqual('gob_camel_case', history._convert_to_snake_case('GOBCamelCase'))
