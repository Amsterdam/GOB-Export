"""
Test export files

Test each exported file.
File characteristics are used to test export files

For all exports:

age hours    age of the file in hours
bytes        length of the file in bytes
first bytes  hash on the first 10,000 bytes

For text exports only:

first line   hash on the first line
first lines  hash on the first 10 lines
chars        Total number of characters in the file
lines        Total number of lines in the file
empty lines  Number of empty lines
max line     maximum line length
min line     minimum line length
avg line     average line length
digits       % numerical characters (digits)
spaces       % whitespace characters (space, tab, newline, ...)
alphas       % alphabetic characters
lowers       % lowercase characters of all alphabetic characters
uppers       % uppercase characters of all alphabetic characters

For CSV exports only (content_type = "text/csv" or filename extension = ".csv":

minlength_col_n   minimum length of column n, e.g. [0, 2]
maxlength_col_n   maximum length of column n, e.g. [10, 15]
unique_cols array of array of columns that should have unique values, e.g. [ [1], [2, 3] ]

"""
import copy
import datetime
from io import TextIOWrapper, BytesIO, BufferedReader, FileIO
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional, Union, Iterator

import dateutil.parser
import hashlib
import json
import math
import re
import numbers

from gobcore.datastore.objectstore import get_full_container_list, get_object, put_object

from gobcore.logging.logger import logger

from gobexport.config import CONTAINER_BASE, EXPORT_DIR, GOB_OBJECTSTORE
from gobconfig.datastore.config import get_datastore_config
from gobcore.datastore.factory import DatastoreFactory
from gobexport.exporter import CONFIG_MAPPING
from gobexport.utils import resolve_config_filenames, json_loads
from gobexport.csv_inspector import CSVInspector
from gobexport.export import cleanup_datefiles

# Collect all export configs
_export_config = {cat: configs.values() for cat, configs in CONFIG_MAPPING.items()}

# Allow for variables in filenames. A variable will be converted into a regular expression
# and vice versa for a generated proposal
_REPLACEMENTS = {
    "{DATE}": "\\d{8}"
}

# Definition of test values
_NTH = {
    1: "first",
    2: "second",
    3: "third",
    4: "fourth"
}
_MAXIMUM_VALUES = ["age_hours"]
_MINIMUM_VALUES = ["bytes", "chars", "lines"]
_ABSOLUTE_VALUES = ["empty_lines", "first_bytes", "first_lines"] + [f"{nth}_line" for nth in _NTH.values()]

# chunksize for downloading from objectstore, must be < 2gb
_CHUNKSIZE = 50_000_000
_OFFLOAD_THRESHOLD = 500_000_000

ENCODING = 'utf-8'
TYPE_FLAT_FILE = ("plain/text", "text/csv", "application/x-ndjson")
TYPE_CSV = ("text/csv", )


def _safe_divide(val1, val2):
    try:
        return val1 / val2
    except ZeroDivisionError:
        return 0


class FlatfileStats:

    def __init__(self, inspector: CSVInspector = None):
        self.chars = 0
        self.lines = 0
        self.digits = 0
        self.alphas = 0
        self.spaces = 0
        self.lowers = 0
        self.uppers = 0
        self.empty_lines = 0
        self.max_line = -1
        self.min_line = -1
        self.total_line = 0

        self.csv_inspector = inspector

        self.first_10 = []

    def calculate(self, lines_checked: int) -> dict:
        if self.csv_inspector:
            self.csv_inspector.check_uniqueness()
            self.csv_inspector.tmp_dir.cleanup()

        return {
            **self._calc_first_lines(),
            **{
                "chars": self.chars,
                "lines": lines_checked,
                "empty_lines": self.empty_lines,
                "max_line": self.max_line,
                "min_line": self.min_line,
                "avg_line": _safe_divide(self.total_line, lines_checked - self.empty_lines),
                "digits": _safe_divide(self.digits, self.chars),
                "alphas": _safe_divide(self.alphas, self.chars),
                "spaces": _safe_divide(self.spaces, self.chars),
                "lowers": _safe_divide(self.lowers, self.alphas),
                "uppers": _safe_divide(self.uppers, self.alphas)
            },
            **(self.csv_inspector.cols if self.csv_inspector else {})
        }

    def _calc_first_lines(self):
        return {
            **{
                f"{_NTH[idx]}_line": hashlib.md5(line.encode(ENCODING)).hexdigest()
                for idx, line in enumerate(self.first_10, 1) if idx <= len(_NTH)
            },
            **{
                "first_lines": hashlib.md5('\n'.join(self.first_10).encode(ENCODING)).hexdigest()
            }
        }

    def check_chars(self, line: bytes):
        len_line = len(line)
        # all chars
        self.chars += len_line

        for idx in range(len_line):
            char = line[idx: idx + 1]
            if char.isalpha():
                self.alphas += 1
                if char.islower():
                    self.lowers += 1
                else:
                    self.uppers += 1
            elif char.isdigit():
                self.digits += 1
            elif char.isspace():  # includes linebreak
                self.spaces += 1

    def check_line(self, line: str):
        min_line = self.min_line
        max_line = self.max_line
        line_len = len(line)

        if line_len == 0:
            self.empty_lines += 1
        else:
            self.total_line += line_len

            if min_line == max_line == -1:
                self.min_line = line_len
                self.max_line = line_len

            elif line_len < min_line:
                self.min_line = line_len
            elif line_len > max_line:
                self.max_line = line_len

        return self

    def check_csv(self, line_no: int, line: bytes):
        if self.csv_inspector and line_no > 1:
            self.csv_inspector.check_line(line, line_no)  # skip header, line no starts at 2

    def check_first_lines(self, line_no: int, line: str):
        """Return hashes for the first min(len(lines, 4) lines and the first 10 lines."""
        if line_no < 10:
            self.first_10.append(line)


