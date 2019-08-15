import os
import importlib
import gobexport.api

from unittest import TestCase
from unittest.mock import patch, MagicMock

from gobexport.exporter import CONFIG_MAPPING
from gobexport.exporter.dat import dat_exporter
from gobexport.exporter.csv import csv_exporter
from gobexport.exporter.esri import esri_exporter


def before_each(monkeypatch):
    import gobexport.exporter
    importlib.reload(gobexport.exporter)

records = [{'identificatie': '1', 'geometrie': {'type': 'Point', 'coordinates': [125.6, 10.1]}}]
graphql_records = [{'identificatie': '2', 'boolean': True, 'geometrie': {'type': 'Point', 'coordinates': [125.6, 10.1]}}]


class MockAPI:
    def __init__(self, host=None, path=None):
        pass

    def __iter__(self):
        global records
        for e in records:
            yield e


class MockGraphQL:
    def __init__(self, host=None, query=None, catalogue=None, collection=None, expand_history=None, sort=None):
        pass

    def __iter__(self):
        global graphql_records
        for e in graphql_records:
            yield e


class MockConfig:

    products = {
        'csv': {
            'api_type': 'graphql',
            'exporter': csv_exporter,
            'filename': 'CSV_Actueel/BAG_woonplaats.csv',
            'mime_type': 'plain/text',
            'format': {
                'identificatie': 'identificatie',
                'boolean': 'boolean',
                'geometrie': 'geometrie',
            },
            'query': 'any query'
        },
        'shape': {
            'exporter': esri_exporter,
            'filename': 'CSV_Actueel/BAG_woonplaats.shp',
            'mime_type': 'plain/text',
            'format': {
                'id': 'identificatie',
                'boolean': 'boolean',
            },
            'query': 'another query'
        }
    }


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
    monkeypatch.setattr(gobexport.graphql, 'GraphQL', MockGraphQL)

    before_each(monkeypatch)
    from gobexport.exporter import export_to_file

    # Test DAT export
    catalogue = 'meetbouten'
    collection = 'meetbouten'

    # Get the configuration for this collection
    config = CONFIG_MAPPING[catalogue][collection]

    export_to_file('host', config.products['dat'], '/tmp/ttt', catalogue, collection)
    assert(MockFile.s == '$$1$$||125,6|10,1||||||||||||||POINT (125.6 10.1)\n')

    MockFile.s = ''

    catalogue = 'gebieden'
    collection = 'stadsdelen'

    # Get the configuration for this collection
    config = CONFIG_MAPPING[catalogue][collection]
    format = config.products['csv_actueel'].get('format')

    export_to_file('host', config.products['csv_actueel'], '/tmp/ttt', catalogue, collection)
    expected_result = 'identificatie;code;naam;beginGeldigheid;eindGeldigheid;documentdatum;documentnummer;ligtIn:BRK.GME.identificatie;ligtIn:BRK.GME.naam;geometrie\r\n1;;;;;;;;;POINT (125.6 10.1)\r\n'
    assert(MockFile.s == expected_result)

    MockFile.s = ''

    # Get the configuration for this collection
    config = MockConfig

    export_to_file('host', config.products['csv'], '/tmp/ttt', catalogue, collection)
    expected_result = 'identificatie;boolean;geometrie\r\n2;J;POINT (125.6 10.1)\r\n'
    assert(MockFile.s == expected_result)

    format = config.products['shape'].get('format')

    file_name = 'esri.shp'

    # Update records to contain an geometry collection
    records = [{'identificatie': '2', 'boolean': False, 'geometrie': {'type': 'GeometryCollection', 'geometries': [{'type': 'LineString', 'coordinates': [[125891.16, 480253.38], [125891.07, 480253.34]]}, {'type': 'Polygon', 'coordinates': [[[125891.16, 480253.38], [125893.06, 480250.0], [125892.57, 480250.0]]]}]}}]

    export_to_file('host', config.products['shape'], file_name, catalogue, collection)

    # Remove created files
    for file in ['esri.shp', 'esri.dbf', 'esri.shx', 'esri.prj']:
        assert(os.path.isfile(file))
        os.remove(file)


class TestExportToFile(TestCase):

    @patch("gobexport.exporter.GraphQLStreaming")
    @patch("gobexport.exporter.BufferedIterable")
    @patch("gobexport.exporter.product_source", lambda x: 'source')
    def test_export_to_file_graphql_streaming(self, mock_buffered_iterable, mock_graphql_streaming):
        from gobexport.exporter import export_to_file

        product = {
            'api_type': 'graphql_streaming',
            'query': 'some query',
            'exporter': MagicMock(),
            'format': 'the format',
        }
        result = export_to_file('host', product, 'file', 'catalogue', 'collection', False)
        mock_graphql_streaming.assert_called_with('host', product['query'], False)

        mock_buffered_iterable.assert_called_with(mock_graphql_streaming.return_value, 'source', buffer_items=False)
        product['exporter'].assert_called_with(mock_buffered_iterable.return_value, 'file', 'the format', append=False)

    @patch("gobexport.exporter.GraphQLStreaming")
    @patch("gobexport.exporter.BufferedIterable")
    @patch("gobexport.exporter.product_source", lambda x: 'source')
    def test_export_to_file_graphql_streaming_with_unfold(self, mock_buffered_iterable, mock_graphql_streaming):
        from gobexport.exporter import export_to_file

        product = {
            'api_type': 'graphql_streaming',
            'query': 'some query',
            'exporter': MagicMock(),
            'format': 'the format',
            'unfold': 'true_or_false',
        }
        result = export_to_file('host', product, 'file', 'catalogue', 'collection', False)
        mock_graphql_streaming.assert_called_with('host', product['query'], 'true_or_false')

    @patch("gobexport.exporter.GraphQLStreaming")
    @patch("gobexport.exporter.BufferedIterable")
    @patch("gobexport.exporter.GroupFilter")
    @patch("gobexport.exporter.product_source", lambda x: 'source')
    def test_export_to_file_entity_filters(self, mock_group_filter, mock_buffered_iterable, mock_graphql_streaming):
        from gobexport.exporter import export_to_file

        mock_entity_filter = MagicMock()
        mock_exporter = MagicMock()

        product = {
            'api_type': 'graphql_streaming',
            'query': 'some query',
            'exporter': mock_exporter,
            'format': 'the format',
            'unfold': 'true_or_false',
            'entity_filters': [
                mock_entity_filter,
            ]
        }
        result = export_to_file('host', product, 'file', 'catalogue', 'collection', False)

        mock_group_filter.assert_called_with([mock_entity_filter])
        mock_exporter.assert_called_with(mock_buffered_iterable.return_value,
                                         'file',
                                         'the format',
                                         append=False,
                                         filter=mock_group_filter.return_value)

