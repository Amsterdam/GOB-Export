import pytest
from unittest import mock, TestCase
from unittest.mock import call, mock_open, patch

from gobcore.exceptions import GOBException

from gobexport.export import (
    cleanup_datefiles,
    get_cleanup_pattern,
    export,
    _export_collection,
)

def fail(msg):
    raise Exception(msg)


class TestExport(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

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
        self.assertEqual(mock_distribute.call_count, 8)

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
    @patch('gobexport.export.export_to_file', mock.MagicMock())
    @patch('gobexport.export.connect_to_objectstore')
    def test_export_file(self, mock_connect_to_objectstore):
        result = _export_collection("host", "meetbouten", "meetbouten", None, "File")
        self.assertEqual(result, None)
        mock_connect_to_objectstore.assert_not_called()

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

        mock_list.return_value = [{'name': name}
            for name in ['..f20201229..', '..f20201230..', '..f20201231..']]
        cleanup_datefiles(connection, container, '..f20201231..')
        mock_list.assert_called_with(connection, container)
        calls = [call(connection, container, {'name': name})
            for name in ['..f20201229..', '..f20201230..']]
        mock_delete.assert_has_calls(calls)


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
