import pytest

import swiftclient

from gobcore.exceptions import GOBException

import gobexport.distributor.objectstore
from gobexport.distributor.objectstore import distribute_to_objectstore


def mock_put_object(connection, container, object_name, contents, content_type):
    if connection == None:
        raise swiftclient.exceptions.ClientException('Error')
    else:
        return True

def test_distribute_to_objectstore(monkeypatch):
    monkeypatch.setattr(gobexport.distributor.objectstore, 'put_object', mock_put_object)

    distribute_to_objectstore('connection', 'container', 'object_name', 'contents', 'content_type')

    # Assert an exception is raised if no connection is provided
    with pytest.raises(GOBException):
        distribute_to_objectstore(None, 'container', 'object_name', 'contents', 'content_type')
