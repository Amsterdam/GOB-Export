from unittest import TestCase
from unittest.mock import MagicMock, patch

from gobexport.csv_inspector import CSVInspector


class TestCSVInspector(TestCase):

    def test_init(self):
        i = CSVInspector('any filename', {})
        self.assertEqual(i.filename, 'any filename')
        self.assertEqual(i.unique_cols, [])

    @patch("gobexport.csv_inspector.logger")
    def test_log_intro(self, mock_logger):
        i = CSVInspector('any filename', {})
        i.unique_cols = []
        i._log_intro()
        mock_logger.info.assert_not_called()

        i.unique_cols = [[1]]
        i._log_intro()
        mock_logger.info.assert_called()

    @patch("gobexport.csv_inspector.logger")
    def test_log_warning(self, mock_logger):
        i = CSVInspector('any filename', {})

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
        i = CSVInspector('any filename', {
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
        i = CSVInspector('any filename', {})
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
        i = CSVInspector('any filename', {})
        i._check_uniqueness = MagicMock()
        i._check_lengths = MagicMock()
        i.check_columns('any columns')
        i._check_uniqueness.assert_called_with('any columns')
        i._check_lengths.assert_called_with('any columns')

    def test_check_lines(self):
        i = CSVInspector('any filename', {})
        i.check_columns = MagicMock()
        lines = [
            'HEADERS',
            'A;B;C\n'
        ]

        i.check_lines(lines)
        i.check_columns.assert_called_with(['A', 'B', 'C'])