import pytest
import swiftclient
from unittest.mock import call, patch, MagicMock

from gobcore.exceptions import GOBException
import gobexport.distributor.objectstore
from gobexport.distributor.objectstore import (
    cleanup_objectstore,
    distribute_to_objectstore,
)


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


def mock_put_object(connection, container, object_name, contents, content_type, proxy=None):
    if connection == None:
        raise swiftclient.exceptions.ClientException('Error')
    else:
        return True


def mock_get_full_container_list(connection, container):
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


@pytest.mark.parametrize(
    "catalogue, cleanup_mask, object_name, get_full_container_list_called, objects, deleted_objects",
    [
        # good match. delete objects.
        ("a", "b/c*.txt", "a/b/c1.txt", True,
        [{"name": "a/b/c1.txt"}, {"name": "a/b/c2.txt"}, {"name": "a/b/c3.txt"}],
        [{"name": "a/b/c2.txt"}, {"name": "a/b/c3.txt"}]),

        # good match. delete one object.
        ("a", "b/c2.txt", "a/b/c1.txt", True,
        [{"name": "a/b/c1.txt"}, {"name": "a/b/c2.txt"}, {"name": "a/b/c3.txt"}],
        [{"name": "a/b/c2.txt"}]),

        # object_name is the same as cleanup_mask. preservation has priority. no deletion.
        ("a", "b/c1.txt", "b/c1.txt", True,
        [{"name": "a/b/c1.txt"}, {"name": "a/b/c2.txt"}, {"name": "a/b/c3.txt"}],
        []),

        # good match. no object to preserve. delete objects.
        ("a", "b/c*.txt", None, True,
        [{"name": "a/b/c1.txt"}, {"name": "a/b/c2.txt"}, {"name": "a/b/c3.txt"}],
        [{"name": "a/b/c1.txt"}, {"name": "a/b/c2.txt"}, {"name": "a/b/c3.txt"}],),

        # no match. nothing to delete.
        ("a", "d*.txt", "a/b/c1.txt", True,
        [{"name": "a/b/c1.txt"}, {"name": "a/b/c2.txt"}, {"name": "a/b/c3.txt"}],
        []),

        # no objects. nothing to delete.
        ("a", "b/c*.txt", "a/b/c1.txt", True,
        [],
        []),

        # no objects. no object to preserve. nothing to delete.
        ("a", "b/c*.txt", None, True,
        [],
        []),

        # no cleanup_mask. do nothing.
        ("a", None, "a/b/c1.txt", False,
        [{"name": "a/b/c1.txt"}, {"name": "a/b/c2.txt"}, {"name": "a/b/c3.txt"}],
        []),

        # no cleanup_mask. do nothing.
        ("a", "", "a/b/c1.txt", False,
        [{"name": "a/b/c1.txt"}, {"name": "a/b/c2.txt"}, {"name": "a/b/c3.txt"}],
        []),
    ],
)
@patch("gobexport.distributor.objectstore.get_full_container_list")
@patch("gobexport.distributor.objectstore.delete_object")
@patch('gobexport.distributor.objectstore.logger', MagicMock())
def test_cleanup_objectstore(mock_delete_object, mock_get_full_container_list,
                             catalogue, cleanup_mask, object_name,
                             get_full_container_list_called, objects, deleted_objects):
    connection = "the connection"
    container = "XYZ"
    mock_get_full_container_list.return_value = objects

    cleanup_objectstore(connection, container, catalogue, cleanup_mask, object_name)

    if get_full_container_list_called:
        mock_get_full_container_list.assert_called_with(connection, container)

    if deleted_objects:
        calls = [call(connection, container, file) for file in deleted_objects]
        mock_delete_object.assert_has_calls(calls)
    else:
        mock_delete_object.assert_not_called()


def test_cleanup_objectstore_failed(monkeypatch):
    monkeypatch.setattr(gobexport.distributor.objectstore, 'get_full_container_list', mock_get_full_container_list)

    # Assert an exception is raised if no connection is provided
    with pytest.raises(GOBException):
        cleanup_objectstore(None, "XYZ", "a", "b/c*.txt", "a/b/c1.txt")
