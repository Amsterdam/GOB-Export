import requests
import pytest


next = None


class MockResponse:

    def __init__(self, ok, results):
        self.ok = ok
        self.results = results
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
    return lambda url: MockResponse(ok, results)


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
