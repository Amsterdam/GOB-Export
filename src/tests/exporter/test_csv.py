from unittest import TestCase
from unittest.mock import patch, MagicMock, mock_open, call

from gobcore.exceptions import GOBException
from gobexport.exporter.csv import _split_field_reference, evaluate_condition, get_entity_value, \
    _get_headers_from_file, _ensure_fieldnames_match_existing_file, csv_exporter, evaluate_action, \
    _evaluate_concat_action, _evaluate_literal_action, \
    _get_entity_value_dict_lookup_key


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
            'trueval': 'some.other.reference',
        }

        res = evaluate_condition(entity, condition)
        mock_get_entity_value.assert_called_with(entity, ['some', 'reference'])

        self.assertEqual(None, res)

    @patch('gobexport.exporter.csv.get_entity_value')
    def test_evaluate_condition_negated(self, mock_get_entity_value):
        mock_get_entity_value.side_effect = ['some truthy value', 'some value']
        entity = MagicMock()
        condition = {
            'reference': 'some.reference',
            'condition': 'isempty',
            'trueval': 'some.other.reference',
            'negate': True,
        }

        res = evaluate_condition(entity, condition)
        mock_get_entity_value.assert_has_calls([
            call(entity, ['some', 'reference']),
            call(entity, 'some.other.reference'),
        ])

        self.assertEqual('some value', res)

    @patch('gobexport.exporter.csv.get_entity_value')
    def test_evaluate_condition_trueval(self, mock_get_entity_value):
        mock_get_entity_value.return_value = ''
        entity = MagicMock()
        condition = {
            'reference': 'some.reference',
            'condition': 'isempty',
            'trueval': 'true val'
        }

        res = evaluate_condition(entity, condition)
        mock_get_entity_value.assert_called_with(entity, 'true val')

        self.assertEqual(mock_get_entity_value.return_value, res)

    @patch('gobexport.exporter.csv.get_entity_value')
    def test_evaluate_condition_override_false(self, mock_get_entity_value):
        mock_get_entity_value.return_value = 'not empty'
        entity = MagicMock()
        condition = {
            'reference': 'some.reference',
            'condition': 'isempty',
            'trueval': 'true val',
            'falseval': 'false val'
        }

        res = evaluate_condition(entity, condition)
        mock_get_entity_value.assert_called_with(entity, 'false val')

        self.assertEqual(mock_get_entity_value.return_value, res)

    @patch('gobexport.exporter.csv.get_entity_value')
    def test_evaluate_condition_notimplemented_condition(self, mock_get_entity_value):
        condition = {
            'reference': 'some.reference',
            'condition': 'invalidcondition',
            'trueval': 'some.other.reference',
        }

        with self.assertRaises(NotImplementedError):
            evaluate_condition({}, condition)

    def test_evaluate_condition_assertionerrors(self):
        testcases = [
            {'condition': 'c', 'reference': 'r'},
            {'condition': 'c', 'trueval': 'v'},
            {'reference': 'r', 'trueval': 'v'},
            {'reference': 'value', 'trueval': 'value'},
        ]

        for case in testcases:
            with self.assertRaises(AssertionError):
                evaluate_condition({}, case)

    @patch('gobexport.exporter.csv.evaluate_condition')
    def test_get_entity_value_dict_lookup_key_condition(self, mock_evaluate_condition):
        entity = {'entity': 'definition'}
        lookup_key = {'condition': 'somecondition'}

        res = _get_entity_value_dict_lookup_key(entity, lookup_key)
        mock_evaluate_condition.assert_called_with(entity, lookup_key)
        self.assertEqual(mock_evaluate_condition.return_value, res)

    @patch('gobexport.exporter.csv.evaluate_action')
    def test_get_entity_value_dict_lookup_key_action(self, mock_evaluate_action):
        entity = {'entity': 'definition'}
        lookup_key = {'action': 'someaction'}

        res = _get_entity_value_dict_lookup_key(entity, lookup_key)
        mock_evaluate_action.assert_called_with(entity, lookup_key)
        self.assertEqual(mock_evaluate_action.return_value, res)

    def test_get_entity_value_notimplemented(self):
        with self.assertRaises(NotImplementedError):
            _get_entity_value_dict_lookup_key({}, {})

    def test_get_entity_value(self):
        entity = {'key': 'value'}
        lookup_key = 'key'
        self.assertEqual('value', get_entity_value(entity, lookup_key))

    @patch('gobexport.exporter.csv.nested_entity_get')
    @patch('gobexport.exporter.csv._split_field_reference')
    def test_get_entity_value_nested(self, mock_split_ref, mock_nested_get):
        entity = {'some': 'entity'}
        lookup_key = 'some.key'
        mock_split_ref.return_value = ['some', 'key']

        res = get_entity_value(entity, lookup_key)
        self.assertEqual(mock_nested_get.return_value, res)
        mock_split_ref.assert_called_with('some.key')
        mock_nested_get.assert_called_with(entity, ['some', 'key'])

    def test_get_entity_value_none_key(self):
        self.assertIsNone(get_entity_value({}, None))

    @patch('gobexport.exporter.csv._split_field_reference')
    def test_get_entity_value_bool(self, mock_split_ref):
        mock_split_ref.return_value = 'key'

        self.assertEqual('J', get_entity_value({'key': True}, 'key'))
        self.assertEqual('N', get_entity_value({'key': False}, 'key'))

    @patch('gobexport.exporter.csv._get_entity_value_dict_lookup_key')
    def test_get_entity_value_dict_key(self, mock_dict):
        entity = {'some': 'entity'}
        lookup_key = {'some': 'dict lookup key'}
        self.assertEqual(mock_dict.return_value, get_entity_value(entity, lookup_key))
        mock_dict.assert_called_with(entity, lookup_key)

    @patch('gobexport.exporter.csv.get_entity_value')
    def test_evaluate_concat_action(self, mock_get_entity_value):
        entity = {}
        action = {
            'action': 'concat',
            'fields': [
                'a',
                'b',
                'c',
            ]
        }
        mock_get_entity_value.side_effect = ['val a', None, 'val b']
        res = _evaluate_concat_action(entity, action)
        self.assertEqual('val aval b', res)

        mock_get_entity_value.assert_has_calls([
            call(entity, 'a'),
            call(entity, 'b'),
            call(entity, 'c'),
        ])

        with self.assertRaises(AssertionError, msg='Missing fields key should raise AssertionError'):
            _evaluate_concat_action(entity, {})

    def test_evaluate_literal_action(self):
        action = {
            'action': 'literal',
            'value': 'some value',
        }

        self.assertEqual(action['value'], _evaluate_literal_action(action))

    @patch('gobexport.exporter.csv._evaluate_concat_action')
    @patch('gobexport.exporter.csv._evaluate_literal_action')
    def test_evaluate_action(self, mock_literal, mock_concat):
        entity = {}
        action = {'action': 'concat'}
        self.assertEqual(mock_concat.return_value, evaluate_action(entity, action))
        mock_concat.assert_called_with(entity, action)

        action = {'action': 'literal'}
        self.assertEqual(mock_literal.return_value, evaluate_action(entity, action))
        mock_literal.assert_called_with(action)

        with self.assertRaises(NotImplementedError):
            evaluate_action({}, {})

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
