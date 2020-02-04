from unittest import TestCase
from unittest.mock import patch
from datetime import datetime

from gobexport.exporter.config.brk.utils import brk_filename, sort_attributes, format_timestamp, _get_filename_date


class TestBrkConfigHelpers(TestCase):

    @patch("gobexport.exporter.config.brk.utils._get_filename_date", datetime.now)
    def test_brk_filename(self):
        self.assertEqual(f"AmsterdamRegio/CSV_Actueel/BRK_FileName_{datetime.now().strftime('%Y%m%d')}.csv",
                         brk_filename('FileName'))

        self.assertEqual(f"AmsterdamRegio/SHP_Actueel/BRK_FileName_{datetime.now().strftime('%Y%m%d')}.shp",
                         brk_filename('FileName', type='shp'))

        self.assertEqual(f"AmsterdamRegio/SHP_Actueel/BRK_FileName.prj",
                         brk_filename('FileName', type='prj', append_date=False, ))

        # Assert undefined file type raises error
        with self.assertRaises(AssertionError):
            brk_filename('FileName', type='xxx')

    @patch("gobexport.exporter.config.brk.utils._get_filename_date", lambda: None)
    def test_brk_filename_none_date(self):
        self.assertEqual(f"AmsterdamRegio/CSV_Actueel/BRK_FileName_00000000.csv",
                         brk_filename('FileName'))

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

    def test_format_timestamp_with_format(self):
        inp = '2035-03-31T01:02:03.000000'
        format = '%Y-%m-%d'
        outp = '2035-03-31'
        self.assertEqual(outp, format_timestamp(inp, format=format))

        for inp in ['invalid_str', None]:
            # These inputs should not change
            self.assertEqual(inp, format_timestamp(inp, format=format))

    @patch("gobexport.exporter.config.brk.utils.requests.get")
    def test_get_filename_date(self, mock_request_get):
        mock_request_get.return_value.status_code = 200
        mock_request_get.return_value.json.return_value = {
            'id': 1,
            'kennisgevingsdatum': "2019-09-03T00:00:00",
        }

        expected_date = datetime(year=2019, month=9, day=3)
        self.assertEqual(expected_date, _get_filename_date())

    @patch("gobexport.exporter.config.brk.utils.requests.get")
    def test_get_filename_date_no_meta(self, mock_request_get):
        mock_request_get.return_value.status_code = 500

        self.assertIsNone(_get_filename_date())
