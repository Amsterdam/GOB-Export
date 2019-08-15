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


class MockGet:
    pass


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

    @patch("gobexport.requests.requests")
    def test_stream(self, mock_requests):

        mock_get = MockGet()
        mock_get.iter_lines = MagicMock()

        mock_requests.get.return_value = mock_get

        result = gobexport.requests.get_stream('any url')
        mock_get.iter_lines.assert_called()

    @patch("gobexport.requests.requests")
    def test_post(self, mock_requests):
        result = gobexport.requests.post_stream('url', 'some json')
        mock_requests.post.assert_called_with('url', stream=True, json='some json')
        self.assertEqual(mock_requests.post.return_value.iter_lines.return_value, result)

    @patch("gobexport.requests.requests")
    def test_post_stream_params(self, mock_requests):
        kwargs = {'abc': 'def', 'ghi': 'jkl'}
        result = gobexport.requests.post_stream('url', 'some json', **kwargs)
        mock_requests.post.assert_called_with('url', stream=True, json='some json', **kwargs)

    @patch('gobexport.requests.urllib.request.urlopen')
    def test_urlopen(self, mock_open):
        result = gobexport.requests.urlopen('any url')
        mock_open.assert_called_with('any url')
