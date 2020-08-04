from gobcore.logging.logger import logger


class CSVInspector:

    MAX_WARNINGS = 25

    def __init__(self, filename, check):
        """

        :param unique_cols: array of arrays, e.g. [[1, 3], [5]] if col1 + col3, and col5 should contain unique values
        """
        self.filename = filename
        self.unique_cols = check.get("unique_cols", [])

        # Create a set of values for each combination, take the string value as the key, e.g. '[1, 3]' and '[5]'
        self.unique_values = {str(uniques): set() for uniques in self.unique_cols}

        # Create a dict to store the results, assume all unique_cols are unique (which is the case for no columns)
        # e.g. {'[1, 3]': True, '[5]': True}
        self.cols = {f"{str(uniques)}_is_unique": True for uniques in self.unique_cols}

        # Count warnings to prevent flooding warnings
        self.warnings = 0

        self._log_intro()

    def _log_intro(self):
        """
        If any unique columns have been defined, log an informational message stating that the file is checked

        :return:
        """
        if self.unique_cols:
            unique_cols = ", ".join([str(cols) for cols in self.unique_cols])
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
        for uniques in self.unique_cols:
            # unique is an array of column indexes
            key = str(uniques)
            # The value is the column values separated by a ".", columns start counting at 0
            value = ".".join(columns[unique - 1] for unique in uniques)
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
        for line in [l for l in lines[1:] if l]:
            columns = line.strip().split(";")
            self.check_columns(columns)
        return self.cols
