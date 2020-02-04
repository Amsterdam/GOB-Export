import requests
import dateutil.parser as dt_parser

from requests.exceptions import HTTPError
from operator import itemgetter
from typing import Optional

from gobexport.config import get_host


FILE_TYPE_MAPPING = {
    'csv': {
        'dir': 'CSV_Actueel',
        'extension': 'csv'
    },
    'shp': {
        'dir': 'SHP_Actueel',
        'extension': 'shp'
    },
    'dbf': {
        'dir': 'SHP_Actueel',
        'extension': 'dbf'
    },
    'shx': {
        'dir': 'SHP_Actueel',
        'extension': 'shx'
    },
    'prj': {
        'dir': 'SHP_Actueel',
        'extension': 'prj'
    },
}


def _get_filename_date():
    response = requests.get(f"{get_host()}/gob/brk/meta/1")

    try:
        response.raise_for_status()
    except HTTPError:
        return None

    meta = response.json()
    return dt_parser.parse(meta.get('kennisgevingsdatum'))


def brk_directory(type='csv'):
    type_dir, _ = itemgetter('dir', 'extension')(FILE_TYPE_MAPPING[type])
    return f"AmsterdamRegio/{type_dir}"


def brk_filename(name, type='csv', append_date=True):
    assert type in FILE_TYPE_MAPPING.keys(), "Invalid file type"
    _, extension = itemgetter('dir', 'extension')(FILE_TYPE_MAPPING[type])
    date = _get_filename_date()
    datestr = f"_{date.strftime('%Y%m%d') if date else '00000000'}" if append_date else ""
    return f'{brk_directory(type)}/BRK_{name}{datestr}.{extension}'


def format_timestamp(datetimestr: str, format: str = '%Y%m%d%H%M%S') -> Optional[str]:
    """Transforms the datetimestr from ISO-format to the format used in the BRK exports: yyyymmddhhmmss

    :param datetimestr:
    :return:
    """
    if not datetimestr:
        # Input variable may be empty
        return None

    try:
        dt = dt_parser.parse(datetimestr)
        return dt.strftime(format)
    except ValueError:
        # If invalid datetimestr, just return the original string so that no data is lost
        return datetimestr


def sort_attributes(attrs: dict, ordering: list):
    assert len(attrs.keys()) == len(ordering), "Number of attributes does not match the number of items to sort"
    assert set(attrs.keys()) == set(ordering), "Attribute keys don't match the items to sort"

    return {k: attrs[k] for k in ordering}
