import importlib
import os
import pytest
import tempfile
import time

import swiftclient

from unittest import mock

from gobcore.exceptions import GOBException

import gobexport
import gobexport.config
import gobexport.exporter
import gobexport.connector.objectstore


class MockLogger:

    def __init__(self):
        pass

    def info(self, *args, **kwargs):
        pass

    def error(self, *args, **kwargs):
        pass


def mock_get_logger(name):
    return MockLogger()


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

    def put_object(container, object_name, contents, content_type, proxy=None):
        if object_name == None:
            raise swiftclient.exceptions.ClientException()
        else:
            return None

    def _retry(*args):
        return None


def mock_connection(config):
    return MockConnection


def mock_put_object(connection, container, object_name, contents, content_type, proxy=None):
    if connection == None:
        raise GOBException('Error')
    else:
        return True


host = None
file_name = None


def export_entity(h, en, ex, f, fo):
    global host, file_name
    host = h
    file_name = f


def mock_sleep(t):
    gobexport.export.keep_alive = False


def test_export(monkeypatch):
    monkeypatch.setitem(__builtins__, 'open', mock_open)
    monkeypatch.setattr(gobexport.config, 'get_host', lambda: 'host')
    monkeypatch.setattr(gobexport.exporter, 'export_to_file', export_entity)
    monkeypatch.setattr(gobexport.connector.objectstore, 'get_connection', mock_connection)
    monkeypatch.setattr(os, 'remove', lambda file: True)

    from gobexport import export
    export.logger = mock.MagicMock()
    export.logger.info = mock.MagicMock()

    temporary_file = export._get_filename("test")
    tmp_dir = tempfile.gettempdir()
    assert(temporary_file == f"{tmp_dir}/test")

    # export.export("meetbouten", "meetbouten", "Objectstore")
    # export._export_collection("host", "meetbouten", "meetbouten", "Objectstore")
    #
    # export._export_collection("host", "meetbouten", "meetbouten", "File")


def test_export_without_connection(monkeypatch):
    monkeypatch.setitem(__builtins__, 'open', mock_open)
    monkeypatch.setattr(gobexport.config, 'get_host', lambda: 'host')
    monkeypatch.setattr(gobexport.exporter, 'export_to_file', export_entity)
    monkeypatch.setattr(gobexport.connector.objectstore, 'get_connection', lambda config: None)
    monkeypatch.setattr(gobexport.distributor.objectstore, 'put_object', mock_put_object)
    monkeypatch.setattr(os, 'remove', lambda file: True)

    importlib.reload(gobexport.export)

    from gobexport import export
    export.logger = mock.MagicMock()
    export.logger.info = mock.MagicMock()

    export.export("meetbouten", "meetbouten", "Objectstore")
    export._export_collection("host", "meetbouten", "meetbouten", "Objectstore")
