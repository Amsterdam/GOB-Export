from unittest import mock, TestCase
from unittest.mock import mock_open, patch

from gobexport.export import export, _export_collection

class TestExport(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @patch('gobexport.export.logger', mock.MagicMock())
    @patch('gobexport.export._with_retries', lambda m: 1/0)
    def test_export_exception(self):
        result = _export_collection("host", "meetbouten", "meetbouten", "Objectstore")
        self.assertEqual(result, None)

    @patch('gobexport.export.logger', mock.MagicMock())
    @patch('gobexport.export._with_retries', lambda m: m)
    @patch("builtins.open", mock_open())
    def test_export_objectstore_exception(self):
        result = _export_collection("host", "meetbouten", "meetbouten", "Objectstore")
        self.assertEqual(result, False)

    @patch('gobexport.export.logger', mock.MagicMock())
    @patch('gobexport.export._with_retries', lambda m: m)
    @patch('gobexport.export.distribute_to_objectstore', mock.MagicMock())
    @mock.patch('builtins.open', mock_open())
    @mock.patch('gobexport.export.os.remove', lambda f: None)
    def test_export_objectstore(self):
        result = _export_collection("host", "meetbouten", "meetbouten", "Objectstore")
        self.assertEqual(result, None)

    @patch('gobexport.export.logger', mock.MagicMock())
    @patch('gobexport.export._with_retries', lambda m: m)
    def test_export_file(self):
        result = _export_collection("host", "meetbouten", "meetbouten", "File")
        self.assertEqual(result, None)

    @patch('gobexport.export.logger', mock.MagicMock())
    @patch('gobexport.export._with_retries', lambda m: m)
    def test_export(self):
        result = export("meetbouten", "meetbouten", "File")
        self.assertEqual(result, None)