import importlib
import os

import unittest
from unittest import mock

from gobexport.config import _getenv, get_public_key

class MockArgumentParser:

    def __init__(self, description):
        MockArgumentParser.description = description
        MockArgumentParser.arguments = []
        pass

    def add_argument(self, collection, **kwargs):
        MockArgumentParser.arguments.append(collection)
        pass

    def parse_args(self):
        return MockArgumentParser.arguments

def before_each(monkeypatch):
    import argparse
    monkeypatch.setattr(argparse, 'ArgumentParser', MockArgumentParser)

    import gobexport
    importlib.reload(gobexport)


def test_host(monkeypatch):
    before_each(monkeypatch)
    from gobexport.config import get_host

    assert(get_host() == os.getenv('API_HOST', 'http://localhost:8141'))


class TestConfig(unittest.TestCase):

    @mock.patch("os.getenv")
    def test_getenv_notset(self, mock_getenv):
        mock_getenv.side_effect = lambda varname, value=None: value

        # Test for variable that is not set
        with self.assertRaises(AssertionError):
            _getenv("SOME UNKNOWN VARIABLE")

        # Test for optional value
        value = _getenv("UNSET VARIABLE", is_optional=True)
        self.assertIsNone(value)

        # Test for variable is not set but default value is given
        value = _getenv("SOME UNKNOWN VARIABLE", "DEFAULT VALUE")
        self.assertEqual(value, "DEFAULT VALUE")

    @mock.patch("os.getenv")
    def test_getenv_set(self, mock_getenv):
        mock_getenv.side_effect = lambda varname, value=None: "value"

        # Test for variable that is set
        value = _getenv("SOME KNOWN VARIABLE")
        self.assertEqual(value, "value")

        # But empty values are not allowed

        mock_getenv.side_effect = lambda varname, value=None: ""

        # Not as default value
        with self.assertRaises(AssertionError):
            _getenv("SOME KNOWN VARIABLE", "")

        # Not as variable value
        with self.assertRaises(AssertionError):
            _getenv("SOME KNOWN VARIABLE")

    @mock.patch("gobexport.config._getenv")
    def test_get_public_key(self, mock_getenv):
        get_public_key("value")

        mock_getenv.assert_called_with('PUBLIC_KEY_VALUE')