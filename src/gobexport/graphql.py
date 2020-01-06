"""GraphQL

Encapsulates a paged GraphQL endpoint into an iterator

"""
import re
import gobexport.requests as requests
import time

from gobcore.model import GOBModel

from gobexport.config import PUBLIC_URL, SECURE_URL
from gobexport.formatter.graphql import GraphQLResultFormatter

GRAPHQL_PUBLIC_ENDPOINT = f'{PUBLIC_URL}/graphql/'
GRAPHQL_SECURE_ENDPOINT = f'{SECURE_URL}/graphql/'
NUM_RECORDS = 1  # Initially ask for only one record
TARGET_DURATION = 30  # Target request duration is 30 seconds


class GraphQL:
    sorter = None

    def __init__(self, host, query, catalogue, collection, expand_history=False, sort=None, unfold=False,
                 row_formatter=None, cross_relations=False, secure=False):
        """Constructor

        Lazy loading, Just register host and query and wait for the iterator to be called
        to load the data

        :param host:
        :param query:
        :param catalogue:
        :param collection:
        """
        self.host = host
        self.url = self.host + (GRAPHQL_SECURE_ENDPOINT if secure else GRAPHQL_PUBLIC_ENDPOINT)
        self.catalogue = catalogue
        self.collection = collection
        self.schema_collection_name = f'{self.catalogue}{self.collection.title()}'
        self.end_cursor = ""
        self.query = self._update_query(query, NUM_RECORDS)
        self.has_next_page = True
        self.gob_model = GOBModel().get_collection(self.catalogue, self.collection)

        self.formatter = GraphQLResultFormatter(expand_history, sort=sort, unfold=unfold, row_formatter=row_formatter,
                                                cross_relations=cross_relations)

    def __repr__(self):
        """Representation

        Provide for a readable representation
        """
        return f'GraphQL {self.schema_collection_name}'

    def __iter__(self):
        """Iteration method

        Reads pages and return enitities in each page until no pages left (next == None)

        Raises:
            AssertionError: if endpoint cannot be read

        :return:
        """
        num_records = NUM_RECORDS
        while self.has_next_page:
            start = time.time()
            print(f"Request {num_records} rows...")
            response = requests.post(self.url, json={'query': self.query})
            end = time.time()
            duration = round(end - start, 2)
            # Adjust number of records to get to the target duration
            correction = TARGET_DURATION / duration
            num_records = max(int(num_records * correction), 1)
            print(f"Request data end ({duration} secs), records set to {num_records}")
            assert response.ok, f"API Response not OK for query {self.query}"
            data = response.json()

            # Update the cursor and has_next_page
            self.end_cursor = data['data'][self.schema_collection_name]['pageInfo']['endCursor']
            self.has_next_page = data['data'][self.schema_collection_name]['pageInfo']['hasNextPage']

            if self.has_next_page:
                self.query = self._update_query(self.query, num_records)

            for edge in data['data'][self.schema_collection_name]['edges']:
                yield from self.formatter.format_item(edge)

    def _update_query(self, query, num_records):
        """Updates a graphql query for pagination

        Adds the first and after parameters and the pageInfo node

        :return: updated query
        """
        # First check if the query has a filter
        filters = re.search(f'{self.schema_collection_name}\s*\((.+)?\)', query)
        if filters:
            # adjust number of records to request
            match = re.search('first:\s?(([\d]+)?)', query)
            if match:
                query = query.replace(match[1], f"{num_records}")

            # Try to find the after parameter, or else add it
            match = re.search('after:\s?("([a-zA-Z\d=]+)?")', query)
            if match:
                query = query.replace(match[1], f'"{self.end_cursor}"')
            else:
                append_string = f', after: "{self.end_cursor}")' if 'first' in filters[0] \
                    else f', first: {num_records}, after: "{self.end_cursor}")'
                filters_end = filters.span()[1]
                query = query[:filters_end-1] + append_string + query[filters_end:]
        else:
            # Add first and after parameter after the main collection
            query = query.replace(self.schema_collection_name,
                                  f'{self.schema_collection_name}(first: {num_records}, after: "{self.end_cursor}")')

        # Add pageInfo if it doesn't exist
        if not re.search('pageInfo', query):
            match = list(re.finditer('}', query))
            """
            Add pageInfo at the correct level of the query
            {
                collection {
                    edges {
                        node {

                        }
                    }
                    pageInfo {}
                }
            }
            """
            pageInfo = 'pageInfo { endCursor, hasNextPage }'
            query = query[:match[-2].span()[0]] + pageInfo + query[match[-2].span()[0]:]

        return query
