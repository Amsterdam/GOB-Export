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
import itertools
from codecs import BOM_UTF8
from collections import Counter
from io import TextIOWrapper, BytesIO, FileIO
from itertools import islice
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional, Union, IO

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
_CHUNKSIZE = 100_000_000
# download files bigger then this threshold to disk
_OFFLOAD_THRESHOLD = 500_000_000

# read chunk size from IOstream
READ_CHUNK_SIZE = 10_000_000

ENCODING = 'utf-8-sig'
STRIP_CHARS = BOM_UTF8 + b"\t\n\r\v\f"

TYPE_FLAT_FILE = ("plain/text", "text/csv", "application/x-ndjson")
TYPE_CSV = ("text/csv", )


def _safe_divide(val1: int, val2: int) -> Union[int, float]:
    try:
        result = val1 / val2
    except ZeroDivisionError:
        return 0
    else:
        if result.is_integer():
            return int(result)
        return round(result, 4)


class FlatfileStats:

    def __init__(self):
        self.chars = 0
        self.lines = 0
        self.digits = 0
        self.alphas = 0
        self.spaces = 0
        self.lowers = 0
        self.uppers = 0
        self.empty_lines = 0
        self.max_line = 0
        self.min_line = 0
        self.total_line = 0
        self.first_10: list[bytes] = []
        self.counter: dict[str, int] = Counter()

    def calculate(self) -> dict:
        """Return a dict of flatfile statistics for characters and lines."""
        counts = self.counter

        self.chars = sum(counts.values())
        self.uppers = sum(cnt for char, cnt in counts.items() if char.isupper())
        self.lowers = sum(cnt for char, cnt in counts.items() if char.islower())
        self.digits = sum(cnt for char, cnt in counts.items() if char.isdigit())
        self.spaces = sum(cnt for char, cnt in counts.items() if char.isspace())
        self.alphas = self.uppers + self.lowers

        return {
            **self._hash_first_lines(),
            **{
                "chars": self.chars,
                "lines": self.lines,
                "empty_lines": self.empty_lines,
                "max_line": self.max_line,
                "min_line": self.min_line,
                "avg_line": _safe_divide(self.total_line, self.lines - self.empty_lines),
                "digits": _safe_divide(self.digits, self.chars),
                "alphas": _safe_divide(self.alphas, self.chars),
                "spaces": _safe_divide(self.spaces, self.chars),
                "lowers": _safe_divide(self.lowers, self.alphas),
                "uppers": _safe_divide(self.uppers, self.alphas)
            }
        }

    def _hash_first_lines(self) -> dict[str, str]:
        """
        Return dict with hashed first N lines and first 10 lines. First line == header if present.
        The hash should be equal for lines with different line breaks and byte order marks (if present).
        """
        return (
            {f"{idx}_line": hashlib.md5(line).hexdigest() for idx, line in zip(_NTH.values(), self.first_10)}
            |
            {"first_lines": hashlib.md5(b'\n'.join(self.first_10)).hexdigest()}
        )

    def count_lines(self, line_length: int):
        """
        Update line length statistics:
        - empty
        - maximum
        - minimum
        - total
        - number of lines seen
        """
        self.empty_lines += line_length == 0
        self.total_line += line_length

        if (line_length and line_length < self.min_line) or self.lines == 0:
            self.min_line = line_length
        if line_length and line_length > self.max_line:
            self.max_line = line_length

        self.lines += 1


