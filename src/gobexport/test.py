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
import dateutil.parser
import hashlib
import json
import math
import re
import statistics
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
_CHUNKSIZE = 500_000_000


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

    # Get test definitions for the given catalogue
    checks = _get_checks(conn_info, catalogue)

    # Make proposals for any missing test definitions
    proposals = {}
    for config in _export_config[catalogue]:
        resolve_config_filenames(config)

        for name, product in config.products.items():
            filenames = [product['filename']] + [product['filename'] for product in product.get('extra_files', [])]

            for filename in filenames:
                # Check the previously exported file at its temporary location
                obj_info, obj_contents = _get_file(conn_info, f"{EXPORT_DIR}/{catalogue}/{filename}")

                if obj_info is None:
                    logger.error(f"File {filename} MISSING")
                    continue

                # Clone check so that changes to the check file don't affect other runs
                if file_checks := copy.deepcopy(_get_check(checks, filename)):
                    # Report results with the name of the matched file
                    matched_filename = obj_info['name']

                    if _run_checks_on_file(obj_info, obj_contents, file_checks, matched_filename):
                        logger.info(f"Check {matched_filename} OK")
                        # Copy the file to its final location
                        distribute_file(conn_info, matched_filename)
                    else:
                        logger.info(f"Check {matched_filename} FAILED")
                else:
                    logger.warning(f"File {filename} UNCHECKED")
                    # Do not copy unchecked files
                _propose_check_file(proposals, filename, obj_info, obj_contents)

    # Write out any missing test definitions
    _write_proposals(conn_info, catalogue, checks, proposals)


def _run_checks_on_file(obj_info, obj_contents, file_checks, matched_filename):
    stats = _get_analysis(obj_info, obj_contents, file_checks)
    return _check_file(file_checks, matched_filename, stats)


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


def _get_file(conn_info, filename):
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
    for item in get_full_container_list(conn_info['connection'], conn_info['container']):
        item_name = item['name']
        for src, dst in _REPLACEMENTS.items():
            item_name = re.sub(dst, src, item_name)

        if item_name == filename and (obj_info is None or item['last_modified'] > obj_info['last_modified']):
            # If multiple matches, match with the most recent item
            obj_info = dict(item)
            obj = get_object(conn_info['connection'], item, conn_info['container'], chunk_size=_CHUNKSIZE)

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


def _get_checks(conn_info, catalogue):
    """
    Get test definitions for the given catalogue

    :param conn_info: Objectstore connection
    :param catalogue: Catalogue name
    :return:
    """
    filename = f"checks.{catalogue}.json"
    _, checks_file = _get_file(conn_info, filename)
    if checks_file is None:
        logger.error(f"Missing checks file: {filename}")
        return {}
    try:
        return json_loads(checks_file.decode("utf-8"))
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


def _propose_check_file(proposals, filename, obj_info, obj):
    """
    Build a proposal to check the given file

    :param filename: Name of the file to check
    :param obj_info: Current file object info
    :param obj: Current file object
    :return: proposal object
    """
    proposal_key = filename
    for src, dst in _REPLACEMENTS.items():
        # heuristic method to convert variable values to a variable name
        if re.search(dst, filename):
            proposal_key = re.sub(dst, src, proposal_key)

    # Base the proposal on the analysis of the current file
    analysis = _get_analysis(obj_info, obj)
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
        check.update(
            {f"{str(uniques)}_is_unique": [True] for uniques in check['unique_cols']}
        )
        del check['unique_cols']


def _fmt(margin):
    return '{:,}'.format(margin) if isinstance(margin, numbers.Number) else '{}'.format(margin)


def _check_file(check, filename, stats):
    """
    Test if all checks that have been defined for the given file are OK

    :param filename: Name of the file to check
    :param stats: Statistics of the file
    :param checks: Check to apply onto the statistics
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


def _get_analysis(obj_info, obj, check=None):
    """
    Get statistics for the given file (object)

    :param obj_info: meta information
    :param obj: contents
    :return:
    """
    ENCODING = 'utf-8'
    check = check or {}

    last_modified = obj_info["last_modified"]
    age = datetime.datetime.now() - dateutil.parser.parse(last_modified)
    age_hours = age.total_seconds() / (60 * 60)

    bytes = obj_info["bytes"]

    first_bytes = hashlib.md5(obj[:10000]).hexdigest()

    base_analysis = {
        "age_hours": age_hours,
        "bytes": bytes,
        "first_bytes": first_bytes
    }

    if obj_info['content_type'] not in ["plain/text", "text/csv", "application/x-ndjson"] or bytes == 0:
        return base_analysis

    content = obj.decode(ENCODING)
    chars = len(content)

    lines = content.split('\n')

    cols = _check_csv(lines, obj_info, check)

    analyses = range(min(max(_NTH.keys()), len(lines)))
    lines_analysis = {f"{_NTH[n + 1]}_line": hashlib.md5(lines[n].encode(ENCODING)).hexdigest() for n in analyses}

    first_lines = '\n'.join(lines[:10])

    line_lengths = [len(line) for line in lines]
    zero_line_lengths = [n for n in line_lengths if n == 0]
    other_line_lengths = [m for m in line_lengths if m > 0]
    avg_line = statistics.mean(other_line_lengths)

    digits = sum(c.isdigit() for c in content)
    alphas = sum(c.isalpha() for c in content)
    spaces = sum(c.isspace() for c in content)
    lowers = sum(c.islower() for c in content)
    uppers = sum(c.isupper() for c in content)

    return {
        **base_analysis,
        **lines_analysis,
        "first_lines": hashlib.md5(first_lines.encode(ENCODING)).hexdigest(),
        "chars": chars,
        "lines": len(lines),
        "empty_lines": len(zero_line_lengths),
        "max_line": max(other_line_lengths),
        "min_line": min(other_line_lengths),
        "avg_line": avg_line,
        "digits": digits / chars,
        "alphas": alphas / chars,
        "spaces": spaces / chars,
        "lowers": 0 if alphas == 0 else lowers / alphas,
        "uppers": 0 if uppers == 0 else uppers / alphas,
        **cols
    }


def _check_csv(lines, obj_info, check):
    """
    Check a csv file for column lengths and duplicate values

    :param lines:
    :param obj_info:
    :return:
    """
    def replace_header_references(uniques: list, header: list):
        """
        Replaces column names in a uniques list with column indexes (1-based)

        Example, with header A;B;C;D;E;F :
            replace_header_references(['A', 'B', 'D']) => [1, 2, 4]
            replace_header_references([1, 2, 5]) => [1, 2, 5]  # Leave as is

        :param uniques:
        :param header:
        :return:
        """
        replaced = [header.index(col) + 1 if isinstance(col, str) else col for col in uniques]

        if uniques != replaced:
            logger.info(f"Interpreting columns {str(uniques)} as {str(replaced)}")

        return replaced

    if obj_info['content_type'] in ["text/csv"] or obj_info['name'][-4:].lower() == ".csv":
        # encode in utf-8 and decode as utf-8-sig to get rid of UTF-8 BOM
        header = lines[0].encode('utf-8').decode('utf-8-sig').strip().split(';')

        if check.get('unique_cols'):
            # Replace column names with column indexes
            check['unique_cols'] = [replace_header_references(uniques, header) for uniques in check['unique_cols']]

        return CSVInspector(obj_info['name'], check).check_lines(lines)
    else:
        return {}
