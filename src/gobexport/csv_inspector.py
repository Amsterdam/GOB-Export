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
        self.unique_values = {uniques: set() for uniques in self.unique_cols.keys()}

        # Create a dict to store the results, assume all unique_cols are unique (which is the case for no columns)
        # e.g. {'[1, 3]': True, '[5]': True}
        self.cols = {f"{uniques}_is_unique": True for uniques in self.unique_cols.keys()}

        # Count warnings to prevent flooding warnings
        self.warnings = 0

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

    def _log_warning(self, key, value):
        """
        Issue a warning if any duplicate values are found. Stop issuing warnings after MAX_WARNINGS

        :param key:
        :param value:
        :return:
        """
        self.warnings += 1
        if self.warnings <= self.MAX_WARNINGS:
            logger.warning(f"Non unique value found for {key}: {value}")
        if self.warnings == self.MAX_WARNINGS:
            logger.warning(f"More than {self.MAX_WARNINGS} duplicate values found")

    def _check_uniqueness(self, columns):
        """
        Check the given columns for any duplicate values

        :param columns:
        :return:
        """
        for key, col_idxs in self.unique_cols.items():
            # The value is the column values separated by a ".", columns start counting at 0
            value = ".".join(columns[col_idx - 1] for col_idx in col_idxs)
            if value in self.unique_values[key]:
                self.cols[f"{key}_is_unique"] = False
                self._log_warning(key, value)
            else:
                self.unique_values[key].add(value)

    def _check_lengths(self, columns):
        """
        Check the column lengths

        Why min and max per column?
        Suppose you want to assure that a column is either 3 or 8 characters long, but not 5
        Then specify that min is between 3 and 3 and max is between 8 and 8
        If any column should ever have length 5 the constraint is violated

        :param columns:
        :return:
        """
        for i, column in enumerate(columns):
            column_len = len(column)
            self.cols[f"minlength_col_{i + 1}"] = min(column_len, self.cols.get(f"minlength_col_{i + 1}", column_len))
            self.cols[f"maxlength_col_{i + 1}"] = max(column_len, self.cols.get(f"maxlength_col_{i + 1}", column_len))

    def check_columns(self, columns):
        """
        Check the given columns for any duplicate values

        :param columns:
        :return:
        """
        self._check_uniqueness(columns)
        self._check_lengths(columns)

    def check_lines(self, lines):
        # Start at line 1 (skip header) and stop at end of lines. Skip any (possibly trailing) empty line
        for line in [lin for lin in lines[1:] if lin]:
            columns = line.strip().split(";")
            self.check_columns(columns)
        return self.cols
