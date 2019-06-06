import csv

from shapely.geometry import shape

from gobcore.exceptions import GOBException
from gobcore.utils import ProgressTicker

from gobexport.exporter.utils import nested_entity_get


def build_mapping_from_format(format):
    """Builds a mapping dictionary with csv column name and the lookup key

    :param format: A format description, see csv exporter for examples of format
    :return: the mapping
    """
    mapping = {}
    for key, value in format.items():
        mapping[key] = _split_field_reference(value)

    return mapping


def _split_field_reference(ref: str):
    return ref.split('.') if '.' in ref else ref


def evaluate_condition(entity: dict, condition: dict):
    """Expects an entity and a condition as dict, which has as keys:

    condition: for example 'isempty'
    reference: the field reference to which to apply the condition
    trueval: the value (field reference) to return if condition evaluates to true
    falseval: you get it

    negate:    optional. if true, negate the condition

    :param condition:
    :return:
    """
    assert all([k in condition for k in ['condition', 'reference', 'trueval']]), "Invalid condition definition"

    condition_type = condition.get('condition')
    reference = condition.get('reference')
    trueval = condition.get('trueval')
    falseval = condition.get('falseval')
    negate = condition.get('negate', False)
    condition_should_be = not negate

    onfield_value = get_entity_value(entity, _split_field_reference(reference))

    if condition_type == 'isempty':
        condition_result = not bool(onfield_value)
    else:
        raise NotImplementedError(f"Not implemented condition f{condition_type}")

    if condition_result is condition_should_be:
        result = trueval
    else:
        result = falseval

    if result:
        return get_entity_value(entity, result)


def _evaluate_concat_action(entity: dict, action: dict):
    assert 'fields' in action
    return "".join([str(item) if item is not None else "" for
                    item in [get_entity_value(entity, field) for field in action['fields']]])


def _evaluate_literal_action(action: dict):
    return action.get('value')


def evaluate_action(entity: dict, action: dict):
    if action.get('action') == 'concat':
        return _evaluate_concat_action(entity, action)
    elif action.get('action') == 'literal':
        return _evaluate_literal_action(action)
    else:
        raise NotImplementedError()


def _get_entity_value_dict_lookup_key(entity: dict, lookup_key: dict):
    if lookup_key.get('action'):
        return evaluate_action(entity, lookup_key)
    elif lookup_key.get('condition'):
        return evaluate_condition(entity, lookup_key)

    raise NotImplementedError()


def get_entity_value(entity, lookup_key):
    """Get the value from the entity using a key or a list of keys

    lookup_key can be of type dict, with either 'action' or 'condition' set.

    An action overrides the remainder of this function and returns the value immediately.
    A condition returns a new (or the same) lookup key/dict for further processing.

    If lookup_key is of type list or string, we perform a lookup on entity.

    :param entity: The API entity to get the value from
    :param lookup_key: A attribute name or a list of attribute names
    :return: the value of the entity's attribute or None
    """
    if not lookup_key:
        return None

    if isinstance(lookup_key, str):
        lookup_key = _split_field_reference(lookup_key)

    if isinstance(lookup_key, dict):
        return _get_entity_value_dict_lookup_key(entity, lookup_key)

    assert isinstance(lookup_key, str) or isinstance(lookup_key, list)

    value = nested_entity_get(entity, lookup_key) if isinstance(lookup_key, list) else entity.get(lookup_key)
    # Return J or N when the value is a boolean
    if isinstance(value, bool):
        value = 'J' if value else 'N'
    return value


def _get_headers_from_file(file: str) -> list:
    """Returns existing column names from a CSV file

    :param file:
    :return:
    """
    with open(file, 'r') as fp:
        reader = csv.DictReader(fp, delimiter=';')
        headers = reader.fieldnames
    return headers


def _ensure_fieldnames_match_existing_file(fieldnames, file):
    existing_headers = _get_headers_from_file(file)

    if existing_headers != fieldnames:
        raise GOBException('Fields from existing file do not match fields to append')


def csv_exporter(api, file, format=None, append=False):
    """CSV Exporter

    Exports the output of the API to a ; delimited csv file.

    Format is a dictionary which can have the following attributes:

    columns: A list of attributes which can be mapped 1-on-1 with the API output and csv column name

        Example: ['identificatie', 'code', 'naam']

    reference: Can be found in the _embedded block of the HAL JSON output. Reference will contain a
               dictionary of API attributes with information on how to map them to csv columns.

        Example:
            ligtInBuurt: {
                'ref': 'GBD.SDL',   -- The abbreviations for this catalog and collection
                'ref_name': 'ligtIn',  -- A description of the relation used in the csv column name
                'columns': ['identificatie', 'naam'],  -- The columns to be taken from this _embedded reference
            }

    mapping: A dictionary of mapings between API output and CSV columns. This is currently being used for the
             state endpints as these aren't according to HAL JSON specs yet.

        Example: 'ligtIn:GBD.SDL.identificatie': 'gebieden:stadsdelenIdentificatie',



    :param api: the API wrapper which can be iterated through
    :param file: the local file to write to
    :param format: format definition, see above for examples
    :param append:
    :return:
    """
    row_count = 0

    mapping = build_mapping_from_format(format)
    fieldnames = [*mapping.keys()]

    if append:
        _ensure_fieldnames_match_existing_file(fieldnames, file)

    with open(file, 'a' if append else 'w') as fp, ProgressTicker(f"Export entities", 10000) as progress:
        # Get the fieldnames from the mapping
        writer = csv.DictWriter(fp, fieldnames=fieldnames, delimiter=';')

        if not append:
            writer.writeheader()

        for entity in api:
            row = {}
            for attribute_name, lookup_key in mapping.items():
                row[attribute_name] = get_entity_value(entity, lookup_key)

            # Convert geojson to wkt
            if 'geometrie' in row:
                row['geometrie'] = shape(entity['geometrie']).wkt if entity['geometrie'] else ''

            writer.writerow(row)
            row_count += 1
            progress.tick()

    return row_count
