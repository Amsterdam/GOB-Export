from flask import Flask
from flask_cors import CORS


def _health():
    """

    :return: Message telling the API is OK
    """
    return 'Connectivity OK'


def get_flask_app():
    """
    Initializes the Flask App

    :return: Flask App
    """

    ROUTES = [
        # Health check URL
        ('/status/health/', _health, ['GET']),
    ]

    app = Flask(__name__)
    CORS(app)

    for route, view_func, methods in ROUTES:
        app.route(rule=route, methods=methods)(view_func)

    return app
