from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import call, patch
from gobexport.csv_inspector import CSVInspector


class TestCSVInspector(TestCase):

    def test_init(self):
        i = CSVInspector('any filename', [], {}, 'tmp')
        self.assertEqual(i.filename, 'any filename')
        self.assertEqual(i.unique_cols, {})
        self.assertEqual(i.tmp_dir, 'tmp')

    @patch("gobexport.csv_inspector.logger")
    def test_init_set_unique_cols(self, mock_logger):
        """
        Tests that unique_cols is properly initialised when header names are provided
        """
        i = CSVInspector('any filename', ["a", "b", "c"], {
            'unique_cols': [['a', 'b'], ['c'], ['a', 'c']]
        }, 'tmp')
        self.assertEqual({
            "['a','b']": [1, 2],
            "['c']": [3],
            "['a','c']": [1, 3]
        }, i.unique_cols)

        msg = "Checking any filename for unique column values in columns ['a','b'], ['c'], ['a','c']"
        mock_logger.info.assert_called_with(msg)

    @patch("gobexport.csv_inspector.logger")
    def test_init_set_unique_cols_no_replacement(self, mock_logger):
        """
        Tests that unique_cols is properly initialised when column indexes are provided
        """
        i = CSVInspector('any filename', ["a", "b", "c"], {
            'unique_cols': [[1, 2], [3], [1, 3]]
        }, 'tmp')
        self.assertEqual({
            "[1,2]": [1, 2],
            "[3]": [3],
            "[1,3]": [1, 3]
        }, i.unique_cols)
        mock_logger.info.assert_called_with("Checking any filename for unique column values in columns [1,2], [3], [1,3]")

    @patch("gobexport.csv_inspector.logger")
    def test_log_intro(self, mock_logger):
        i = CSVInspector('any filename', [], {}, 'tmp')
        i.unique_cols = {}
        i._log_intro()
        mock_logger.info.assert_not_called()

        i.unique_cols = {'1': [1]}
        i._log_intro()
        mock_logger.info.assert_called()

    @patch("gobexport.csv_inspector.logger")
    def test_collect_values_for_uniquess_check(self, _):
        i = CSVInspector('any filename', [], {
            'unique_cols': [[1], [2, 3]]
        }, 'tmp')

        i._collect_values_for_uniquess_check(['a', 'b', 'c'], 1)

        self.assertEqual(i._write_cache["[1]"].getvalue(), '1 a\n')
        self.assertEqual(i._write_cache["[2,3]"].getvalue(), '1 b.c\n')

    def test_check_lengths(self):
        i = CSVInspector('any filename', [], {}, 'tmp')
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

    @patch("gobexport.csv_inspector.logger")
    def test_check_lines_unique(self, mock_logger):
        # [a,b] and [c] are non-unique, [d] is unique
        lines = [
            ['a', 'b', 'c', 'd'],
            ["1", "2", "3", "4"],
            ["1", "3", "4", "5"],
            ["1", "2", "2", "6"],
            ["2", "3", "3", "7"],
        ]

        with TemporaryDirectory() as tmp_dir:
            i = CSVInspector('any filename', lines[0], {'unique_cols': [['a', 'b'], ['c'], ['d']]}, tmp_dir)
            for nr, l in enumerate(lines[1:], start=1):
                i.check_line(l, nr + 1)

            i.check_uniqueness()

        mock_logger.warning.assert_has_calls([
            call("Non unique value found for ['a','b']: 1.2 on lines 2,4"),
            call("Non unique value found for ['c']: 3 on lines 2,5"),
        ])
        self.assertEqual(mock_logger.warning.call_count, 2)

        self.assertEqual({
            "['a','b']_is_unique": False,
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
        }, i.cols)

    @patch("gobexport.csv_inspector.logger")
    def test_check_lines_unique_max_warnings(self, mock_logger):
        lines = [
            ["a", "b", "c"],
            ["1", "2", "2"],
            ["2", "3", "4"],
            ["3", "2", "2"],
            ["4", "3", "3"],
            ["5", "2", "3"],
            ["6", "3", "4"],
            ["7", "2", "2"],
            ["8", "3", "3"],
        ]
        with TemporaryDirectory() as tmp_dir:
            i = CSVInspector('any filename', lines[0], {'unique_cols': [['a'], ['c']]}, tmp_dir)
            i.MAX_WARNINGS = 2

            for nr, l in enumerate(lines[1:], start=2):
                i.check_line(l, nr)

            i.check_uniqueness()

        mock_logger.warning.assert_has_calls([
            call("Found more than 2 duplicated values for ['c']. Logging first 2 values."),
            call("Non unique value found for ['c']: 2 on lines 2,4,8"),
            call("Non unique value found for ['c']: 3 on lines 5,6,9"),
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
        }, i.cols)
