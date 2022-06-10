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
    def test_log_warning(self, mock_logger):
        i = CSVInspector('any filename', '', {})

        i.warnings = 0
        i._log_warning("any key", "any value")
        self.assertEqual(mock_logger.warning.call_count, 1)
        self.assertEqual(i.warnings, 1)

        mock_logger.warning.reset_mock()
        i.warnings = i.MAX_WARNINGS - 2
        i._log_warning("any key", "any value")
        self.assertEqual(mock_logger.warning.call_count, 1)

        mock_logger.warning.reset_mock()
        i.warnings = i.MAX_WARNINGS - 1
        i._log_warning("any key", "any value")
        self.assertEqual(mock_logger.warning.call_count, 2)

        mock_logger.warning.reset_mock()
        i.warnings = i.MAX_WARNINGS
        i._log_warning("any key", "any value")
        mock_logger.warning.assert_not_called()

    @patch("gobexport.csv_inspector.logger", MagicMock())
    def test_check_uniqueness(self):
        i = CSVInspector('any filename', '', {
            'unique_cols': [[1], [2, 3]]
        })
        i._log_warning = MagicMock()

        i._check_uniqueness(['a', 'b', 'c'])
        i._log_warning.assert_not_called()

        i._log_warning.reset_mock()
        i._check_uniqueness(['a', 'b', 'd'])
        self.assertEqual(i._log_warning.call_count, 1)

        i._log_warning.reset_mock()
        i._check_uniqueness(['b', 'b', 'd'])
        self.assertEqual(i._log_warning.call_count, 1)

        i._log_warning.reset_mock()
        i._check_uniqueness(['b', 'b', 'd'])
        self.assertEqual(i._log_warning.call_count, 2)

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
        i._check_uniqueness = MagicMock()
        i._check_lengths = MagicMock()
        i.check_columns('any columns')
        i._check_uniqueness.assert_called_with('any columns')
        i._check_lengths.assert_called_with('any columns')

    def test_check_lines(self):
        i = CSVInspector('any filename', '', {})
        i.check_columns = MagicMock()
        lines = [
            'HEADERS',
            'A;B;C\n'
        ]

        i.check_lines(lines)
        i.check_columns.assert_called_with(['A', 'B', 'C'])

    @patch("gobexport.csv_inspector.logger")
    def test_check_lines_unique(self, mock_logger):
        lines = [
            'a;b;c',
            '1;2;3',
            '1;3;4',
            '1;2;2',
            '2;3;3'
        ]

        i = CSVInspector('any filename', lines[0], {'unique_cols': [['a', 'b'], ['c']]})

        res = i.check_lines(lines)

        mock_logger.warning.assert_has_calls([
            call("Non unique value found for ['a', 'b']: 1.2"),
            call("Non unique value found for ['c']: 3"),
        ])

        self.assertEqual({
            "['a', 'b']_is_unique": False,
            "['c']_is_unique": False,
            'minlength_col_1': 1,
            'maxlength_col_1': 1,
            'minlength_col_2': 1,
            'maxlength_col_2': 1,
            'minlength_col_3': 1,
            'maxlength_col_3': 1
        }, res)
