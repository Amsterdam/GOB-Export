from unittest import TestCase
from unittest.mock import patch, MagicMock, mock_open, call

from gobcore.exceptions import GOBException
from gobexport.exporter.csv import get_entity_value, \
    _get_headers_from_file, _ensure_fieldnames_match_existing_file, csv_exporter


class TestCsvExporter(TestCase):

    def test_get_headers_from_file(self):

        with patch("builtins.open", mock_open(read_data="SOME;DATA")) as mock_file, \
                patch('gobexport.exporter.csv.csv') as mock_csv:
            res = _get_headers_from_file('somefile')

            mock_csv.DictReader.assert_called_with(mock_file.return_value, delimiter=';')
            mock_file.assert_called_with('somefile', 'r')
            self.assertEqual(mock_csv.DictReader().fieldnames, res)

    @patch("gobexport.exporter.csv._get_headers_from_file")
    def test_ensure_fieldnames_match_existing_file(self, mock_get_headers):
        existing_fields = ['A', 'B', 'C']
        mock_get_headers.return_value = existing_fields

        # Headers match, no exception
        _ensure_fieldnames_match_existing_file(existing_fields.copy(), 'somefile')
        mock_get_headers.assert_called_with('somefile')

        error_cases = [
            [],
            ['a', 'b', 'c'],
            ['A', 'B'],
            ['A', 'C', 'B'],
            ['A', 'B', 'C', 'D'],
        ]

        for error_case in error_cases:
            with self.assertRaises(GOBException):
                _ensure_fieldnames_match_existing_file(error_case, 'somefile')

    @patch("gobexport.exporter.csv._ensure_fieldnames_match_existing_file")
    @patch("gobexport.exporter.csv.build_mapping_from_format")
    @patch("builtins.open", mock_open())
    @patch("gobexport.exporter.csv.csv")
    def test_csv_exporter_append(self, mock_csv, mock_build_mapping, mock_match_fieldnames):
        api = []
        file = ""

        csv_exporter(api, file)
        mock_match_fieldnames.assert_not_called()

        csv_exporter(api, file, append=True)
        mock_match_fieldnames.assert_called_once()
