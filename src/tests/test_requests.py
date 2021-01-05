from unittest import TestCase, mock
from unittest.mock import MagicMock, patch

import pytest

from requests.exceptions import RequestException
import gobexport.requests


class MockResponse:

    def __init__(self, exc):
        self.exc = exc
        self.status_code = 'any status code'

    def raise_for_status(self):
        raise self.exc("Any reason")
    


class MockGet:
    status_code = 123

    def raise_for_status(self):
        pass


class TestRequests(TestCase):

    def setUp(self):
        pass

    @patch('gobexport.requests._updated_headers', lambda url, **kwargs: {})
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

    def test_handle_streaming_gob_response(self):
        correct_result = ['a', 'b', b'']

        f = gobexport.requests.handle_streaming_gob_response(lambda: iter(correct_result))
        result = list(f())
        self.assertEqual(correct_result[:-1], result)

        # No closing newline
        incorrect_result = ['a', 'b']
        f = gobexport.requests.handle_streaming_gob_response(lambda: iter(incorrect_result))

        with self.assertRaisesRegex(gobexport.requests.APIException, "Incomplete request received"):
            result = list(f())

    @patch('gobexport.requests._updated_headers', lambda *args, **kwargs: {})
    @patch("gobexport.requests.requests")
    @patch("gobexport.requests.Worker")
    def test_stream(self, mock_worker, mock_requests):

        mock_get = MockGet()
        mock_get.iter_lines = MagicMock(return_value=['some item', b''])
        mock_worker.handle_response = mock_get.iter_lines

        mock_requests.get.return_value = mock_get

        result = list(gobexport.requests.get_stream('any url'))
        mock_get.iter_lines.assert_called()
        self.assertEqual(mock_get.iter_lines.return_value[:-1], result)

    @patch('gobexport.requests._updated_headers', lambda *args, **kwargs: {})
    @patch("gobexport.requests.requests.get")
    def test_get_stream_exception(self, mock_requests_get):
        mock_get = MockGet()
        mock_get.raise_for_status = MagicMock(side_effect=RequestException)
        mock_requests_get.return_value = mock_get

        with self.assertRaisesRegexp(gobexport.requests.APIException, 'Request failed due to API exception'):
            list(gobexport.requests.get_stream('any url'))

    @patch('gobexport.requests._updated_headers', lambda *args, **kwargs: {'updated': 'headers'})
    @patch("gobexport.requests.requests")
    @patch("gobexport.requests.Worker")
    def test_post(self, mock_worker, mock_requests):
        mock_requests.post.return_value.iter_lines.return_value = ['something', b'']
        mock_worker.handle_response.return_value = ['something', b'']
        result = list(gobexport.requests.post_stream('url', 'some json'))
        mock_requests.post.assert_called_with('url', headers={'updated': 'headers'}, stream=True, json='some json')
        self.assertEqual(mock_requests.post.return_value.iter_lines.return_value[:-1], result)

    @patch('gobexport.requests._updated_headers', lambda *args, **kwargs: {'updated': 'headers'})
    @patch("gobexport.requests.requests")
    @patch("gobexport.requests.Worker")
    def test_post_stream_params(self, mock_worker, mock_requests):
        kwargs = {'abc': 'def', 'ghi': 'jkl'}
        mock_requests.post.return_value.iter_lines.return_value = ['one line', b'']
        mock_worker.handle_response.return_value = ['one line', b'']
        result = list(gobexport.requests.post_stream('url', 'some json', **kwargs))
        mock_requests.post.assert_called_with('url', headers={'updated': 'headers'}, stream=True, json='some json', **kwargs)
        self.assertEqual(result, ['one line'])

    @patch('gobexport.requests._updated_headers', lambda *args, **kwargs: {})
    @patch("gobexport.requests.requests.post")
    def test_post_stream_exception(self, mock_requests_post):
        mock_get = MockGet()
        mock_get.raise_for_status = MagicMock(side_effect=RequestException)
        mock_requests_post.return_value = mock_get

        with self.assertRaisesRegexp(gobexport.requests.APIException, 'Request failed due to API exception'):
            list(gobexport.requests.post_stream('any url', True))

    @patch('gobexport.requests._updated_headers', lambda *args, **kwargs: {})
    @patch('gobexport.requests.urllib.request.Request', lambda url, headers: url)
    @patch('gobexport.requests.urllib.request.urlopen')
    def test_urlopen(self, mock_open):
        result = gobexport.requests.urlopen('any url')
        mock_open.assert_called_with('any url')

    @patch('gobexport.requests.get_secure_header')
    def test_updated_headers(self, mock_secure_header):
        result = gobexport.requests._updated_headers(f"any {gobexport.requests._PUBLIC_URL} url", "any header")
        self.assertEqual(result, "any header")

        mock_secure_header.return_value = {'secure key': 'secure value'}
        url = f"some secured url"
        headers = {
            'some key': "some value",
            'secure key': "some obsolete value"
        }
        result = gobexport.requests._updated_headers(url, headers)
        self.assertEqual(result, {
            'some key': 'some value',
            'secure key': 'secure value'
        })
