from datetime import date

from unittest import TestCase
from unittest.mock import patch, MagicMock, mock_open, call

from gobcore.exceptions import GOBException
from gobexport.exporter.uva2 import _get_uva2_headers, CRLF, uva2_exporter


class TestUVA2Exporter(TestCase):

    def test_get_uva2_headers(self):
        expected_result = f"VAN;20350101{CRLF}" \
                          f"TM;20350101{CRLF}" \
                          f"HISTORISCHE_CYCLI;N{CRLF}"

        with patch('gobexport.exporter.uva2.date') as mock_date:
            mock_date.today.return_value = date(2035, 1, 1)
            self.assertEqual(expected_result, _get_uva2_headers())

    @patch("gobexport.exporter.uva2.build_mapping_from_format")
    @patch("builtins.open", mock_open())
    @patch("gobexport.exporter.uva2.ProgressTicker")
    def test_csv_exporter_filter(self, mock_progress_ticker, mock_build_mapping):
        api = ['a']
        file = ""

        uva2_exporter(api, file)
        mock_tick = mock_progress_ticker.return_value.__enter__.return_value
        mock_tick.tick.assert_called_once()
        mock_tick.tick.reset_mock()

        mock_filter = MagicMock()
        mock_filter.filter.return_value = False
        uva2_exporter(api, file, filter=mock_filter)

        mock_filter.filter.assert_called_with('a')
        mock_tick.tick.assert_not_called()
