"""Shared BRK classes and functions."""


from operator import itemgetter
from typing import Optional

import dateutil.parser as dt_parser


class BrkCsvFormat:
    """CSV format class for BRK exports."""

    def _prefix_dict(self, dct: dict, key_prefix: str, val_prefix: str):
        return {f"{key_prefix}{key}": f"{val_prefix}{val}" for key, val in dct.items()}

    def _add_condition_to_attrs(self, condition: dict, attrs: dict):
        return {k: {**condition, "trueval": v} for k, v in attrs.items()}

    def show_when_field_notempty_condition(self, fieldref: str):
        return {
            "condition": "isempty",
            "reference": fieldref,
            "negate": True,
        }

    def show_when_field_empty_condition(self, fieldref: str):
        return {
            "condition": "isempty",
            "reference": fieldref,
        }


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


def brk_directory(file_type="csv", use_sensitive_dir=True):
    """Return BRK directory."""
    dir_part, sensitive_dir_part = itemgetter("dir", "dir_sensitive")(FILE_TYPE_MAPPING[file_type])
    return f"AmsterdamRegio/{sensitive_dir_part}" if use_sensitive_dir else f"AmsterdamRegio/{dir_part}"


def format_timestamp(datetimestr: str, format: str = "%Y%m%d%H%M%S") -> Optional[str]:
    """Transform the datetimestr from ISO-format to the format used in the BRK exports: yyyymmddhhmmss

    :param datetimestr:
    :return:
    """
    if not datetimestr:
        # Input variable may be empty.
        return None

    try:
        dt = dt_parser.parse(datetimestr)
        return dt.strftime(format)
    except ValueError:
        # If invalid datetimestr, just return the original string so that no data is lost.
        return datetimestr


def order_attributes(attrs: dict, ordering: list):
    """Order attributes."""
    assert len(attrs.keys()) == len(ordering), "Number of attributes does not match the number of items to order"
    assert set(attrs.keys()) == set(ordering), "Attribute keys don't match the items to order"

    return {k: attrs[k] for k in ordering}
