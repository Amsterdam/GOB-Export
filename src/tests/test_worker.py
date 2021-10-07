from unittest import mock

import pytest
import requests
import requests_mock

from gobexport.worker import Worker


class TestWorker:

    @mock.patch("gobexport.worker.get_host", lambda: 'host')
    @mock.patch("gobexport.worker.requests")
    def test_handle_response(self, mock_request, app):
        mock_result = mock.MagicMock()
        mock_result.iter_lines.return_value = [b'1', b'2', b'OK']

        mock_worker_result = mock.MagicMock()
        mock_request.get.return_value = mock_worker_result
        mock_worker_result.iter_lines.return_value = ['line1', 'line2']

        result = [line for line in Worker.handle_response(mock_result)]
        assert result == ['line1', 'line2']
        mock_request.delete.assert_called()
        mock_request.delete.reset_mock()

        mock_request.get.side_effect = mock.Mock(side_effect=Exception('Test'))
        with pytest.raises(Exception):
            result = [line for line in Worker.handle_response(mock_result)]

        mock_request.delete.assert_called()
        mock_request.delete.reset_mock()

        mock_result.iter_lines.return_value = [b'1', b'2', b'FAILURE']
        with pytest.raises(Exception):
            result = [line for line in Worker.handle_response(mock_result)]
        mock_request.delete.assert_not_called()

        mock_result.iter_lines.return_value = [b'1', b'2']
        with pytest.raises(Exception):
            result = [line for line in Worker.handle_response(mock_result)]
        mock_request.delete.assert_not_called()

    def test_handle_response_logs_request_id(self, app, caplog):
        """Make sure logging is correctly setup and adds the x-request-id."""
        with requests_mock.Mocker() as m:
            m.get(
                "mock://gobapi.nl",
                content=b"1\n2\nOK",
                headers={
                    Worker._WORKER_ID_RESPONSE: "test-id",
                    Worker._REQUEST_ID: "test-request-id"
                }
            )
            m.get("http://localhost:8141/gob/public/worker/test-id", content=b"")
            m.delete("http://localhost:8141/gob/public/worker/end/test-id", content=b"")
            response = requests.get("mock://gobapi.nl")
            list(Worker.handle_response(response))

        assert "test-request-id" in caplog.records[0].message
