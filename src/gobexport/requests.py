import requests

import time

_MAX_TRIES = 60          # Maximum number of times to try the request
_RETRY_TIMEOUT = 60     # Seconds between consecetive retries
_REQUEST_TIMEOUT = 300  # Request timout to 300 seconds to get a response


class APIException(IOError):
    pass


def _exec(method, **kwargs):
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
            response = method(**kwargs)
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


def get(url):
    return _exec(requests.get, url=url, timeout=_REQUEST_TIMEOUT)


def post(url, json):
    return _exec(requests.post, url=url, json=json, timeout=_REQUEST_TIMEOUT)
