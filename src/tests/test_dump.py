from unittest import TestCase
from unittest.mock import MagicMock, patch

from gobexport.dump import Dumper

mock_logger = MagicMock()

@patch('gobexport.dump.PUBLIC_URL', "public_url")
@patch('gobexport.dump.SECURE_URL', "secure_url")
@patch('gobexport.dump.get_host', lambda : "host/")
@patch('gobexport.dump.get_secure_header', lambda x: {'secure user': x})
@patch('gobexport.dump.SECURE_USER', "any secure user")
@patch('gobexport.dump.logger', mock_logger)
@patch('gobexport.dump.get_datastore_config', lambda x: {'datastore': 'config'} if x == 'GOBAnalyse' else None)
class TestDumper(TestCase):

    def test_create(self):
        dumper = Dumper()
        self.assertEqual({'datastore': 'config'}, dumper.db_config)
        self.assertEqual(dumper.dump_api, "host/secure_url")

    def test_update_headers_secure(self):
        dumper = Dumper()
        result = dumper.update_headers("secure_url")
        self.assertEqual(result, {'secure user': "any secure user"})

    def test_update_headers_public(self):
        dumper = Dumper()
        result = dumper.update_headers("any not secure url")
        self.assertEqual(result, {})

    @patch('gobexport.dump.get')
    def test_get_catalog_collections(self, mock_get):
        dumper = Dumper()
        mock_get.return_value.json.return_value = {
            'catalog': 'any catalog',
            '_embedded': {
                'collections': [
                    'collection 1',
                    'collection 2'
                ]
            }
        }
        result = dumper.get_catalog_collections('any catalog name')
        self.assertEqual(result, ({'catalog': 'any catalog'}, ['collection 1', 'collection 2']))

    @patch('gobexport.dump.get')
    def test_get_relations(self, mock_get):
        dumper = Dumper()
        catalog = {
            'abbreviation': 'Cat'
        }
        collection = {
            'abbreviation': 'Col'
        }
        mock_get.return_value.json.return_value = {
            '_embedded': {
                'collections': [
                    {
                        'name': 'cat_col_rel'
                    },
                    {
                        'name': 'tac_loc_rel'
                    }
                ]
            }
        }
        result = dumper.get_relations(catalog, collection)
        self.assertEqual(result, [{'name': "cat_col_rel"}])

    @patch('gobexport.dump.get', MagicMock())
    def test_dump(self):
        dumper = Dumper()
        dumper.get_catalog_collections = MagicMock()
        dumper.get_catalog_collections.return_value = 'any catalog', [{'name': 'any collection'}, {'name': 'any other collection'}]
        dumper.get_relations = MagicMock()
        dumper.get_relations.return_value = [{'name': 'any relation'}]
        dumper._dump_collection = MagicMock()
        dumper.dump("any catalog", "any collection")
        # Dump collection should be called for the collection and the relation
        self.assertEqual(dumper._dump_collection.call_count, 2)
        dumper._dump_collection.reset_mock()

        dumper.dump("any catalog", "any collection", False)
        self.assertEqual(dumper._dump_collection.call_count, 1)

        # Check missing collection. Should not make a difference when include_relations == False
        mock_logger.reset_mock()
        dumper.dump("any catalog", "not found collection", False)
        mock_logger.error.assert_not_called()

        # Check missing collection. Should make a different when include_relations == True
        mock_logger.reset_mock()
        dumper.dump("any catalog", "not found collection", True)
        mock_logger.error.assert_called_with("Collection not found collection could not be found in any catalog")

    @patch('gobexport.dump.time.sleep')
    def test_dump_collection(self, mock_sleep):
        dumper = Dumper()
        dumper.try_dump_collection = MagicMock()
        dumper.try_dump_collection.return_value = True
        dumper._dump_collection('any schema', 'any catalog', 'any collection')
        mock_sleep.assert_not_called()
        dumper.try_dump_collection.assert_called_with('any schema', 'any catalog', 'any collection', False)

        # With force_full True
        dumper._dump_collection('any schema', 'any catalog', 'any collection', force_full=True)
        mock_sleep.assert_not_called()
        dumper.try_dump_collection.assert_called_with('any schema', 'any catalog', 'any collection', True)

        # Retry
        dumper.try_dump_collection.side_effect = [False, True]
        dumper._dump_collection('any schema', 'any catalog', 'any collection')
        self.assertEqual(mock_sleep.call_count, 1)
        mock_sleep.reset_mock()
        # Stop after 3 tries
        dumper.try_dump_collection.side_effect = [False, False, False, False]
        dumper._dump_collection('any schema', 'any catalog', 'any collection')
        self.assertEqual(mock_sleep.call_count, Dumper.MAX_TRIES)

    @patch('gobexport.dump.requests.post')
    def test_try_dump_collection(self, mock_post):
        dumper = Dumper()

        mock_post.return_value.iter_lines.return_value = [b"line 1", b"line 2"]
        result = dumper.try_dump_collection('any schema', 'any catalog', 'any collection')
        self.assertFalse(result)

        mock_post.return_value.iter_lines.return_value = [123]
        result = dumper.try_dump_collection('any schema', 'any catalog', 'any collection')
        self.assertFalse(result)

        mock_post.return_value.iter_lines.return_value = [b"line 1", b"line 2", b"Export completed"]
        result = dumper.try_dump_collection('any schema', 'any catalog', 'any collection')
        self.assertTrue(result)
        mock_post.assert_called_with(
            url='host/secure_url/dump/any catalog/any collection/',
            json={
                "db": {"datastore": "config"},
                "schema": "any schema",
                "include_relations": False,
                "force_full": False,
            },
            headers={'Content-Type': 'application/json', 'secure user': 'any secure user'},
            stream=True,
        )

        # Assert post is called with the correct arguments if force_full True
        mock_post.return_value.iter_lines.return_value = [123]
        result = dumper.try_dump_collection('any schema', 'any catalog', 'any collection', True)
        self.assertFalse(result)
        mock_post.assert_called_with(
            url='host/secure_url/dump/any catalog/any collection/',
            json={
                "db": {"datastore": "config"},
                "schema": "any schema",
                "include_relations": False,
                "force_full": True,
            },
            headers={'Content-Type': 'application/json', 'secure user': 'any secure user'},
            stream=True,
        )
