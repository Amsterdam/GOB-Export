
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

    def _extract_value_from_item(self, item: dict, key: str):
        """Returns value for given key in item

        :param item:
        :return:
        """
        head, *tail = key.split('.')

        val = item['node'].get(head)

        if not val:
            return None

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

    def sort_items(self, items: list):
        """Sorts (the nested relations in) an item with the sorters defined in self.sorters.
        Self.sort is dictionary with key => sorter pairs, where key is of the form attr.nested.attribute and sorter is
        a function that takes two parameters x and y. Sorter should return True if x ranks higher than y.

        Method expects rows to be unfolded (boxed, see GraphQLResultFormatter). Only the top result will be returned.

        The sorted version of the item is returned.

        :param item:
        :return:
        """

        for key, sorter in self.sorters.items():
            items = self._sort_and_eliminate(items, key, sorter)

        # Return first item
        return items[0]
