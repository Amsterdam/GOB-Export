from unittest import TestCase
from unittest.mock import patch, MagicMock, mock_open, call

from gobcore.exceptions import GOBException
from gobexport.exporter.csv import (
    get_entity_value, _get_headers_from_file, _ensure_fieldnames_match_existing_file,
    _get_csv_ids, csv_exporter
)


class TestCsvExporter(TestCase):

    def test_get_headers_from_file(self):

        with patch("builtins.open", mock_open(read_data="SOME;DATA")) as mock_file, \
                patch('gobexport.exporter.csv.csv') as mock_csv:
            res = _get_headers_from_file('somefile')
            mock_csv.DictReader.assert_called_with(mock_file.return_value, delimiter=';')
            mock_file.assert_called_with('somefile', 'r', encoding='utf-8-sig')
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

    @patch("gobexport.exporter.csv._ensure_fieldnames_match_existing_file")
    @patch("gobexport.exporter.csv.build_mapping_from_format")
    @patch("builtins.open", mock_open())
    @patch("gobexport.exporter.csv.csv")
    @patch("gobexport.exporter.csv.ProgressTicker")
    def test_csv_exporter_filter(self, mock_progress_ticker, mock_csv, mock_build_mapping,
                                 mock_match_fieldnames):
        api = ['a']
        file = ""

        csv_exporter(api, file)
        mock_tick = mock_progress_ticker.return_value.__enter__.return_value
        mock_tick.tick.assert_called_once()
        mock_tick.tick.reset_mock()

        mock_filter = MagicMock()
        mock_filter.filter.return_value = False
        csv_exporter(api, file, filter=mock_filter)

        mock_filter.filter.assert_called_with('a')
        mock_tick.tick.assert_not_called()

    @patch("gobexport.exporter.csv._ensure_fieldnames_match_existing_file")
    @patch("gobexport.exporter.csv.build_mapping_from_format")
    @patch("builtins.open", mock_open())
    @patch("gobexport.exporter.csv.csv")
    @patch("gobexport.exporter.csv._get_csv_ids")
    def test_csv_exporter_unique_csv_id(self, mock_csv_ids, mock_csv, mock_build_mapping, mock_match_fieldnames):
        api_id = "id"
        api = [{api_id: "b", "field": "data"}, {api_id: "c", "field": "data"}, {api_id: "d", "field": "data"}]
        csv_id = "BRK2_AANTEK_ID"
        csv_file = "file.csv"
        mock_csv_ids.return_value = ["a", "b"]

        mock_build_mapping.return_value = MagicMock(spec_set=dict)
        csv_map = {csv_id: api_id}
        mock_build_mapping.return_value.__getitem__.side_effect = csv_map.__getitem__

        count = csv_exporter(api, csv_file, append=True, unique_csv_id=csv_id)
        self.assertEqual(count, 2)
        mock_csv_ids.assert_called_with(csv_file, csv_id)

    @patch("builtins.open", mock_open())
    @patch("gobexport.exporter.csv.csv.DictReader")
    def test_get_csv_ids(self, mock_reader):
        mock_reader.return_value = [{"BRK2_AANTEK_ID": "x", "field": "data"}, {"BRK2_AANTEK_ID": "y", "field": "data"}]
        result = _get_csv_ids("file.csv", "BRK2_AANTEK_ID")
        self.assertEqual(result, set(["x", "y"]))
