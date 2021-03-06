import requests
import time

import urllib.request

from gobexport.config import PUBLIC_URL
from gobexport.keycloak import get_secure_header
from gobexport.worker import Worker

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


def _exec(method, url, headers, **kwargs):
    """
    Execute method _MAX_TRIES times to get a result

    :raise APIException when all _MAX_TRIES requests have failed
    :param method: get or post
    :param kwargs: any arguments
    :return: the result of the get or post request
    """
    n_tries = 0
    while n_tries < _MAX_TRIES:
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
            # Update headers because access token might be expired
            headers = _updated_headers(url=url, headers=headers)

    request = ', '.join([f"{k}='{v}'" for k, v in kwargs.items()])
    raise APIException(f"Request '{request}' failed, tried {n_tries} times")


def _updated_headers(url, headers=None, secure_user=None):
    if _PUBLIC_URL not in url:
        headers = headers or {}
        headers.update(get_secure_header(secure_user))
    return headers


def get(url, secure_user=None):
    return _exec(requests.get, url=url, headers=_updated_headers(url, secure_user=secure_user),
                 timeout=_REQUEST_TIMEOUT)


def post(url, json, secure_user=None):
    return _exec(requests.post, url=url, headers=_updated_headers(url, secure_user=secure_user), json=json,
                 timeout=_REQUEST_TIMEOUT)


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
            raise APIException(f"Incomplete request received from API. See API logs for more info.")

    return wrapper


@handle_streaming_gob_response
def get_stream(url, secure_user=None):

    result = None
    try:
        result = requests.get(url=url, headers=_updated_headers(url, Worker.headers, secure_user=secure_user),
                              stream=True)
        result.raise_for_status()
        result = Worker.handle_response(result)
    except requests.exceptions.RequestException as e:
        raise APIException(f"Request failed due to API exception, response code {result and result.status_code}")
    return result


@handle_streaming_gob_response
def post_stream(url, json, secure_user=None, **kwargs):

    result = None
    try:
        result = requests.post(url, headers=_updated_headers(url, Worker.headers, secure_user),
                               stream=True, json=json, **kwargs)
        result.raise_for_status()
        result = Worker.handle_response(result)
    except requests.exceptions.RequestException as e:
        raise APIException(f"Request failed due to API exception, response code {result and result.status_code}")
    return result


def urlopen(url):
    request = urllib.request.Request(url, headers=_updated_headers(url))
    return urllib.request.urlopen(request)
