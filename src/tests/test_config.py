import importlib
import os


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

    import export
    importlib.reload(export)


def test_host(monkeypatch):
    before_each(monkeypatch)
    from export.config import get_host

    assert(get_host() == os.getenv('API_HOST', 'http://localhost:5000'))


def test_args(monkeypatch):
    before_each(monkeypatch)
    from export.config import get_args

    assert(get_args() == ['collection', 'file'])
