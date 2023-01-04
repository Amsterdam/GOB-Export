from unittest import TestCase
from unittest.mock import patch

from shapely.errors import GeometryTypeError

from gobexport.formatter.geometry import format_geometry


class MockShape:

    def __init__(self, value):
        self.value = f"{value['type'].upper()} ({value['coordinates'][0]} {value['coordinates'][1]})"

    @property
    def wkt(self):
        return self.value

class TestGeometryFormatter(TestCase):

    @patch("gobexport.formatter.geometry.shape")
    def test_format_geometry_geojson(self, mock_shape):
        geojson = {'type': 'Point', 'coordinates': [125.6, 10.1]}
        expected_result = 'POINT (125.6 10.1)'

        mock_shape.return_value = MockShape(geojson)

        self.assertEqual(format_geometry(geojson), expected_result)

    def test_format_geometry_invalid_geojson(self):
        geojson = {'type': 'Invalid', 'false': 'attribute'}

        with self.assertRaises(GeometryTypeError):
            format_geometry(geojson)

    def test_format_geometry_none(self):
        geojson = None
        expected_result = ''

        self.assertEqual(format_geometry(geojson), expected_result)

    def test_format_geometry_wkt(self):
        wkt = 'POINT (125.6 10.1)'
        expected_result = 'POINT (125.6 10.1)'

        self.assertEqual(format_geometry(wkt), expected_result)
