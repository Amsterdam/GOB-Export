from unittest import TestCase
from unittest.mock import patch, MagicMock, mock_open

from gobcore.exceptions import GOBException
from gobexport.exporter.csv import _split_field_reference, evaluate_condition, get_entity_value, update_entity_value, \
    _get_headers_from_file, _ensure_fieldnames_match_existing_file, csv_exporter


class TestCsvExporter(TestCase):

    def test_split_field_reference(self):
        testcases = [
            ('some.field', ['some', 'field']),
            ('field', 'field'),
        ]

        for case, result in testcases:
            self.assertEqual(result, _split_field_reference(case))

    @patch('gobexport.exporter.csv.get_entity_value')
    def test_evaluate_condition(self, mock_get_entity_value):
        mock_get_entity_value.return_value = 'some truthy value'
        entity = MagicMock()
        condition = {
            'reference': 'some.reference',
            'condition': 'isempty',
            'value': 'some.other.reference',
        }

        res = evaluate_condition(entity, condition)
        mock_get_entity_value.assert_called_with(entity, ['some', 'reference'])

        self.assertEqual(None, res)

    @patch('gobexport.exporter.csv.get_entity_value')
    def test_evaluate_condition_negated(self, mock_get_entity_value):
        mock_get_entity_value.return_value = 'some truthy value'
        entity = MagicMock()
        condition = {
            'reference': 'some.reference',
            'condition': 'isempty',
            'value': 'some.other.reference',
            'negate': True,
        }

        res = evaluate_condition(entity, condition)
        mock_get_entity_value.assert_called_with(entity, ['some', 'reference'])

        self.assertEqual(['some', 'other', 'reference'], res)

    @patch('gobexport.exporter.csv.get_entity_value')
    @patch('gobexport.exporter.csv.update_entity_value')
    def test_evaluate_condition_override_true(self, mock_update_entity_value, mock_get_entity_value):
        mock_get_entity_value.return_value = ''
        entity = MagicMock()
        condition = {
            'reference': 'some.reference',
            'condition': 'isempty',
            'override': 'override value'
        }

        res = evaluate_condition(entity, condition)
        mock_get_entity_value.assert_called_with(entity, ['some', 'reference'])
        mock_update_entity_value.assert_called_with(entity, ['some', 'reference'], 'override value')

        self.assertEqual(['some', 'reference'], res)

    @patch('gobexport.exporter.csv.get_entity_value')
    @patch('gobexport.exporter.csv.update_entity_value')
    def test_evaluate_condition_override_false(self, mock_update_entity_value, mock_get_entity_value):
        mock_get_entity_value.return_value = 'not empty'
        entity = MagicMock()
        condition = {
            'reference': 'some.reference',
            'condition': 'isempty',
            'override': 'override value'
        }

        res = evaluate_condition(entity, condition)
        mock_get_entity_value.assert_called_with(entity, ['some', 'reference'])
        mock_update_entity_value.assert_not_called()

        self.assertEqual(['some', 'reference'], res)

    @patch('gobexport.exporter.csv.get_entity_value')
    def test_evaluate_condition_notimplemented_condition(self, mock_get_entity_value):
        condition = {
            'reference': 'some.reference',
            'condition': 'invalidcondition',
            'value': 'some.other.reference',
        }

        with self.assertRaises(NotImplementedError):
            evaluate_condition({}, condition)

    def test_evaluate_condition_assertionerrors(self):
        testcases = [
            {'condition': 'c', 'reference': 'r'},
            {'condition': 'c', 'value': 'v'},
            {'reference': 'r', 'value': 'v'},
            {'reference': 'value', 'value': 'value'},
        ]

        for case in testcases:
            with self.assertRaises(AssertionError):
                evaluate_condition({}, case)

    @patch('gobexport.exporter.csv.evaluate_condition')
    def test_get_entity_value(self, mock_evaluate_condition):
        mock_evaluate_condition.return_value = None
        entity = {'some': 'entity'}
        condition = {'some': 'condition'}
        res = get_entity_value(entity, condition)
        mock_evaluate_condition.assert_called_with(entity, condition)
        self.assertIsNone(res)

    def test_update_entity_value(self):
        entity = {'some': 'entity'}
        res = update_entity_value(entity, 'some', 'new value')
        self.assertEqual(entity['some'], 'new value')

    def test_update_entity_value_nested(self):
        entity = {'some': {'other': {'key': 'entity'}}}
        res = update_entity_value(entity, ['some', 'other', 'key'], 'new value')
        self.assertEqual(entity['some']['other']['key'], 'new value')

    def test_update_entity_value_nested_non_existent_key(self):
        entity = {'some': 'entity'}
        res = update_entity_value(entity, 'another', 'new value')
        self.assertEqual(entity['some'], 'entity')

        entity = {'some': {'other': {'key': 'entity'}}}
        res = update_entity_value(entity, 'another', 'new value')
        self.assertEqual(entity['some']['other']['key'], 'entity')

    def test_get_headers_from_file(self):

        with patch("builtins.open", mock_open(read_data="SOME;DATA")) as mock_file, \
                patch('gobexport.exporter.csv.csv') as mock_csv:
            res = _get_headers_from_file('somefile')

            mock_csv.DictReader.assert_called_with(mock_file.return_value, delimiter=';')
            mock_file.assert_called_with('somefile', 'r')
            self.assertEqual(mock_csv.DictReader().fieldnames, res)

    @patch("gobexport.exporter.csv._get_headers_from_file")
    def test_ensure_fieldnames_match_existing_file(self, mock_get_headers):
        existing_fields = ['A', 'B', 'C']
        mock_get_headers.return_value = existing_fields

        # Headers match, no exception
        _ensure_fieldnames_match_existing_file(existing_fields.copy(), 'somefile')
        mock_get_headers.assert_called_with('somefile')

        error_cases = [
            [],
            ['a', 'b', 'c'],
            ['A', 'B'],
            ['A', 'C', 'B'],
            ['A', 'B', 'C', 'D'],
        ]

        for error_case in error_cases:
            with self.assertRaises(GOBException):
                _ensure_fieldnames_match_existing_file(error_case, 'somefile')

    @patch("gobexport.exporter.csv._ensure_fieldnames_match_existing_file")
    @patch("gobexport.exporter.csv.build_mapping_from_format")
    @patch("builtins.open", mock_open())
    @patch("gobexport.exporter.csv.csv")
    def test_csv_exporter_append(self, mock_csv, mock_build_mapping, mock_match_fieldnames):
        api = []
        file = ""

        csv_exporter(api, file)
        mock_match_fieldnames.assert_not_called()

        csv_exporter(api, file, append=True)
        mock_match_fieldnames.assert_called_once()
