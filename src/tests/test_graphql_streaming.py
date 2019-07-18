from unittest import TestCase
from unittest.mock import patch, MagicMock

from gobexport.graphql_streaming import GraphQLStreaming
from typing import Generator


class TestGraphQLStreaming(TestCase):

    @patch("gobexport.graphql_streaming.post_stream")
    @patch("gobexport.graphql_streaming.json.loads", lambda x: 'jl_' + x)
    def test_iter(self, mock_post_stream):
        graphql_streaming = GraphQLStreaming('host', 'query')

        mock_post_stream.return_value = ['a', 'b', 'c', 'd', 'e', 'f']

        expected_result = ['jl_' + item for item in mock_post_stream.return_value]
        self.assertIsInstance(graphql_streaming.__iter__(), Generator)

        result = [item for item in graphql_streaming]
        self.assertEqual(expected_result, result)
