from unittest import TestCase
from unittest.mock import patch, MagicMock

from gobexport.exporter.csv import _split_field_reference, evaluate_condition, get_entity_value


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

        self.assertEqual(['some', 'other', 'reference'], res)

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

        self.assertIsNone(res)

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
