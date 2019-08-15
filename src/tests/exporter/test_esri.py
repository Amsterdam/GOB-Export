from unittest import TestCase
from unittest.mock import MagicMock, mock_open, patch

from gobexport.exporter.esri import esri_exporter


class TestEsriExporter(TestCase):

    def test_append_raises_notimplementederror(self):
        with self.assertRaises(NotImplementedError):
            esri_exporter([], '', append=True)

    @patch("builtins.open", mock_open())
    @patch("gobexport.exporter.esri.ProgressTicker")
    @patch("gobexport.exporter.esri.ogr", MagicMock())
    @patch("gobexport.exporter.esri._get_geometry_type", MagicMock())
    def test_esri_exporter_filter(self, mock_progress_ticker):

        api = [{'geometrie': False}]
        file = ""

        esri_exporter(api, file, {})
        mock_tick = mock_progress_ticker.return_value.__enter__.return_value
        mock_tick.tick.assert_called_once()
        mock_tick.tick.reset_mock()

        mock_filter = MagicMock()
        mock_filter.filter.return_value = False
        esri_exporter(api, file, {}, filter=mock_filter)

        mock_filter.filter.assert_called_with(api[0])
        mock_tick.tick.assert_not_called()

