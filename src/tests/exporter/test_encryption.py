import base64

from unittest import TestCase
from unittest.mock import patch, MagicMock, mock_open

from gobexport.exporter.encryption import _encrypt_symmetric_key, encrypt_file


class TestEncryption(TestCase):

    @patch("gobexport.exporter.encryption.default_backend", MagicMock())
    @patch("gobexport.exporter.encryption.padding", MagicMock())
    @patch("gobexport.exporter.encryption.hashes", MagicMock())
    @patch("gobexport.exporter.encryption.serialization")
    @patch("builtins.open")
    def test_encrypt_symmetric_key(self, mock_open, mock_serialization):
        mock_file = mock_open.return_value.__enter__.return_value
        mock_public_key = MagicMock()

        mock_serialization.load_pem_public_key.return_value = mock_public_key
        mock_public_key.encrypt.return_value = b'any bytes'

        result = _encrypt_symmetric_key('any public key', 'any symmetric key')

        mock_serialization.load_pem_public_key.assert_called()

        mock_public_key.encrypt.assert_called()
        
        self.assertEqual(base64.b64encode(b'any bytes'), result)

    @patch("gobexport.exporter.encryption.get_public_key")
    @patch("gobexport.exporter.encryption.Fernet")
    @patch("gobexport.exporter.encryption._encrypt_symmetric_key")
    def test_encrypt_file(self, mock_encrypt_symmetric_key, mock_Fernet, mock_get_public_key):
        mock_get_public_key.return_value = 'any public key'

        mock_Fernet.generate_key.return_value = 'any symmetric key'
        mocked_fernet = MagicMock()
        mock_Fernet.return_value = mocked_fernet

        mock_encrypt_symmetric_key.return_value = b'any encrypted key'
        mocked_fernet.encrypt.return_value = b'any bytes'

        mocked_file = mock_open(read_data="any data")
        with patch('builtins.open', mocked_file):
            encrypt_file('any file', 'any key name')
            assert mocked_file.call_count == 2
            
            handle = mocked_file()
            handle.write.assert_called_once_with(b'0017:any encrypted key:any bytes')

            mock_get_public_key.assert_called_with('any key name')
            mock_Fernet.assert_called_with('any symmetric key')

            mocked_fernet.encrypt.assert_called_with('any data')

            mock_encrypt_symmetric_key.assert_called_with('any public key', 'any symmetric key')
