import json
import datetime
import dateutil.parser

from objectstore.objectstore import get_full_container_list, get_object

from gobcore.logging.logger import logger

from gobexport.config import CONTAINER_BASE
from gobexport.connector.objectstore import connect_to_objectstore
from gobexport.exporter.config import nap


export_config = {
    "nap": [nap.PeilmerkenExportConfig]
}


def test(catalogue):
    logger.info(f"Test export for catalogue {catalogue}")

    logger.info(f"Connect to Objectstore")
    connection, _ = connect_to_objectstore()
    container_name = CONTAINER_BASE

    logger.info(f"Load files from {container_name}")
    conn_info = {
        "connection": connection,
        "container": {
            "name": container_name,
            "list": get_full_container_list(connection, container_name)
        }
    }

    logger.info("Load checks")
    checks = get_checks(conn_info)

    if checks is None:
        logger.info(f"No checks defined for {container_name}")
        return

    for config in export_config[catalogue]:
        for name, product in config.products.items():
            filename = product['filename']
            if checks[filename]:
                logger.info(f"Check {filename}")
                obj_info, obj = get_file(conn_info, f"{catalogue}/{filename}")
                stats = get_analyses(obj_info, obj)
                if not check_file(filename, stats, checks):
                    logger.info(f"Check failed for {filename}")
            else:
                logger.warning(f"No checks defined for {filename}")


def get_checks(conn_info):
    _, checks_file = get_file(conn_info, "checks.json")
    return None if checks_file is None else json.loads(checks_file.decode("utf-8"))


def get_file(conn_info, filename):
    for item in conn_info['container']['list']:
        if item["name"] == filename:
            obj_info = dict(item)
            obj = get_object(conn_info['connection'], item, conn_info['container']['name'])
            return obj_info, obj
    return None, None


def check_file(filename, stats, checks):
    check = checks[filename]
    total_result = True
    for key, margin in check.items():
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

        if not result:
            str_value = f"{value:.2f}".replace(".00", "")
            logger.error(f"Check on {key} failed: {str_value} <> {margin}")
    return total_result


def get_analyses(obj_info, obj):
    last_modified = obj_info["last_modified"]
    age = datetime.datetime.now() - dateutil.parser.parse(last_modified)
    age_hours = age.total_seconds() / (60 * 60)

    bytes = obj_info["bytes"]

    content = obj.decode("utf-8")
    chars = len(content)

    lines = content.split('\n')

    line_lengths = [len(line) for line in lines]
    zero_line_lengths = [n for n in line_lengths if n == 0]
    other_line_lengths = [m for m in line_lengths if m > 0]

    digits = sum(c.isdigit() for c in content)
    alphas = sum(c.isalpha() for c in content)
    spaces = sum(c.isspace() for c in content)
    lowers = sum(c.islower() for c in content)
    uppers = sum(c.isupper() for c in content)

    return {
        "age_hours": age_hours,
        "bytes": bytes,
        "chars": chars,
        "empty_lines": len(zero_line_lengths),
        "max_line": max(other_line_lengths),
        "min_line": min(other_line_lengths),
        "digits": digits / chars,
        "alphas": alphas / chars,
        "spaces": spaces / chars,
        "lowers": lowers / alphas,
        "uppers": uppers / alphas
    }
