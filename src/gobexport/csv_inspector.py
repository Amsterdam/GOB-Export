from collections import defaultdict
from functools import cache

from gobcore.logging.logger import logger


class CSVInspector:

    MAX_WARNINGS = 25

    def __init__(self, filename: str, headerline: str, check: dict):
        """

        :param unique_cols: array of arrays, e.g. [[1, 3], [5]] if col1 + col3, and col5 should contain unique values
        """
        self.filename = filename
        header = headerline.encode('utf-8').decode('utf-8-sig').strip().split(';')
        self.unique_cols = {
            str(unique_cols): self._replace_header_references(unique_cols, header)
            for unique_cols in check.get("unique_cols", [])
        }

        # Create a set of values for each combination, take the string value as the key, e.g. '[1, 3]' and '[5]'
        self.unique_values = {uniques: defaultdict(list) for uniques in self.unique_cols.keys()}

        # Create a dict to store the results, assume all unique_cols are unique (which is the case for no columns)
        # e.g. {'[1, 3]': True, '[5]': True}
        self.cols = {f"{uniques}_is_unique": True for uniques in self.unique_cols.keys()}

        self._log_intro()

    def _replace_header_references(self, uniques: list, header: list):
        """
        Replaces column names in a uniques list with column indexes (1-based)

        Example, with header A;B;C;D;E;F :
            replace_header_references(['A', 'B', 'D']) => [1, 2, 4]
            replace_header_references([1, 2, 5]) => [1, 2, 5]  # Leave as is

        :param uniques:
        :param header:
        :return:
        """
        return [header.index(col) + 1 if isinstance(col, str) else col for col in uniques]

    def _log_intro(self):
        """
        If any unique columns have been defined, log an informational message stating that the file is checked

        :return:
        """
        if self.unique_cols.keys():
            unique_cols = ", ".join([cols for cols in self.unique_cols.keys()])
            logger.info(f"Checking {self.filename} for unique column values in columns {unique_cols}")

    def _collect_values_for_uniquess_check(self, columns: list[str], line_no: int):
        """
        Saves the values for the uniqueness check in the self.unique_values structure

        :param columns:
        :param line_no:
        :return:
        """
        for key, col_idxs in self.unique_cols.items():
            # The value is the column values separated by a ".", columns start counting at 0
            value = ".".join(columns[col_idx - 1] for col_idx in col_idxs)
            self.unique_values[key][value].append(line_no)

    def _filter_non_uniques(self, unique_values: dict[dict[list[int]]]):
        """
        Filters unique_values dict on values that occur in more than one line
        """

        return {
            key: {
                value: lineidxs for value, lineidxs in values.items() if len(lineidxs) > 1
            } for key, values in unique_values.items()}

    def _check_uniqueness(self):
        """
        Performs the actual check for uniqueness on the self.unique_values structure. The unique_values structure is
        built by using repeated calls to self._collect_values_for_uniqueness_check for each line
        """
        non_uniques = self._filter_non_uniques(self.unique_values)

        for key, values in non_uniques.items():
            if not values:
                continue

            if len(values) > self.MAX_WARNINGS:
                logger.warning(f"Found more than {self.MAX_WARNINGS} duplicated values for {key}. "
                               f"Logging first {self.MAX_WARNINGS} values.")

            for value in [v for v in values.keys()][:self.MAX_WARNINGS]:
                lines = ','.join([str(lineno) for lineno in values[value]])
                logger.warning(f"Non unique value found for {key}: {value} on lines {lines}")

            self.cols[f"{key}_is_unique"] = False

    @cache
    def cols_min_len(self, length: int):
        return tuple(f"minlength_col_{i+1}" for i in range(length))

    @cache
    def cols_max_len(self, length: int):
        return tuple(f"maxlength_col_{i+1}" for i in range(length))

    def _check_lengths(self, columns: list[str]):
        """
        Check the column lengths

        Why min and max per column?
        Suppose you want to assure that a column is either 3 or 8 characters long, but not 5
        Then specify that min is between 3 and 3 and max is between 8 and 8
        If any column should ever have length 5 the constraint is violated

        :param columns:
        :return:
        """
        cols = self.cols
        result = {}
        minlen_str = self.cols_min_len(len(columns))
        maxlen_str = self.cols_max_len(len(columns))

        for i, column in enumerate(columns):
            length = len(column)

            try:
                if length < cols[minlen_str[i]]:
                    result[minlen_str[i]] = length
                elif length > cols[maxlen_str[i]]:
                    result[maxlen_str[i]] = length
            except KeyError:
                result[minlen_str[i]] = length
                result[maxlen_str[i]] = length

        if result:
            cols.update(result)

    def _check_columns(self, columns: list[str], line_no: int):
        """
        Check the given columns for any duplicate values

        :param columns:
        :param line_no:
        :return:
        """
        self._collect_values_for_uniquess_check(columns, line_no)
        self._check_lengths(columns)

    def check_lines(self, lines):
        # Start at line 1 (skip header) and stop at end of lines. Skip any (possibly trailing) empty line
        for line_idx, line in enumerate(lines):
            if line and line_idx > 0:
                columns = line.split(";")
                self._check_columns(columns, line_idx + 1)  # +1 = 1 for 0 offset

        self._check_uniqueness()
        self.unique_values.clear()  # clear refs

        return self.cols
