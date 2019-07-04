import requests
from unittest import TestCase
from unittest.mock import MagicMock, patch

from gobexport.graphql import GraphQL

next = False


def get_node(id, with_history):
    if with_history:
        return {
            'node': {
                'id': id,
                'beginGeldigheid': '2000-01-01',
                'eindGeldigheid': '',
                'ligtInGemeente': {
                    'edges': [
                        {
                            'node': {
                                'id': id,
                                'beginGeldigheid': '2010-01-01',
                                'eindGeldigheid': ''
                            }
                        }
                    ]
                }
            }
        }
    else:
        return {
            'node': {
                'id': id,
                'ligtInGemeente': {
                    'edges': []
                },
                'heeftBrondocumenten': {
                    'edges': [
                        {
                            'node': {
                                'id': id
                            },
                        },
                        {
                            'node': {
                                'id': id + 1
                            }
                        }
                    ]
                }
            }
        }


class MockResponse:

    def __init__(self, ok, results, with_history=False):
        self.ok = ok
        self.results = [get_node(i, with_history) for i in range(0, results)]
        pass

    def json(self):
        global next
        result = {
            'data': {
                'woonplaatsen': {
                    'edges': self.results,
                    'pageInfo': {
                        'endCursor': 'YXJyYXljb25uZWN0aW9uOjU=',
                        'hasNextPage': next
                    }
                }
            }
        }
        if next:
            next = False
        return result


def mock_post(ok=True, results=1, with_history=False):
    return lambda url, json: MockResponse(ok, results, with_history)


def test_graphql(monkeypatch):
    monkeypatch.setattr(requests, 'post', mock_post())

    from gobexport.graphql import GraphQL

    query = '{woonplaatsen {edges {node { id}}}}'

    api = GraphQL('host', query, 'bag', 'woonplaatsen')
    assert (str(api) == 'GraphQL woonplaatsen')

    # # Expect first, after and pageInfo to be present the query
    # expected_query = '{woonplaatsen(first: 100, after: "") {edges {node { id}}pageInfo { endCursor, hasNextPage }}}'
    # assert(expected_query == api.query)
    #
    # new_query = api._update_query('{woonplaatsen(filter: "value") {edges {node { id}}}}')
    # # Expect filter to be in the qeuery
    # expected_query = '{woonplaatsen(filter: "value", first: 100, after: "") {edges {node { id}}pageInfo { endCursor, hasNextPage }}}'
    # assert(expected_query == new_query)
    #
    # api.end_cursor = "abcde"
    # new_query = api._update_query('{woonplaatsen(filter: "value") {edges {node { id}}}}')
    # # Expect the endCursor to be filled
    # expected_query = '{woonplaatsen(filter: "value", first: 100, after: "abcde") {edges {node { id}}pageInfo { endCursor, hasNextPage }}}'
    # assert(expected_query == new_query)
    #
    # api.end_cursor = "edcba"
    # new_query = api._update_query('{woonplaatsen(filter: "value", first: 100, after: "abcde") {edges {node { id}}}}')
    # # Expect the endCursor to be updated
    # expected_query = '{woonplaatsen(filter: "value", first: 100, after: "edcba") {edges {node { id}}pageInfo { endCursor, hasNextPage }}}'
    # assert(expected_query == new_query)
    #
    # # Expect record to be flattened and count is 1
    # expected_record = {'id': 0, 'ligtInGemeente': [], 'heeftBrondocumenten': [{'id': 0}, {'id': 1}]}
    # cnt = 0
    # for e in api:
    #     cnt += 1
    #     assert(e == expected_record)
    # assert(cnt == 1)
    #
    # monkeypatch.setattr(requests, 'post', mock_post(ok=True, results=3))
    # api = GraphQL('host', query, 'bag', 'woonplaatsen')
    #
    # # Expect count is 3
    # cnt = 0
    # for e in api:
    #     cnt += 1
    # assert(cnt == 3)
    #
    # global next
    # next = True
    #
    # api = GraphQL('host', query, 'bag', 'woonplaatsen')
    # # Expect count is 6 (two pages of 3)
    # cnt = 0
    # for e in api:
    #     cnt += 1
    # assert(cnt == 6)
    #
    # # Test expansion of history
    # monkeypatch.setattr(requests, 'post', mock_post(ok=True, results=1, with_history=True))
    # api = GraphQL('host', query, 'bag', 'woonplaatsen', expand_history=True)
    #
    # # Expect count is 2 (two combined states)
    # cnt = 0
    # for e in api:
    #     cnt += 1
    # assert(cnt == 2)


