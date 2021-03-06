from unittest import TestCase
from unittest.mock import patch, MagicMock, ANY

from gobexport.exporter import export_to_file


class TestInit(TestCase):

    @patch("gobexport.exporter._init_api", MagicMock())
    @patch("gobexport.exporter.BufferedIterable", MagicMock())
    def test_export_to_file_append(self):

        exporter = MagicMock()
        product = {
            'exporter': exporter,
            'format': 'the format',
            'append': True,
            'append_to_filename': 'the filename',
        }

        # Do append, pass value of append_to_filename to exporter
        self.assertEqual(exporter(), export_to_file('host', product, 'file', 'catalogue', 'collection'))
        exporter.assert_called_with(ANY, 'file', 'the format', append='the filename', filter=None)

        # Don't append
        product['append'] = False
        self.assertEqual(exporter(), export_to_file('host', product, 'file', 'catalogue', 'collection'))
        exporter.assert_called_with(ANY, 'file', 'the format', append=False, filter=None)

    @patch("gobexport.exporter._init_api", MagicMock())
    @patch("gobexport.exporter.BufferedIterable", MagicMock())
    @patch("gobexport.exporter.encrypt_file")
    def test_export_encrypt_file(self, mock_encrypt_file):

        exporter = MagicMock()
        product = {
            'exporter': exporter,
            'format': 'the format',
            'encryption_key': 'any key'
        }

        # Do append, pass value of append_to_filename to exporter
        export_to_file('host', product, 'file', 'catalogue', 'collection')
        mock_encrypt_file.assert_called_with('file', 'any key')
