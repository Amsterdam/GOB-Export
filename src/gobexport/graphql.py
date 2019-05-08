"""GraphQL

Encapsulates a paged GraphQL endpoint into an iterator

"""
import re
import requests

from gobcore.model import GOBModel

from gobexport.converters.history import convert_to_history_rows

GRAPHQL_ENDPOINT = '/gob/graphql/'
NUM_RECORDS = 100


class GraphQL:

    def __init__(self, host, query, catalogue, collection, expand_history=False):
        """Constructor

        Lazy loading, Just register host and query and wait for the iterator to be called
        to load the data

        :param host:
        :param query:
        :param catalogue:
        :param collection:
        """
        self.host = host
        self.url = self.host + GRAPHQL_ENDPOINT
        self.catalogue = catalogue
        self.collection = collection
        self.expand_history = expand_history
        self.end_cursor = ""
        self.query = self._update_query(query)
        self.has_next_page = True
        self.gob_model = GOBModel().get_collection(self.catalogue, self.collection)

    def __repr__(self):
        """Representation

        Provide for a readable representation
        """
        return f'GraphQL {self.collection}'

    def __iter__(self):
        """Iteration method

        Reads pages and return enitities in each page until no pages left (next == None)

        Raises:
            AssertionError: if endpoint cannot be read

        :return:
        """
        while self.has_next_page:
            response = requests.post(self.url, json={'query': self.query})
            assert response.ok
            data = response.json()

            # Update the cursor and has_next_page
            self.end_cursor = data['data'][self.collection]['pageInfo']['endCursor']
            self.has_next_page = data['data'][self.collection]['pageInfo']['hasNextPage']

            if self.has_next_page:
                self.query = self._update_query(self.query)

            for edge in data['data'][self.collection]['edges']:
                if self.expand_history:
                    history_rows = convert_to_history_rows(self._flatten_edge(edge))
                    for row in history_rows:
                        yield row
                else:
                    yield self._flatten_edge(edge)

    def _flatten_edge(self, edge, main=None):
        """Flatten edges and nodes from the graphql response, places all nested references
        as keys in the main dictionary

        :return: a list of dictionaries
        """
        flat_edge = {}
        for key, value in edge['node'].items():
            # References
            if isinstance(value, dict) and 'edges' in value:
                if main:
                    main.setdefault(key, []).extend([self._flatten_edge(e, main) for e in value['edges']])
                else:
                    flat_edge.setdefault(key, []).extend([self._flatten_edge(e, flat_edge) for e in value['edges']])
            else:
                flat_edge[key] = value
        return flat_edge

    def _update_query(self, query):
        """Updates a graphql query for pagination

        Adds the first and after parameters and the pageInfo node

        :return: updated query
        """
        # First check if the query has a filter
        filters = re.search(f'{self.collection}\((.+)?\)', query)
        if filters:
            # Try to find the after parameter, or else add it
            match = re.search('after:\s?("([a-zA-Z\d=]+)?")', query)
            if match:
                query = query.replace(match[1], f'"{self.end_cursor}"')
            else:
                append_string = f', after: "{self.end_cursor}")' if 'first' in filters[0] \
                    else f', first: {NUM_RECORDS}, after: "{self.end_cursor}")'
                filters_end = filters.span()[1]
                query = query[:filters_end-1] + append_string + query[filters_end:]
        else:
            # Add first and after parameter after the main collection
            query = query.replace(self.collection,
                                  f'{self.collection}(first: {NUM_RECORDS}, after: "{self.end_cursor}")')

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
