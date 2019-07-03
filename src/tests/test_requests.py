from unittest import TestCase, mock
from unittest.mock import MagicMock, patch

import pytest

from requests.exceptions import RequestException
import gobexport.requests


class MockResponse:

    def __init__(self, exc):
        self.exc = exc

    def raise_for_status(self):
        raise self.exc("Any reason")


class TestRequests(TestCase):

    def setUp(self):
        pass

    @patch("gobexport.requests.requests")
    @patch("gobexport.requests.time", MagicMock())
    def test_get(self, mock_requests):
        mock_requests.exceptions.RequestException = RequestException
        mock_requests.get.return_value = MockResponse(RequestException)
        mock_requests.post.return_value = MockResponse(RequestException)

        gobexport.requests._MAX_TRIES = 10
        gobexport.requests._RETRY_TIMEOUT = 0
        with pytest.raises(gobexport.requests.APIException):
            gobexport.requests.get("any url")
        self.assertEqual(mock_requests.get.call_count, 10)

        with pytest.raises(gobexport.requests.APIException):
            gobexport.requests.post("any url", "any json")
        self.assertEqual(mock_requests.post.call_count, 10)
