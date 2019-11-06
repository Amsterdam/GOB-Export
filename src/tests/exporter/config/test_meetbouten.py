from unittest import TestCase
from unittest.mock import patch, MagicMock
from datetime import datetime

from gobexport.exporter.config.meetbouten import RollagenExportConfig


class MockGeom:

    @property
    def centroid(self):
        return 'centroid'


class TestMeetboutenConfigHelpers(TestCase):

    @patch("gobexport.exporter.config.meetbouten.shape")
    @patch("gobexport.exporter.config.meetbouten.mapping")
    def test_row_formatter_rollagen(self, mock_mapping, mock_shape):
        mock_geom = MockGeom()
        mock_shape.return_value = mock_geom
        mock_mapping.return_value = {
            'type': 'Point',
            'coordinates': [123.12345, 123.02]
        }

        # Test woonfuctie without gebruiksdoelWoonfunctie
        row = {
            'node': {
                'isGemetenVanBouwblok': {
                    'edges': [{
                        'node': {
                            'geometrie': 'input'
                        }
                    }]
                }
            }
        }

        # Expect result to include geomtrie with rounded coordinates
        expected_row = {
            'node': {
                'isGemetenVanBouwblok': {
                    'edges': [{
                        'node': {
                            'geometrie': 'input'
                        }
                    }]
                },
                'geometrie': {
                    'type': 'Point',
                    'coordinates': ['123.123', '123.02']
                }
            }
        }

        result = RollagenExportConfig.row_formatter_rollagen(row)

        mock_shape.assert_called_with('input')
        mock_mapping.assert_called_with('centroid')

        self.assertEqual(result, expected_row)
