"""API

Encapsulates a paged API endpoint into an iterator

"""
import gobexport.requests as requests


class API:

    def __init__(self, host, path):
        """Constructor

        Lazy loading, Just register host and path and wait for the iterator to be called
        to load the data

        :param host:
        :param path:
        """
        self.host = host
        self.path = path

    def __repr__(self):
        """Representation

        Provide for a readable representation
        """
        return f'API {self.host}{self.path}'

    def __iter__(self):
        """Iteration method

        Reads pages and return enitities in each page until no pages left (next == None)

        Raises:
            AssertionError: if endpoint cannot be read

        :return:
        """
        while self.path is not None:
            response = requests.get(f'{self.host}{self.path}')
            assert response.ok, self.path
            data = response.json()
            self.path = data['_links']['next']['href']
            for entity in data['results']:
                yield entity
