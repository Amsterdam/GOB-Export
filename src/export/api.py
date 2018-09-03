"""API

Encapsulates a paged API endpoint into a iterator

"""
import requests


class API:

    def __init__(self, host, path):
        self.host = host
        self.path = path

    def __repr__(self):
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
            assert(response.ok)
            data = response.json()
            self.path = data['_links']['next']['href']
            for entity in data['results']:
                yield entity
