import os
import importlib

import gobexport.api

from gobexport.exporter import CONFIG_MAPPING
from gobexport.exporter.dat import dat_exporter
from gobexport.exporter.csv import csv_exporter
from gobexport.exporter.esri import esri_exporter


def before_each(monkeypatch):
    import gobexport.exporter
    importlib.reload(gobexport.exporter)

records = [{'identificatie': '1', 'geometrie': {'type': 'Point', 'coordinates': [125.6, 10.1]}}]


class MockAPI:
    def __init__(self, host=None, path=None):
        pass

    def __iter__(self):
        global records
        for e in records:
            yield e


class MockFile:
    s = ''

    def __iter__(self, file, mode):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def write(self, s):
        MockFile.s += s


def mock_open(file, mode):
    return MockFile()


def test_export_to_file(monkeypatch):
    global records
    monkeypatch.setitem(__builtins__, 'open', mock_open)
    monkeypatch.setattr(gobexport.api, 'API', MockAPI)

    before_each(monkeypatch)
    from gobexport.exporter import export_to_file

    # Test DAT export

    catalogue = 'meetbouten'
    collection = 'meetbouten'

    # Get the configuration for this collection
    config = CONFIG_MAPPING[catalogue][collection]

    export_to_file(catalogue, collection, dat_exporter, '/tmp/ttt', config.products['dat']['format'])
    assert(MockFile.s == '$$1$$||125,6|10,1||||||||||||||POINT (125.6 10.1)\n')

    MockFile.s = ''

    catalogue = 'gebieden'
    collection = 'stadsdelen'

    # Get the configuration for this collection
    config = CONFIG_MAPPING[catalogue][collection]
    format = config.products['csv_actueel'].get('format')

    export_to_file(catalogue, collection, csv_exporter, '/tmp/ttt', format)
    expected_result = 'identificatie;code;naam;beginGeldigheid;eindGeldigheid;documentdatum;documentnummer;ligtIn:BRK.GME.identificatie;ligtIn:BRK.GME.naam;geometrie\r\n1;;;;;;;;;POINT (125.6 10.1)\r\n'
    assert(MockFile.s == expected_result)

    catalogue = 'gebieden'
    collection = 'stadsdelen'

    # Get the configuration for this collection
    config = CONFIG_MAPPING[catalogue][collection]
    format = config.products['esri_actueel'].get('format')

    file_name = 'esri.shp'

    # Update records to contain an geometry collection
    records = [{'identificatie': '2', 'geometrie': {'type': 'GeometryCollection', 'geometries': [{'type': 'LineString', 'coordinates': [[125891.16, 480253.38], [125891.07, 480253.34]]}, {'type': 'Polygon', 'coordinates': [[[125891.16, 480253.38], [125893.06, 480250.0], [125892.57, 480250.0]]]}]}}]

    export_to_file(catalogue, collection, esri_exporter, file_name, format)

    # Remove created files
    for file in ['esri.shp', 'esri.dbf', 'esri.shx', 'esri.prj']:
        assert(os.path.isfile(file))
        os.remove(file)
