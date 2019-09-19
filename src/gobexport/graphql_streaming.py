import json
from gobexport.requests import post_stream

from gobexport.formatter.graphql import GraphQLResultFormatter

STREAMING_GRAPHQL_ENDPOINT = '/gob/graphql/streaming/'


class GraphQLStreaming:

    def __init__(self, host, query, unfold=False, sort=None, row_formatter=None):
        self.host = host
        self.query = query

        self.formatter = GraphQLResultFormatter(sort, unfold=unfold, row_formatter=row_formatter)

    def __iter__(self):
        items = post_stream(f'{self.host}{STREAMING_GRAPHQL_ENDPOINT}', {'query': self.query})
        for item in items:
            yield from self.formatter.format_item(json.loads(item))
