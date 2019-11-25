from unittest import TestCase
from unittest.mock import ANY

from gobexport.utils import resolve_config


class TestUtils(TestCase):
    class MockConfig:
        products = {
            'product1': {
                'filename': 'fname',
                'extra_files': [
                    {'filename': 'extra_file_name'}
                ]
            }
        }

    class MockConfigFunctions:
        products = {
            'product1': {
                'filename': lambda: 'l_fname',
                'extra_files': [
                    {'filename': lambda: 'l_extra_file_name'}
                ]
            }
        }

    def test_resolve_config_filename(self):
        config = self.MockConfig()
        expected = {
            'product1': {
                'filename': 'fname',
                'resolve_filename': ANY,
                'extra_files': [
                    {'filename': 'extra_file_name', 'resolve_filename': ANY}
                ]
            }
        }
        resolve_config(config, "filename")

        self.assertEqual(expected, config.products)

        # Test that resolver method resolved to the expected filename
        product = config.products['product1']
        self.assertEqual(product['resolve_filename'](), expected['product1']['filename'])

        # Test that next run should give the same result
        product['filename'] = None
        resolve_config(config, "filename")
        product = config.products['product1']
        self.assertEqual(product['filename'], expected['product1']['filename'])

        expected = {
            'product1': {
                'filename': 'l_fname',
                'resolve_filename': ANY,
                'extra_files': [
                    {'filename': 'l_extra_file_name', 'resolve_filename': ANY}
                ]
            }
        }
        config = self.MockConfigFunctions()
        resolve_config(config, "filename")

        self.assertEqual(expected, config.products)
