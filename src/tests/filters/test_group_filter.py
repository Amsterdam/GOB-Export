from unittest import TestCase

from gobexport.filters.group_filter import GroupFilter


class TestGroupFilter(TestCase):

    class MockEntityFilter:
        def __init__(self, value: bool):
            self.value = value
            self.resetted = False

        def filter(self, entity: dict):
            return self.value
        
        def reset(self):
            self.resetted = True

    def test_filter(self):

        test_cases = [
            ([], True),
            ([self.MockEntityFilter(True)], True),
            ([self.MockEntityFilter(True), self.MockEntityFilter(True)], True),
            ([self.MockEntityFilter(False)], False),
            ([self.MockEntityFilter(False), self.MockEntityFilter(True)], False),
        ]

        for filters, result in test_cases:
            group_filter = GroupFilter(filters)
            self.assertEqual(result, group_filter.filter({}))
            
            group_filter.reset()
            for filter in filters:
                self.assertEqual(filter.resetted, True)
