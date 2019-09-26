from unittest import TestCase
from unittest.mock import patch

from gobexport.filters.notempty_filter import NotEmptyFilter


def mock_get_entity_value(entity: dict, field: str):
    return entity.get(field)


class TestNotEmptyFilter(TestCase):

    @patch("gobexport.filters.notempty_filter.get_entity_value", mock_get_entity_value)
    def test_filter(self):
        field = 'some_field'

        test_cases = [
            ({field: None}, False),
            ({field: ''}, False),
            ({field: []}, False),
            ({field: 'value'}, True),
            ({field: 42}, True),
        ]

        notempty_filter = NotEmptyFilter(field)

        for entity, result in test_cases:
            self.assertEqual(result, notempty_filter.filter(entity))

    @patch("gobexport.filters.notempty_filter.get_entity_value", mock_get_entity_value)
    def test_filter_multiple_values(self):
        field = 'some_field'
        field2 = 'some_other_field'

        test_cases = [
            ({field: None, field2: True}, True),
            ({field: '', field2: True}, True),
            ({field: [], field2: True}, True),
            ({field: 'value', field2: True}, True),
            ({field: 42, field2: True}, True),
            ({field: False, field2: False}, False),
            ({field: None, field2: ''}, False),
        ]

        notempty_filter = NotEmptyFilter(field, field2)

        for entity, result in test_cases:
            self.assertEqual(result, notempty_filter.filter(entity))
