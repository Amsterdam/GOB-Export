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

        # Expect resolved_filename to be added
        expected = {
            'product1': {
                'filename': 'fname',
                'resolved_filename': 'fname',
                'extra_files': [
                    {
                        'filename': 'extra_file_name',
                        'resolved_filename': 'extra_file_name'
                    }
                ]
            }
        }
        resolve_config_filenames(config)

        self.assertEqual(expected, config.products)

        # Expect filename to still be the same function, and resolved filename to be added
        expected = {
            'product1': {
                'filename': self.MockConfigFunctions.products['product1']['filename'],
                'resolved_filename': 'l_fname',
                'extra_files': [
                    {
                        'filename': self.MockConfigFunctions.products['product1']['extra_files'][0]['filename'],
                        'resolved_filename': 'l_extra_file_name'
                    }
                ]
            }
        }
        config = self.MockConfigFunctions()
        resolve_config_filenames(config)

        self.assertEqual(expected, config.products)
