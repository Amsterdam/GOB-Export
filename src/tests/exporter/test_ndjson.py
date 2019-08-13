from unittest import TestCase
from unittest.mock import patch, MagicMock, mock_open

from gobexport.exporter.ndjson import ndjson_exporter


class TestNDJSONExporter(TestCase):

    def test_append_raises_notimplementederror(self):

        with self.assertRaises(NotImplementedError):
            ndjson_exporter([], '', append=True)

    def test_write(self):
        mock_api = [{}, {"a": 1}]
        with patch("builtins.open", mock_open()) as mock_file:
            ndjson_exporter(mock_api, "any file")
            mock_file.assert_called_with("any file", 'w')
            handle = mock_file()
            handle.write.assert_any_call('{}\n')
            handle.write.assert_any_call('{"a": 1}\n')
            self.assertEqual(mock_file.call_count, 2)

    @patch("builtins.open", mock_open())
    @patch("gobexport.exporter.ndjson.ProgressTicker")
    def test_esri_exporter_filter(self, mock_progress_ticker):

        api = ['a']
        file = ""

        ndjson_exporter(api, file, {})
        mock_tick = mock_progress_ticker.return_value.__enter__.return_value
        mock_tick.tick.assert_called_once()
        mock_tick.tick.reset_mock()

        mock_filter = MagicMock()
        mock_filter.filter.return_value = False
        ndjson_exporter(api, file, {}, filter=mock_filter)

        mock_filter.filter.assert_called_with('a')
        mock_tick.tick.assert_not_called()

