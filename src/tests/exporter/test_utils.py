from unittest import TestCase
from unittest.mock import patch, MagicMock, mock_open, call

from gobexport.exporter.utils import nested_entity_get, split_field_reference, evaluate_condition, \
     evaluate_action, _evaluate_concat_action, _evaluate_literal_action, \
     _get_entity_value_dict_lookup_key, get_entity_value


class TestUtils(TestCase):

    def test_split_field_reference(self):
        testcases = [
            ('some.field', ['some', 'field']),
            ('field', 'field'),
        ]

        for case, result in testcases:
            self.assertEqual(result, split_field_reference(case))

    @patch('gobexport.exporter.utils.get_entity_value')
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

    @patch('gobexport.exporter.utils.get_entity_value')
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

    @patch('gobexport.exporter.utils.get_entity_value')
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

    @patch('gobexport.exporter.utils.get_entity_value')
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

    @patch('gobexport.exporter.utils.get_entity_value')
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

    @patch('gobexport.exporter.utils.evaluate_condition')
    def test_get_entity_value_dict_lookup_key_condition(self, mock_evaluate_condition):
        entity = {'entity': 'definition'}
        lookup_key = {'condition': 'somecondition'}

        res = _get_entity_value_dict_lookup_key(entity, lookup_key)
        mock_evaluate_condition.assert_called_with(entity, lookup_key)
        self.assertEqual(mock_evaluate_condition.return_value, res)

    @patch('gobexport.exporter.utils.evaluate_action')
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

    @patch('gobexport.exporter.utils.nested_entity_get')
    @patch('gobexport.exporter.utils.split_field_reference')
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

    @patch('gobexport.exporter.utils.split_field_reference')
    def test_get_entity_value_bool(self, mock_split_ref):
        mock_split_ref.return_value = 'key'

        self.assertEqual('J', get_entity_value({'key': True}, 'key'))
        self.assertEqual('N', get_entity_value({'key': False}, 'key'))

    @patch('gobexport.exporter.utils._get_entity_value_dict_lookup_key')
    def test_get_entity_value_dict_key(self, mock_dict):
        entity = {'some': 'entity'}
        lookup_key = {'some': 'dict lookup key'}
        self.assertEqual(mock_dict.return_value, get_entity_value(entity, lookup_key))
        mock_dict.assert_called_with(entity, lookup_key)

    @patch('gobexport.exporter.utils.get_entity_value')
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

    @patch('gobexport.exporter.utils._evaluate_concat_action')
    @patch('gobexport.exporter.utils._evaluate_literal_action')
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

    def test_nested_entity_get(self):
        # Test nested dict
        result = nested_entity_get({'a': {'b': {'c': 1}}}, ['a', 'b', 'c'])
        assert(result == 1)

        # Test nested dict with list
        result = nested_entity_get({'a': [{'b': 1}, {'c':2}]}, ['a', '[0]', 'b'])
        assert(result == 1)

        # Test nested dict with list index key as string
        result = nested_entity_get({'a': [{'b': 1}, {'c':2}]}, ['a', '[1]', 'c'])
        assert(result == 2)

        # Test nested dict with list index key as string
        result = nested_entity_get({'a': [{'b': 1}, {'c':2}]}, ['a', '[2]', 'c'])
        assert(result == None)

        # Test nested dict with list without specified list index keys
        result = nested_entity_get({'a': [{'b': 1}, {'c':2}]}, ['a', 'b'])
        assert(result == '1')

        # Test nested dict with empty list
        result = nested_entity_get({'a': []}, ['a', 'c'])
        assert(result == '')

        # Test default missing value
        result = nested_entity_get({'a': {'b': {'c': 1}}}, ['a', 'b', 'd'])
        assert(result == None)

        # Test missing list index value
        result = nested_entity_get({'a': [{'b': 1}, {'c':2}]}, ['a', '[2]', 'b'])
        assert(result == None)

        # Test missing value
        result = nested_entity_get({'a': {'b': {'c': 1}}}, ['a', 'b', 'd'], 'missing')
        assert(result == 'missing')
