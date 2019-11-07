from unittest import TestCase
from unittest.mock import patch, MagicMock
from datetime import date

from gobexport.exporter.config.uva2 import (
    get_uva2_filename,
    format_uva2_date,
    format_uva2_mapping,
    format_uva2_buurt,
    format_uva2_coordinate,
    row_formatter_verblijfsobjecten,
)


class TestUVA2ConfigHelpers(TestCase):

    def test_get_uva2_filename(self):
        publish_date = date.today().strftime('%Y%m%d')

        self.assertEqual(f"UVA2_Actueel/ABC_{publish_date}_N_{publish_date}_{publish_date}.UVA2", get_uva2_filename('ABC'))

        # Assert undefined file name raises error
        with self.assertRaises(AssertionError):
            get_uva2_filename(None)

    def test_format_timestamp(self):
        inp = '2035-03-31'
        outp = '20350331'
        self.assertEqual(outp, format_uva2_date(inp))

        for inp in ['invalid_str', None]:
            # These inputs should not change
            self.assertEqual(inp, format_uva2_date(inp))

    def test_format_uva2_buurt(self):
        inp = 'A01p'
        outp = '01p'
        self.assertEqual(outp, format_uva2_buurt(inp))

    def test_format_uva2_status_invalid(self):
        # Test invalid entity names
        with self.assertRaises(AssertionError):
            format_uva2_mapping('1', 'invalid')

    def test_format_uva2_status_openbareruimtes(self):
        # Status 1 and 2 should be mapped to 35, 36 for openbareruimtes
        status = [('1', '35'), ('2', '36'), (1, '35')]

        for input, expected in status:
            self.assertEqual(format_uva2_mapping(input, "openbareruimtes_status"), expected)

        # Test invalid status for openbareruimtes
        status = [3, '4', 'a', None]

        for input in status:
            self.assertEqual(format_uva2_mapping(input, "openbareruimtes_status"), '')

    def test_format_uva2_status_nummeraanduidingen(self):
        # Status 1 and 2 should be mapped to 16, 17 for nummeraanduidingen
        status = [('1', '16'), ('2', '17'), (1, '16')]

        for input, expected in status:
            self.assertEqual(format_uva2_mapping(input, "nummeraanduidingen_status"), expected)

        # Test invalid status for nummeraanduidingen
        status = [3, '4', 'a', None]

        for input in status:
            self.assertEqual(format_uva2_mapping(input, "openbareruimtes_status"), '')

    def test_format_uva2_coordinate(self):
        value = "POINT(124888 486338)"

        self.assertEqual(format_uva2_coordinate(value, "x"), 124888)
        self.assertEqual(format_uva2_coordinate(value, "y"), 486338)

        value = "POINT(124888.8 486338.4)"

        self.assertEqual(format_uva2_coordinate(value, "x"), 124889)
        self.assertEqual(format_uva2_coordinate(value, "y"), 486338)

        with self.assertRaises(AssertionError):
            format_uva2_coordinate(value, "z")

        value = "Invalid"

        # Expect an empty string if no coordinates are present
        self.assertEqual(format_uva2_coordinate(value, "y"), '')


    def test_row_formatter_verblijfsobjecten(self):
        # Test woonfuctie without gebruiksdoelWoonfunctie
        row = {
            'node': {
                'gebruiksdoel': [{'omschrijving': 'woonfunctie'}],
                'gebruiksdoelWoonfunctie': {},
                'gebruiksdoelGezondheidszorgfunctie': {},
            }
        }

        expected_row = {
            'node': {
                'gebruiksdoel': [{'omschrijving': 'woonfunctie'}],
                'gebruiksdoelWoonfunctie': {},
                'gebruiksdoelGezondheidszorgfunctie': {},
                'GebruiksdoelVerblijfsobjectDomein': '2075',
                'OmschrijvingGebruiksdoelVerblijfsobjectDomein': '2075 Woning'
            }
        }

        self.assertEqual(row_formatter_verblijfsobjecten(row), expected_row)

        # Test gebruiksdoelWoonfunctie
        row = {
            'node': {
                'gebruiksdoel': [{'omschrijving': 'woonfunctie'}],
                'gebruiksdoelWoonfunctie': {'omschrijving': 'Verpleeghuis'},
                'gebruiksdoelGezondheidszorgfunctie': {},
            }
        }

        expected_row = {
            'node': {
                'gebruiksdoel': [{'omschrijving': 'woonfunctie'}],
                'gebruiksdoelWoonfunctie': {'omschrijving': 'Verpleeghuis'},
                'gebruiksdoelGezondheidszorgfunctie': {},
                'GebruiksdoelVerblijfsobjectDomein': '1310',
                'OmschrijvingGebruiksdoelVerblijfsobjectDomein': 'BEST-verpleeghuis'
            }
        }

        self.assertEqual(row_formatter_verblijfsobjecten(row), expected_row)

        # Test gebruiksdoelGezondheidszorgfunctie
        row = {
            'node': {
                'gebruiksdoel': [{'omschrijving': 'gezondheidszorgfunctie'}],
                'gebruiksdoelWoonfunctie': {},
                'gebruiksdoelGezondheidszorgfunctie': {'omschrijving': 'Verpleeghuis'},
            }
        }

        expected_row = {
            'node': {
                'gebruiksdoel': [{'omschrijving': 'gezondheidszorgfunctie'}],
                'gebruiksdoelWoonfunctie': {},
                'gebruiksdoelGezondheidszorgfunctie': {'omschrijving': 'Verpleeghuis'},
                'GebruiksdoelVerblijfsobjectDomein': '2310',
                'OmschrijvingGebruiksdoelVerblijfsobjectDomein': '2310 Verpleeghuis'
            }
        }

        self.assertEqual(row_formatter_verblijfsobjecten(row), expected_row)