def test(catalogue):
    """
    Test export files for a given catalogue.

    :param catalogue: catalogue to test
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
    # get full container_list only once
    container_list = list(get_full_container_list(conn_info["connection"], conn_info["container"]))

    # tmp dir for downloading/offloading files
    tmp_dir = TemporaryDirectory()

    # Get test definitions for the given catalogue
    checks = _get_checks(container_list, conn_info, catalogue)

    # Make proposals for any missing test definitions
    proposals = {}
    for config in _export_config[catalogue]:
        resolve_config_filenames(config)

        # get the unique products based on filename, input needs to be sorted
        unique_products = itertools.groupby(
            iterable=sorted(config.products.values(), key=lambda x: x["filename"]),
            key=lambda x: x["filename"]
        )

        for _, product in unique_products:
            product = next(product)  # product is iterable, get first one

            filenames = [product['filename']] + [product['filename'] for product in product.get('extra_files', [])]

            for filename in filenames:
                obj_info, obj = _get_file(
                    container_list, conn_info, f"{EXPORT_DIR}/{catalogue}/{filename}", destination=tmp_dir.name
                )

                if obj_info is None:
                    logger.error(f"File {filename} MISSING")
                    continue

                # Clone check so that changes to the check file don't affect other runs
                if file_checks := copy.deepcopy(_get_check(checks, filename)):
                    stats = _get_analysis(obj_info, obj, check=file_checks, tmp_dir=tmp_dir.name)

                    # Report results with the name of the matched file
                    matched_filename = obj_info['name']
                    if _check_file(file_checks, matched_filename, stats):
                        logger.info(f"Check {matched_filename} OK")
                        # Copy the file to its final location
                        distribute_file(conn_info, matched_filename)
                    else:
                        logger.info(f"Check {matched_filename} FAILED")
                else:
                    # Do not copy unchecked files
                    logger.warning(f"File {filename} UNCHECKED")
                    stats = _get_analysis(obj_info, obj, tmp_dir=tmp_dir.name)

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
) -> tuple[dict[str, str], Optional[IO]]:
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

            logger.info(f"Downloading {item['name']}")
            # if obj_info["bytes"] == 0 we dont know the size, offload to be sure
            if destination and (obj_info["bytes"] > _OFFLOAD_THRESHOLD or obj_info["bytes"] == 0):
                tmp_path = Path(destination, filename)
                tmp_path.parent.mkdir(parents=True, exist_ok=True)

                with open(tmp_path, 'wb') as writer:
                    chunk_gen = get_object(
                        connection=conn_info['connection'],
                        object_meta_data=item,
                        dirname=conn_info['container'],
                        chunk_size=_CHUNKSIZE
                    )

                    for chunk in chunk_gen:
                        writer.write(chunk)

                obj = FileIO(tmp_path, mode='rb')
            else:
                obj = BytesIO(get_object(conn_info['connection'], item, conn_info['container'], chunk_size=None))

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

    try:
        with TextIOWrapper(checks_file, encoding='utf-8') as buffer:
            return json_loads("".join(buffer))
    except (AttributeError, TypeError):
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


def _check_file(check: dict[str, str], filename: str, stats: dict[str, str]):
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


def _peek(obj: IO, size: int) -> bytes:
    cur_pos = obj.tell()
    data = obj.read(size)
    obj.seek(cur_pos)
    return data


def _get_base_anlysis(obj: IO, obj_info: dict) -> dict[str, str]:
    return {
        "age_hours":
            (datetime.datetime.now() - dateutil.parser.parse(obj_info["last_modified"])).total_seconds() / 3600,
        "bytes": obj_info["bytes"],  # can be zero, file still has content
        "first_bytes": hashlib.md5(_peek(obj, 10_000)).hexdigest()
    }


def _read_text(obj: IO) -> str:
    """
    Read text from IO buffer, tries to decode using utf-8.
    In case of UnicodeDecodeError add up to 4 extra bytes and try again.
    After 4 extra bytes raises the UnicodeDecodeError
    """
    bytes_obj = obj.read(READ_CHUNK_SIZE)
    error = None

    for extra in range(0, 4):
        bytes_obj += obj.read(extra)

        try:
            return bytes_obj.decode(ENCODING)
        except UnicodeDecodeError as err:
            # we may end up with split bytes
            error = err

    if error:
        raise error


def _get_analysis(
    obj_info: dict,
    obj: IO,
    tmp_dir: str,
    check: Optional[dict] = None
) -> dict[str, Union[str, float, int]]:
    """
    Return statistics for the given object.
    Object can be stored in memory or on disk, using the same interface.

    :param obj_info: meta information
    :param obj: contents in bytes using BytesIO or FileIO backed by a file on disk
    :param check: checks to perform on csv file
    :param tmp_dir: Temporary dir for offloading
    :return: dict
    """
    is_flatfile = obj_info['content_type'] in TYPE_FLAT_FILE
    is_csv = obj_info['content_type'] in TYPE_CSV or Path(obj_info['name']).suffix.lower() == ".csv"

    with obj:
        base = _get_base_anlysis(obj, obj_info)

        if not _peek(obj, 1):
            return base  # empty object

        if is_flatfile:
            stats = FlatfileStats()

            obj.seek(0)
            while chunk := _read_text(obj):
                stats.counter.update(chunk)

            obj.seek(0)
            stats.first_10 = [line.strip(STRIP_CHARS) for line in islice(obj, 10)]

            header = stats.first_10[0]
            inspector = CSVInspector(obj_info["name"], header, check, tmp_dir)
            stats.count_lines(len(header))

            obj.seek(0)
            for idx, line in enumerate(islice(obj, 1, None), 1):  # skip header
                line = line.strip(STRIP_CHARS)
                stats.count_lines(len(line))

                if is_csv:
                    inspector.check_line(line, idx)

                if idx % 250_000 == 0:
                    logger.info(f"Checking lines {idx:,}")  # report status, can take some time

    assert obj.closed, "Object not closed."

    base |= stats.calculate() if is_flatfile else {}
    base |= inspector.check_uniqueness() if is_csv else {}
    return base
