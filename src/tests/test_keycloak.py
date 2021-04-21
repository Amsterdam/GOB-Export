from unittest import TestCase, mock

from gobexport.keycloak import get_credentials, refresh_credentials, get_secure_header, _init_credential_store
from gobexport import keycloak

@mock.patch('gobexport.keycloak.OIDC_TOKEN_ENDPOINT', "any keycloak url")
@mock.patch('gobexport.keycloak.get_oidc_client', lambda x: {'id': f'{x}_id', 'secret': f'{x}_secret'})
class TestKeycloak(TestCase):

    @mock.patch('gobexport.keycloak.requests.post')
    def test_get_credentials(self, mock_post):
        credentials = get_credentials('any secure user')

        mock_post.assert_called_with(
            data={
                'grant_type': 'client_credentials',
                'client_id': 'any secure user_id',
                'client_secret': 'any secure user_secret'
            },
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            url='any keycloak url'
        )

    @mock.patch('gobexport.keycloak.requests.post')
    def test_refresh_credentials(self, mock_post):
        credentials = {
            'refresh_token': "any refresh token"
        }
        credentials = refresh_credentials(credentials, 'any secure user')
        mock_post.assert_called_with(
            data={
                'grant_type': 'refresh_token',
                'client_id': 'any secure user_id',
                'client_secret': 'any secure user_secret',
                'refresh_token': 'any refresh token'
            },
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            url='any keycloak url'
        )

    @mock.patch('gobexport.keycloak._init_credential_store')
    @mock.patch('gobexport.keycloak._credential_store')
    def test_secure_header(self, mock_credential_store, mock_init_credentials_store):
        mock_credential_store.get_credentials.return_value = {
            'access_token': "any access token",
            'token_type': "any token type"
        }
        # Token type should be capitalized
        result = get_secure_header('any secure user')

        mock_init_credentials_store.assert_called_with('any secure user')
        mock_credential_store.get_credentials.assert_called_with()

        self.assertEqual(result, {'Authorization': 'Any token type any access token'})

    @mock.patch('gobexport.keycloak.CredentialStore')
    @mock.patch('gobexport.keycloak.get_credentials')
    @mock.patch('gobexport.keycloak.refresh_credentials')
    def test_init_credential_store(self, mock_refresh_credentials, mock_get_credentials, mock_credential_store):
        keycloak._credential_store = None
        _init_credential_store('any secure user')

        mocked_instance = mock_credential_store.return_value
        mocked_instance.get_secure_user.return_value = 'any secure user'

        mock_credential_store.assert_called_with(get_credentials=mock_get_credentials,
                                                  refresh_credentials=mock_refresh_credentials,
                                                  secure_user='any secure user')

        self.assertIsNotNone(keycloak._credential_store)
        mock_credential_store.reset_mock()

        _init_credential_store('any secure user')
        mock_credential_store.assert_not_called()

        mock_credential_store.reset_mock()

        _init_credential_store('any other secure user')
        mock_credential_store.assert_called_with(get_credentials=mock_get_credentials,
                                                  refresh_credentials=mock_refresh_credentials,
                                                  secure_user='any other secure user')