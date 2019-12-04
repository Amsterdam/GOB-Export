import pytest
from unittest import TestCase
from unittest.mock import MagicMock, mock_open, patch

from gobexport.exporter.esri import get_centroid, get_x, get_y, get_longitude, get_latitude, esri_exporter


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


@pytest.mark.parametrize(
    "wkt, expected",
    [
        ("POINT (121897.414 486037.556)",
            "POINT (121897.414 486037.556)"),

        ("POLYGON ((121892.581 486045.918, 121897.245 486027.899, 121902.247 486029.194, 121897.583 486047.213, 121892.581 486045.918))",
            "POINT (121897.414 486037.556)"),
    ],
)
def test_get_centroid(wkt, expected):
    assert get_centroid(wkt).ExportToWkt() == expected


@pytest.mark.parametrize(
    "wkt, x, y, longitude, latitude",
    [
        ("POINT (5542965.5321530355 -25292905.275564767)",  # City Hall Park in New York
            5542965, -25292905, 40.7127984, -74.0059993),

        ("POINT (155000 463000)",  # Onze Lieve Vrouwetoren in Amersfoort
            155000, 463000, 5.3872036, 52.1551723),

        ("POLYGON ((121892.580878004 486045.918087506, 121897.244877565 486027.899089311, 121902.246877063 486029.194089191, 121897.582877501 486047.213087381, 121892.580878004 486045.918087506))",
            121897, 486037, 4.9012422, 52.3612313),
    ],
)
def test_get_coordinates(wkt, x, y, longitude, latitude):
    assert get_x(wkt) == x
    assert get_y(wkt) == y
    assert get_longitude(wkt) == longitude
    assert get_latitude(wkt) == latitude
