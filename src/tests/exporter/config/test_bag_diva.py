from unittest import TestCase
from unittest.mock import patch, MagicMock
from datetime import date

from gobexport.exporter.config.bag_diva import (
    get_uva2_filename,
    get_uva2_adresobject_filename,
    get_dat_landelijke_sleutel_filename,
    get_dat_geometrie_filename,
    format_uva2_date,
    format_uva2_mapping,
    format_uva2_buurt,
    format_uva2_coordinate,
    row_formatter_verblijfsobjecten,
    row_formatter_geometrie,
)


class TestUVA2ConfigHelpers(TestCase):

    def test_get_uva2_filename(self):
        publish_date = date.today().strftime('%Y%m%d')

        self.assertEqual(f"UVA2_Actueel/ABC_{publish_date}_N_{publish_date}_{publish_date}.UVA2", get_uva2_filename('ABC'))

        # Assert undefined abbreviation raises error
        with self.assertRaises(AssertionError):
            get_uva2_filename(None)

    def test_get_uva2_adresobject_filename(self):
        publish_date = date.today().strftime('%Y%m%d')

        self.assertEqual(f"UVA2_ADRESOBJECT/ADRESOBJECT_ABC_{publish_date}.UVA2", get_uva2_adresobject_filename('ABC'))

        # Assert undefined abbreviation raises error
        with self.assertRaises(AssertionError):
            get_uva2_adresobject_filename(None)

    def test_get_dat_landelijke_sleutel_filename(self):
        publish_date = date.today().strftime('%Y%m%d')

        self.assertEqual(f"DEF_LandelijkeSleutel/ABC_{publish_date}.dat", get_dat_landelijke_sleutel_filename('DEF', 'ABC'))

        # Assert undefined file name raises error
        with self.assertRaises(AssertionError):
            get_dat_landelijke_sleutel_filename(None, None)

    def test_get_dat_geometrie_filename(self):
        self.assertEqual(f"DEF_Geometrie/DEF_ABC_GEOMETRIE.dat", get_dat_geometrie_filename('DEF', 'ABC'))

        # Assert undefined file name raises error
        with self.assertRaises(AssertionError):
            get_dat_geometrie_filename(None, None)

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

    def test_format_uva2_ligplaatsen_status_code(self):
        # Status 1 and 2 should be mapped to 33, 34 for ligplaatsen
        status = [('1', '33'), ('2', '34'), (1, '33'), (2, '34')]

        for input, expected in status:
            self.assertEqual(format_uva2_mapping(input, "ligplaatsen_status_code"), expected)

        # Test invalid status for ligplaatsen
        status = [3, '4', 'a', None]

        for input in status:
            self.assertEqual(format_uva2_mapping(input, "ligplaatsen_status_code"), '')

    def test_format_uva2_ligplaatsen_status_vervallen(self):
        # Status 1 and 2 should be mapped to N, J for ligplaatsen Indicatie-vervallen
        status = [('1', 'N'), ('2', 'J'), (1, 'N'), (2, 'J')]

        for input, expected in status:
            self.assertEqual(format_uva2_mapping(input, "ligplaatsen_status_vervallen"), expected)

        # Test invalid status for ligplaatsen
        status = [3, '4', 'a', None]

        for input in status:
            self.assertEqual(format_uva2_mapping(input, "ligplaatsen_status_vervallen"), '')

    def test_format_uva2_status_openbareruimtes(self):
        # Status 1 and 2 should be mapped to 35, 36 for openbareruimtes
        status = [('1', '35'), ('2', '36'), (1, '35')]

        for input, expected in status:
            self.assertEqual(format_uva2_mapping(input, "openbareruimtes_status"), expected)

        # Test invalid status for openbareruimtes
        status = [3, '4', 'a', None]

        for input in status:
            self.assertEqual(format_uva2_mapping(input, "openbareruimtes_status"), '')

    def test_format_uva2_nummeraanduidingen_status_code(self):
        # Status 1 and 2 should be mapped to 16, 17 for nummeraanduidingen
        status = [('1', '16'), ('2', '17'), (1, '16'), (2, '17')]

        for input, expected in status:
            self.assertEqual(format_uva2_mapping(input, "nummeraanduidingen_status_code"), expected)

        # Test invalid status for nummeraanduidingen
        status = [3, '4', 'a', None]

        for input in status:
            self.assertEqual(format_uva2_mapping(input, "nummeraanduidingen_status_code"), '')

    def test_format_uva2_nummeraanduidingen_status_vervallen(self):
        # Status 1 and 2 should be mapped to N, J for nummeraanduidingen Indicatie-vervallen
        status = [('1', 'N'), ('2', 'J'), (1, 'N'), (2, 'J')]

        for input, expected in status:
            self.assertEqual(format_uva2_mapping(input, "nummeraanduidingen_status_vervallen"), expected)

        # Test invalid status for nummeraanduidingen
        status = [3, '4', 'a', None]

        for input in status:
            self.assertEqual(format_uva2_mapping(input, "nummeraanduidingen_status_vervallen"), '')

    def test_format_uva2_standplaatsen_status_code(self):
        # Status 1 and 2 should be mapped to 37, 38 for standplaatsen
        status = [('1', '37'), ('2', '38'), (1, '37'), (2, '38')]

        for input, expected in status:
            self.assertEqual(format_uva2_mapping(input, "standplaatsen_status_code"), expected)

        # Test invalid status for standplaatsen
        status = [3, '4', 'a', None]

        for input in status:
            self.assertEqual(format_uva2_mapping(input, "standplaatsen_status_code"), '')

    def test_format_uva2_standplaatsen_status_vervallen(self):
        # Status 1 and 2 should be mapped to N, J for standplaatsen Indicatie-vervallen
        status = [('1', 'N'), ('2', 'J'), (1, 'N'), (2, 'J')]

        for input, expected in status:
            self.assertEqual(format_uva2_mapping(input, "standplaatsen_status_vervallen"), expected)

        # Test invalid status for standplaatsen
        status = [3, '4', 'a', None]

        for input in status:
            self.assertEqual(format_uva2_mapping(input, "standplaatsen_status_vervallen"), '')

    def test_format_uva2_panden_status_code(self):
        status = [('1', '24'), ('2', '25'), ('3', '26'), ('7', '27'), ('8', '28'),
                  ('10', '30'), ('11', '31'), ('12', '32'), ('13', '50'), ('14', '51'),
                  (1, '24'), (2, '25'), (3, '26'), (7, '27'), (8, '28'),
                  (10, '30'), (11, '31'), (12, '32'), (13, '50'), (14, '51')]

        for input, expected in status:
            self.assertEqual(format_uva2_mapping(input, "panden_status_code"), expected)

        # Test invalid status for panden
        status = [5, '4', 'a', None]

        for input in status:
            self.assertEqual(format_uva2_mapping(input, "panden_status_code"), '')

    def test_format_uva2_panden_status_vervallen(self):
        status = [('1', 'N'), ('2', 'N'), ('3', 'N'), ('7', 'N'),
                  ('8', 'J'), ('9', 'J'), ('10', 'N'), ('11', 'N'), ('12', 'N'),
                  ('13', 'N'), ('14', 'J'),
                  (1, 'N'), (2, 'N'), (3, 'N'), (7, 'N'),
                  (8, 'J'), (9, 'J'), (10, 'N'), (11, 'N'), (12, 'N'), (13, 'N'), (14, 'J')]

        for input, expected in status:
            self.assertEqual(format_uva2_mapping(input, "panden_status_vervallen"), expected)

        # Test invalid status for panden
        status = [5, '4', 'a', None]

        for input in status:
            self.assertEqual(format_uva2_mapping(input, "panden_status_vervallen"), '')

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
                'gebruiksdoel': [{'omschrijving': 'woonfunctie', 'code': '1'}],
                'gebruiksdoelWoonfunctie': {},
                'gebruiksdoelGezondheidszorgfunctie': {},
            }
        }

        expected_row = {
            'node': {
                'gebruiksdoel': [{'omschrijving': 'woonfunctie', 'code': '1'}],
                'gebruiksdoelWoonfunctie': {},
                'gebruiksdoelGezondheidszorgfunctie': {},
                'GebruiksdoelVerblijfsobjectDomein': '2075',
                'OmschrijvingGebruiksdoelVerblijfsobjectDomein': '2075 Woning'
            }
        }

        self.assertEqual(row_formatter_verblijfsobjecten(row), expected_row)
        self.assertEqual(row_formatter_verblijfsobjecten(row['node']), expected_row['node'])

        # Test woonfuctie multiple, expect first record sorted by code
        row = {
            'node': {
                'gebruiksdoel': [{'omschrijving': 'sportfunctie', 'code': '2'}, {'omschrijving': 'woonfunctie', 'code': '1'}],
                'gebruiksdoelWoonfunctie': {},
                'gebruiksdoelGezondheidszorgfunctie': {},
            }
        }

        expected_row = {
            'node': {
                'gebruiksdoel': [{'omschrijving': 'sportfunctie', 'code': '2'}, {'omschrijving': 'woonfunctie', 'code': '1'}],
                'gebruiksdoelWoonfunctie': {},
                'gebruiksdoelGezondheidszorgfunctie': {},
                'GebruiksdoelVerblijfsobjectDomein': '2075',
                'OmschrijvingGebruiksdoelVerblijfsobjectDomein': '2075 Woning'
            }
        }

        self.assertEqual(row_formatter_verblijfsobjecten(row), expected_row)
        self.assertEqual(row_formatter_verblijfsobjecten(row['node']), expected_row['node'])

        # Test gebruiksdoelWoonfunctie
        row = {
            'node': {
                'gebruiksdoel': [{'omschrijving': 'woonfunctie', 'code': '1'}],
                'gebruiksdoelWoonfunctie': {'omschrijving': 'Verpleeghuis'},
                'gebruiksdoelGezondheidszorgfunctie': {},
            }
        }

        expected_row = {
            'node': {
                'gebruiksdoel': [{'omschrijving': 'woonfunctie', 'code': '1'}],
                'gebruiksdoelWoonfunctie': {'omschrijving': 'Verpleeghuis'},
                'gebruiksdoelGezondheidszorgfunctie': {},
                'GebruiksdoelVerblijfsobjectDomein': '1310',
                'OmschrijvingGebruiksdoelVerblijfsobjectDomein': 'BEST-verpleeghuis'
            }
        }

        self.assertEqual(row_formatter_verblijfsobjecten(row), expected_row)
        self.assertEqual(row_formatter_verblijfsobjecten(row['node']), expected_row['node'])

        # Test gebruiksdoelGezondheidszorgfunctie
        row = {
            'node': {
                'gebruiksdoel': [{'omschrijving': 'gezondheidszorgfunctie', 'code': '1'}],
                'gebruiksdoelWoonfunctie': {},
                'gebruiksdoelGezondheidszorgfunctie': {'omschrijving': 'Verpleeghuis'},
            }
        }

        expected_row = {
            'node': {
                'gebruiksdoel': [{'omschrijving': 'gezondheidszorgfunctie', 'code': '1'}],
                'gebruiksdoelWoonfunctie': {},
                'gebruiksdoelGezondheidszorgfunctie': {'omschrijving': 'Verpleeghuis'},
                'GebruiksdoelVerblijfsobjectDomein': '2310',
                'OmschrijvingGebruiksdoelVerblijfsobjectDomein': '2310 Verpleeghuis'
            }
        }

        self.assertEqual(row_formatter_verblijfsobjecten(row), expected_row)
        self.assertEqual(row_formatter_verblijfsobjecten(row['node']), expected_row['node'])

    def test_row_formatter_geometrie(self):
        row = {
            'node': {
                'amsterdamseSleutel': '03630000000000',
                'geometrie': 'POINT(123, 456)'
            }
        }

        expected_row = {
            'node': {
                'amsterdamseSleutel': '3630000000000',
                'geometrie': 'POINT (123, 456)'
            }
        }

        self.assertEqual(row_formatter_geometrie(row), expected_row)

        row = {
            'node': {
                'amsterdamseSleutel': '03630000000000',
                'geometrie': None
            }
        }

        expected_row = {
            'node': {
                'amsterdamseSleutel': '3630000000000',
                'geometrie': ''
            }
        }

        self.assertEqual(row_formatter_geometrie(row), expected_row)