def test(catalogue):
    """
    Test export files for a given catalogue

    :param catalogue: catalogue to test
    :return: None
    """
    logger.info(f"Test export for catalogue {catalogue}")

    logger.info("Connect to Objectstore")

    config = get_datastore_config(GOB_OBJECTSTORE)
    datastore = DatastoreFactory.get_datastore(config)
    datastore.connect()
    container_name = CONTAINER_BASE

    logger.info(f"Load files from {container_name}")
    conn_info = {
        "connection": datastore.connection,
        "container": container_name
    }
    # get container_list only once
    container_list = list(get_full_container_list(conn_info["connection"], conn_info["container"]))

    # tmp dir for downloading big files
    tmp_dir = TemporaryDirectory()

    # Get test definitions for the given catalogue
    checks = _get_checks(container_list, conn_info, catalogue)

    # Make proposals for any missing test definitions
    proposals = {}
    for config in _export_config[catalogue]:
        resolve_config_filenames(config)

        for name, product in config.products.items():
            filenames = [product['filename']] + [product['filename'] for product in product.get('extra_files', [])]

            for filename in filenames:
                # Check the previously exported file at its temporary location
                obj_info, obj = _get_file(
                    container_list, conn_info, f"{EXPORT_DIR}/{catalogue}/{filename}", destination=tmp_dir.name
                )

                if obj_info is None:
                    logger.error(f"File {filename} MISSING")
                    continue

                # Clone check so that changes to the check file don't affect other runs
                if file_checks := copy.deepcopy(_get_check(checks, filename)):
                    # Report results with the name of the matched file
                    stats = _get_analysis(obj_info, obj, file_checks)

                    matched_filename = obj_info['name']
                    if _check_file(file_checks, matched_filename, stats):
                        logger.info(f"Check {matched_filename} OK")
                        # Copy the file to its final location
                        # distribute_file(conn_info, matched_filename)
                    else:
                        logger.info(f"Check {matched_filename} FAILED")
                else:
                    # Do not copy unchecked files
                    logger.warning(f"File {filename} UNCHECKED")
                    stats = _get_analysis(obj_info, obj)

                _propose_check_file(proposals, filename, stats)

    # Write out any missing test definitions
    _write_proposals(conn_info, catalogue, checks, proposals)
    tmp_dir.cleanup()


def distribute_file(conn_info, filename):
    """
    Copy the checked file to its final location

    Check and copy is implemented as a indivisible action.
    If the check is OK then the file is copied to its final location in one action.
    The time between the check and the copy action is as short as possible
    So no extra workflow step has been introduced (possible queueing)

    :param conn_info:
    :param filename:
    :return:
    """
    # Remove export dir from filename to get destination file name
    dst = re.sub(rf'^{EXPORT_DIR}/', '', filename)

    # Copy the file to the destination location
    logger.info(f"Distribute to {dst}")
    conn_info['connection'].copy_object(CONTAINER_BASE, filename, f"{CONTAINER_BASE}/{dst}")

    # Do not delete the file from its temporary location because a re-run would cause missing file errors

    # Cleanup any date files at the destination location
    cleanup_datefiles(conn_info['connection'], CONTAINER_BASE, dst)


