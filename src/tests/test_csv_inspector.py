from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from gobexport.csv_inspector import CSVInspector


class TestCSVInspector(TestCase):

    def test_init(self):
        i = CSVInspector('any filename', '', {})
        self.assertEqual(i.filename, 'any filename')
        self.assertEqual(i.unique_cols, {})

    @patch("gobexport.csv_inspector.logger")
    def test_init_set_unique_cols(self, mock_logger):
        """
        Tests that unique_cols is properly initialised when header names are provided
        """
        i = CSVInspector('any filename', 'a;b;c', {
            'unique_cols': [['a', 'b'], ['c'], ['a', 'c']]
        })
        self.assertEqual({
            "['a', 'b']": [1, 2],
            "['c']": [3],
            "['a', 'c']": [1, 3]
        }, i.unique_cols)
        mock_logger.info.assert_called_with("Checking any filename for unique column values in columns ['a', 'b'], ['c'], ['a', 'c']")

    @patch("gobexport.csv_inspector.logger")
    def test_init_set_unique_cols_decode_utf8_bom(self, mock_logger):
        """
        Tests that unique_cols works properly when UTF-8 BOM is present
        """
        headers = [
            '\ufeffa;b;c\r\n',
            '\ufeffa;b;c\r',
            '\ufeffa;b;c\n',
            '\ufeffa;b;c',
        ]

        for header in headers:
            i = CSVInspector('any filename', header, {
                'unique_cols': [['a', 'b'], ['c'], ['a', 'c']]
            })
            self.assertEqual({
                "['a', 'b']": [1, 2],
                "['c']": [3],
                "['a', 'c']": [1, 3]
            }, i.unique_cols)

    @patch("gobexport.csv_inspector.logger")
    def test_init_set_unique_cols_no_replacement(self, mock_logger):
        """
        Tests that unique_cols is properly initialised when column indexes are provided
        """
        i = CSVInspector('any filename', 'a;b;c', {
            'unique_cols': [[1, 2], [3], [1, 3]]
        })
        self.assertEqual({
            "[1, 2]": [1, 2],
            "[3]": [3],
            "[1, 3]": [1, 3]
        }, i.unique_cols)
        mock_logger.info.assert_called_with("Checking any filename for unique column values in columns [1, 2], [3], [1, 3]")

    @patch("gobexport.csv_inspector.logger")
    def test_log_intro(self, mock_logger):
        i = CSVInspector('any filename', '', {})
        i.unique_cols = {}
        i._log_intro()
        mock_logger.info.assert_not_called()

        i.unique_cols = {'1': [1]}
        i._log_intro()
        mock_logger.info.assert_called()

    @patch("gobexport.csv_inspector.logger")
    def test_collect_values_for_uniquess_check(self, mock_logger):
        i = CSVInspector('any filename', '', {
            'unique_cols': [[1], [2, 3]]
        })

        i._collect_values_for_uniquess_check(['a', 'b', 'c'], 1)
        self.assertEqual({
            '[1]': {
                'a': [1]
            },
            '[2, 3]': {
                'b.c': [1]
            }
        }, i.unique_values)

        i._collect_values_for_uniquess_check(['a', 'b', 'd'], 2)
        self.assertEqual({
            '[1]': {
                'a': [1, 2]
            },
            '[2, 3]': {
                'b.c': [1],
                'b.d': [2]
            }
        }, i.unique_values)

        i._collect_values_for_uniquess_check(['b', 'b', 'd'], 3)
        self.assertEqual({
            '[1]': {
                'a': [1, 2],
                'b': [3]
            },
            '[2, 3]': {
                'b.c': [1],
                'b.d': [2, 3]
            }
        }, i.unique_values)

        i._collect_values_for_uniquess_check(['b', 'b', 'd'], 4)
        self.assertEqual({
            '[1]': {
                'a': [1, 2],
                'b': [3, 4]
            },
            '[2, 3]': {
                'b.c': [1],
                'b.d': [2, 3, 4]
            }
        }, i.unique_values)

    def test_check_lengths(self):
        i = CSVInspector('any filename', '', {})
        self.assertEqual(i.cols, {})

        i._check_lengths(['', 'a', 'bc'])
        i._check_lengths(['', 'ab', 'bc'])
        i._check_lengths(['', 'acdef', 'bc'])
        i._check_lengths(['', 'a', 'bc'])

        self.assertEqual(i.cols, {
            'minlength_col_1': 0,
            'maxlength_col_1': 0,
            'minlength_col_2': 1,
            'maxlength_col_2': 5,
            'minlength_col_3': 2,
            'maxlength_col_3': 2
        })

    def test_check_columns(self):
        i = CSVInspector('any filename', '', {})
        i._collect_values_for_uniquess_check = MagicMock()
        i._check_lengths = MagicMock()
        i._check_columns('any columns', 2)
        i._collect_values_for_uniquess_check.assert_called_with('any columns', 2)
        i._check_lengths.assert_called_with('any columns')

    def test_check_lines(self):
        i = CSVInspector('any filename', '', {})
        i._check_columns = MagicMock()
        lines = [
            'HEADERS',
            'A;B;C\n'
        ]

        i.check_lines(lines)
        i._check_columns.assert_called_with(['A', 'B', 'C'], 2)

    @patch("gobexport.csv_inspector.logger")
    def test_check_lines_unique(self, mock_logger):
        # [a,b] and [c] are non-unique, [d] is unique
        lines = [
            'a;b;c;d',
            '1;2;3;4',
            '1;3;4;5',
            '1;2;2;6',
            '2;3;3;7'
        ]

        i = CSVInspector('any filename', lines[0], {'unique_cols': [['a', 'b'], ['c'], ['d']]})
        res = i.check_lines(lines)

        mock_logger.warning.assert_has_calls([
            call("Non unique value found for ['a', 'b']: 1.2 on lines 2,4"),
            call("Non unique value found for ['c']: 3 on lines 2,5"),
        ])
        self.assertEqual(mock_logger.warning.call_count, 2)

        self.assertEqual({
            "['a', 'b']_is_unique": False,
            "['c']_is_unique": False,
            "['d']_is_unique": True,
            'minlength_col_1': 1,
            'maxlength_col_1': 1,
            'minlength_col_2': 1,
            'maxlength_col_2': 1,
            'minlength_col_3': 1,
            'maxlength_col_3': 1,
            'minlength_col_4': 1,
            'maxlength_col_4': 1
        }, res)

    @patch("gobexport.csv_inspector.logger")
    def test_check_lines_unique_max_warnings(self, mock_logger):
        lines = [
            'a;b;c',
            '1;2;2',
            '2;3;4',
            '3;2;2',
            '4;3;3',
            '5;2;3',
            '6;3;4',
            '7;2;2',
            '8;3;3',
        ]

        i = CSVInspector('any filename', lines[0], {'unique_cols': [['a'], ['c']]})
        i.MAX_WARNINGS = 2

        res = i.check_lines(lines)

        mock_logger.warning.assert_has_calls([
            call("Found more than 2 duplicated values for ['c']. Logging first 2 values."),
            call("Non unique value found for ['c']: 2 on lines 2,4,8"),
            call("Non unique value found for ['c']: 4 on lines 3,7"),
        ])

        self.assertEqual({
            "['a']_is_unique": True,
            "['c']_is_unique": False,
            'minlength_col_1': 1,
            'maxlength_col_1': 1,
            'minlength_col_2': 1,
            'maxlength_col_2': 1,
            'minlength_col_3': 1,
            'maxlength_col_3': 1
        }, res)

    def test_filter_non_uniques(self):
        i = CSVInspector('any filename', '', {})

        non_filtered = {
            'key1': {
                'value1': [1, 2],
                'value2': [3],
                'value3': [4, 7],
                'value4': [5],
            },
            'key2': {
                'value1': [],
                'value2': [2],
            },
            'key3': {
                'value1': [1, 2, 3, 5],
            }
        }

        expected_result = {
            'key1': {
                'value1': [1, 2],
                'value3': [4, 7],
            },
            'key2': {
            },
            'key3': {
                'value1': [1, 2, 3, 5],
            }
        }

        self.assertEqual(expected_result, i._filter_non_uniques(non_filtered))
