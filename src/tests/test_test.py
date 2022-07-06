import datetime
import json
from io import BytesIO, BufferedReader, FileIO

from unittest import TestCase, mock
from unittest.mock import MagicMock, patch, call

import gobexport.test as test

class MockConfig:
    products = {}

def raise_exception():
    raise Exception


class TestExportTest(TestCase):

    def setUp(self):
        self.maxDiff = None

    @patch('gobexport.test.logger', MagicMock())
    def test_get_check(self):
        checks = {
            'key': 'value',
            'any_{DATE}_key': 'any date value'
        }
        self.assertEqual(test._get_check(checks, 'key'), 'value')
        self.assertEqual(test._get_check(checks, 'any_20200130_key'), 'any date value')
        self.assertEqual(test._get_check(checks, 'some other key'), None)

    @patch('gobexport.test.logger', MagicMock())
    def test_low_high(self):
        low, high = test._get_low_high(0.5)
        self.assertEqual(low, 0.47)
        self.assertEqual(high, 0.53)

        low, high = test._get_low_high(0)
        self.assertEqual(low, -1)
        self.assertEqual(high, 1)

        low, high = test._get_low_high(1)
        self.assertEqual(low, 0)
        self.assertEqual(high, 2)

        low, high = test._get_low_high(100)
        self.assertEqual(low, 95)
        self.assertEqual(high, 105)

    @patch('gobexport.test.logger', MagicMock())
    def test_get_analysis(self):
        iso_now = datetime.datetime.now().isoformat()
        obj = BytesIO(b"1234567890")
        len_obj = len(obj.getvalue())
        obj_info = {
            "last_modified": datetime.datetime.now().isoformat(),
            "bytes": len_obj,
            "content_type": "not plain/text",
            "name": "not csv"
        }
        analysis = test._get_analysis(obj_info, obj, 'tmp')
        self.assertEqual(analysis, {
            'age_hours': mock.ANY,
            'bytes': len_obj,
            'first_bytes': mock.ANY
        })

        obj = BytesIO(b"")
        len_obj = len(obj.getvalue())
        obj_info['content_type'] = "plain/text"
        obj_info['bytes'] = len_obj

        analysis = test._get_analysis(obj_info, obj, 'tmp')
        self.assertEqual(analysis, {
            'age_hours': mock.ANY,
            'bytes': len_obj,
            'first_bytes': mock.ANY,
        })

        obj = BytesIO(b"123")
        len_obj = len(obj.getvalue())
        obj_info['content_type'] = "plain/text"
        obj_info['name'] = "any name"
        obj_info['bytes'] = len_obj
        analysis = test._get_analysis(obj_info, obj, 'tmp')
        self.assertEqual(analysis, {
            'age_hours': mock.ANY,
            'bytes': len_obj,
            'first_bytes': mock.ANY,
            'first_line': mock.ANY,
            'first_lines': mock.ANY,
            'chars': len_obj,
            'lines': 1,
            'empty_lines': 0,
            'max_line': len_obj,
            'min_line': len_obj,
            'avg_line': len_obj / 1,
            'digits': 1.0,
            'alphas': 0.0,
            'spaces': 0.0,
            'lowers': 0,
            'uppers': 0
        })

        obj = BytesIO(b"123\n\nabc def")  # 12 chars, 1 zero line
        len_obj = len(obj.getvalue())
        obj_info['content_type'] = "plain/text"
        obj_info['bytes'] = len_obj
        analysis = test._get_analysis(obj_info, obj, 'tmp')
        self.assertEqual(analysis, {
            'age_hours': mock.ANY,
            'bytes': len_obj,
            'first_bytes': mock.ANY,
            'first_line': mock.ANY,
            'second_line': mock.ANY,
            'third_line': mock.ANY,
            'first_lines': mock.ANY,
            'chars': len_obj,
            'lines': 3,
            'empty_lines': 1,
            'max_line': 7,
            'min_line': 3,
            'avg_line': 5.0,
            'digits': 0.25,
            'alphas': 0.5,
            'spaces': 0.25,
            'lowers': 1.0,
            'uppers': 0.0
        })

        obj = BytesIO(b"123\n\nabc def\nx\ny")  # 5 lines
        len_obj = len(obj.getvalue())
        obj_info['content_type'] = "plain/text"
        obj_info['bytes'] = len_obj
        analysis = test._get_analysis(obj_info, obj, 'tmp')
        self.assertEqual(analysis, {
            'age_hours': mock.ANY,
            'bytes': len_obj,
            'first_bytes': mock.ANY,
            'first_line': mock.ANY,
            'second_line': mock.ANY,
            'third_line': mock.ANY,
            'fourth_line': mock.ANY,
            'first_lines': mock.ANY,
            'chars': len_obj,
            'lines': 5,
            'empty_lines': 1,
            'max_line': 7,
            'min_line': 1,
            'avg_line': 3,
            'digits': 0.1875,
            'alphas': 0.5,
            'spaces': 0.3125,
            'lowers': 1.0,
            'uppers': 0.0
        })

        # use digits, lower, upper and spaces.
        obj = BytesIO(b"123\n\nabc DEF\nx\ny")
        len_obj = len(obj.getvalue())
        obj_info['content_type'] = "plain/text"
        obj_info['bytes'] = len_obj
        analysis = test._get_analysis(obj_info, obj, 'tmp')
        self.assertEqual(analysis, {
            'age_hours': mock.ANY,
            'bytes': len_obj,
            'first_bytes': mock.ANY,
            'first_line': mock.ANY,
            'second_line': mock.ANY,
            'third_line': mock.ANY,
            'fourth_line': mock.ANY,
            'first_lines': mock.ANY,
            'chars': len_obj,
            'lines': 5,
            'empty_lines': 1,
            'max_line': 7,
            'min_line': 1,
            'avg_line': 3,
            'digits': 0.1875,
            'alphas': 0.5,
            'spaces': 0.3125,
            'lowers': 0.625,
            'uppers': 0.375
        })

    @patch('gobexport.test.logger')
    def test_get_analysis_log_status(self, mock_logger):
        b = b"a;b" + b"\n".join([b"1;2"] * 255_000)
        obj = BytesIO(b)

        obj_info = {
            "name": "any name",
            "last_modified": datetime.datetime.now().isoformat(),
            "bytes": len(b),
            "content_type": "text/csv"
        }
        test._get_analysis(obj_info, obj, 'tmp')
        mock_logger.info.assert_called_with("Checking lines 250,000")

    @patch('gobexport.test.logger', MagicMock())
    def test_get_analysis_csv(self):
        b = b"a;b;c\n12;;1234\n1;123;1234\n"
        obj = BytesIO(b)
        len_obj = len(b)
        obj_info = {
            "name": "any name",
            "last_modified": datetime.datetime.now().isoformat(),
            "bytes": len_obj,
            "content_type": "text/csv"
        }
        analysis = test._get_analysis(obj_info, obj, 'tmp')

        self.assertEqual(analysis, {
            'age_hours': mock.ANY,
            'bytes': len_obj,
            'first_bytes': mock.ANY,
            'first_line': mock.ANY,
            'second_line': mock.ANY,
            'third_line': mock.ANY,
            # 'fourth_line': mock.ANY,  used to be there, BytesIO last line is not an empty line
            'first_lines': mock.ANY,
            'chars': len_obj,
            'lines': mock.ANY,
            'empty_lines': mock.ANY,
            'max_line': mock.ANY,
            'min_line': mock.ANY,
            'avg_line': mock.ANY,
            'digits': mock.ANY,
            'alphas': mock.ANY,
            'spaces': mock.ANY,
            'lowers': mock.ANY,
            'uppers': mock.ANY,
            'minlength_col_1': 1,
            'maxlength_col_1': 2,
            'minlength_col_2': 0,
            'maxlength_col_2': 3,
            'minlength_col_3': 4,
            'maxlength_col_3': 4
        })

        # check types, mock.ANY.
        types = [
            ('age_hours', float),
            ('first_bytes', str),
            ('first_line', str),
            ('second_line', str),
            ('third_line', str),
            ('lines', int),
            ('empty_lines', int),
            ('max_line', int),
            ('min_line', int),
            ('avg_line', float),
            ('digits', float),
            ('alphas', float),
            ('spaces', float),
            ('lowers', int),
            ('uppers', int)
        ]
        for key, type_ in types:
            print(key)
            self.assertEqual(type(analysis[key]), type_)

    @patch('gobexport.test.logger', MagicMock())
    def test_check_file_margin_string(self):
        filename = 'any filename'
        stats = {
            'equal': 'string'
        }
        check = {
            'equal': ['string']
        }
        self.assertEqual(test._check_file(check, filename, stats), True)

    @patch('gobexport.test.logger', MagicMock())
    def test_check_file(self):
        filename = 'any filename'
        stats = {
            'equal': 1
        }
        check = {
            'equal': [1]
        }
        self.assertEqual(test._check_file(check, filename, stats), True)
        stats['equal'] = 2
        self.assertEqual(test._check_file(check, filename, stats), False)

        stats = {
            '<=': 1
        }
        check = {
            '<=': [None, 2]
        }
        self.assertEqual(test._check_file(check, filename, stats), True)
        stats['<='] = 3
        self.assertEqual(test._check_file(check, filename, stats), False)

        stats = {
            '>=': 1
        }
        check = {
            '>=': [0, None]
        }
        self.assertEqual(test._check_file(check, filename, stats), True)
        stats['>='] = -1
        self.assertEqual(test._check_file(check, filename, stats), False)

        stats = {
            'between': 1
        }
        check = {
            'between': [0, 2]
        }
        self.assertEqual(test._check_file(check, filename, stats), True)
        stats['between'] = 3
        self.assertEqual(test._check_file(check, filename, stats), False)
        stats['between'] = -1
        self.assertEqual(test._check_file(check, filename, stats), False)

    @patch('gobexport.test.logger')
    def test_check_file_warning(self, mock_logger):
        filename = 'fname'
        check = {
            'k1': 'margin',
        }
        stats = []

        test._check_file(check, filename, stats)
        mock_logger.warning.assert_called_with('Value missing for k1 check in fname')

    @patch('gobexport.test.logger', MagicMock())
    def test_propose_check_file(self):
        stats = {
            'age_hours': 100,
            'bytes': 100,
            'first_bytes': "any hash",
            'chars': 100,
            'empty_lines': 1,
            'max_line': 1000,
            'min_line': 100,
            'avg_line': 500,
            'digits': 0.25,
            'alphas': 0.5,
            'spaces': 0.25,
            'lowers': 1.0,
            'uppers': 0.0,
            "[a, b]_is_unique": True
        }
        filename = 'any file'
        proposals = {}
        test._propose_check_file(proposals, filename, stats)
        self.assertEqual(proposals['any file'], {
            'age_hours': [0, 24],
            'bytes': [100, None],
            'first_bytes': ['any hash'],
            'chars': [100, None],
            'empty_lines': [1],
            'max_line': [950, 1050],
            'min_line': [95, 105],
            'avg_line': [475, 525],
            'digits': [0.24, 0.26],
            'alphas': [0.47, 0.53],
            'spaces': [0.24, 0.26],
            'lowers': [0.95, 1.05],
            'uppers': [-0.01, 0.01]
        })
        filename = 'any 20200130 file'
        proposals = {}
        test._propose_check_file(proposals, filename, {})
        self.assertTrue('any {DATE} file' in proposals)

    @patch('gobexport.test.logger', MagicMock())
    @patch('gobexport.test.put_object')
    def test_write_proposals(self, mock_put_object):
        conn_info = {
            'connection': "any connection",
            'container': "any container"
        }
        test._write_proposals(None, 'any catalogue', None, {})
        mock_put_object.assert_not_called()

        proposals = {'any proposal': 'any value'}
        test._write_proposals(conn_info, 'any catalogue', {}, proposals)
        mock_put_object.assert_called_with(
            'any connection',
            'any container',
            'checks.any catalogue.json',
            content_type='application/json',
            contents=json.dumps(proposals, indent=4)
        )

        proposals = {'any proposal': 'any value'}
        test._write_proposals(conn_info, 'any catalogue', {'any check': 'any value'}, proposals)
        mock_put_object.assert_called_with(
            'any connection',
            'any container',
            'checks.any catalogue.proposal.json',
            content_type='application/json',
            contents=json.dumps(proposals, indent=4)
        )

    @patch('gobexport.test.logger', MagicMock())
    @patch('gobexport.test._get_file')
    def test_get_checks(self, mock_get_file):
        conn_info = {
            'connection': "any connection",
            'container': "any container"
        }
        catalogue = "any catalogue"
        container_list = ["list"]

        mock_get_file.return_value = None, BytesIO(b'{}')
        result = test._get_checks(container_list, conn_info, catalogue)
        self.assertEqual(result, {})

        mock_get_file.return_value = None, BytesIO(b"1234")
        result = test._get_checks(container_list, conn_info, catalogue)
        self.assertEqual(result, 1234)

        mock_get_file.return_value = None, BytesIO(b"abc123")
        result = test._get_checks(container_list, conn_info, catalogue)
        self.assertEqual(result, {})

        mock_get_file.return_value = None, None
        result = test._get_checks(container_list, conn_info, catalogue)
        self.assertEqual(result, {})

    @patch('gobexport.test.logger')
    @patch('gobexport.test.get_object')
    def test_get_file(self, mock_get_object, mock_logger):
        conn_info = {
            'connection': "any connection",
            'container': "any container"
        }
        filename = "any filename"

        obj_info, obj = test._get_file([], conn_info, filename)
        self.assertIsNone(obj_info)
        self.assertIsNone(obj)
        mock_get_object.assert_not_called()
        mock_logger.assert_not_called()

        mock_get_object.return_value = b"get object"
        obj_info, obj = test._get_file([{'name': filename}], conn_info, filename)
        self.assertEqual(obj_info, {'name': filename})
        self.assertEqual(obj.read(), b"get object")
        mock_get_object.assert_called_with('any connection', {'name': filename}, 'any container',
                                           chunk_size=None)
        mock_logger.info.assert_called_with(f"Downloading {filename}")
        mock_logger.reset_mock()

        filename = "20201201yz"
        mock_container_list = [
            {'name': '20201101yz', 'last_modified': '100'},
            {'name': '20201103yz', 'last_modified': '300'},
            {'name': '20201102yz', 'last_modified': '200'},
        ]
        mock_get_object.return_value = b"get object"
        obj_info, obj = test._get_file(mock_container_list, conn_info, filename)
        self.assertEqual(obj_info, {'name': '20201103yz', 'last_modified': '300'})
        mock_logger.info.assert_has_calls(
            [call('Downloading 20201101yz'), call('Downloading 20201103yz')]
        )

    @patch('gobexport.test.logger', MagicMock())
    @patch('gobexport.test.get_object')
    def test_get_file_chunks(self, mock_get_object):
        filename = '20201101yz'
        conn_info = {'connection': "any connection", 'container': "any container"}
        mock_container_list = [{'name': '20201101yz', 'last_modified': '100', "bytes": test._OFFLOAD_THRESHOLD + 1}]
        mock_get_object.return_value = BytesIO(b"get object")

        obj_info, obj = test._get_file(mock_container_list, conn_info, filename, destination='/tmp/mock_get_file')

        self.assertIsInstance(obj, FileIO)
        self.assertEqual(open('/tmp/mock_get_file/{DATE}yz', mode='rb').read(), b'get object')
        mock_get_object.assert_called_with(
            connection='any connection',
            object_meta_data=mock_container_list[0],
            dirname='any container',
            chunk_size=test._CHUNKSIZE
        )

        mock_get_object.return_value = BytesIO(b"get object")
        mock_container_list = [{'name': '20201101yz', 'last_modified': '100', "bytes": 0}]
        test._get_file(mock_container_list, conn_info, filename, destination='/tmp/mock_get_file')
        self.assertEqual(open('/tmp/mock_get_file/{DATE}yz', mode='rb').read(), b'get object')

    @patch('gobexport.test.logger')
    @patch('gobexport.test._get_file')
    @patch('gobexport.test._write_proposals')
    @patch('gobexport.test._get_checks')
    @patch('gobexport.test.get_datastore_config')
    @patch('gobexport.test.DatastoreFactory.get_datastore')
    @patch('gobexport.test.distribute_file')
    @patch('gobexport.test.CONTAINER_BASE', 'development')
    @patch('gobexport.test.get_full_container_list', lambda x, y: ["list"])
    def test_test(self, mock_distribute, mock_get_datastore, mock_get_datastore_config, mock_get_checks, mock_write_proposals, mock_get_file, mock_logger):
        catalogue = "any catalogue"
        connection = mock_get_datastore.return_value.connection
        config = MockConfig()

        test._export_config[catalogue] = []
        mock_get_checks.return_value = {}
        test.test(catalogue)
        mock_write_proposals.assert_called_with(
            {'connection': connection, 'container': 'development'},
            'any catalogue',
            {},
            {})

        mock_get_datastore.assert_called_with(mock_get_datastore_config.return_value)

        filename = 'any filename'
        config.products = {
            'any product': {
                'filename': filename
            }
        }

        test._export_config[catalogue] = [config]
        mock_get_checks.return_value = {}
        mock_get_file.return_value = None, None

        test.test(catalogue)
        mock_write_proposals.assert_called_with(
            {'connection': connection, 'container': 'development'},
            'any catalogue',
            {},
            {})

        obj_info = {
            'name': "matched filename",
            'last_modified': datetime.datetime.now().isoformat(),
            'bytes': 100,
            'content_type': 'any content typs'
        }
        mock_get_file.return_value = obj_info, BytesIO(b"123")
        test.test(catalogue)
        mock_write_proposals.assert_called_with(
            {'connection': connection, 'container': 'development'},
            'any catalogue',
            {},
            {filename: {'age_hours': [0, 24], 'bytes': [100, None], 'first_bytes': [mock.ANY]}})

        mock_get_checks.return_value = {
            filename: {
                'bytes': [100]
            }
        }
        mock_get_file.return_value = obj_info, BytesIO(b"123")
        test.test(catalogue)
        mock_write_proposals.assert_called_with(
            {'connection': connection, 'container': 'development'},
            'any catalogue',
            {filename: {'bytes': [100]}},
            {filename: {'age_hours': [0, 24], 'bytes': [100, None], 'first_bytes': [mock.ANY]}})
        mock_distribute.assert_called()

        mock_get_checks.return_value = {
            filename: {
                'bytes': [0]
            }
        }
        mock_get_file.return_value = obj_info, BytesIO(b"123")
        test.test(catalogue)
        mock_write_proposals.assert_called_with(
            {'connection': connection, 'container': 'development'},
            'any catalogue',
            {filename: {'bytes': [0]}},
            {filename: {'age_hours': [0, 24], 'bytes': [100, None], 'first_bytes': [mock.ANY]}})

        # Check case in which check is defined, but filename is missing
        mock_get_file.return_value = None, None
        test.test(catalogue)
        mock_logger.error.assert_called_with("File any filename MISSING")

    def test_check_uniqueness(self):
        check = {}
        test._check_uniqueness(check)
        self.assertEqual(check, {})

        check = {'unique_cols': [[1]]}
        test._check_uniqueness(check)
        self.assertEqual(check, {
            '[1]_is_unique': [True]
        })

        check = {'unique_cols': [[1], [2, 3, 4]]}
        test._check_uniqueness(check)
        self.assertEqual(check, {
            '[1]_is_unique': [True],
            '[2,3,4]_is_unique': [True]

        })

    @patch('gobexport.test.logger', MagicMock())
    @patch("gobexport.test.cleanup_datefiles")
    def test_distribute_file(self, mock_cleanup_datefiles):
        conn_info = {
            'connection': MagicMock(),
            'container': "any container"
        }
        filename = f"{test.EXPORT_DIR}/any filename"
        test.distribute_file(conn_info, filename)
        conn_info['connection'].copy_object.assert_called_with(
            test.CONTAINER_BASE,
            filename,
            f"{test.CONTAINER_BASE}/any filename")
        mock_cleanup_datefiles.assert_called_with(
            conn_info['connection'],
            test.CONTAINER_BASE,
            "any filename")
