import json
import re

from gobexport.requests import post_stream

from gobexport.formatter.graphql import GraphQLResultFormatter

STREAMING_GRAPHQL_ENDPOINT = '/gob/graphql/streaming/'


class GraphQLStreaming:

    def __init__(self, host, query, unfold=False, sort=None, row_formatter=None, cross_relations=False,
                 batch_size=None):
        self.host = host
        self.query = query
        self.batch_size = batch_size

        self.formatter = GraphQLResultFormatter(sort=sort, unfold=unfold, row_formatter=row_formatter,
                                                cross_relations=cross_relations)

        self.current_page = None

    def _execute_query(self, query):
        yield from post_stream(f"{self.host}{STREAMING_GRAPHQL_ENDPOINT}", {'query': query})

    def _query_all(self):
        """Query on the input query as is. Don't add pagination.

        :return:
        """
        for item in self._execute_query(self.query):
            yield from self.formatter.format_item(json.loads(item))

    def _add_pagination_to_query(self, query: str, after: str, batch_size: int):
        existing_arguments_pattern = re.compile(r'^(\s*{\s*)(\w+)\s*\((.*)\)')
        existing_arguments = existing_arguments_pattern.search(query)

        if existing_arguments is not None:
            # Transform arguments to dictionary
            arguments = {k.strip(): v.strip() for k, v in [arg.split(':') for arg in existing_arguments[3].split(',')]}

            # Set first and after, overwrite if already exist
            arguments['first'] = batch_size

            if after is not None:
                arguments['after'] = after

            args_string = ", ".join([f'{k}: {v}' for k, v in arguments.items()])
            paginated_query = existing_arguments_pattern.sub(f'\g<1>\g<2>({args_string})', query, count=1)

        else:
            after_str = f", after: {after}" if after is not None else ""
            # Query does not have any arguments. Add arguments after first word
            paginated_query = re.sub(r'(\w+)', f'\g<0>(first: {batch_size}{after_str})', query, count=1)

        # Add cursor to query if not yet exists on root level.
        if not re.search(r'^\s*{\s*\w+\s*\(?[^\n]*\)?\s*{\s*edges\s*{\s*node\s*{[^{]*cursor', paginated_query):
            return re.sub(r'(node\s*{)(\s*)(\w*)', '\g<1>\g<2>cursor\g<2>\g<3>', paginated_query, count=1)

        return paginated_query

    def _query_page(self, after: str):
        page_query = self._add_pagination_to_query(self.query, after, self.batch_size)
        yield from self._execute_query(page_query)

    def _query_paginated(self):
        last_item = None
        while True:
            items = self._query_page(last_item)
            result_cnt = 0

            for item in items:
                result_cnt += 1

                for formatted_item in self.formatter.format_item(json.loads(item)):
                    last_item = formatted_item['cursor']
                    yield formatted_item

            if result_cnt == 0:
                break

    def __iter__(self):
        if self.batch_size is None:
            yield from self._query_all()
        else:
            yield from self._query_paginated()
