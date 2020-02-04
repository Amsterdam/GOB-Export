from unittest import TestCase

from gobcore.exceptions import GOBException
from gobexport.merged_api import MergedApi


class TestMergedApi(TestCase):

    def test_item_key(self):
        mapi = MergedApi('primary', 'secondary', ['a', 'b'], ['c'])

        item = {
            'a': 'val a',
            'b': 'val b',
            'c': 'val c',
            'd': 'val d',
        }

        self.assertEqual(('val a', 'val b'), mapi._item_key(item))

    def test_iter(self):
        primary = [
            {'key_a': 1, 'key_b': 2, 'attr_a': 3, 'attr_b': 4},
            {'key_a': 2, 'key_b': 2, 'attr_a': 4, 'attr_b': 5},
            {'key_a': 3, 'key_b': 2, 'attr_a': 5, 'attr_b': 6, 'attr_c': 8},
            {'key_a': 4, 'key_b': 2, 'attr_a': 6, 'attr_b': 7},
        ]
        secondary = [
            {'key_a': 1, 'key_b': 2, 'attr_c': 3},
            {'key_a': 2, 'key_b': 2, 'attr_c': 4},
            {'key_a': 3, 'key_b': 2, 'attr_c': 5},
            {'key_a': 4, 'key_b': 2, 'attr_c': 6},
        ]

        mapi = MergedApi(primary, secondary, ['key_a', 'key_b'], ['attr_c'])

        result = list(mapi)

        expected_result = [
            {'key_a': 1, 'key_b': 2, 'attr_a': 3, 'attr_b': 4, 'attr_c': 3},
            {'key_a': 2, 'key_b': 2, 'attr_a': 4, 'attr_b': 5, 'attr_c': 4},
            {'key_a': 3, 'key_b': 2, 'attr_a': 5, 'attr_b': 6, 'attr_c': 5},
            {'key_a': 4, 'key_b': 2, 'attr_a': 6, 'attr_b': 7, 'attr_c': 6},
        ]
        self.assertEqual(expected_result, result)

    def test_iter_non_matching(self):
        primary = [
            {'key_a': 1, 'key_b': 2, 'attr_a': 3, 'attr_b': 4},
        ]
        secondary = [
            {'key_a': 1, 'key_b': 3, 'attr_c': 3},
        ]

        with self.assertRaisesRegex(GOBException, "Rows in API results don't match."):
            list(MergedApi(primary, secondary, ['key_a', 'key_b'], ['attr_c']))

    def test_iter_different_length(self):
        primary = [
            {'key_a': 1, 'key_b': 2, 'attr_a': 3, 'attr_b': 4},
            {'key_a': 1, 'key_b': 3, 'attr_a': 3, 'attr_b': 4},

        ]
        secondary = [
            {'key_a': 1, 'key_b': 2, 'attr_c': 3},
        ]

        with self.assertRaisesRegex(GOBException, "Length of results from API's don't match."):
            list(MergedApi(primary, secondary, ['key_a', 'key_b'], ['attr_c']))
