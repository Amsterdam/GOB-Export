from unittest import TestCase, mock

from gobexport.exporter.ndjson import ndjson_exporter


class TestNDJSONExporter(TestCase):

    def test_append_raises_notimplementederror(self):

        with self.assertRaises(NotImplementedError):
            ndjson_exporter([], '', append=True)

    def test_write(self):
        mock_api = [{}, {"a": 1}]
        with mock.patch("builtins.open", mock.mock_open()) as mock_file:
            ndjson_exporter(mock_api, "any file")
            mock_file.assert_called_with("any file", 'w')
            handle = mock_file()
            handle.write.assert_any_call('{}\n')
            handle.write.assert_any_call('{"a": 1}\n')
            self.assertEqual(mock_file.call_count, 2)
