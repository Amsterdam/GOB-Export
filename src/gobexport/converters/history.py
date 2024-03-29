import datetime
import operator
import re

from gobcore.exceptions import GOBTypeException
from gobcore.typesystem import GOB

from gobexport import gob_model

START_TIMESLOT = 'beginTijdvak'
END_TIMESLOT = 'eindTijdvak'
START_VALIDITY = 'beginGeldigheid'
END_VALIDITY = 'eindGeldigheid'

_BEGIN_OF_TIME = datetime.datetime.min
_END_OF_TIME = datetime.datetime.max
# Dates compare at start of day
_START_OF_DAY = datetime.time(0, 0, 0)


def _compare_date(value):
    """Transform value to datetime to allow date - datetime comparison.

    :param value: datetime.date or datetime.datatime
    :return: value as datetime.datetime value
    """
    if not isinstance(value, datetime.datetime):
        return _date_to_datetime(value)
    return value


def _compare_dates(date1, compare, date2):
    """Compare two dates.

    If the values have equal type, use the plain comparison function
    Else, transform the value into universally comparable value
    :param date1:
    :param compare: the compare function, e.g. operator.lt
    :param date2:
    :return:
    """
    if isinstance(date1, type(date2)):
        return compare(date1, date2)
    return compare(_compare_date(date1), _compare_date(date2))


def _date_to_datetime(value):
    """Convert a date value to a datetime value.

    :param value: a date value
    :return: The corresponding datetime value
    """
    return datetime.datetime.combine(value, _START_OF_DAY)


def convert_to_history_rows(row):
    """Converts a row with cycles and references into seperate rows with all timeslots expanded.

    :param row: a dict with references and validities for each reference
    :return: a list of expanded rows for each timeslot
    """
    history_rows = []
    timeslots = _get_timeslots(row)

    all_references = _get_all_references()
    for timeslot in timeslots:
        if _compare_dates(
            timeslot[START_TIMESLOT], operator.lt, _convert_to_date(row[START_VALIDITY])) or (
            row[END_VALIDITY] and _compare_dates(
                timeslot[END_TIMESLOT], operator.gt, _convert_to_date(row[END_VALIDITY]))):
            continue  # pragma: no cover

        state_row = _get_state_row(timeslot, row)

        for key, value in row.items():
            if _convert_to_snake_case(key) in all_references:
                state_row[key] = _get_valid_reference(value, timeslot)
            else:
                state_row[key] = value
        history_rows.append(state_row)
    return history_rows


def _get_state_row(timeslot, row):
    date_type = datetime.date if len(row.get(START_VALIDITY)) == len('YYYY-MM-DD') else datetime.datetime

    state_row = {
        START_TIMESLOT: _convert_date_to_string(timeslot[START_TIMESLOT], date_type)
        if timeslot[START_TIMESLOT] != _BEGIN_OF_TIME else '',
        END_TIMESLOT: _convert_date_to_string(timeslot[END_TIMESLOT], date_type)
        if timeslot[END_TIMESLOT] != _END_OF_TIME else ''
    }
    return state_row


def _get_all_references():
    """Gets all possible references in the GOB Model.

    Used to select the valid reference from a list of references.

    :return: a dict all references by key
    """
    references = {}
    for catalogue in gob_model.values():
        for collection in catalogue['collections'].values():
            references.update(collection['references'])
    return references


def _get_timeslots(row):
    """Get all unique timeslots in the row.

    :return: a list of dictionaries with start and end times
    """
    start_times = set([_convert_to_date(row.get(START_VALIDITY))])
    start_times.add(_convert_to_date(_get_end_validity(row)))
    for value in row.values():
        # Find all start times in a list of references
        if isinstance(value, list):
            start_times.update([_convert_to_date(ref.get(START_VALIDITY)) for ref in value])
            start_times.update([_convert_to_date(_get_end_validity(ref)) for ref in value])
    start_times.discard(None)
    start_times = list(sorted(start_times))

    return _create_timeslots(start_times)


def _create_timeslots(start_times):
    """For a list of timeslots generate a list with dicts containing the start and
    end of each timeslot.

    :param start_times: a list of unique timeslots
    :return: a list of dicts with all timeslots
    """
    timeslots = []
    for count, time in enumerate(start_times):
        try:
            end = start_times[count + 1]
            timeslots.append({START_TIMESLOT: time, END_TIMESLOT: end})
        except IndexError:
            pass

    return timeslots


def _get_end_validity(entity):
    """Get the end validity of an entity or return the end of time.

    :param entity:
    :return: the end validity of this row
    """
    return entity.get(END_VALIDITY) if entity.get(END_VALIDITY) else _END_OF_TIME


def _get_valid_reference(references, timeslot):
    """For a list of references get the correct reference for the given timeslot.

    :param references:
    :param timeslot:
    :return: the correct reference
    """
    for reference in references:
        ref_start = _convert_to_date(reference.get(START_VALIDITY))
        ref_end = reference.get(END_VALIDITY)
        ref_end = _convert_to_date(ref_end) if ref_end else _END_OF_TIME
        if ref_start <= timeslot.get(START_TIMESLOT) and ref_end >= timeslot.get(END_TIMESLOT):
            return reference


def _convert_to_date(value):
    """Convert a string to a datetime object for comparisons.

    :param value:
    :return: a date(time) object
    """
    if len(str(value)) == len('YYYY-MM-DD'):
        value = f'{value}T{_START_OF_DAY.isoformat()}'

    try:
        return GOB.DateTime.from_value(value).to_value
    except GOBTypeException:
        pass


def _convert_date_to_string(obj, date_type=datetime.datetime):
    """Convert a date(time) object to a string.

    :param obj:
    :return: a date(time) string
    """
    if date_type == datetime.datetime:
        value = obj.isoformat()
    else:
        value = obj.strftime('%Y-%m-%d')
    return value


def _convert_to_snake_case(value):
    """Convert a CamelCase string snake_case.

    :param value:
    :return: the snake_case of value
    """
    regex = re.compile('((?<=[a-z0-9])[A-Z]|[A-Z](?=[a-z]))')
    return regex.sub(r'_\1', value).lower()
