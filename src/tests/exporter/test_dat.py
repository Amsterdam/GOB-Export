from unittest import TestCase
from unittest.mock import patch, mock_open, MagicMock

from gobexport.exporter.dat import dat_exporter


class TestDatExporter(TestCase):

    def test_append_raises_notimplementederror(self):

        with self.assertRaises(NotImplementedError):
            dat_exporter([], '', append=True)

    @patch("builtins.open", mock_open())
    @patch("gobexport.exporter.dat.ProgressTicker")
    @patch("gobexport.exporter.dat.re", MagicMock())
    def test_dat_exporter_filter(self, mock_progress_ticker):

        api = [{'a': 'b'}]
        file = ""

        dat_exporter(api, file)
        mock_tick = mock_progress_ticker.return_value.__enter__.return_value
        mock_tick.tick.assert_called_once()
        mock_tick.tick.reset_mock()

        mock_filter = MagicMock()
        mock_filter.filter.return_value = False
        dat_exporter(api, file, filter=mock_filter)

        mock_filter.filter.assert_called_with({'a': 'b', 'row_count': 1})
        mock_tick.tick.assert_not_called()
