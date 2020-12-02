"""API

Encapsulates a paged API endpoint into an iterator

"""
import time
import ijson

import gobexport.requests as requests
from gobexport.utils import json_loads


class API:

    def __init__(self, host, path, row_formatter=None, secure_user=None):
        """Constructor

        Lazy loading, Just register host and path and wait for the iterator to be called
        to load the data

        :param host:
        :param path:
        """
        self.host = host
        self.path = path
        self.row_formatter = row_formatter
        self.secure_user = secure_user

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
        if "stream=true" in self.path:
            print("Streaming")
            result = requests.urlopen(f'{self.host}{self.path}', secure_user=self.secure_user)
            items = ijson.items(result, prefix='item')
            for item in items:
                yield self.format_item(item)
        elif "ndjson=true" in self.path:
            print("ndjson")
            items = requests.get_stream(f'{self.host}{self.path}', secure_user=self.secure_user)
            for item in items:
                yield self.format_item(json_loads(item))
        else:
            while self.path is not None:
                start = time.time()
                response = requests.get(f'{self.host}{self.path}', secure_user=self.secure_user)
                duration = round(time.time() - start, 2)
                print(f"Query duration for {self.path}: {duration} secs")
                assert response.ok, f"API Response not OK for url {self.path}"
                data = response.json()
                self.path = data['_links']['next']['href']
                for entity in data['results']:
                    yield self.format_item(entity)

    def format_item(self, item):
        if self.row_formatter:
            return self.row_formatter(item)
        else:
            return item
