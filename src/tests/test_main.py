import importlib
import pytest

import export.config
import export.meetbouten


class MockArgs:

    def __init__(self, catalog, collection, file):
        self.catalog = catalog
        self.collection = collection
        self.file = file


host = None
file = None


def export_entity(c, h, f):
    global host, file
    host = h
    file = f


def test_main(monkeypatch):
    monkeypatch.setattr(export.config, 'get_host', lambda: 'host')
    monkeypatch.setattr(export.config, 'get_args', lambda: MockArgs('meetbouten', 'meetbouten', 'file'))
    monkeypatch.setattr(export.meetbouten, 'export_meetbouten', export_entity)

    from export import __main__
    assert(host == 'host')
    assert(file == 'file')

    monkeypatch.setattr(export.config, 'get_args', lambda: MockArgs('unknow', 'unknown', 'file'))

    with pytest.raises(KeyError):
        importlib.reload(export.__main__)
