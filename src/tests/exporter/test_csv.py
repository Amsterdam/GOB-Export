from unittest import TestCase
from unittest.mock import patch, MagicMock

from gobexport.exporter.csv import _split_field_reference, evaluate_condition, get_entity_value, update_entity_value


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
