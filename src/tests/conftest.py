from collections import Generator

import pytest
from flask import Flask

from gobexport.flask_api import get_flask_app


@pytest.fixture
def app() -> Generator[Flask, None, None]:
    """Creates a flask test app, with an app context.

    The app can be used to create a test http client as well:
    with app.test_client() as client:
        client.get(...)
    """
    app = get_flask_app({"TESTING": True})
    with app.app_context():
        yield app
