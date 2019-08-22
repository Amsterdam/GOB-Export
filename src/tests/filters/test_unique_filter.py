from unittest import TestCase
from unittest.mock import patch

from gobexport.filters.unique_filter import UniqueFilter


def mock_get_entity_value(entity: dict, field: str):
    return entity.get(field)


class TestUniqueFilter(TestCase):

    @patch("gobexport.filters.unique_filter.get_entity_value", mock_get_entity_value)
    def test_filter(self):
        field = 'some_field'

        test_cases = [
            ({field: 'Value 1'}, True),
            ({field: 'Value 2'}, True),
            ({field: 'Value 1'}, False),
        ]

        unique_filter = UniqueFilter(field)

        for entity, result in test_cases:
            self.assertEqual(result, unique_filter.filter(entity))
