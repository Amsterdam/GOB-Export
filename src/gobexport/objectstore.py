"""ObjectstoreFile

Encapsulates a file read from Objectstore into an iterator

"""

from gobconfig.datastore.config import get_datastore_config
from gobcore.datastore.factory import DatastoreFactory
from gobcore.datastore.objectstore import ObjectDatastore


class ObjectstoreFile:

    def __init__(self, config, row_formatter=None):
        """Constructor

        Lazy loading, Just register objectstore connection and reader and wait for the iterator to be called
        to load the data

        :param config:
        """
        self.config = config
        self.objectstore_config = get_datastore_config(self.config['objectstore'])

        self.datastore = DatastoreFactory.get_datastore(self.objectstore_config, self.config)

        assert isinstance(self.datastore, ObjectDatastore)

        self.datastore.connect()
        self.row_formatter = row_formatter

    def __repr__(self):
        """Representation

        Provide for a readable representation
        """
        return f"ObjectstoreFile {self.objectstore_config['TENANT_NAME']}"

    def __iter__(self):
        """Iteration method

        Reads the file and returns enitities

        Raises:
            AssertionError: if file cannot be read

        :return:
        """
        query = self.datastore.query(None)
        for result in query:
            yield self.format_item(result)

    def format_item(self, item):
        if self.row_formatter:
            return self.row_formatter(item)
        else:
            return item
