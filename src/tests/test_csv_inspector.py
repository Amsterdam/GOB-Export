from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import MagicMock, call, patch
from codecs import BOM_UTF8
from gobexport.csv_inspector import CSVInspector


class TestCSVInspector(TestCase):

    def test_init(self):
        i = CSVInspector('any filename', b'', {}, 'tmp')
        self.assertEqual(i.filename, 'any filename')
        self.assertEqual(i.unique_cols, {})
        self.assertEqual(i.tmp_dir, 'tmp')

    @patch("gobexport.csv_inspector.logger")
    def test_init_set_unique_cols(self, mock_logger):
        """
        Tests that unique_cols is properly initialised when header names are provided
        """
        i = CSVInspector('any filename', b'a;b;c', {
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
    def test_init_set_unique_cols_decode_utf8_bom(self, mock_logger):
        """
        Tests that unique_cols works properly when UTF-8 BOM is present
        """
        headers = [
            BOM_UTF8 + b'a;b;c\r\n',
            BOM_UTF8 + b'a;b;c\r',
            BOM_UTF8 + b'a;b;c\n',
            BOM_UTF8 + b'a;b;c',
        ]

        for header in headers:
            i = CSVInspector('any filename', header, {
                'unique_cols': [['a', 'b'], ['c'], ['a', 'c']]
            }, 'tmp')
            self.assertEqual({
                "['a','b']": [1, 2],
                "['c']": [3],
                "['a','c']": [1, 3]
            }, i.unique_cols)

    @patch("gobexport.csv_inspector.logger")
    def test_init_set_unique_cols_no_replacement(self, mock_logger):
        """
        Tests that unique_cols is properly initialised when column indexes are provided
        """
        i = CSVInspector('any filename', b'a;b;c', {
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
        i = CSVInspector('any filename', b'', {}, 'tmp')
        i.unique_cols = {}
        i._log_intro()
        mock_logger.info.assert_not_called()

        i.unique_cols = {'1': [1]}
        i._log_intro()
        mock_logger.info.assert_called()

    @patch("gobexport.csv_inspector.logger")
    def test_collect_values_for_uniquess_check(self, mock_logger):
        i = CSVInspector('any filename', b'', {
            'unique_cols': [[1], [2, 3]]
        }, 'tmp')

        i._collect_values_for_uniquess_check([b'a', b'b', b'c'], 1)

        self.assertEqual(i._write_cache["[1]"].getvalue(), b'1 a\n')
        self.assertEqual(i._write_cache["[2,3]"].getvalue(), b'1 b.c\n')

    def test_check_lengths(self):
        i = CSVInspector('any filename', b'', {}, 'tmp')
        self.assertEqual(i.cols, {})

        i._check_lengths([b'', b'a', b'bc'])
        i._check_lengths([b'', b'ab', b'bc'])
        i._check_lengths([b'', b'acdef', b'bc'])
        i._check_lengths([b'', b'a', b'bc'])

        self.assertEqual(i.cols, {
            'minlength_col_1': 0,
            'maxlength_col_1': 0,
            'minlength_col_2': 1,
            'maxlength_col_2': 5,
            'minlength_col_3': 2,
            'maxlength_col_3': 2
        })

    def test_check_line(self):
        i = CSVInspector('any filename', b'', {}, 'tmp')
        i._collect_values_for_uniquess_check = MagicMock()
        i._check_lengths = MagicMock()

        i.check_line(b"A;B;C", 2)

        i._collect_values_for_uniquess_check.assert_called_with([b'A', b'B', b'C'], 2)

    @patch("gobexport.csv_inspector.logger")
    def test_check_lines_unique(self, mock_logger):
        # [a,b] and [c] are non-unique, [d] is unique
        lines = [
            b'a;b;c;d',
            b'1;2;3;4',
            b'1;3;4;5',
            b'1;2;2;6',
            b'2;3;3;7'
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
            b'a;b;c',
            b'1;2;2',
            b'2;3;4',
            b'3;2;2',
            b'4;3;3',
            b'5;2;3',
            b'6;3;4',
            b'7;2;2',
            b'8;3;3',
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
