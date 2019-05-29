from unittest import TestCase, mock
from unittest.mock import MagicMock, patch

import pytest

from requests import RequestException
import gobexport.requests


class TestRequests(TestCase):

    def setUp(self):
        pass

    @patch("gobexport.requests.requests")
    @patch("gobexport.requests.time", MagicMock())
    def test_get(self, mock_requests):
        mock_requests.RequestException = RequestException
        mock_requests.get.side_effect = RequestException("Any reason")
        mock_requests.post.side_effect = RequestException("Any reason")

        gobexport.requests._MAX_TRIES = 10
        gobexport.requests._RETRY_TIMEOUT = 0
        with pytest.raises(gobexport.requests.RequestException):
            gobexport.requests.get("any url")
        self.assertEqual(mock_requests.get.call_count, 10)

        with pytest.raises(gobexport.requests.RequestException):
            gobexport.requests.post("any url", "any json")
        self.assertEqual(mock_requests.post.call_count, 10)