def test_flatten_edge():
    api = GraphQL('host', '{woonplaatsen {edges {node { id}}}}', 'bag', 'woonplaatsen')
    edge = {
        'node': {
            'reference': {
                'edges': [
                    {
                        'node': {
                            'value': 'value'
                        }
                    }
                ]
            }
        }
    }

    nested_edge = {
        "node": {
            "value": "value",
            "reference": {
                "edges": [
                    {
                        "node": {
                            "value": "value",
                            "nested_reference": {
                                "edges": [
                                    {
                                        "node": {
                                            "nested_value": "value"
                                        }
                                    }
                                ]
                            }
                        }
                    }
                ]
            },
            "empty_reference": {
                "edges": [
                    {
                        "node": {
                            "empty_nested_reference": {
                                "edges": []
                            }
                        }
                    }
                ]
            }
        }
    }

    expected_result = {'reference': [{'value': 'value'}]}
    result = api._flatten_edge(edge)
    assert (expected_result == result)

    expected_result = {
        'value': 'value',
        'reference': [{'value': 'value'}],
        'nested_reference': [{'nested_value': 'value'}],
        'empty_reference': [],
        'empty_nested_reference': [],
    }
    result = api._flatten_edge(nested_edge)
    assert (expected_result == result)


class TestGraphQl(TestCase):

    def test_constructor_sorter(self):
        api = GraphQL('host', '{woonplaatsen {edges {node { id}}}}', 'bag', 'woonplaatsen')
        self.assertIsNone(api.sorter)

        api = GraphQL('host', '{woonplaatsen {edges {node { id}}}}', 'bag', 'woonplaatsen', sort=MagicMock())
        self.assertIsNotNone(api.sorter)

    @patch("gobexport.graphql.requests.post")
    @patch("gobexport.graphql.GraphQlResultSorter")
    @patch("gobexport.graphql.time.time")
    def test_iter_with_sorter(self, mock_time, mock_sorter, mock_post):
        sort = {"some": "sortdef"}
        api = GraphQL('host', '{woonplaatsen {edges {node { id}}}}', 'bag', 'woonplaatsen', sort=sort)
        api._flatten_edge = MagicMock()
        mock_time.side_effect = [2, 1]  # Prevent division by zero
        mock_post.return_value = MagicMock()
        mock_post.return_value.json.return_value = {
            'data': {
                'woonplaatsen': {
                    'pageInfo': {
                        'endCursor': True,
                        'hasNextPage': False,
                    },
                    'edges': [
                        'THE EDGE'
                    ]
                }
            }
        }

        for a in api:
            pass

        mock_sorter.assert_called_with(sort)
        mock_sorter.return_value.sort_item.assert_called_once()
        api._flatten_edge.assert_called_with(mock_sorter.return_value.sort_item.return_value)

    def test_update_query(self):
        api = GraphQL('host', '{woonplaatsen {edges {node { id}}}}', 'bag', 'woonplaatsen')
        new_query = api._update_query(api.query, 100)
        expected_query = '{woonplaatsen(first: 100, after: "") {edges {node { id}}pageInfo { endCursor, hasNextPage }}}'

        self.assertEqual(new_query, expected_query)
