from unittest import TestCase, mock

from gobexport.keycloak import get_credentials, refresh_credentials, get_secure_header


@mock.patch('gobexport.keycloak.OIDC_TOKEN_ENDPOINT', "any keycloak url")
@mock.patch('gobexport.keycloak.OIDC_CLIENT_ID', "any keycloak client id")
@mock.patch('gobexport.keycloak.OIDC_CLIENT_SECRET', "any keycloak secret")
class TestKeycloak(TestCase):

    @mock.patch('gobexport.keycloak.requests.post')
    def test_get_credentials(self, mock_post):
        credentials = get_credentials()

        mock_post.assert_called_with(
            data={
                'grant_type': 'client_credentials',
                'client_id': 'any keycloak client id',
                'client_secret': 'any keycloak secret'
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
        credentials = refresh_credentials(credentials)
        mock_post.assert_called_with(
            data={
                'grant_type': 'refresh_token',
                'client_id': 'any keycloak client id',
                'client_secret': 'any keycloak secret',
                'refresh_token': 'any refresh token'
            },
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            url='any keycloak url'
        )

    @mock.patch('gobexport.keycloak.get_credentials')
    def test_secure_header(self, mock_credentials):
        mock_credentials.return_value = {
            'access_token': "any access token",
            'token_type': "any token type"
        }
        self.assertEqual(get_secure_header(), {'Authorization': 'any token type any access token'})
