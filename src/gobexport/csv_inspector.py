import shutil
import subprocess
from collections import defaultdict
from functools import cache
from io import BytesIO
from itertools import islice

from pathlib import Path
from typing import Optional, Iterator
import re

from gobcore.logging.logger import logger

# Store some byte constants used in iteration
BYTE_SPACE = b" "
BYTE_POINT = b"."
BYTE_LE = b"\n"
BYTE_EMPTY = b""


class CSVInspector:
    """
    Check a csv file based on given checks.
    - Unique values in columns defined in the check dict
    - Maximum and minimum value length for all columns
    - Columns to check can be numbers or names

    Usage:
        Initialize a instance with the filename, header checks and a (temporary) dir.
        Iterate over the lines by calling check_line(line, line_no).
        Call check_uniqueness() on the instance to return a dict with statistics.

    Note:
        The instance needs a storage for all the values and linenumbers to check, which can be all values from all
        columns.
        This is done by offloading the data to temporary files per column combination.
        The files are streamed to `sort` and `uniq` and the output with non-uniques is used again.
        If the csv file is very wide and long this way prevents out of memory errors.
    """

    MAX_WARNINGS = 25
    ENCODING = 'utf-8'
    SEP = b";"

    def __init__(self, filename: str, headerline: bytes, check: Optional[dict], tmp_dir: str):
        self.check = check or {}
        self.filename = filename

        # headers should already be stripped of linebreaks and BOM
        header = headerline.decode(self.ENCODING).split(';')

        # remove spaces from keys, doesnt work when writing to file
        self.unique_cols = {
            str(unique_cols).replace(" ", ""): self._replace_header_references(unique_cols, header)
            for unique_cols in self.check.get("unique_cols", [])
        }

        # Create a dict to store the results, assume all unique_cols are unique (which is the case for no columns)
        # e.g. {'[1, 3]': True, '[5]': True}
        self.cols = {f"{uniques}_is_unique": True for uniques in self.unique_cols.keys()}

        # use existing temporary dir, caller is responsible for cleaning up
        self.tmp_dir = tmp_dir

        # Use BytesIO as cache for writing to disk per key
        self._write_cache = {key: BytesIO(b'') for key in self.unique_cols}

        self._log_intro()

    def _replace_header_references(self, uniques: list, header: list) -> list:
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
        If any unique columns have been defined, log an informational message stating that the file is checked.
        """
        if self.unique_cols.keys():
            unique_cols = ", ".join([cols for cols in self.unique_cols.keys()])
            logger.info(f"Checking {self.filename} for unique column values in columns {unique_cols}")

    def _sort_uniq(self, path: Path) -> Iterator[str]:
        """
        Return duplicate values from file in `path`.
        """
        sort_process = None
        uniq_process = None

        try:
            # uniq requires sorted data, sort on the second column
            sort_process = subprocess.Popen(
                args=["/usr/bin/sort", "-k2,2", str(path)],
                stdout=subprocess.PIPE,
                shell=False,
            )
            # pipe stream to uniq, check for duplicates on the second column (skip 1)
            # only keep the duplicates
            uniq_process = subprocess.Popen(
                args=["/usr/bin/uniq", "--all-repeated", "--skip-fields=1"],
                stdin=sort_process.stdout,
                stdout=subprocess.PIPE,
                shell=False,
                text=True
            )
            yield from uniq_process.stdout
        finally:
            if sort_process:
                sort_process.kill()
            if uniq_process:
                uniq_process.kill()

    def _get_path_for_key(self, key: str) -> Path:
        """Return path for `key` with only alphanum and commas."""
        return Path(self.tmp_dir, re.sub(r"[^\w,]+", "", key))

    def _offload_cache(self, key: str):
        """Write BytesIO object for `key` to disk in tmp_dir."""
        with self._write_cache[key] as src, open(self._get_path_for_key(key), mode='wb') as dst:
            src.seek(0)
            shutil.copyfileobj(src, dst)

    def _get_non_uniques(self) -> dict[str, dict[str, list]]:
        """Filters unique values file on values that occur in more than one line."""
        non_unique_values = {uniques: defaultdict(list) for uniques in self.unique_cols.keys()}

        for key in self.unique_cols:
            self._offload_cache(key)

            for line in self._sort_uniq(self._get_path_for_key(key)):
                line_no, value = line.split()
                non_unique_values[key][value].append(line_no)

        return non_unique_values

    def check_uniqueness(self):
        """
        Performs the actual check for uniqueness on the self.unique_values structure. The unique_values structure is
        built by using repeated calls to self._collect_values_for_uniqueness_check for each line
        """
        non_uniques = self._get_non_uniques()

        for key, values in non_uniques.items():
            if not values:
                continue

            if len(values) > self.MAX_WARNINGS:
                logger.warning(
                    f"Found more than {self.MAX_WARNINGS} duplicated values for {key}. "
                    f"Logging first {self.MAX_WARNINGS} values."
                )

            for value, lines in islice(values.items(), self.MAX_WARNINGS):
                logger.warning(
                    f"Non unique value found for {key}: {value} on lines {','.join(lines)}"
                )

            self.cols[f"{key}_is_unique"] = False

        return self.cols

    @cache
    def cols_min_len(self, length: int):
        """Calculates cached minlength strings for columns."""
        return tuple(f"minlength_col_{i+1}" for i in range(length))

    @cache
    def cols_max_len(self, length: int):
        """Calculates cached maxlength strings for columns."""
        return tuple(f"maxlength_col_{i+1}" for i in range(length))

    def _check_lengths(self, columns: list[bytes]):
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
        minlen_str = self.cols_min_len(len(columns))  # cached, called many times with same value
        maxlen_str = self.cols_max_len(len(columns))

        for i, column in enumerate(columns):
            length = len(column)

            try:
                if length < cols[minlen_str[i]]:
                    result[minlen_str[i]] = length
                elif length > cols[maxlen_str[i]]:
                    result[maxlen_str[i]] = length
            except KeyError:
                # The first time we get here, the key is not there
                result[minlen_str[i]] = length
                result[maxlen_str[i]] = length

        if result:
            cols.update(result)  # only update if we have to

    def _collect_values_for_uniquess_check(self, columns: list[bytes], line_no: int):
        """
        Saves the values for the uniqueness check in a BytesIO structure.

        :param columns: values to combine into one
        :param line_no: line number to add
        :return:
        """
        for key, col_idxs in self.unique_cols.items():
            self._write_cache[key].write(
                BYTE_EMPTY.join([
                    str(line_no).encode(self.ENCODING),
                    BYTE_SPACE,
                    BYTE_POINT.join(columns[col_idx - 1] for col_idx in col_idxs),
                    BYTE_LE
                ])
            )

    def check_line(self, line: bytes, line_no: int):
        """Perform checks per line. The byte line assumes line endings are stripped."""
        columns = line.split(self.SEP)
        self._collect_values_for_uniquess_check(columns, line_no)
        self._check_lengths(columns)
