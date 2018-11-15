import os
import importlib

import gobexport.api

from gobexport.exporter import CONFIG_MAPPING


def before_each(monkeypatch):
    import gobexport.exporter
    importlib.reload(gobexport.exporter)


def test_export_entity(monkeypatch):
    before_each(monkeypatch)
    from gobexport.exporter import _export_entity

    meetbout = {}
    config = CONFIG_MAPPING['meetbouten']['meetbouten']
    assert(_export_entity(meetbout, config.format) == "|||||||||||||||||")

    meetbout = {
        'identificatie': '1'
    }
    assert(_export_entity(meetbout, config.format) == "$$1$$|||||||||||||||||")

    meetbout = {
        'identificatie': '1',
        'x': 'y'
    }
    assert(_export_entity(meetbout, config.format) == "$$1$$|||||||||||||||||")


class MockAPI:
    def __init__(self, host=None, path=None):
        pass

    def __iter__(self):
        for e in [{'identificatie': '1'}]:
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


def test_export_to_file(monkeypatch):
    monkeypatch.setitem(__builtins__, 'open', mock_open)
    monkeypatch.setattr(gobexport.api, 'API', MockAPI)

    before_each(monkeypatch)
    from gobexport.exporter import export_to_file

    export_to_file('meetbouten', 'meetbouten', 'host', '/tmp/ttt')
    assert(MockFile.s == '$$1$$|||||||||||||||||\n')
