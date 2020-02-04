from unittest import TestCase, mock

from gobexport.worker import Worker

@mock.patch("gobexport.worker.get_host", lambda : 'host')
class TestWorker(TestCase):

    @mock.patch("gobexport.worker.requests")
    def test_handle_response(self, mock_request):
        mock_result = mock.MagicMock()
        mock_result.iter_lines.return_value = [b'1', b'2', b'OK']

        mock_worker_result = mock.MagicMock()
        mock_request.get.return_value = mock_worker_result
        mock_worker_result.iter_lines.return_value = ['line1', 'line2']

        result = [line for line in Worker.handle_response(mock_result)]
        self.assertEqual(result, ['line1', 'line2'])
        mock_request.delete.assert_called()
        mock_request.delete.reset_mock()

        mock_request.get.side_effect = mock.Mock(side_effect=Exception('Test'))
        with self.assertRaises(Exception):
            result = [line for line in Worker.handle_response(mock_result)]
        mock_request.delete.assert_called()
        mock_request.delete.reset_mock()

        mock_result.iter_lines.return_value = [b'1', b'2', b'FAILURE']
        with self.assertRaises(Exception):
            result = [line for line in Worker.handle_response(mock_result)]
        mock_request.delete.assert_not_called()

        mock_result.iter_lines.return_value = [b'1', b'2']
        with self.assertRaises(Exception):
            result = [line for line in Worker.handle_response(mock_result)]
        mock_request.delete.assert_not_called()
