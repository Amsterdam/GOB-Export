import copy

from typing import List


class GraphQlResultSorter:
    """GraphQlResultSorter

    Sorts the relations defined within a GraphQL result item with the supplied sorters.

    With GraphQL we can sort objects and nested objects, but we cannot sort an object based on the value of one of its
    children. This class solves that problem by first determining all possible combinations of key -> values within an
    object considered all nested objects/relations. We then sort these results with the given sorters. Only the top
    result is returned.

    A sorter is a function that takes two parameters x and y. The sorter should return True if x has priority over y.
    """

    def __init__(self, sorters: dict):
        """sorters is a dict of key => sorter pairs where key is the attribute to sort on with given sorter

        :param sorters:
        """
        self.sorters = sorters

    def _set_value_for_all(self, lst: List[dict], key: str, value):
        """Sets key to value for all dicts in lst

        :param lst:
        :param key:
        :param value:
        :return:
        """
        for item in lst:
            item[key] = value

    def _box_item(self, item):
        """Boxes (flattens) an item. The input item is an item with (possibly) multiple nested relations. The result
        is a list of all possible combinations of relations of the input item.

        For example (simplified):

        input = {a: 1, b: 2, c: [4,5,6]}

        output = [
            {a: 1, b: 2, c: 4},
            {a: 1, b: 2, c: 5},
            {a: 1, b: 2, c: 6},
        ]

        :param item:
        :return:
        """

        # base_item is a reference item, boxed_items are the results
        base_item = {}
        duplicated = []

        for key, value in item['node'].items():
            if isinstance(value, dict) and 'edges' in value:
                # Nested relation
                base_item[key] = {'edges': []}

                for edge in value['edges']:
                    for nested_edge in self._box_item(edge):
                        # Recursively box nested relations
                        new_item = copy.deepcopy(base_item)
                        new_item[key]['edges'] = [nested_edge]
                        duplicated.append(new_item)
            else:
                # Copy key, value to base_item and update boxed_items
                base_item[key] = value
                self._set_value_for_all(duplicated, key, value)

        if len(duplicated) == 0:
            # In case we haven't duplicated base_item into boxed_items
            duplicated = [base_item]

        return [{'node': item} for item in duplicated]

    def _extract_value_from_item(self, item: dict, key: str):
        """Returns value for given key in item

        :param item:
        :return:
        """
        head, *tail = key.split('.')

        val = item['node'][head]

        if len(tail) > 0:
            if len(val['edges']) > 0:
                val = self._extract_value_from_item(val['edges'][0], ".".join(tail))
            else:
                val = None

        return val

    def _sort_and_eliminate(self, items: list, key: str, sorter) -> list:
        """Sorts a list of items on given attribute (key) using sorter. Returns top result(s) only; drops any lower
        ranking results.

        :param items: List with items to sort
        :param key: Key to sort on.
        :param sorter: Sorter function to use
        :return:
        """

        result = []
        highest = None
        for item in items:
            value = self._extract_value_from_item(item, key)

            if value == highest:
                # If both values equal, add to result
                result.append(item)
            elif highest is None or sorter(value, highest):
                # Replace existing value
                highest = value
                result = [item]
        return result

    def sort_item(self, item):
        """Sorts (the nested relations in) an item with the sorters defined in self.sorters.
        Self.sort is dictionary with key => sorter pairs, where key is of the form attr.nested.attribute and sorter is
        a function that takes two parameters x and y. Sorter should return True if x ranks higher than y.

        This method first "boxes" the item; an item with relations with multiple values is transformed in a list of
        multiple copies of the same item, but with relations containing only one element. This makes it easier to sort
        the relations.

        The sorted version of the item is returned.

        :param item:
        :return:
        """
        boxed_items = self._box_item(item)

        for key, sorter in self.sorters.items():
            boxed_items = self._sort_and_eliminate(boxed_items, key, sorter)

        # Return first item
        return boxed_items[0]
