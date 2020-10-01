from unittest import TestCase
from unittest.mock import patch, MagicMock

from gobexport.flask_api import get_flask_app, _health


class TestAPI(TestCase):

    def test_health(self):
        self.assertEqual('Connectivity OK', _health())

    @patch("gobexport.flask_api.CORS", MagicMock())
    @patch("gobexport.flask_api.Flask")
    def test_get_flask_app(self, mock_flask):
        mock_app = MagicMock()
        mock_flask.return_value = mock_app
        app = get_flask_app()
        mock_flask.assert_called()
        mock_app.route.assert_called()
