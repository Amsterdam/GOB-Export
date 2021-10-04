from typing import Optional

import requests

from gobexport.config import OIDC_TOKEN_ENDPOINT, get_oidc_client
from gobexport.credential_store import CredentialStore

_ACCESS_TOKEN = "access_token"
_TOKEN_TYPE = "token_type"

_credential_store: Optional[CredentialStore] = None


def _init_credential_store(secure_user):
    """
    Initialize the Credential Store

    :return:
    """
    global _credential_store

    # Recreate the credential store for a new secure user
    if not _credential_store or secure_user != _credential_store.get_secure_user():
        _credential_store = CredentialStore(get_credentials=get_credentials, refresh_credentials=refresh_credentials,
                                            secure_user=secure_user)


def get_secure_header(secure_user):
    """
    Get the request header to access secure endpoints
    """
    _init_credential_store(secure_user)
    credentials = _credential_store.get_credentials()
    return {
        'Authorization': f"{credentials[_TOKEN_TYPE].capitalize()} {credentials[_ACCESS_TOKEN]}"
    }


def get_credentials(secure_user):
    """
    Get Keycloak credentials

    Main attributes are:
    access_token:       to be send in the Authorization header with each request to a secure endpoint
    expires_in:         number of seconds that the access token remains valid (normally 900 seconds)
    refresh_token:      token needed to refresh the access token
    refresh_expires_in: number of seconds that the refresh token remains valid (normally 1800 seconds)
    token_type:         token type to set in the Authorization header
    """
    assert secure_user, "A secure user is needed to get the client id and secret"
    oidc_client = get_oidc_client(secure_user)

    data = {
        'grant_type': "client_credentials",
        'client_id': oidc_client.get('id'),
        'client_secret': oidc_client.get('secret')
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    result = requests.post(url=OIDC_TOKEN_ENDPOINT, data=data, headers=headers)
    result.raise_for_status()
    return result.json()


def refresh_credentials(credentials, secure_user):
    """
    Refresh Keycloak credentials

    """
    oidc_client = get_oidc_client(secure_user)

    data = {
        'grant_type': "refresh_token",
        'client_id': oidc_client.get('id'),
        'client_secret': oidc_client.get('secret'),
        'refresh_token': credentials['refresh_token']
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    result = requests.post(url=OIDC_TOKEN_ENDPOINT, data=data, headers=headers)
    result.raise_for_status()
    return result.json()