def _get_file(
        container_list: list, conn_info: dict, filename: str, destination: str = None
) -> tuple[dict[str, str], Optional[BufferedReader]]:
    """
    Get a file from Objectstore

    :param conn_info: Objectstore connection
    :param filename: name of the file to retrieve
    :return:
    """
    # If the filename contains any replacement patterns, use the pattern to find the file
    for src, dst in _REPLACEMENTS.items():
        filename = re.sub(dst, src, filename)

    obj_info = None
    obj = None
    for item in container_list:
        item_name = item['name']
        for src, dst in _REPLACEMENTS.items():
            item_name = re.sub(dst, src, item_name)

        if item_name == filename and (obj_info is None or item['last_modified'] > obj_info['last_modified']):
            # If multiple matches, match with the most recent item
            obj_info = dict(item)

            print("Downloading object", filename)
            if destination and (obj_info["bytes"] > _OFFLOAD_THRESHOLD or obj_info["bytes"] == 0):
                tmp_path = Path(destination, filename)
                tmp_path.parent.mkdir(parents=True, exist_ok=True)

                with open(tmp_path, 'wb') as writer:
                    chunk_gen = get_object(conn_info['connection'], item, conn_info['container'], chunk_size=_CHUNKSIZE)
                    for chunk in chunk_gen:
                        print("Writing chunk... ", f"{_CHUNKSIZE:,}")
                        writer.write(chunk)

                obj = FileIO(tmp_path, mode='rb')
            else:
                obj = BytesIO(get_object(conn_info['connection'], item, conn_info['container'], chunk_size=None))

            obj = BufferedReader(obj)  # wrap different buffers in single (higher level) BufferedReader

    return obj_info, obj


def _get_check(checks, filename):
    """
    Find a test specification (check) for the give filename

    :param checks: all test specifications
    :param filename: a filename, possibly containing variables
    :return: the test specification for the given filename or None if not found
    """
    if checks.get(filename):
        # Simple case, filename without variables
        return checks[filename]

    for check in checks.keys():
        # Try variable substitution
        pattern = re.escape(check)
        for src, dst in _REPLACEMENTS.items():
            pattern = pattern.replace(re.escape(src), dst)
        if re.match(pattern, filename):
            return checks[check]


def _get_checks(container_list, conn_info, catalogue):
    """
    Get test definitions for the given catalogue

    :param conn_info: Objectstore connection
    :param catalogue: Catalogue name
    :return:
    """
    filename = f"checks.{catalogue}.json"
    _, checks_file = _get_file(container_list, conn_info, filename)

    with TextIOWrapper(checks_file, encoding=ENCODING) as buffer:
        checks_file = "".join(buffer)  # line iterator

    try:
        return json_loads(checks_file)
    except TypeError:
        logger.error(f"Missing checks file: {filename}")
    except json.JSONDecodeError as e:
        logger.error(f"JSON error in checks file '{filename}': {str(e)}")

    return {}


def _write_proposals(conn_info, catalogue, checks, proposals):
    """
    Write proposals for missing test definitions to Objectstore

    :param conn_info: Objectstore connection
    :param catalogue: Catalogue name
    :param checks: Current checks for the given catalogue
    :param proposals: Proposals for missing test definitions
    :return: None
    """
    if proposals.keys():
        # Write a proposal file
        # If no checks have yet been defined write an initial check definitions file
        proposal = ".proposal" if checks.keys() else ""
        filename = f"checks.{catalogue}{proposal}.json"
        put_object(conn_info['connection'],
                   conn_info['container'],
                   filename,
                   contents=json.dumps(proposals, indent=4),
                   content_type="application/json")


def _propose_check_file(proposals, filename, stats):
    """
    Build a proposal to check the given file

    :param filename: Name of the file to check
    :return: proposal object
    """
    proposal_key = filename
    for src, dst in _REPLACEMENTS.items():
        # heuristic method to convert variable values to a variable name
        if re.search(dst, filename):
            proposal_key = re.sub(dst, src, proposal_key)

    # Base the proposal on the analysis of the current file
    analysis = {k: v for k, v in stats.items() if not k.endswith("_is_unique")}

    analysis["age_hours"] = 24

    proposal = {}
    for key, value in analysis.items():
        if key in _MAXIMUM_VALUES:
            proposal[key] = [0, value]
        elif key in _MINIMUM_VALUES:
            proposal[key] = [value, None]
        elif key in _ABSOLUTE_VALUES:
            proposal[key] = [value]
        else:
            # Within limits
            low, high = _get_low_high(value)
            proposal[key] = [low, high]

    logger.info(f"Proposal generated for {proposal_key}")
    proposals[proposal_key] = proposal


