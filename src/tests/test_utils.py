from unittest import TestCase

from gobexport.utils import resolve_config_filenames


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

    def test_resolve_config_filenames(self):
        config = self.MockConfig()
        expected = {
            'product1': {
                'filename': 'fname',
                'extra_files': [
                    {'filename': 'extra_file_name'}
                ]
            }
        }
        resolve_config_filenames(config)

        self.assertEqual(expected, config.products)

        expected = {
            'product1': {
                'filename': 'l_fname',
                'extra_files': [
                    {'filename': 'l_extra_file_name'}
                ]
            }
        }
        config = self.MockConfigFunctions()
        resolve_config_filenames(config)

        self.assertEqual(expected, config.products)
