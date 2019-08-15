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
