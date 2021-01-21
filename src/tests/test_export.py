import pytest
import tempfile
import os

from unittest import mock, TestCase
from unittest.mock import call, mock_open, patch

from gobcore.exceptions import GOBException

from gobexport.exporter.csv import csv_exporter
from gobexport.export import (
    cleanup_datefiles,
    get_cleanup_pattern,
    export,
    _export_collection,
    _append_to_file
)


def fail(msg):
    raise Exception(msg)


class TestExport(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_append_to_file(self):
        file1 = tempfile.mkstemp()[1]
        file2 = tempfile.mkstemp()[1]

        with open(file1, 'w') as f1, open(file2, 'w') as f2:
            f1.write('A')
            f2.write('B')

        _append_to_file(file1, file2)

        with open(file2, 'r') as f:
            self.assertEqual('BA', f.read())

        os.remove(file1)
        os.remove(file2)

    @patch('gobexport.export.logger', mock.MagicMock())
    @patch('gobexport.export.time.sleep', lambda n: None)
    @patch('gobexport.export.export_to_file')
    def test_export_exception(self, mock_export_to_file):
        mock_export_to_file.side_effect = lambda *args: fail("Export failed")
        result = _export_collection("host", "meetbouten", "meetbouten", None, "Objectstore")
        self.assertEqual(result, None)
        self.assertEqual(mock_export_to_file.call_count, 3)

    @patch('gobexport.export.logger', mock.MagicMock())
    @patch('gobexport.export.time.sleep', lambda n: None)
    @patch('gobexport.export.export_to_file')
    @patch('gobexport.export.distribute_to_objectstore')
    @patch("builtins.open", mock_open())
    def test_export_objectstore_exception(self, mock_distribute, mock_export_to_file):
        mock_export_to_file.side_effect = lambda *args, **kwargs: True
        mock_distribute.side_effect = GOBException
        result = _export_collection("host", "meetbouten", "meetbouten", None, "Objectstore")
        self.assertEqual(result, False)

    @patch('gobexport.export.logger', mock.MagicMock())
    @patch('gobexport.export.time.sleep', lambda n: None)
    @mock.patch('builtins.open', mock_open())
    @mock.patch('gobexport.export.os.remove', lambda f: None)
    @patch('gobexport.export.distribute_to_objectstore')
    @patch('gobexport.export.export_to_file')
    def test_export_objectstore_all_products(self, mock_export_to_file, mock_distribute):
        mock_export_to_file.side_effect = lambda *args, **kwargs: True
        # All products (6 files) should be exported
        result = _export_collection("host", "gebieden", "stadsdelen", None, "Objectstore")
        self.assertEqual(result, None)
        mock_distribute.assert_called()
        self.assertEqual(mock_distribute.call_count, 6)

    @patch('gobexport.export.logger', mock.MagicMock())
    @patch('gobexport.export.time.sleep', lambda n: None)
    @mock.patch('builtins.open', mock_open())
    @mock.patch('gobexport.export.os.remove', lambda f: None)
    @patch('gobexport.export.distribute_to_objectstore')
    @patch('gobexport.export.export_to_file')
    @patch('gobexport.export.cleanup_datefiles')
    def test_export_objectstore_one_product(self, mock_clean, mock_export_to_file, mock_distribute):
        mock_export_to_file.side_effect = lambda *args, **kwargs: True
        # Only csv_actueel should be exported
        result = _export_collection("host", "gebieden", "stadsdelen", "csv_actueel", "Objectstore")
        self.assertEqual(result, None)
        mock_distribute.assert_called()
        self.assertEqual(mock_distribute.call_count, 1)
        mock_clean.assert_called()

    @patch('gobexport.export.logger', mock.MagicMock())
    @patch('gobexport.export.time.sleep', lambda n: None)
    @mock.patch('builtins.open', mock_open())
    @mock.patch('gobexport.export.os.remove', lambda f: None)
    @patch('gobexport.export.distribute_to_objectstore')
    @patch('gobexport.export.export_to_file')
    @patch('gobexport.export.cleanup_datefiles')
    def test_export_objectstore_one_product(self, mock_clean, mock_export_to_file, mock_distribute):
        mock_export_to_file.side_effect = lambda *args, **kwargs: True
        # Only csv_actueel should be exported
        result = _export_collection("host", "gebieden", "stadsdelen", "not exists", "Objectstore")
        self.assertEqual(result, None)
        mock_distribute.assert_not_called()
        mock_clean.assert_not_called()

    @patch('gobexport.export.logger', mock.MagicMock())
    @patch('gobexport.export.time.sleep', lambda n: None)
    @mock.patch('builtins.open', mock_open())
    @mock.patch('gobexport.export.os.remove', lambda f: None)
    @patch('gobexport.export.distribute_to_objectstore')
    @patch('gobexport.export._get_filename', lambda x: '/tmpfile/' + x)
    @patch('gobexport.export.export_to_file')
    @patch('gobexport.export.cleanup_datefiles')
    @patch('gobexport.export._append_to_file')
    def test_export_collection_append(self, mock_append, mock_clean, mock_export_to_file, mock_distribute):
        products = {
            'prod1': {
                'api_type': 'graphql_streaming',
                'exporter': csv_exporter,
                'query': 'q1',
                'filename': 'the/filename.csv',
                'mime_type': 'mime/type'
            },
            'prod2': {
                'api_type': 'graphql_streaming',
                'exporter': csv_exporter,
                'query': 'q1',
                'append': True,
                'filename': 'the/filename.csv',
                'mime_type': 'mime/type'
            }
        }

        config_object = type('Config', (), {
            'products': products
        })
        config = {
            'cat': {
                'coll': config_object
            }
        }
        mock_export_to_file.side_effect = lambda *args, **kwargs: True

        with patch("gobexport.export.CONFIG_MAPPING", config):
            result = _export_collection("host", "cat", "coll", None, "File")

        mock_export_to_file.assert_has_calls([
            call('host', products['prod1'], 'the/filename.csv', 'cat', 'coll', buffer_items=True),
            call('host', products['prod2'], '/tmpfile/the/filename.csv.to_append', 'cat', 'coll', buffer_items=True)
        ])

        mock_append.assert_called_with('/tmpfile/the/filename.csv.to_append', 'the/filename.csv')

        # Objectstore, uses two tmp files
        mock_export_to_file.reset_mock()
        with patch("gobexport.export.CONFIG_MAPPING", config):
            result = _export_collection("host", "cat", "coll", None, "Objectstore")

        mock_export_to_file.assert_has_calls([
            call('host', products['prod1'], '/tmpfile/the/filename.csv', 'cat', 'coll', buffer_items=True),
            call('host', products['prod2'], '/tmpfile/the/filename.csv.to_append', 'cat', 'coll', buffer_items=True)
        ])

        mock_append.assert_called_with('/tmpfile/the/filename.csv.to_append', '/tmpfile/the/filename.csv')

    @patch('gobexport.export.logger', mock.MagicMock())
    @patch('gobexport.export.time.sleep', lambda n: None)
    @patch('gobexport.export.export_to_file', mock.MagicMock())
    @patch('gobexport.export.get_datastore_config')
    def test_export_file(self, mock_get_datastore_config):
        result = _export_collection("host", "meetbouten", "meetbouten", None, "File")
        self.assertEqual(result, None)
        mock_get_datastore_config.assert_not_called()

    @patch('gobexport.export.logger', mock.MagicMock())
    @patch('gobexport.export.time.sleep', lambda n: None)
    @patch('gobexport.export._export_collection')
    @patch('gobexport.export.get_host')
    def test_export(self, mock_host, mock_export_collection):
        result = export("catalogue", "collection", "product", "File")
        self.assertEqual(result, None)
        mock_export_collection.assert_called_with(
            host=mock_host.return_value,
            catalogue='catalogue',
            collection='collection',
            product_name='product',
            destination='File',
        )

    @patch('gobexport.export.logger', mock.MagicMock())
    @patch('gobexport.export.get_full_container_list')
    @patch('gobexport.export.delete_object')
    def test_cleanup_datefiles(self, mock_delete, mock_list):
        connection = 'any connection'
        container = 'any container'

        mock_list.return_value = []
        cleanup_datefiles(connection, container, 'any filename')
        mock_list.assert_not_called()
        mock_delete.assert_not_called()

        mock_list.return_value = ['f1', 'f2']
        cleanup_datefiles(connection, container, 'any filename')
        mock_list.assert_not_called()
        mock_delete.assert_not_called()

        mock_list.return_value = [{'name': '..f20201231..'}]
        cleanup_datefiles(connection, container, '..f20201231..')

        mock_list.assert_called_with(connection, container)
        mock_delete.assert_not_called()

        mock_list.return_value = [
            {'name': name} for name in ['..f20201229..', '..f20201230..', '..f20201231..']
        ]

        cleanup_datefiles(connection, container, '..f20201231..')
        mock_list.assert_called_with(connection, container)

        calls = [call(connection, container, {'name': name}) for name in ['..f20201229..', '..f20201230..']]
        mock_delete.assert_has_calls(calls)

        # cleanup_datefiles should not raise
        mock_list.side_effect = Exception
        mock_delete.side_effect = Exception
        cleanup_datefiles(connection, container, 'any filename')


@pytest.mark.parametrize(
    "filename, expected",
    [
        ("ABC_xyz.txt", "ABC_xyz.txt"),
        ("ABC_20181231.txt", "ABC_\\d{8}.txt"),
        ("ABC_20181231_N_20181231_20181231.txt", "ABC_\\d{8}_N_\\d{8}_\\d{8}.txt"),
        ("ABC_12345678_N_12345678_12345678.txt", "ABC_\\d{8}_N_\\d{8}_\\d{8}.txt"),
        ("ABC2018123120181231_20181231.txt", "ABC\\d{8}\\d{8}_\\d{8}.txt"),
    ],
)
def test_get_cleanup_pattern(filename, expected):
    assert get_cleanup_pattern(filename) == expected
