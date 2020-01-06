import requests
import pytest

from unittest import TestCase
from unittest.mock import patch

from gobexport.api import API


next = None


class MockResponse:

    def __init__(self, ok, results):
        self.ok = ok
        self.results = results
        pass

    def raise_for_status(self):
        pass

    def json(self):
        global next

        result = {
            '_links': {
                'next': {
                    'href': next
                }
            },
            'results': self.results
        }
        if next:
            next = None
        return result


def mock_get(ok=True, results=[]):
    return lambda url, headers, timeout: MockResponse(ok, results)


def test_api(monkeypatch):
    monkeypatch.setattr(requests, 'get', mock_get())

    from gobexport.api import API

    api = API('host', 'path')
    for e in api:
        assert(e is not None)

    monkeypatch.setattr(requests, 'get', mock_get(ok=False))
    with pytest.raises(AssertionError):
        api = API('host', 'path')
        for e in api:
            assert(e is not None)

    monkeypatch.setattr(requests, 'get', mock_get(ok=True, results=[1, 2, 3]))
    api = API('host', 'path')
    cnt = 0
    for e in api:
        cnt += 1
    assert(cnt == 3)

    global next
    next = 'has next'
    api = API('host', 'path')
    cnt = 0
    for e in api:
        cnt += 1
    assert(cnt == 6)

    assert(str(api) == 'API hostNone')

class TestStream(TestCase):

    @patch('gobexport.api.requests')
    def test_ndjson_api(self, mock_requests):
        mock_requests.get_stream.return_value = ['1', '2', '3']
        api = API('host', 'path ndjson=true')
        result = [i for i in api]
        self.assertEqual(result, [1, 2, 3])
        self.assertEqual(5, api.format_item(5))

    @patch('gobexport.api.ijson')
    @patch('gobexport.api.requests')
    def test_streaming_api(self, mock_requests, mock_ijson):
        mock_requests.urlopen.return_value = None
        mock_ijson.items.return_value = [1, 2, 3]
        api = API('host', 'path stream=true')
        result = [i for i in api]
        self.assertEqual(result, [1, 2, 3])
        self.assertEqual(5, api.format_item(5))

    @patch('gobexport.api.ijson')
    @patch('gobexport.api.requests')
    def test_format_item_with_row_formatter(self, mock_requests, mock_ijson):
        mock_requests.urlopen.return_value = None
        row_formatter = lambda x: x*2

        mock_requests.get_stream.return_value = ['1', '2', '3']
        api = API('host', 'path ndjson=true', row_formatter=row_formatter)
        result = [i for i in api]
        self.assertEqual(result, [2, 4, 6])

        mock_ijson.items.return_value = [1, 2, 3]
        api = API('host', 'path stream=true', row_formatter=row_formatter)
        result = [i for i in api]
        self.assertEqual(result, [2, 4, 6])

        self.assertEqual(10, api.format_item(5))
