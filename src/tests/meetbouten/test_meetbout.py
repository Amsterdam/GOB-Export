import os
import importlib

import export.api


def before_each(monkeypatch):
    import export.meetbouten.meetbout
    importlib.reload(export.meetbouten.meetbout)


def test_export_meetbout(monkeypatch):
    before_each(monkeypatch)
    from export.meetbouten.meetbout import _export_meetbout

    meetbout = {}
    assert(_export_meetbout(meetbout) == "$$$$|$$$$|||||$$$$|||$$N$$|$$$$|$$$$|$$$$||$$$$|$$$$||")

    meetbout = {
        'meetboutid': '1'
    }
    assert(_export_meetbout(meetbout) == "$$1$$|$$$$|||||$$$$|||$$N$$|$$$$|$$$$|$$$$||$$$$|$$$$||")

    meetbout = {
        'meetboutid': '1',
        'x': 'y'
    }
    assert(_export_meetbout(meetbout) == "$$1$$|$$$$|||||$$$$|||$$N$$|$$$$|$$$$|$$$$||$$$$|$$$$||")


class MockAPI:
    def __init__(self, host=None, path=None):
        pass

    def __iter__(self):
        for e in [{'meetboutid': '1'}]:
            yield e


class MockFile:
    s = ''

    def __iter__(self, file, mode):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def write(self, s):
        MockFile.s = s


def mock_open(file, mode):
    return MockFile()


def test_export_meetbouten(monkeypatch):
    monkeypatch.setitem(__builtins__, 'open', mock_open)
    monkeypatch.setattr(export.api, 'API', MockAPI)

    before_each(monkeypatch)
    from export.meetbouten.meetbout import export_meetbouten

    export_meetbouten('host', '/tmp/ttt')
    assert(MockFile.s == '$$1$$|$$$$|||||$$$$|||$$N$$|$$$$|$$$$|$$$$||$$$$|$$$$||\n')
