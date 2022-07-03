import json
import subprocess
from collections import defaultdict
from functools import cache
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional, Iterator
import re

from gobcore.logging.logger import logger


BYTE_LE = b"\n"
BYTE_SPACE = b" "
BYTE_POINT = b"."


class CSVInspector:

    MAX_WARNINGS = 25
    ENCODING = 'utf-8'
    HEADER_ENCODING = 'utf-8-sig'
    SEP = b";"

    def __init__(self, filename: str, headerline: bytes, check: Optional[dict]):
        self.check = check or {}
        self.filename = filename

        header = headerline.decode(self.HEADER_ENCODING).strip().split(';')

        self.unique_cols = {
            str(unique_cols).replace(" ", ""): self._replace_header_references(unique_cols, header)
            for unique_cols in self.check.get("unique_cols", [])
        }

        # Create a dict to store the results, assume all unique_cols are unique (which is the case for no columns)
        # e.g. {'[1, 3]': True, '[5]': True}
        self.cols = {f"{uniques}_is_unique": True for uniques in self.unique_cols.keys()}

        self.tmp_dir = TemporaryDirectory()

        self.unique_fp = {key: open(self._get_path_for_key(key), mode='ab') for key in self.unique_cols}
        self._write_cache = {key: [] for key in self.unique_cols}

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
        try:
            return [header.index(col) + 1 if isinstance(col, str) else col for col in uniques]
        except ValueError as err:
            print("check_file: \n", json.dumps(self.check, indent=2))
            print("header: \n", header)
            raise err

    def _log_intro(self):
        """
        If any unique columns have been defined, log an informational message stating that the file is checked

        :return:
        """
        if self.unique_cols.keys():
            unique_cols = ", ".join([cols for cols in self.unique_cols.keys()])
            logger.info(f"Checking {self.filename} for unique column values in columns {unique_cols}")

    def _sort_uniq(self, path) -> Iterator[str]:
        sort_process = None
        uniq_process = None

        try:
            sort_process = subprocess.Popen(
                args=["/usr/bin/sort", "-k2,2", path],
                stdout=subprocess.PIPE,
                shell=False,
            )
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

    def _get_path_for_key(self, key):
        return Path(self.tmp_dir.name, re.sub(r"[^\w,]+", "", key))

    def get_offloaded_non_uniques(self, key) -> list[str]:
        self.unique_fp[key].writelines(self._write_cache[key])
        self._write_cache[key].clear()

        self.unique_fp[key].close()

        path = self._get_path_for_key(key)

        for line in self._sort_uniq(path):
            yield line.split()

    def _get_non_uniques(self):
        """
        Filters unique_values dict on values that occur in more than one line
        """
        non_unique_values = {uniques: defaultdict(list) for uniques in self.unique_cols.keys()}

        for key, values in self.unique_cols.items():
            for line_no, value in self.get_offloaded_non_uniques(key):
                non_unique_values[key][value].append(line_no)

        # print(non_unique_values)
        return non_unique_values

    def check_uniqueness(self):
        """
        Performs the actual check for uniqueness on the self.unique_values structure. The unique_values structure is
        built by using repeated calls to self._collect_values_for_uniqueness_check for each line
        """
        for key, values in self._get_non_uniques().items():
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

    def _collect_values_for_uniquess_check(self, columns: list[bytes], line_no: int):
        """
        Saves the values for the uniqueness check in the self.unique_values structure

        :param columns:
        :param line_no:
        :return:
        """
        enc = self.ENCODING

        for key, col_idxs in self.unique_cols.items():
            line = str(line_no).encode(enc)
            line += BYTE_SPACE
            line += BYTE_POINT.join(columns[col_idx - 1] for col_idx in col_idxs)
            line += BYTE_LE

            self._write_cache[key].append(line)

        if line_no % 1000 == 0:
            for key in self.unique_cols:
                self.unique_fp[key].writelines(self._write_cache[key])
                self._write_cache[key].clear()

    def check_line(self, line: bytes, line_no: int):
        columns = line.split(self.SEP)
        self._collect_values_for_uniquess_check(columns, line_no)
        self._check_lengths(columns)


    # def _check_columns(self, columns: list[str]):
    #     """
    #     Check the given columns for any duplicate values
    #
    #     :param columns:
    #     :param line_no:
    #     :return:
    #     """

    # def check_lines(self, lines):
    #     # Start at line 1 (skip header) and stop at end of lines. Skip any (possibly trailing) empty line
    #     for line_idx, line in enumerate(lines):
    #         if line and line_idx > 0:
    #             columns = line.split(";")
    #             self._check_columns(columns, line_idx + 1)  # +1 = 1 for 0 offset
    #
    #     self.check_uniqueness()
    #     self.unique_values.clear()  # clear refs
    #
    #     return self.cols

