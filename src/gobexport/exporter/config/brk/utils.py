import requests
import dateutil.parser as dt_parser
from operator import itemgetter
from typing import Optional

from gobexport.config import get_host
from gobexport.utils import ttl_cache

FILE_TYPE_MAPPING = {
    'csv': {
        'dir': 'CSV_Actueel',
        'dir_sensitive': 'CSV_ActueelMetSubj',
        'extension': 'csv'
    },
    'shp': {
        'dir': 'SHP_Actueel',
        'dir_sensitive': 'SHP_ActueelMetSubj',
        'extension': 'shp'
    },
    'dbf': {
        'dir': 'SHP_Actueel',
        'dir_sensitive': 'SHP_ActueelMetSubj',
        'extension': 'dbf'
    },
    'shx': {
        'dir': 'SHP_Actueel',
        'dir_sensitive': 'SHP_ActueelMetSubj',
        'extension': 'shx'
    },
    'prj': {
        'dir': 'SHP_Actueel',
        'dir_sensitive': 'SHP_ActueelMetSubj',
        'extension': 'prj'
    },
    'cpg': {
        'dir': 'SHP_Actueel',
        'dir_sensitive': 'SHP_ActueelMetSubj',
        'extension': 'cpg'
    },
}


@ttl_cache(seconds_to_live=10)
def _get_filename_date():
    response = requests.get(f"{get_host()}/gob/public/brk/meta/1/", timeout=30)

    if response.status_code == 404:
        # Only acceptable error response code
        return None

    response.raise_for_status()
    meta = response.json()
    return dt_parser.parse(meta.get('kennisgevingsdatum'))


def brk_directory(type='csv', use_sensitive_dir=True):
    dir_part, sensitive_dir_part = itemgetter('dir', 'dir_sensitive')(FILE_TYPE_MAPPING[type])
    return f'AmsterdamRegio/{sensitive_dir_part}' if use_sensitive_dir else f'AmsterdamRegio/{dir_part}'


def brk_filename(name, type='csv', append_date=True, use_sensitive_dir=True):
    assert type in FILE_TYPE_MAPPING.keys(), "Invalid file type"
    extension = itemgetter('extension')(FILE_TYPE_MAPPING[type])
    if append_date:
        date = _get_filename_date()
        datestr = f"_{date.strftime('%Y%m%d') if date else '00000000'}"
        return f'{brk_directory(type,use_sensitive_dir)}/BRK_{name}{datestr}.{extension}'
    else:
        return f'{brk_directory(type,use_sensitive_dir)}/BRK_{name}.{extension}'


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