def _get_low_high(value):
    """
    Get a lower and upper limit for a given value

    :param value: value to evaluate
    :return: low and high limit
    """
    # Use an up-down margin of 5%
    margin = 0.05
    low = value * (1 - margin)
    high = value * (1 + margin)

    # Round the limits to 0.01 for percentages and integers for any other values
    dist = 0.01 if value < 1 else 1
    if value < 1:
        low = round(low, 2)
        high = round(high, 2)

    if low >= value:
        low -= dist
    if high <= value:
        high += dist
    assert low < value < high

    if isinstance(value, int):
        # Use integer bounds for integer values
        low = math.floor(low)
        high = math.ceil(high)

    return low, high


def _check_uniqueness(check):
    if check.get('unique_cols'):
        # Replace the unique_cols key by the outcome of the unique checks
        # don't allow spaces in unique names (list -> str conversion)
        check.update(
            {f"{str(uniques).replace(', ', ',')}_is_unique": [True] for uniques in check['unique_cols']}
        )
        del check['unique_cols']


def _fmt(margin):
    is_number = isinstance(margin, numbers.Number) and not isinstance(margin, bool)
    return f'{margin:,}' if is_number else f'{margin}'


def _check_file(check, filename, stats):
    """
    Test if all checks that have been defined for the given file are OK

    :param filename: Name of the file to check
    :param stats: Statistics of the file
    :param check: Check to apply onto the statistics
    :return: True if all checks succeed
    """
    total_result = True
    _check_uniqueness(check)

    for key, margin in check.items():
        # Get corresponding value for check
        if key not in stats:
            logger.warning(f"Value missing for {key} check in {filename}")
            continue
        value = stats[key]
        if len(margin) == 1:
            result = value == margin[0]
            formatted_margin = f"= {_fmt(margin[0])}"
        elif margin[0] is None:
            result = value <= margin[1]
            formatted_margin = f"<= {_fmt(margin[1])}"
        elif margin[1] is None:
            result = value >= margin[0]
            formatted_margin = f">= {_fmt(margin[0])}"
        else:
            result = margin[0] <= value <= margin[1]
            formatted_margin = f"{_fmt(margin[0])} - {_fmt(margin[1])}"
        total_result = total_result and result

        # Report any errors for the given filename as a group
        str_value = f"{value:,.2f}".replace(".00", "") if type(value) in [float, int] else value
        extra_data = {
            'id': filename,
            'data': {
                key: str_value
            }
        }
        if result:
            extra_data['id'] += " OK"
            logger.info("OK", extra_data)
        else:
            extra_data['data']['margin'] = formatted_margin
            logger.error("Check FAIL", extra_data)
    return total_result


def peek(obj: BufferedReader, size: int) -> bytes:
    cur_pos = obj.tell()
    data = obj.read(size)
    obj.seek(cur_pos)
    return data


def peek_lines(obj: BufferedReader, lines: int = None, start: int = 1) -> Iterator[tuple[int, bytes]]:
    cur_pos = obj.tell()
    line_no = start

    while line := obj.readline():
        yield line_no, line

        if lines and line_no == lines:
            obj.seek(cur_pos)
            break

        line_no += 1


def _get_base_anlysis(obj: BufferedReader, obj_info: dict) -> dict:
    return {
        "age_hours": (
                (datetime.datetime.now() - dateutil.parser.parse(obj_info["last_modified"])).total_seconds() / 3600
        ),
        "bytes": obj_info["bytes"],  # can be zero, file still has content
        "first_bytes": hashlib.md5(peek(obj, 10_000)).hexdigest()
    }


def _get_analysis(obj_info: dict, obj: BufferedReader, check: Optional[dict] = None) -> dict[str, Union[str, float]]:
    """
    Get statistics for the given file (object)

    :param obj_info: meta information
    :param obj: contents
    :return:
    """
    inspector = None

    with obj:
        base = _get_base_anlysis(obj, obj_info)

        if obj_info['content_type'] in TYPE_FLAT_FILE and obj.peek():
            if obj_info['content_type'] in TYPE_CSV or Path(obj_info['name']).suffix.lower() == ".csv":
                _, header = list(peek_lines(obj, 1))[0]
                inspector = CSVInspector(obj_info["name"], header, check)

            stats = FlatfileStats(inspector)

            for line_no, line in peek_lines(obj, start=1):
                # bytes checks
                stats.check_chars(line)

                line = line.strip()   # without linebreaks
                stats.check_csv(line_no, line)

                # text checks
                line = line.decode(ENCODING)
                stats.check_line(line)
                stats.check_first_lines(line_no, line)

            base |= stats.calculate(line_no)

    return base
