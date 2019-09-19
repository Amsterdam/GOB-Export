from unittest import TestCase
from unittest.mock import patch, MagicMock

from gobexport.graphql_streaming import GraphQLStreaming, STREAMING_GRAPHQL_ENDPOINT
from typing import Generator


class TestGraphQLStreaming(TestCase):

    @patch("gobexport.graphql_streaming.post_stream")
    @patch("gobexport.graphql_streaming.GraphQLResultFormatter")
    @patch("gobexport.graphql_streaming.json.loads", lambda x: 'jl_' + x)
    def test_iter(self, mock_formatter, mock_post_stream):
        graphql_streaming = GraphQLStreaming('host', 'query', sort='sort')
        mock_formatter.return_value.format_item = lambda x: iter([x])

        mock_post_stream.return_value = ['a', 'b', 'c', 'd', 'e', 'f']

        expected_result = ['jl_' + item for item in mock_post_stream.return_value]
        self.assertIsInstance(graphql_streaming.__iter__(), Generator)

        result = [item for item in graphql_streaming]
        self.assertEqual(expected_result, result)
        mock_formatter.assert_called_with('sort', unfold=False, row_formatter=None)

    @patch("gobexport.graphql_streaming.post_stream")
    @patch("gobexport.graphql_streaming.GraphQLResultFormatter")
    @patch("gobexport.graphql_streaming.json.loads", lambda x: 'jl_' + x)
    def test_iter_with_lists(self, mock_formatter, mock_post_stream):
        graphql_streaming = GraphQLStreaming('host', 'query', sort='sort')
        mock_formatter.return_value.format_item.return_value = ['aa', 'ab', 'ac']

        mock_post_stream.return_value = ['a']

        result = [item for item in graphql_streaming]
        self.assertEqual(['aa', 'ab', 'ac'], result)

    @patch("gobexport.graphql_streaming.post_stream")
    @patch("gobexport.graphql_streaming.GraphQLResultFormatter")
    @patch("gobexport.graphql_streaming.json.loads", lambda x: 'jl_' + x)
    def test_unfold_variable(self, mock_formatter, mock_post_stream):
        graphql_streaming = GraphQLStreaming('host', 'query')
        mock_post_stream.return_value = ['a', 'b']
        result = [i for i in graphql_streaming]

        url = 'host' + STREAMING_GRAPHQL_ENDPOINT
        mock_post_stream.assert_called_with(url, {'query': 'query'})

