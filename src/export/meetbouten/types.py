"""Meetbouten types

This module contains logic to convert Meetbouten types to the correct export format

"""
import datetime


def _to_string(value):
    """Convert to string

    :param value:
    :return:
    """
    return f'$${str(value) if value else ""}$$'


def _to_boolean(value):
    """Convert to boolean

    :param value:
    :return:
    """
    return _to_string('' if value else 'N')


def _to_number(value):
    """Convert to number

    :param value:
    :return:
    """
    return '' if value is None else str(value).replace('.', ',')


def _to_date(value):
    """Convert to date

    :param value:
    :return:
    """
    return _to_string(
        '' if value is None else datetime.datetime.strptime(str(value), "%Y-%m-%d").date().strftime("%Y%m%d"))


def _to_geometry(value):
    """Convert to geometry

    :param value:
    :return:
    """
    return '' if value is None else str(value).replace('(', ' (').replace('.', ',')


def type_convert(type_name, value):
    """Convert a value fo a given type

    :param type_name: The name of the type, e.g. str
    :param value: A value
    :return: The converted value
    """
    converters = {
        'str': _to_string,
        'bool': _to_boolean,
        'num': _to_number,
        'dat': _to_date,
        'geo': _to_geometry
    }
    return converters[type_name](value)
