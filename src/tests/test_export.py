from unittest import mock, TestCase
from unittest.mock import mock_open, patch

from gobcore.exceptions import GOBException

from gobexport.export import export, _export_collection

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
    def test_export_objectstore(self, mock_export_to_file, mock_distribute):
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
    def test_export_objectstore(self, mock_export_to_file, mock_distribute):
        mock_export_to_file.side_effect = lambda *args, **kwargs: True
        # Only csv_actueel should be exported
        result = _export_collection("host", "gebieden", "stadsdelen", "csv_actueel", "Objectstore")
        self.assertEqual(result, None)
        mock_distribute.assert_called()
        self.assertEqual(mock_distribute.call_count, 1)

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
    def test_export(self):
        result = export("meetbouten", "meetbouten", None, "File")
        self.assertEqual(result, None)
