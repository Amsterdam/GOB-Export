import requests
from unittest import TestCase
from unittest.mock import MagicMock, patch

from gobexport.graphql import GraphQL
from gobexport.graphql import GRAPHQL_PUBLIC_ENDPOINT, GRAPHQL_SECURE_ENDPOINT

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
                'bagWoonplaatsen': {
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

    query = '{bagWoonplaatsen {edges {node { id}}}}'

    api = GraphQL('host', query, 'bag', 'woonplaatsen')
    assert (str(api) == 'GraphQL bagWoonplaatsen')

hasNextPage = True
def response():
    global hasNextPage
    result = {
        'data': {
            'bagWoonplaatsen': {
                'pageInfo': {
                    'endCursor': True,
                    'hasNextPage': hasNextPage,
                },
                'edges': [
                    'THE EDGE'
                ]
            }
        }
    }
    hasNextPage = not hasNextPage
    return result

class TestGraphQl(TestCase):

    def test_constructor_sorter(self):
        api = GraphQL('host', '{bagWoonplaatsen {edges {node { id}}}}', 'bag', 'woonplaatsen')
        self.assertIsNotNone(api.formatter)

        api = GraphQL('host', '{bagWoonplaatsen {edges {node { id}}}}', 'bag', 'woonplaatsen', sort=MagicMock())
        self.assertIsNotNone(api.formatter)

    def test_secure(self):
        api = GraphQL('host', '{bagWoonplaatsen {edges {node { id}}}}', 'bag', 'woonplaatsen')
        self.assertEqual(api.url, f'host{GRAPHQL_PUBLIC_ENDPOINT}')

        api = GraphQL('host', '{bagWoonplaatsen {edges {node { id}}}}', 'bag', 'woonplaatsen', secure=True)
        self.assertEqual(api.url, f'host{GRAPHQL_SECURE_ENDPOINT}')

    @patch("gobexport.graphql.requests.post")
    @patch("gobexport.graphql.GraphQLResultFormatter")
    @patch("gobexport.graphql.time.time")
    def test_iter_with_formatter(self, mock_time, mock_formatter, mock_post):
        sort = {"some": "sortdef"}
        api = GraphQL('host', '{bagWoonplaatsen {edges {node { id}}}}', 'bag', 'woonplaatsen', sort=sort)
        api._flatten_edge = MagicMock()
        mock_time.side_effect = [5, 4, 3, 2, 1]  # Prevent division by zero
        mock_post.return_value = MagicMock()
        mock_post.return_value._update_query = lambda q, n: q
        mock_post.return_value.json = response

        for a in api:
            pass

        mock_formatter.assert_called_with(False, sort=sort, unfold=False, row_formatter=None, cross_relations=False)
        self.assertEqual(mock_formatter.return_value.format_item.call_count, 2)

    def test_update_query(self):
        api = GraphQL('host', '{bagWoonplaatsen {edges {node { id}}}}', 'bag', 'woonplaatsen')
        new_query = api._update_query(api.query, 100)
        expected_query = '{bagWoonplaatsen(first: 100, after: "") {edges {node { id}}pageInfo { endCursor, hasNextPage }}}'

        self.assertEqual(new_query, expected_query)

    def test_update_query_with_filters(self):
        api = GraphQL('host', '{bagWoonplaatsen(id: "test") {edges {node { id}}}}', 'bag', 'woonplaatsen')
        # Expect the query to contain 'first' and 'after' after initilization
        expected_query = '{bagWoonplaatsen(id: "test", first: 1, after: "") {edges {node { id}}pageInfo { endCursor, hasNextPage }}}'
        self.assertEqual(api.query, expected_query)

        new_query = api._update_query(api.query, 100)
        expected_query = '{bagWoonplaatsen(id: "test", first: 100, after: "") {edges {node { id}}pageInfo { endCursor, hasNextPage }}}'

        self.assertEqual(new_query, expected_query)
