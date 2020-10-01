import unittest
from unittest import mock


class TestWsgi(unittest.TestCase):

    @mock.patch('gobexport.app.get_app')
    def test_wsgi(self, mock_get_app):
        import gobexport.wsgi
        mock_get_app.assert_called()
