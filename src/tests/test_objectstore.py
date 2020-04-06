import random

from unittest import TestCase
from unittest.mock import patch, MagicMock

from gobexport.objectstore import ObjectstoreFile, ObjectDatastore


class TestObjectstoreFile(TestCase):
    
    @patch("gobexport.objectstore.get_datastore_config")
    @patch("gobexport.objectstore.DatastoreFactory")
    def test_objectstore(self, mock_factory, mock_get_datastore_config):
        mock_config = {
            'objectstore': 'the objectstore',
        }
        
        mock_get_datastore_config.return_value = {
            'TENANT_NAME': 'mock_objectstore'
        }
        mock_factory.get_datastore.return_value = MagicMock(spec=ObjectDatastore)
        
        objectstore = ObjectstoreFile(mock_config, row_formatter=None)
        mock_factory.get_datastore.assert_called_with(mock_get_datastore_config.return_value, mock_config)
        mock_factory.get_datastore.return_value.query.return_value = [1, 2, 3]

        result = [i for i in objectstore]
        self.assertEqual(result, [1, 2, 3])

        assert(str(objectstore) == 'ObjectstoreFile mock_objectstore')

    @patch("gobexport.objectstore.get_datastore_config")
    @patch("gobexport.objectstore.DatastoreFactory")
    def test_objectstore_with_formatter(self, mock_factory, mock_get_datastore_config):
        mock_config = {
            'objectstore': 'the objectstore',
        }
        mock_factory.get_datastore.return_value = MagicMock(spec=ObjectDatastore)
        row_formatter = lambda x: x + 1
        objectstore = ObjectstoreFile(mock_config, row_formatter=row_formatter)

        mock_factory.get_datastore.return_value.query.return_value = [1, 2, 3]

        result = [i for i in objectstore]
        self.assertEqual(result, [2, 3, 4])
