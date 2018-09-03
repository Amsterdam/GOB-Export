import importlib
import pytest

import export.config
import export.meetbouten.meetbout


class MockArgs:

    def __init__(self, collection, file):
        self.collection = collection
        self.file = file


host = None
file = None


def export_entity(h, f):
    global host, file
    host = h
    file = f


def test_main(monkeypatch):
    monkeypatch.setattr(export.config, 'get_host', lambda: 'host')
    monkeypatch.setattr(export.config, 'get_args', lambda: MockArgs('meetbouten', 'file'))
    monkeypatch.setattr(export.meetbouten.meetbout, 'export_meetbouten', export_entity)

    from export import __main__
    assert(host == 'host')
    assert(file == 'file')

    monkeypatch.setattr(export.config, 'get_args', lambda: MockArgs('unknown', 'file'))

    with pytest.raises(KeyError):
        importlib.reload(export.__main__)
