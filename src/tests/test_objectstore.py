import random

from unittest import TestCase
from unittest.mock import patch, MagicMock

from gobexport.objectstore import ObjectstoreFile


class TestObjectstoreFile(TestCase):
    
    @patch("gobexport.objectstore.get_objectstore_config")
    @patch("gobexport.objectstore.connect_to_objectstore")
    @patch("gobexport.objectstore.query_objectstore")
    def test_objectstore(self, mock_query_objectstore, mock_connect, mock_get_objectstore_config):
        mock_config = {
            'objectstore': 'the objectstore',
        }
        
        mock_get_objectstore_config.return_value = {
            'TENANT_NAME': 'mock_objectstore'
        }
        
        mock_objectstore_config = mock_get_objectstore_config.return_value
        mock_connect.return_value = ('mock_connection', 'mock_user')

        objectstore = ObjectstoreFile(mock_config, row_formatter=None)
        mock_connect.assert_called_with(mock_objectstore_config)
        
        mock_query_objectstore.return_value = [1,2,3]
        
        result = [i for i in objectstore]
        self.assertEqual(result, [1, 2, 3])
        
        mock_query_objectstore.assert_called_with(objectstore.connection, objectstore.config)
        
        assert(str(objectstore) == 'Objectstore mock_objectstore')

    @patch("gobexport.objectstore.get_objectstore_config")
    @patch("gobexport.objectstore.connect_to_objectstore")
    @patch("gobexport.objectstore.query_objectstore")
    def test_objectstore_with_formatter(self, mock_query_objectstore, mock_connect, mock_get_objectstore_config):
        mock_config = {
            'objectstore': 'the objectstore',
        }

        row_formatter = lambda x: x + 1

        mock_connect.return_value = ('mock_connection', 'mock_user')

        objectstore = ObjectstoreFile(mock_config, row_formatter=row_formatter)
        mock_query_objectstore.return_value = [1,2,3]

        result = [i for i in objectstore]
        self.assertEqual(result, [2, 3, 4])
