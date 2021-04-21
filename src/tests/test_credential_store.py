from unittest import TestCase
from unittest.mock import MagicMock

import datetime

from gobexport.credential_store import CredentialStore


class TestCredentialStore(TestCase):

    def test_init(self):
        # AssertionError is raised without a secure user
        with self.assertRaises(AssertionError):
            cs = CredentialStore('get', 'refresh')

        cs = CredentialStore('get', 'refresh', secure_user='any user')
        self.assertEqual(cs._get_credentials, 'get')
        self.assertEqual(cs._refresh_credentials, 'refresh')
        self.assertIsNone(cs._credentials)
        self.assertEqual(cs._secure_user, 'any user')

    def test_get_secure_user(self):
        cs = CredentialStore('get', 'refresh', secure_user='any user')
        self.assertEqual(cs.get_secure_user(), 'any user')

    def test_save_credentials(self):
        cs = CredentialStore('get', 'refresh', 'any user')
        self.assertIsNone(cs._credentials)
        self.assertIsNone(cs._timestamp)

        before = datetime.datetime.now()
        cs._save_credentials('cred')
        after = datetime.datetime.now()
        self.assertEqual(cs._credentials, 'cred')
        self.assertIsNotNone(cs._timestamp)
        self.assertTrue(cs._timestamp >= before)
        self.assertTrue(cs._timestamp <= after)

    def test_get_credentials(self):
        expires_in = 10
        refresh_expires_in = 20
        threshold = CredentialStore.THRESHOLD
        access_threshold = int(expires_in * threshold)
        refresh_threshold = int(refresh_expires_in * threshold)

        get = MagicMock()
        get.return_value = {
            'token': 'access token',
            'expires_in': expires_in,
            'refresh_expires_in': refresh_expires_in
        }
        mock_refresh_token = get.return_value
        refresh = MagicMock()
        refresh.return_value = {
            'token': 'refreshed access token',
            'expires_in': expires_in,
            'refresh_expires_in': refresh_expires_in
        }

        cs = CredentialStore(get, refresh, 'any user')

        cs._now = MagicMock()
        cs._now.return_value = datetime.datetime(2020, 1, 1, 12)

        # Initial call => get credentials
        cs.get_credentials()
        get.assert_called_with('any user')
        refresh.assert_not_called()
        self.assertEqual(cs._credentials, get.return_value)

        get.reset_mock()

        # Ask again => use stored credentials
        cs.get_credentials()
        get.assert_not_called()
        refresh.assert_not_called()

        # Ask again within access validity interval => use stored credentials
        cs._now.return_value = cs._now.return_value + datetime.timedelta(seconds=access_threshold - 1)
        cs.get_credentials()
        get.assert_not_called()
        refresh.assert_not_called()

        # Ask again outside access validity interval => refresh credentials
        cs._now.return_value = cs._now.return_value + datetime.timedelta(seconds=2)
        cs.get_credentials()
        get.assert_not_called()
        refresh.assert_called_with(mock_refresh_token, 'any user')
        self.assertEqual(cs._credentials, refresh.return_value)

        refresh.reset_mock()

        # Ask outside access and refresh validity interval => get new credentials
        cs._now.return_value = cs._now.return_value + datetime.timedelta(seconds=refresh_threshold + 1)
        cs.get_credentials()
        get.assert_called_with('any user')
        refresh.assert_not_called()
