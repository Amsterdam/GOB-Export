import importlib
import os
import unittest

from gobcore.exceptions import GOBException
from gobexport.config import get_objectstore_config, OBJECTSTORE_CONFIGS


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


class TestGetConfig(unittest.TestCase):

    def test_get_objectstore_config(self):
        name = "Basisinformatie"
        result = get_objectstore_config(name)

        expected = OBJECTSTORE_CONFIGS[name].copy()
        expected['name'] = name

        self.assertEqual(expected, result)

    def test_get_nonexistend_objectstore_config(self):
        name = 'NonExistent'

        with self.assertRaises(GOBException):
            get_objectstore_config(name)
