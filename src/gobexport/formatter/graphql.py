import copy

from typing import List

from gobexport.converters.history import convert_to_history_rows
from gobexport.formatter.sorter.graphql import GraphQlResultSorter


class GraphQLResultFormatter:

    def __init__(self, expand_history=False, sort=None, unfold=False, row_formatter=None, cross_relations=False):
        """
        :param expand_history:
        :param sort:
        :param unfold:
        :param row_formatter:
        :param cross_relations:  When set to True, all relations are combined in the result rows. If an item, for
        example, has 2 relations A and B of length 2, this will result in 2*2=4 result rows, where each row contains
        a combination of these relations: A1-B1, A1-B2, A2-B1, A2-B2. The default behaviour for when cross_relations is
        set to False is to create separate rows for both relations, so that relations A and B are never combined. This
        would result in two rows where only relation A is present and two rows where only relation B is present. This
        parameter can only be used in combination with unfold=True (otherwise crossing relations would not make any
        sense).
        """
        self.sorter = None
        self.expand_history = expand_history
        self.unfold = unfold
        self.row_formatter = row_formatter
        self.cross_relations = cross_relations

        if sort:
            self.sorter = GraphQlResultSorter(sort)

    def _expand_history(self, edge):
        history_rows = convert_to_history_rows(self._flatten_edge(edge))
        for row in history_rows:
            yield row

    def _expand_history_items(self, items: list):
        for item in items:
            yield from self._expand_history(item)

    def _flatten_edge(self, edge, main=None):
        """Flatten edges and nodes from the graphql response, places all nested references
        as keys in the main dictionary, as well as keeping them in their original place to still be able to find
        values 2-dimensionally.

        :return: a list of dictionaries
        """
        flat_edge = {}
        for key, value in edge['node'].items():
            # References
            if isinstance(value, dict) and 'edges' in value:
                if main:
                    main.setdefault(key, []).extend([self._flatten_edge(e, main) for e in value['edges']])

                flat_edge.setdefault(key, []).extend([self._flatten_edge(e, flat_edge) for e in value['edges'] if e])
            else:
                flat_edge[key] = value

        # Clear the final reference lists of empty dicts
        if not main:
            for key, value in flat_edge.items():
                if isinstance(value, list):
                    flat_edge[key] = [v for v in value if v]
        return flat_edge

    def _flatten_edges(self, edges: list):
        for edge in edges:
            yield self._flatten_edge(edge)

    def _unfold_items(self, items):
        for item in items:
            yield from self._unfold(item)

    def _unfold(self, item):
        items = self._box_item(item)

        for item in items:
            yield self._flatten_edge(item)

    def _sort_items(self, items):
        for item in items:
            yield from self._sort(item)

    def _sort(self, item):
        items = self._box_item(item)
        sorted_item = self.sorter.sort_items(items)

        yield self._flatten_edge(sorted_item)

    def format_item(self, item):
        if self.row_formatter:
            item = self.row_formatter(item)

        # Convert to list
        items = item if isinstance(item, list) else [item]

        if self.expand_history:
            yield from self._expand_history_items(items)
        elif self.unfold:
            yield from self._unfold_items(items)
        elif self.sorter:
            yield from self._sort_items(items)
        else:
            yield from self._flatten_edges(items)

    def _box_cross_relations_duplicates(self, duplicates: list, childs: list, relation_key: str):
        """Generates duplicates for childs of relation with relation_key.

        Given a list of duplicates, add the first child to all the existing duplicates. Create new duplicates for the
        other childs.

        :param duplicates:
        :param childs:
        :param relation_key:
        :return:
        """
        new_duplicates = []

        self._add_child_to_duplicates(duplicates, childs[0], relation_key)

        for child in childs[1:]:
            for dup in duplicates:
                new_item = copy.deepcopy(dup)
                new_item[relation_key]['edges'] = [child]
                new_duplicates.append(new_item)
        return new_duplicates

    def _add_child_to_duplicates(self, duplicates: list, child: dict, relation_key: str):
        """Adds child to each of the duplicates

        :param duplicates:
        :param child:
        :param relation_key:
        :return:
        """

        for duplicate in duplicates:
            duplicate[relation_key] = {'edges': [child]}

    def _create_duplicates_for_childs(self, item: dict, childs: list, relation_key: str):
        """Duplicates base_item and adds each child to one of the duplicates.

        :param item:
        :param childs:
        :param relation_key:
        :return:
        """
        duplicates = []
        for child in childs:
            # Recursively box nested relations
            new_item = copy.deepcopy(item)
            new_item[relation_key]['edges'] = [child]
            duplicates.append(new_item)

        return duplicates

    def _undouble(self, items: list):
        """Undoubles items in list

        :param items:
        :return:
        """
        return [item for i, item in enumerate(items) if item not in items[:i]]

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
        duplicates = []

        for key, value in item['node'].items():
            if isinstance(value, dict) and 'edges' in value:
                # Nested relation

                childs = self._get_children(value['edges'])

                if len(childs) == 1:
                    # If only one child, do not duplicate. Only update base_item and duplicates
                    base_item[key] = {'edges': [childs[0]]}

                    self._add_child_to_duplicates(duplicates, childs[0], key)
                elif len(childs) > 1 and self.cross_relations and duplicates:
                    # Already have duplicated rows. Set first child to already duplicated rows and duplicate the
                    # duplicates for the other childs
                    # If cross_relations is True, but no duplicates are set yet, we should reach the 'else' statement,
                    # which just creates duplicates for the current object.
                    base_item[key] = {'edges': []}
                    duplicates += self._box_cross_relations_duplicates(duplicates, childs, key)
                else:
                    # Have multiple childs for this relation. Create separate objects for all childs.
                    base_item[key] = {'edges': []}
                    duplicates += self._create_duplicates_for_childs(base_item, childs, key)
            else:
                # Copy key, value to base_item and update boxed_items
                base_item[key] = value
                self._set_value_for_all(duplicates, key, value)

        if len(duplicates) == 0:
            # In case we haven't duplicated base_item into boxed_items
            duplicates = [base_item]

        return self._undouble([{'node': item} for item in duplicates])

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
