import random

from unittest import TestCase
from unittest.mock import patch, MagicMock

from gobexport.graphql_streaming import GraphQLStreaming
from gobexport.graphql_streaming import STREAMING_GRAPHQL_PUBLIC_ENDPOINT, STREAMING_GRAPHQL_SECURE_ENDPOINT
from typing import Generator


@patch("gobexport.graphql_streaming.GraphQLResultFormatter")
class TestGraphQLStreaming(TestCase):

    def test_without_batchsize(self, mock_formatter):
        graphql_streaming = GraphQLStreaming('host', 'query', batch_size=None)
        graphql_streaming._query_all = MagicMock(return_value=['a', 'b'])

        self.assertEqual(['a', 'b'], list(graphql_streaming))

        graphql_streaming._query_all.assert_called_once()

    def test_with_batchsize(self, mock_formatter):
        graphql_streaming = GraphQLStreaming('host', 'query', batch_size=100)
        graphql_streaming._query_paginated = MagicMock(return_value=iter(['a', 'b', 'c']))

        self.assertEqual(['a', 'b', 'c'], list(graphql_streaming))

        graphql_streaming._query_paginated.assert_called_once()

    def test_secure(self, mock_formatter):
        api = GraphQLStreaming('host', 'query')
        self.assertEqual(api.url, f'host{STREAMING_GRAPHQL_PUBLIC_ENDPOINT}')

        api = GraphQLStreaming('host', 'query', secure=True)
        self.assertEqual(api.url, f'host{STREAMING_GRAPHQL_SECURE_ENDPOINT}')

    @patch("gobexport.graphql_streaming.post_stream")
    def test_execute_query(self, mock_post, mock_formatter):
        mock_post.return_value = iter(['a', 'b', 'c', 'd'])
        graphql_streaming = GraphQLStreaming('host', 'query')

        result = graphql_streaming._execute_query('the query')

        self.assertEqual(['a', 'b', 'c', 'd'], list(result))
        mock_post.assert_called_with(f'host{STREAMING_GRAPHQL_PUBLIC_ENDPOINT}', {'query': 'the query'})

    @patch("gobexport.graphql_streaming.json_loads", lambda x: x)
    def test_query_all(self, mock_formatter):
        query = f'query{random.randint(0, 1000)}'
        exp_result = [random.randint(0, 1000) for _ in range(10)]
        graphql_streaming = GraphQLStreaming('host', query)
        graphql_streaming._execute_query = MagicMock(return_value=iter(exp_result))
        graphql_streaming.formatter = MagicMock()
        graphql_streaming.formatter.format_item = MagicMock(side_effect=lambda x: iter([x]))

        res = graphql_streaming._query_all()

        self.assertEqual(exp_result, list(res))
        graphql_streaming._execute_query.assert_called_with(query)

    def test_query_page(self, mock_formatter):
        batch_size = random.randint(0, 1000)
        query = f'query{random.randint(0, 1000)}'
        exp_result = [random.randint(0, 1000) for _ in range(10)]
        after = random.randint(0, 1000)

        graphql_streaming = GraphQLStreaming('host', query, batch_size=batch_size)
        graphql_streaming._add_pagination_to_query = MagicMock()
        graphql_streaming._execute_query = MagicMock(return_value=iter(exp_result))

        self.assertEqual(exp_result, list(graphql_streaming._query_page(after)))

        graphql_streaming._add_pagination_to_query.assert_called_with(query, after, batch_size)
        graphql_streaming._execute_query.assert_called_with(graphql_streaming._add_pagination_to_query.return_value)

    @patch("gobexport.graphql_streaming.json_loads", lambda x: x)
    def test_query_paginated(self, mock_formatter):
        res = {
            None: [
                {'cursor': 'a', 'other': 'field'},
                {'cursor': 'b', 'other': 'field'},
                {'cursor': 'c', 'other': 'field'},
                {'cursor': 'd', 'other': 'field'},
                {'cursor': 'e', 'other': 'field'}
            ],
            'e': [
                {'cursor': 'f', 'other': 'field'},
                {'cursor': 'g', 'other': 'field'},
                {'cursor': 'h', 'other': 'field'},
                {'cursor': 'i', 'other': 'field'},
                {'cursor': 'j', 'other': 'field'}
            ],
            'j': []
        }

        expected_result = res[None] + res['e']

        graphql_streaming = GraphQLStreaming('host', 'query')
        graphql_streaming._query_page = lambda x: res[x]
        graphql_streaming.formatter = MagicMock()
        graphql_streaming.formatter.format_item = lambda x: [x]

        self.assertEqual(expected_result, list(graphql_streaming._query_paginated()))


    def test_add_pagination_to_query(self, mock_formatter):
        batch_size = 802
        after = '4024'

        expected_query = """
{
  theCollection(first: 802, after: 4024) {
    edges {
      node {
        cursor
        fieldA
        fieldB
      }
    }
  }
}
"""
        # Input query should all transform to above result
        input_queries = [
            """
{
  theCollection (first: 203, after: 203) {
    edges {
      node {
        fieldA
        fieldB
      }
    }
  }
}
""",
            """
{
  theCollection {
    edges {
      node {
        cursor
        fieldA
        fieldB
      }
    }
  }
}
""",
            """
{
  theCollection {
    edges {
      node {
        fieldA
        fieldB
      }
    }
  }
}
""",
        ]

        graphql_streaming = GraphQLStreaming('host', 'query')

        for query in input_queries:
            self.assertEqual(expected_query, graphql_streaming._add_pagination_to_query(query, after, batch_size))

        query = """
{
  theCollection {
    edges {
      node {
        fieldA
        fieldB
        cursor
      }
    }
  }
}
"""

        # Cursor is already present at a different position. Should not change.
        expected_query = """
{
  theCollection(first: 802, after: 4024) {
    edges {
      node {
        fieldA
        fieldB
        cursor
      }
    }
  }
}
"""
        self.assertEqual(expected_query, graphql_streaming._add_pagination_to_query(query, after, batch_size))

        query = """
{
  theCollection {
    edges {
      node {
        fieldA
        fieldB
        otherCollection {
          edges {
            node {
              cursor
              fieldC
            }
          }
        }
      }
    }
  }
}
"""

        # Cursor is present in child relation, but not on top level
        expected_query = """
{
  theCollection(first: 802, after: 4024) {
    edges {
      node {
        cursor
        fieldA
        fieldB
        otherCollection {
          edges {
            node {
              cursor
              fieldC
            }
          }
        }
      }
    }
  }
}
"""
        self.assertEqual(expected_query, graphql_streaming._add_pagination_to_query(query, after, batch_size))

