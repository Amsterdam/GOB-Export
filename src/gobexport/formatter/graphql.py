import copy

from typing import List

from gobexport.converters.history import convert_to_history_rows
from gobexport.formatter.sorter.graphql import GraphQlResultSorter


class GraphQLResultFormatter:

    def __init__(self, expand_history=False, sort=None, unfold=False):
        self.sorter = None
        self.expand_history = expand_history
        self.unfold = unfold

        if sort:
            self.sorter = GraphQlResultSorter(sort)

    def _expand_history(self, edge):
        history_rows = convert_to_history_rows(self._flatten_edge(edge))
        for row in history_rows:
            yield row

    def _flatten_edge(self, edge, main=None):
        """Flatten edges and nodes from the graphql response, places all nested references
        as keys in the main dictionary

        :return: a list of dictionaries
        """
        flat_edge = {}
        for key, value in edge['node'].items():
            # References
            if isinstance(value, dict) and 'edges' in value:
                if main:
                    main.setdefault(key, []).extend([self._flatten_edge(e, main) for e in value['edges']])
                else:
                    flat_edge.setdefault(key, []).extend([self._flatten_edge(e, flat_edge) for e in value['edges']])
            else:
                flat_edge[key] = value

        # Clear the final reference lists of empty dicts
        if not main:
            for key, value in flat_edge.items():
                if isinstance(value, list):
                    flat_edge[key] = [v for v in value if v]
        return flat_edge

    def format_item(self, item):
        if self.expand_history:
            yield from self._expand_history(item)
        else:
            if self.unfold or self.sorter:
                items = self._box_item(item)

                if self.unfold:
                    for item in items:
                        yield self._flatten_edge(item)
                elif self.sorter:
                    item = self.sorter.sort_items(items)
                    yield self._flatten_edge(item)
            else:
                yield self._flatten_edge(item)

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

                childs = self._get_children(value['edges'])

                if len(childs) == 1:
                    # If only one child, do not duplicate. Only update base_item and duplicates
                    base_item[key] = {'edges': [childs[0]]}

                    for dup in duplicated:
                        dup[key] = {'edges': [childs[0]]}
                else:
                    base_item[key] = {'edges': []}

                    for child in childs:
                        # Recursively box nested relations
                        new_item = copy.deepcopy(base_item)
                        new_item[key]['edges'] = [child]
                        duplicated.append(new_item)
            else:
                # Copy key, value to base_item and update boxed_items
                base_item[key] = value
                self._set_value_for_all(duplicated, key, value)

        if len(duplicated) == 0:
            # In case we haven't duplicated base_item into boxed_items
            duplicated = [base_item]

        return [{'node': item} for item in duplicated]

    def _get_children(self, edges: list):
        childs = []
        for edge in edges:
            for nested_edge in self._box_item(edge):
                childs.append(nested_edge)
        return childs

    def _set_value_for_all(self, lst: List[dict], key: str, value):
        """Sets key to value for all dicts in lst

        :param lst:
        :param key:
        :param value:
        :return:
        """
        for item in lst:
            item[key] = value