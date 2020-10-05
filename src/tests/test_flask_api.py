from unittest import TestCase
from unittest.mock import patch, MagicMock

from gobexport.flask_api import get_flask_app, _health, _products


def mock_config_object(products):
    return type('MockConfig', (), {
        'products': products
    })()

mock_config_mapping = {
    'catalog1': {
        'collection1': mock_config_object({
            'product1': {
                'filename': 'file1.csv',
                'extra_files': [
                    {'filename': 'file2.shp'}
                ]
            },
            'product2': {
                'filename': lambda: 'file3.dat',
            }
        }),
        'collection2': mock_config_object({
            'product3': {
                'filename': 'file4.dat'
            }
        })
    },
    'catalog2': {
        'collection3': mock_config_object({
            'product4': {
                'filename': 'file5.csv',
                'extra_files': [
                    {'filename': lambda: 'file6.shp'}
                ]
            }
        }),
    }
}


class TestAPI(TestCase):

    def test_health(self):
        self.assertEqual('Connectivity OK', _health())

    @patch("gobexport.flask_api.CONFIG_MAPPING", mock_config_mapping)
    def test_products(self):
        self.assertEqual({
            'catalog1': {
                'collection1': {
                    'product1': [
                        'file1.csv',
                        'file2.shp',
                    ],
                    'product2': [
                        'file3.dat',
                    ],
                },
                'collection2': {
                    'product3': [
                        'file4.dat'
                    ],
                },
            },
            'catalog2': {
                'collection3': {
                    'product4': [
                        'file5.csv',
                        'file6.shp',
                    ],
                },
            },
        }, _products())

    @patch("gobexport.flask_api.CORS", MagicMock())
    @patch("gobexport.flask_api.Flask")
    def test_get_flask_app(self, mock_flask):
        mock_app = MagicMock()
        mock_flask.return_value = mock_app
        app = get_flask_app()
        mock_flask.assert_called()
        mock_app.route.assert_called()
