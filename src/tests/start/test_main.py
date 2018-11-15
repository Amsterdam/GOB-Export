import gobcore.message_broker

class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)

class MockArgumentParser:

    def __init__(self, prog, description, epilog):
        MockArgumentParser.description = description
        MockArgumentParser.arguments = {}

    def add_argument(self, collection, **kwargs):
        MockArgumentParser.arguments[collection] = collection

    def parse_args(self):
        return Struct(**MockArgumentParser.arguments)

def test_main(monkeypatch):
    import argparse
    monkeypatch.setattr(argparse, 'ArgumentParser', MockArgumentParser)
    monkeypatch.setattr(gobcore.message_broker, 'publish', lambda a, b, c: None)

    from gobexport.start import __main__
