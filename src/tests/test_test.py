import datetime
import json

from unittest import TestCase, mock
from unittest.mock import MagicMock, patch

import gobexport.test as test

class MockConfig:
    products = {}

def raise_exception():
    raise Exception


class TestExportTest(TestCase):

    def setUp(self):
        pass

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
        obj = b"1234567890"
        obj_info = {
            "last_modified": datetime.datetime.now().isoformat(),
            "bytes": len(obj),
            "content_type": "not plain/text"
        }
        analysis = test._get_analysis(obj_info, obj)
        self.assertEqual(analysis, {
            'age_hours': mock.ANY,
            'bytes': len(obj),
            'first_bytes': mock.ANY
        })

        obj = b""
        obj_info['content_type'] = "plain/text"
        obj_info['bytes'] = len(obj)
        analysis = test._get_analysis(obj_info, obj)
        self.assertEqual(analysis, {
            'age_hours': mock.ANY,
            'bytes': len(obj),
            'first_bytes': mock.ANY,
        })

        obj = b"123"
        obj_info['content_type'] = "plain/text"
        obj_info['name'] = "any name"
        obj_info['bytes'] = len(obj)
        analysis = test._get_analysis(obj_info, obj)
        self.assertEqual(analysis, {
            'age_hours': mock.ANY,
            'bytes': len(obj),
            'first_bytes': mock.ANY,
            'first_line': mock.ANY,
            'first_lines': mock.ANY,
            'chars': len(obj),
            'lines': 1,
            'empty_lines': 0,
            'max_line': len(obj),
            'min_line': len(obj),
            'avg_line': len(obj),
            'digits': 1.0,
            'alphas': 0.0,
            'spaces': 0.0,
            'lowers': 0,
            'uppers': 0
        })

        obj = b"123\n\nabc def" # 12 chars
        obj_info['content_type'] = "plain/text"
        obj_info['bytes'] = len(obj)
        analysis = test._get_analysis(obj_info, obj)
        self.assertEqual(analysis, {
            'age_hours': mock.ANY,
            'bytes': len(obj),
            'first_bytes': mock.ANY,
            'first_line': mock.ANY,
            'second_line': mock.ANY,
            'third_line': mock.ANY,
            'first_lines': mock.ANY,
            'chars': len(obj),
            'lines': 3,
            'empty_lines': 1,
            'max_line': 7,
            'min_line': 3,
            'avg_line': 5,
            'digits': 0.25,
            'alphas': 0.5,
            'spaces': 0.25,
            'lowers': 1.0,
            'uppers': 0.0
        })

        obj = b"123\n\nabc def\nx\ny" # 5 lines
        obj_info['content_type'] = "plain/text"
        obj_info['bytes'] = len(obj)
        analysis = test._get_analysis(obj_info, obj)
        self.assertEqual(analysis, {
            'age_hours': mock.ANY,
            'bytes': len(obj),
            'first_bytes': mock.ANY,
            'first_line': mock.ANY,
            'second_line': mock.ANY,
            'third_line': mock.ANY,
            'fourth_line': mock.ANY,
            'first_lines': mock.ANY,
            'chars': len(obj),
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

    @patch('gobexport.test.logger', MagicMock())
    def test_get_analysis_csv(self):
        iso_now = datetime.datetime.now().isoformat()

        obj = b"a;b;c\n12;;1234\n1;123;1234\n"
        obj_info = {
            "name": "any name",
            "last_modified": datetime.datetime.now().isoformat(),
            "bytes": len(obj),
            "content_type": "text/csv"
        }
        analysis = test._get_analysis(obj_info, obj)
        print(analysis)
        self.assertEqual(analysis, {
            'age_hours': mock.ANY,
            'bytes': len(obj),
            'first_bytes': mock.ANY,
            'first_line': mock.ANY,
            'second_line': mock.ANY,
            'third_line': mock.ANY,
            'fourth_line': mock.ANY,
            'first_lines': mock.ANY,
            'chars': len(obj),
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
    @patch('gobexport.test._get_analysis')
    def test_propose_check_file(self, mock_analysis):
        mock_analysis.return_value = {
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
            'uppers': 0.0
        }
        filename = 'any file'
        proposals = {}
        test._propose_check_file(proposals, filename, None, None)
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
        test._propose_check_file(proposals, filename, None, None)
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

        mock_get_file.return_value = None, None
        result = test._get_checks(conn_info, catalogue)
        self.assertEqual(result, {})

        mock_get_file.return_value = None, b"1234"
        result = test._get_checks(conn_info, catalogue)
        self.assertEqual(result, 1234)

        mock_get_file.return_value = None, b"abc123"
        result = test._get_checks(conn_info, catalogue)
        self.assertEqual(result, {})

    @patch('gobexport.test.logger', MagicMock())
    @patch('gobexport.test.get_object')
    @patch('gobexport.test.get_full_container_list')
    def test_get_file(self, mock_get_full_container_list, mock_get_object):
        conn_info = {
            'connection': "any connection",
            'container': "any container"
        }
        filename = "any filename"

        mock_get_full_container_list.return_value = iter([])
        obj_info, obj = test._get_file(conn_info, filename)
        self.assertIsNone(obj_info)
        self.assertIsNone(obj)
        mock_get_object.assert_not_called()

        mock_get_full_container_list.return_value = iter([{'name': filename}])
        mock_get_object.return_value = "get object"
        obj_info, obj = test._get_file(conn_info, filename)
        self.assertEqual(obj_info, {'name': filename})
        self.assertEqual(obj, "get object")
        mock_get_object.assert_called_with('any connection', {'name': filename}, 'any container')

        filename = "20201201yz"
        mock_get_full_container_list.return_value = iter([
            {'name': '20201101yz', 'last_modified': '100'},
            {'name': '20201103yz', 'last_modified': '300'},
            {'name': '20201102yz', 'last_modified': '200'},
        ])
        mock_get_object.return_value = "get object"
        obj_info, obj = test._get_file(conn_info, filename)
        self.assertEqual(obj_info, {'name': '20201103yz', 'last_modified': '300'})

    @patch('gobexport.test.logger')
    @patch('gobexport.test._get_file')
    @patch('gobexport.test._write_proposals')
    @patch('gobexport.test._get_checks')
    @patch('gobexport.test.connect_to_objectstore')
    @patch('gobexport.test.distribute_file')
    @patch('gobexport.test.CONTAINER_BASE', 'development')
    def test_test(self, mock_distribute, mock_connect_to_objectstore, mock_get_checks, mock_write_proposals, mock_get_file, mock_logger):
        catalogue = "any catalogue"
        mock_connect_to_objectstore.return_value = "Any connection", None
        config = MockConfig()

        test._export_config[catalogue] = []
        mock_get_checks.return_value = {}
        test.test(catalogue)
        mock_write_proposals.assert_called_with(
            {'connection': 'Any connection', 'container': 'development'},
            'any catalogue',
            {},
            {})

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
            {'connection': 'Any connection', 'container': 'development'},
            'any catalogue',
            {},
            {})

        mock_get_file.return_value = {
            'name': "matched filename",
            'last_modified': datetime.datetime.now().isoformat(),
            'bytes': 100,
            'content_type': 'any content typs'
                                     }, b"123"
        test.test(catalogue)
        mock_write_proposals.assert_called_with(
            {'connection': 'Any connection', 'container': 'development'},
            'any catalogue',
            {},
            {filename: {'age_hours': [0, 24], 'bytes': [100, None], 'first_bytes': [mock.ANY]}})

        mock_get_checks.return_value = {
            filename: {
                'bytes': [100]
            }
        }
        test.test(catalogue)
        mock_write_proposals.assert_called_with(
            {'connection': 'Any connection', 'container': 'development'},
            'any catalogue',
            {filename: {'bytes': [100]}},
            {filename: {'age_hours': [0, 24], 'bytes': [100, None], 'first_bytes': [mock.ANY]}})
        mock_distribute.assert_called()

        mock_get_checks.return_value = {
            filename: {
                'bytes': [0]
            }
        }
        test.test(catalogue)
        mock_write_proposals.assert_called_with(
            {'connection': 'Any connection', 'container': 'development'},
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

        check = {'unique_cols': [[1], [2,3,4]]}
        test._check_uniqueness(check)
        self.assertEqual(check, {
            '[1]_is_unique': [True],
            '[2, 3, 4]_is_unique': [True]

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
