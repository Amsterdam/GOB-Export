"""Meetbouten types

This module contains logic to convert Meetbouten types to the correct export format.

Some conversions contain logic to make the output comparable with the DIVA output.
This can for instance be seen in the _to_geometry method

Todo: The final model for the meetbouten collection is required
    The storage of the entities and the publication by the API in this format is required
    to finish the conversion methods. Especially the None tests should be re-evaluated

"""

import datetime
import re

from gobcore.utils import ProgressTicker

from gobexport.exporter.utils import nested_entity_get


def _to_plain(value, *args):
    """Convert to plain string value

    :param value:
    :param args:
    :return:
    """
    return str(value)


def _to_string(value, mapping=None):
    """Convert to string

    Strings are enclosed in $$

    Example:
        X => $$X$$
        1,{"1": "A", "3": "V"} => $$A$$

    :param value:
    :param mapping: A dictionary of values to convert using a mapping. E.g. {1:"A", 3:"V"}
    :return:
    """
    # Get the mapped value if a mapping is provided, as mapping is returned as a string we need to evaluate it
    try:
        value = eval(mapping)[value] if mapping else value
    except KeyError:
        pass

    assert(type(value) is str or value is None)
    value = '' if value is None or value == '' else str(f'$${value}$$').replace("\r", "").replace("\n", " ")
    return value


def _to_boolean(value, *args):
    """Convert to boolean

    True => "", False or None => "N"

    :param value:
    :return:
    """
    assert(type(value) is bool or value is None)
    return _to_string('' if value is True else 'N')


def _to_number(value, precision=None):
    """Convert to number

    The decimal dot is replaced by a comma

    Example:
        2.5 => 2,5

    :param value:
    :return:
    """
    assert(type(value) in [int, float, str] or value is None)
    value = format(value, f'.{precision}f') if precision and value else value
    return '' if value is None else str(value)\
        .replace('.', ',')


def _to_date(value, *args):
    """Convert to date

    Date parsing and conversion is used for implicit date validation

    Example:
        2020-05-20 => 20200520

    :param value:
    :return:
    """
    assert(type(value) is str or value is None)
    return _to_string(
        '' if value is None else datetime.datetime.strptime(value, "%Y-%m-%d").date().strftime("%Y%m%d"))


def _to_geometry(value, *args):
    """Convert to geometry

    The geometry is translated to match the DIVA output format.

    Example:

        {
            type: "Point",
            coordinates: [
                119411.7,
                487201.6
            ]
        }
        Output: POINT (119411.7 487201.6)

    :param value:
    :return:
    """
    assert(type(value) is dict or value is None)
    return '' if value is None else f"{value['type'].upper()} ({value['coordinates'][0]} {value['coordinates'][1]})"\
        .replace(',', '')


def _to_coord(value, coord):
    """Convert to coord

    The geometry is translated to match the DIVA output format.

    Example:

        {
            type: "Point",
            coordinates: [
                119411.7,
                487201.6
            ]
        }
        Output: 487201,6

    :param value:
    :param coord:
    :return:
    """
    assert(type(value) is dict or value is None)
    assert(coord in ['x', 'y'])
    if coord == 'x':
        index = 0
    elif coord == 'y':
        index = 1
    return '' if value is None else f"{value['coordinates'][int(index)]}"\
        .replace(',', '')\
        .replace('.', ',')


def type_convert(type_name, value, *args):
    """Convert a value fo a given type

    :param type_name: The name of the type, e.g. str
    :param value: A value
    :return: The converted value
    """
    converters = {
        'plain': _to_plain,
        'str': _to_string,
        'bool': _to_boolean,
        'num': _to_number,
        'dat': _to_date,
        'geo': _to_geometry,
        'coo': _to_coord,
    }
    return converters[type_name](value, *args)


def dat_exporter(api, file, format=None, append=False):
    """Exports a single entity

    Headers:       None
    Separator:     |
    String marker: $$


    The export format is a string containing the attributes and types to be converted.
    A declarative way of describing exports is used:
    The export format is used both to read the attributes and types and to write the correct output format.

    :return:
    """
    if append:
        raise NotImplementedError("Appending not implemented for this exporter")

    row_count = 0
    with open(file, 'w') as fp, ProgressTicker(f"Export entities", 10000) as progress:
        # Get the headers from the first record in the API
        for entity in api:
            pattern = re.compile('([\[\]\w.]+):(\w+):?({[\d\w\s:",]*}|\w+)?\|?')
            export = []
            for (attr_name, attr_type, args) in re.findall(pattern, format):
                # Get the nested value if a '.' is in the attr_name
                value = nested_entity_get(entity, attr_name.split('.')) if '.' in attr_name else entity.get(attr_name)
                attr_value = type_convert(attr_type, value, args)
                export.append(attr_value)

            fp.write('|'.join(export) + '\n')

            row_count += 1
            progress.tick()

    return row_count
