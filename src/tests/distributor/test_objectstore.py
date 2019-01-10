import pytest

import swiftclient

from gobcore.exceptions import GOBException

import gobexport.distributor.objectstore
from gobexport.distributor.objectstore import distribute_to_objectstore


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


def mock_put_object(connection, container, object_name, contents, content_type):
    if connection == None:
        raise swiftclient.exceptions.ClientException('Error')
    else:
        return True

def test_distribute_to_objectstore(monkeypatch):
    monkeypatch.setitem(__builtins__, 'open', mock_open)
    monkeypatch.setattr(gobexport.distributor.objectstore, 'put_object', mock_put_object)

    distribute_to_objectstore('connection', 'container', 'object_name', 'contents', 'content_type')

    # Assert an exception is raised if no connection is provided
    with pytest.raises(GOBException):
        distribute_to_objectstore(None, 'container', 'object_name', 'contents', 'content_type')
