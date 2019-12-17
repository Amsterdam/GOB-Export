import requests

from gobexport.config import OIDC_TOKEN_ENDPOINT, OIDC_CLIENT_ID, OIDC_CLIENT_SECRET

_ACCESS_TOKEN = "access_token"
_TOKEN_TYPE = "token_type"


def get_secure_header():
    """
    Get the request header to access secure endpoints

    """
    credentials = get_credentials()
    return {
        'Authorization': f"{credentials[_TOKEN_TYPE]} {credentials[_ACCESS_TOKEN]}"
    }


def get_credentials():
    """
    Get Keycloak credentials

    Main attributes are:
    access_token:       to be send in the Authorization header with each request to a secure endpoint
    expires_in:         number of seconds that the access token remains valid (normally 900 seconds)
    refresh_token:      token needed to refresh the access token
    refresh_expires_in: number of seconds that the refresh token remains valid (normally 1800 seconds)
    token_type:         token type to set in the Authorization header
    """
    data = {
        'grant_type': "client_credentials",
        'client_id': OIDC_CLIENT_ID,
        'client_secret': OIDC_CLIENT_SECRET
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    result = requests.post(url=OIDC_TOKEN_ENDPOINT, data=data, headers=headers)
    result.raise_for_status()
    return result.json()


def refresh_credentials(credentials):
    """
    Refresh Keycloak credentials

    """
    data = {
        'grant_type': "refresh_token",
        'client_id': OIDC_CLIENT_ID,
        'client_secret': OIDC_CLIENT_SECRET,
        'refresh_token': credentials['refresh_token']
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    result = requests.post(url=OIDC_TOKEN_ENDPOINT, data=data, headers=headers)
    result.raise_for_status()
    return result.json()
