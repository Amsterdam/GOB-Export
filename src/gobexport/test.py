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

"""
import json
import hashlib
import statistics
import datetime
import dateutil.parser

from objectstore.objectstore import get_full_container_list, get_object, put_object

from gobcore.logging.logger import logger

from gobexport.config import CONTAINER_BASE
from gobexport.connector.objectstore import connect_to_objectstore
from gobexport.exporter.config import nap, gebieden, meetbouten, bag, test
from gobexport.utils import resolve_config_filenames


# All export configurations per catalogue
_export_config = {
    "nap": nap.configs,
    "gebieden": gebieden.configs,
    "meetbouten": meetbouten.configs,
    "bag": bag.configs,
    "test_catalogue": test.configs
}


def test(catalogue):
    """
    Test export files for a given catalogue

    :param catalogue: catalogue to test
    :return: None
    """
    logger.info(f"Test export for catalogue {catalogue}")

    logger.info(f"Connect to Objectstore")
    connection, _ = connect_to_objectstore()
    container_name = CONTAINER_BASE

    logger.info(f"Load files from {container_name}")
    conn_info = {
        "connection": connection,
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
                obj_info, obj = _get_file(conn_info, f"{catalogue}/{filename}")
                if checks.get(filename):
                    stats = _get_analysis(obj_info, obj)
                    if _check_file(filename, stats, checks):
                        logger.info(f"{filename} OK")
                    else:
                        logger.info(f"{filename} FAILED")
                elif obj_info is None:
                    logger.error(f"{filename} MISSING")
                else:
                    logger.warning(f"{filename} UNCHECKED")
                    proposal = _propose_check_file(filename, obj_info, obj)
                    proposals[filename] = proposal

    # Write out any missing test definitions
    _write_proposals(conn_info, catalogue, checks, proposals)


def _get_file(conn_info, filename):
    """
    Get a file from Objectstore

    :param conn_info: Objectstore connection
    :param filename: name of the file to retrieve
    :return:
    """
    try:
        for item in get_full_container_list(conn_info['connection'], conn_info['container']):
            if item["name"] == filename:
                obj_info = dict(item)
                obj = get_object(conn_info['connection'], item, conn_info['container'])
                return obj_info, obj
    except Exception:
        return None, None


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
        return json.loads(checks_file.decode("utf-8"))
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


def _propose_check_file(filename, obj_info, obj):
    """
    Build a proposal to check the given file

    :param filename: Name of the file to check
    :param obj_info: Current file object info
    :param obj: Current file object
    :return: proposal object
    """
    # Base the proposal on the analysis of the current file
    analysis = _get_analysis(obj_info, obj)
    analysis["age_hours"] = 24

    proposal = {}
    for key, value in analysis.items():
        if key in ["age_hours"]:
            # Maximum value
            proposal[key] = [0, value]
        elif key in ["bytes", "chars", "lines"]:
            # Minimum value
            proposal[key] = [value, None]
        elif key in ["empty_lines", "first_bytes", "first_line", "first_lines"]:
            # Absolute value
            proposal[key] = [value]
        else:
            # Within limits
            low, high = _get_low_high(value)
            proposal[key] = [low, high]
    return proposal


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

    return low, high


def _check_file(filename, stats, checks):
    """
    Test if all checks that have been defined for the given file are OK

    :param filename: Name of the file to check
    :param stats: Statistics of the file
    :param checks: Check to apply onto the statistics
    :return: True if all checks succeed
    """
    check = checks[filename]
    total_result = True
    for key, margin in check.items():
        # Get corresponding value for check
        if key not in stats:
            logger.warning(f"Value missing for {key} check in {filename}")
            continue
        value = stats[key]
        if len(margin) == 1:
            result = value == margin[0]
        elif margin[0] is None:
            result = value <= margin[1]
        elif margin[1] is None:
            result = value >= margin[0]
        else:
            result = margin[0] <= value <= margin[1]
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
            extra_data['data']['margin'] = margin
            logger.error("Check FAIL", extra_data)
    return total_result


def _get_analysis(obj_info, obj):
    """
    Get statistics for the given file (object)

    :param obj_info: meta information
    :param obj: contents
    :return:
    """
    ENCODING = 'utf-8'

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

    first_line = lines[0]
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
        "first_line": hashlib.md5(first_line.encode(ENCODING)).hexdigest(),
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
        "uppers": 0 if uppers == 0 else uppers / alphas
    }
