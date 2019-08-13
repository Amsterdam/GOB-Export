from unittest import TestCase
from gobexport.filters.entity_filter import EntityFilter


class TestEntityFilter(TestCase):

    def test_filter(self):
        entity_filter = EntityFilter()

        with self.assertRaises(NotImplementedError):
            entity_filter.filter({})
