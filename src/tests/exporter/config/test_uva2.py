from unittest import TestCase
from unittest.mock import patch, MagicMock
from datetime import date

from gobexport.exporter.config.uva2 import get_uva2_filename, format_uva2_date, format_uva2_status


class TestUVA2ConfigHelpers(TestCase):

    def test_get_uva2_filename(self):
        publish_date = date.today().strftime('%Y%m%d')
        self.assertEqual(f"UVA2_Actueel/ABC_{publish_date}_N_{publish_date}_{publish_date}.UVA2",
                         get_uva2_filename('ABC'))

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

    def test_format_uva2_status_invalid(self):
        # Test invalid entity names
        with self.assertRaises(AssertionError):
            format_uva2_status('1', 'invalid')

    def test_format_uva2_status_openbareruimtes(self):
        # Status 1 and 2 should be mapped to 35, 36 for openbareruimtes
        status = [('1', '35'), ('2', '36'), (1, '35')]

        for input, expected in status:
            self.assertEqual(expected, format_uva2_status(input, "openbareruimtes"))

        # Test invalid status for openbareruimtes
        status = [3, '4', 'a', None]

        for input in status:
            with self.assertRaises(AssertionError):
                format_uva2_status(input, "openbareruimtes")
