import pytest
from unittest import TestCase
from unittest.mock import patch, MagicMock, mock_open, call

from gobexport.exporter.utils import (
    convert_format,
    nested_entity_get,
    split_field_reference,
    evaluate_condition,
    evaluate_action,
    _evaluate_concat_action,
    _evaluate_literal_action,
    _get_entity_value_dict_lookup_key,
    get_entity_value,
    _get_value_from_list,
    _evaluate_fill_action,
    _evaluate_format_action,
    _evaluate_case_action,
    _evaluate_build_value_action,
)


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
    def test_evaluate_condition_is_none(self, mock_get_entity_value):
        mock_get_entity_value.return_value = 'some truthy value'
        entity = MagicMock()
        condition = {
            'reference': 'some.reference',
            'condition': 'isnone',
            'trueval': 'some.other.reference',
        }

        res = evaluate_condition(entity, condition)
        mock_get_entity_value.assert_called_with(entity, ['some', 'reference'])

        # Expect falseval (None)
        self.assertEqual(None, res)

        mock_get_entity_value.return_value = ''
        condition = {
            'reference': 'some.reference',
            'condition': 'isnone',
            'trueval': 'some.other.reference',
        }

        res = evaluate_condition(entity, condition)

        # Expect falseval (None)
        self.assertEqual(None, res)

        mock_get_entity_value.side_effect = [None, 'some value']
        condition = {
            'reference': 'some.reference',
            'condition': 'isnone',
            'trueval': 'some.other.reference',
        }

        res = evaluate_condition(entity, condition)

        # Expect trueval
        self.assertEqual('some value', res)

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

    @patch("gobexport.exporter.utils.get_entity_value", lambda entity, lookup_key: lookup_key)
    def test_evaluate_fill_action(self):
        entity = {}

        test_cases = [
            ({'length': 5, 'value': 'a', 'character': '2', 'fill_type': 'rjust'}, '2222a'),
            ({'length': 5, 'value': 'ab', 'character': '0', 'fill_type': 'rjust'}, '000ab'),
            ({'length': 1, 'value': 'ab', 'character': '0', 'fill_type': 'rjust'}, 'ab'),
        ]

        for action, result in test_cases:
            self.assertEqual(result, _evaluate_fill_action(entity, action))

    @patch("gobexport.exporter.utils.get_entity_value", lambda entity, lookup_key: lookup_key)
    def test_evaluate_fill_action_ljust(self):
        entity = {}

        test_cases = [
            ({'length': 5, 'value': 'a', 'character': '2', 'fill_type': 'ljust'}, 'a2222'),
            ({'length': 5, 'value': 'ab', 'character': '0', 'fill_type': 'ljust'}, 'ab000'),
            ({'length': 1, 'value': 'ab', 'character': '0', 'fill_type': 'ljust'}, 'ab'),
        ]

        for action, result in test_cases:
            self.assertEqual(result, _evaluate_fill_action(entity, action))

    def test_evaluate_fill_action_missing_keys(self):
        valid_action = {'length': '', 'value': '', 'character': '', 'fill_type': ''}

        for key in valid_action.keys():
            action = valid_action.copy()
            del action[key]

            with self.assertRaises(AssertionError):
                _evaluate_fill_action({}, action)

    def test_evaluate_fill_action_invalid_fill_type(self):
        invalid_action = {'length': '', 'value': '', 'character': '', 'fill_type': 'invalid'}

        with self.assertRaises(AssertionError):
            _evaluate_fill_action({}, invalid_action)

    @patch("gobexport.exporter.utils.get_entity_value")
    def test_evaluate_format_action(self, mock_get_entity_value):
        entity = MagicMock()
        formatter = MagicMock()
        action = {
            'action': 'format',
            'value': 'the_value',
            'formatter': formatter,
        }

        res = _evaluate_format_action(entity, action)
        self.assertEquals(formatter.return_value, res)
        mock_get_entity_value.assert_called_with(entity, 'the_value')
        formatter.assert_called_with(mock_get_entity_value.return_value)

    @patch("gobexport.exporter.utils.get_entity_value")
    def test_evaluate_format_action_with_kwargs(self, mock_get_entity_value):
        entity = MagicMock()
        formatter = MagicMock()
        action = {
            'action': 'format',
            'value': 'the_value',
            'formatter': formatter,
            'kwargs': {'a': 'A', 'b': 'B'},
        }

        res = _evaluate_format_action(entity, action)
        self.assertEquals(formatter.return_value, res)
        mock_get_entity_value.assert_called_with(entity, 'the_value')
        formatter.assert_called_with(mock_get_entity_value.return_value, a='A', b='B')


    @patch("gobexport.exporter.utils.get_entity_value")
    def test_evaluate_format_action_empty_value(self, mock_get_entity_value):
        entity = MagicMock()
        formatter = MagicMock()
        mock_get_entity_value.return_value = None
        action = {
            'action': 'format',
            'value': 'the_value',
            'formatter': formatter,
        }

        res = _evaluate_format_action(entity, action)
        self.assertIsNone(res)
        mock_get_entity_value.assert_called_with(entity, 'the_value')
        formatter.assert_not_called()

    def test_evaluate_format_action_missing_keys(self):
        valid_action = {'formatter': '', 'value': ''}

        for key in valid_action.keys():
            action = valid_action.copy()
            del action[key]

            with self.assertRaises(AssertionError):
                _evaluate_format_action({}, action)

    def test_evaluate_valuebuilder_action(self):
        entity = MagicMock()
        action = {
            'valuebuilder': MagicMock()
        }

        res = _evaluate_build_value_action(entity, action)

        action['valuebuilder'].assert_called_with(entity)
        self.assertEqual(action['valuebuilder'].return_value, res)

        with self.assertRaises(AssertionError):
            _evaluate_build_value_action({}, {})


    @patch("gobexport.exporter.utils.get_entity_value")
    def test_evaluate_case_action(self, mock_get_entity_value):
        entity = MagicMock()
        action = {
            'action': 'case',
            'reference': 'some.reference',
            'values': {
                'A': 'valA',
                'B': 'valB'
            }
        }

        testcases = [('A', 'valA'), ('B', 'valB'), ('C', None)]

        for reference_value, expected_value in testcases:
            mock_get_entity_value.return_value = reference_value
            res = _evaluate_case_action(entity, action)

            mock_get_entity_value.assert_called_with(entity, 'some.reference')
            self.assertEqual(expected_value, res)

    def test_evaluate_case_action_invalid_keys(self):
        entity = MagicMock()
        testcases = [
            {},
            {'reference': 'some.reference'},
            {'values': {}},
            {'reference': 'some.reference', 'values': ''},
        ]

        for testcase in testcases:
            with self.assertRaises(AssertionError):
                _evaluate_case_action(entity, testcase)

    @patch('gobexport.exporter.utils._evaluate_concat_action')
    @patch('gobexport.exporter.utils._evaluate_literal_action')
    @patch('gobexport.exporter.utils._evaluate_fill_action')
    @patch('gobexport.exporter.utils._evaluate_format_action')
    @patch('gobexport.exporter.utils._evaluate_case_action')
    @patch('gobexport.exporter.utils._evaluate_build_value_action')
    def test_evaluate_action(self, mock_valuebuilder, mock_case, mock_format, mock_fill, mock_literal, mock_concat):
        entity = {}
        action = {'action': 'concat'}
        self.assertEqual(mock_concat.return_value, evaluate_action(entity, action))
        mock_concat.assert_called_with(entity, action)

        action = {'action': 'literal'}
        self.assertEqual(mock_literal.return_value, evaluate_action(entity, action))
        mock_literal.assert_called_with(action)

        action = {'action': 'fill'}
        self.assertEqual(mock_fill.return_value, evaluate_action(entity, action))
        mock_fill.assert_called_with(entity, action)

        action = {'action': 'format'}
        self.assertEqual(mock_format.return_value, evaluate_action(entity, action))
        mock_format.assert_called_with(entity, action)

        action = {'action': 'case'}
        self.assertEqual(mock_case.return_value, evaluate_action(entity, action))
        mock_case.assert_called_with(entity, action)

        action = {'action': 'build_value'}
        self.assertEqual(mock_valuebuilder.return_value, evaluate_action(entity, action))
        mock_valuebuilder.assert_called_with(entity, action)

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

    def test_get_value_from_list(self):
        entity = [{'a': 'keyA', 'b': 'keyB'}, {'a': 'keyC', 'b': 'keyD'}]
        key = 'a'
        result = _get_value_from_list(entity, key, None)
        self.assertEqual('keyA|keyC', result)

        entity = [{'a': None, 'b': 'keyB'}, {'a': 'keyC', 'b': 'keyD'}]
        result = _get_value_from_list(entity, key, None)
        self.assertEqual('|keyC', result)

        entity = [{"a": {"b": 1, "c": "12"}}, {"a": {"b": {"d": 14}, "c": "13"}}]
        key = 'a'
        result = _get_value_from_list(entity, key, None)
        self.assertEqual([{"b": 1, "c": "12"}, {"b": {"d": 14}, "c": "13"}], result)


def foo(x):
    return x

@pytest.mark.parametrize(
    "input_format, mapping, output_format, success",
    [
        ({"a": "A", "b": "B"}, {"A": "a"}, {"A": "A"}, True),
        ({"a": "A", "b": {"x": "X"}, "c": "C"}, {"A": "a", "B": "b"}, {"A": "A", "B": {"x": "X"}}, True),
        ({"a": "A", "b": foo(1)}, {"A": "a", "B": "b"}, {"A": "A", "B": foo(1)}, True),
        ({"a": "A", "b": {"x": "X"}, "c": "C"}, {"A": "a", "B": {"y": "Y"}}, {"A": "A", "B": {"y": "Y"}}, True),
        ({"a": "A", "b": {"x": "X"}, "c": "C"}, {"A": "a", "B": foo(1)}, {"A": "A", "B": foo(1)}, True),
        ({"a": "A", "b": "B"}, {"A": "c"}, None, False),
    ],
)
def test_convert_format(input_format, mapping, output_format, success):
    if success:
        assert convert_format(input_format, mapping) == output_format
    else:
        with pytest.raises(KeyError):
            convert_format(input_format, mapping)
