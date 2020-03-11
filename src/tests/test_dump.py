from unittest import TestCase
from unittest.mock import MagicMock, patch

from gobexport.dump import Dumper

@patch('gobexport.dump.PUBLIC_URL', "public_url")
@patch('gobexport.dump.SECURE_URL', "secure_url")
@patch('gobexport.dump.get_host', lambda : "host/")
@patch('gobexport.dump.get_secure_header', lambda : {'secure': "header"})
@patch('gobexport.dump.logger', MagicMock())
class TestDumper(TestCase):

    @patch('gobexport.dump.os.getenv', lambda s: s)
    def test_create(self):
        dumper = Dumper()
        self.assertEqual(dumper.config['ANALYSE_DATABASE_USER'], "ANALYSE_DATABASE_USER")
        self.assertEqual(dumper.dump_api, "host/secure_url")

    @patch('gobexport.dump.os.getenv', lambda s: None)
    def test_create_with_missing_env(self):
        dumper = Dumper()
        self.assertEqual(dumper.config['ANALYSE_DATABASE_USER'], None)

    def test_update_headers_secure(self):
        dumper = Dumper()
        result = dumper.update_headers("secure_url")
        self.assertEqual(result, {'secure': "header"})

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
    def test_dump_catalog(self):
        dumper = Dumper()
        dumper.get_catalog_collections = MagicMock()
        dumper.get_catalog_collections.return_value = 'any catalog', [{'name': 'any collection'}, {'name': 'any other collection'}]
        dumper.get_relations = MagicMock()
        dumper.get_relations.return_value = [{'name': 'any relation'}]
        dumper.dump_collection = MagicMock()
        dumper.dump_catalog("any catalog", "any collection")
        # Dump collection should be called for the collection and the relation
        self.assertEqual(dumper.dump_collection.call_count, 2)
        dumper.dump_collection.reset_mock()
        dumper.dump_catalog("any catalog", None)
        # Dump collection should be called for all collections and their relations
        self.assertEqual(dumper.dump_collection.call_count, 4)

    @patch('gobexport.dump.time.sleep')
    def test_dump_collection(self, mock_sleep):
        dumper = Dumper()
        dumper.try_dump_collection = MagicMock()
        dumper.try_dump_collection.return_value = True
        dumper.dump_collection('any schema', 'any catalog', 'any collection')
        mock_sleep.assert_not_called()
        dumper.try_dump_collection.assert_called_with('any schema', 'any catalog', 'any collection')
        # Retry
        dumper.try_dump_collection.side_effect = [False, True]
        dumper.dump_collection('any schema', 'any catalog', 'any collection')
        self.assertEqual(mock_sleep.call_count, 1)
        mock_sleep.reset_mock()
        # Stop after 3 tries
        dumper.try_dump_collection.side_effect = [False, False, False, False]
        dumper.dump_collection('any schema', 'any catalog', 'any collection')
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
