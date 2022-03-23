import logging
import urllib.request
from typing import Optional, Callable

import requests
import time

from gobexport.config import PUBLIC_URL
from gobexport.keycloak import get_secure_header
from gobexport.worker import Worker

logger = logging.getLogger(__name__)

_MAX_TRIES = 60                # Maximum number of times to try the request
_RETRY_TIMEOUT = 60            # Seconds between consecetive retries

# Pass a tuple to timeout with the first element being a connect timeout
# - the time it allows for the client to establish a connection to the server
# and the second being a read timeout
# - the time it will wait on a response once your client has established a connection
_REQUEST_TIMEOUT = (60, 7200)  # Request timout to 60 seconds to connect and 2 hours for the data

# String that identifies a public GOB url. If an url contains this string it is the url of a public endpoint
_PUBLIC_URL = f'{PUBLIC_URL}/'


class APIException(IOError):
    pass


def _exec(method: Callable[..., requests.models.Response], url: str, secure_user: Optional[str] = None, **kwargs):
    """
    Execute method _MAX_TRIES times to get a result

    :raise APIException when all _MAX_TRIES requests have failed
    :param method: get or post
    :param kwargs: any arguments
    :return: the result of the get or post request
    """
    n_tries = 0
    while n_tries < _MAX_TRIES:
        headers = _updated_headers(url, secure_user=secure_user)
        try:
            response = method(url=url, headers=headers, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            # Errors and Exceptions
            #
            # Network problem (e.g. DNS failure, refused connection, etc) => ConnectionError
            # HTTPError if the HTTP request returned an unsuccessful status code.
            # If a request times out, a Timeout exception is raised.
            # If a request exceeds the configured number of maximum redirections => TooManyRedirects
            #
            # All exceptions that Requests explicitly raises inherit from requests.exceptions.RequestException.
            n_tries += 1
            print(f"Request exception: '{str(e)}'")
            print(f"Retry in {_RETRY_TIMEOUT} seconds, retries left: {_MAX_TRIES - n_tries}")
            time.sleep(_RETRY_TIMEOUT)

    request = ', '.join([f"{k}='{v}'" for k, v in kwargs.items()])
    raise APIException(f"Request '{request}' failed, tried {n_tries} times")


def _updated_headers(
        url: str,
        headers: Optional[dict[str, str]] = None,
        secure_user: Optional[str] = None
) -> dict[str, str]:
    """Update headers with credentials if url is not public.

    :param url: The url to update the headers for
    :param headers: Add secure user to possible existing headers
    :param secure_user: The user id to add the credentials for
    :return: Updated headers
    """
    if _PUBLIC_URL not in url:
        logger.info(f"Updating secure headers for user {secure_user}")
        assert secure_user, f"A secure_user must be defined to request secure url {url}"
        headers = headers or {}
        headers.update(get_secure_header(secure_user))
    return headers


def get(url, secure_user=None):
    return _exec(requests.get, url=url, timeout=_REQUEST_TIMEOUT, secure_user=secure_user)


def post(url, json, secure_user=None):
    return _exec(requests.post, url=url, json=json, timeout=_REQUEST_TIMEOUT, secure_user=secure_user)


def handle_streaming_gob_response(func):
    """Wraps streaming endpoints, adds error handling as implemented by GOB-API
    GOB-API always returns an empty line on a successful request. If the last line is not an empty line, an
    APIException is raised.

    :param func:
    :return:
    """
    def wrapper(*args, **kwargs):
        last_item = None
        for item in func(*args, **kwargs):
            last_item = item

            if last_item != b'':
                yield item

        if last_item != b'':
            raise APIException("Incomplete request received from API. See API logs for more info.")

    return wrapper


@handle_streaming_gob_response
def get_stream(url, secure_user=None):
    try:
        response = requests.get(url=url, headers=_updated_headers(url, Worker.headers, secure_user=secure_user),
                                stream=True)
        response.raise_for_status()
        return Worker.handle_response(response)
    except requests.exceptions.RequestException as e:
        msg = f"Request failed due to API exception, {e.response}"
        raise APIException(msg) from e


@handle_streaming_gob_response
def post_stream(url, json, secure_user=None, **kwargs):
    try:
        response = requests.post(
            url, headers=_updated_headers(url, Worker.headers, secure_user), stream=True, json=json, **kwargs)
        response.raise_for_status()
        return Worker.handle_response(response)
    except requests.exceptions.RequestException as e:
        msg = f"Request failed due to API exception, {e.response}"
        raise APIException(msg) from e


def urlopen(url):
    request = urllib.request.Request(url, headers=_updated_headers(url))
    return urllib.request.urlopen(request)
