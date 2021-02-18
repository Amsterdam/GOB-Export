import requests
import dateutil.parser as dt_parser
import datetime

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
    'dia_csv': {
        'dir': 'DIA_Export',
        'extension': 'csv'
    },
}

_FILENAME_DATE_MAX_AGE_SECONDS = 10

_filename_date = None
_filename_date_expires_at = None


def _get_filename_date():
    global _filename_date, _filename_date_expires_at

    if _filename_date_expires_at is not None and datetime.datetime.utcnow() < _filename_date_expires_at:
        return _filename_date

    response = requests.get(f"{get_host()}/gob/public/brk/meta/1", timeout=5)

    try:
        response.raise_for_status()
    except HTTPError:
        return None

    meta = response.json()
    _filename_date = dt_parser.parse(meta.get('kennisgevingsdatum'))
    _filename_date_expires_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=_FILENAME_DATE_MAX_AGE_SECONDS)
    return _filename_date


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
