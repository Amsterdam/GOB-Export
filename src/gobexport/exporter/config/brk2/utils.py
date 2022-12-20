"""BRK2 utility functions."""


from operator import itemgetter

import dateutil.parser as dt_parser
import requests
from gobexport.config import get_host
from gobexport.utils import ttl_cache

FILE_TYPE_MAPPING = {
    "csv": {
        "dir": "CSV_Actueel",
        "dir_sensitive": "CSV_ActueelMetSubj",
        "extension": "csv",
    },
    "shp": {
        "dir": "SHP_Actueel",
        "dir_sensitive": "SHP_ActueelMetSubj",
        "extension": "shp",
    },
    "dbf": {
        "dir": "SHP_Actueel",
        "dir_sensitive": "SHP_ActueelMetSubj",
        "extension": "dbf",
    },
    "shx": {
        "dir": "SHP_Actueel",
        "dir_sensitive": "SHP_ActueelMetSubj",
        "extension": "shx",
    },
    "prj": {
        "dir": "SHP_Actueel",
        "dir_sensitive": "SHP_ActueelMetSubj",
        "extension": "prj",
    },
    "cpg": {
        "dir": "SHP_Actueel",
        "dir_sensitive": "SHP_ActueelMetSubj",
        "extension": "cpg",
    },
}


# Private Window (token)
@ttl_cache(seconds_to_live=10)
def _get_filename_date():
    """Use BRK2 meta for 'kennisgevingsdatum'."""
    response = requests.get(f"{get_host()}/gob/public/brk2/meta/1/", timeout=30)

    if response.status_code == 404:
        # Only acceptable error response code
        return None

    response.raise_for_status()
    meta = response.json()
    return dt_parser.parse(meta.get("kennisgevingsdatum"))


def brk2_directory(file_type="csv", use_sensitive_dir=True):
    """Return BRK2 directory."""
    dir_part, sensitive_dir_part = itemgetter("dir", "dir_sensitive")(
        FILE_TYPE_MAPPING[file_type]
    )
    return (
        f"AmsterdamRegio/{sensitive_dir_part}"
        if use_sensitive_dir
        else f"AmsterdamRegio/{dir_part}"
    )


def brk2_filename(name, file_type="csv", append_date=True, use_sensitive_dir=True):
    """Return BRK2 file name (path) ."""
    assert file_type in FILE_TYPE_MAPPING, "Invalid file type"
    extension = itemgetter("extension")(FILE_TYPE_MAPPING[file_type])
    if append_date:
        date = _get_filename_date()
        datestr = f"_{date.strftime('%Y%m%d') if date else '00000000'}"
        return f"{brk2_directory(file_type,use_sensitive_dir)}/BRK_{name}{datestr}.{extension}"
    return f"{brk2_directory(file_type,use_sensitive_dir)}/BRK_{name}.{extension}"
