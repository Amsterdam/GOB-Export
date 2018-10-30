import importlib
import os
import pytest
import time

import export
import export.config
import export.meetbouten
import export.connector.objectstore

class MockArgs:

    def __init__(self, catalog, collection, file_name):
        self.catalog = catalog
        self.collection = collection
        self.file_name = file_name


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


class MockConnection:

    def put_object(container, object_name, contents, content_type):
        pass


def mock_connection(config):
    return MockConnection


host = None
file_name = None


def export_entity(c, h, f):
    global host, file_name
    host = h
    file_name = f


def mock_sleep(t):
    export.__main__.keep_alive = False


def test_main(monkeypatch):
    monkeypatch.setitem(__builtins__, 'open', mock_open)
    monkeypatch.setattr(export.config, 'get_host', lambda: 'host')
    monkeypatch.setattr(export.config, 'get_args', lambda: MockArgs('meetbouten', 'meetbouten', 'file_name'))
    monkeypatch.setattr(export.meetbouten, 'export_meetbouten', export_entity)
    monkeypatch.setattr(export.connector.objectstore, 'get_connection', mock_connection)
    monkeypatch.setattr(os, 'remove', lambda file: True)

    from export import __main__

    temporary_file = __main__._get_filename(file_name)
    assert(host == 'host')
    assert(file_name == temporary_file)

    monkeypatch.setattr(export.config, 'get_args', lambda: MockArgs('unknown', 'unknown', 'file_name'))

    with pytest.raises(KeyError):
        importlib.reload(export.__main__)

def test_main_without_args(monkeypatch):
    monkeypatch.setattr(export.config, 'get_host', lambda: 'host')
    monkeypatch.setattr(export.config, 'get_args', lambda: MockArgs(None, None, None))
    monkeypatch.setattr(time, 'sleep', mock_sleep)

    importlib.reload(export.__main__)

    from export import __main__
