import json
from gobexport.requests import post_stream

STREAMING_GRAPHQL_ENDPOINT = '/gob/graphql/streaming/'


class GraphQLStreaming:

    def __init__(self, host, query):
        self.host = host
        self.query = query

    def __iter__(self):
        items = post_stream(f'{self.host}{STREAMING_GRAPHQL_ENDPOINT}', {'query': self.query})

        for item in items:
            yield json.loads(item)
