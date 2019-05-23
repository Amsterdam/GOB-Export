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

    condition: for example 'isnull'
    reference: the field reference to which to apply the condition
    value:     the value (field reference) to return if condition evaluates to true

    negate:    optional. if true, negate the condition

    :param condition:
    :return:
    """
    assert all([k in condition for k in ['condition', 'reference']]), "Invalid condition definition"
    assert any([k in condition for k in ['value', 'override']]), "Value or override should be provided"

    condition_type = condition.get('condition')
    reference = condition.get('reference')
    value = condition.get('value')
    override = condition.get('override')
    negate = condition.get('negate', False)

    if not override:
        # If no override value has been provided, reference and value can't be the same
        assert reference != value, "Reference and value cannot be the same"

    onfield_value = get_entity_value(entity, _split_field_reference(reference))

    if condition_type == 'isempty':
        condition_result = not bool(onfield_value)
    else:
        raise NotImplementedError(f"Not implemented condition f{condition_type}")

    return process_condition_result(entity, condition_result, negate, value, reference, override)


def process_condition_result(entity, condition_result, negate, value, reference, override):
    reference_list = _split_field_reference(reference)

    if condition_result is not negate:
        if value:
            # If a field reference is provided, return this as the new mapping
            return _split_field_reference(value)

        if override:
            # When the condition is met, update the entity reference value
            update_entity_value(entity, reference_list, override)
            return reference_list
    elif override:
        # When the condition isn't met return the original value
        return reference_list

    return None


def get_entity_value(entity, lookup_key):
    """Get the value from the entity using a key or a list of keys

    :param entity: The API entity to get the value from
    :param lookup_key: A attribute name or a list of attribute names
    :return: the value of the entity's attribute or None
    """
    if isinstance(lookup_key, dict):
        lookup_key = evaluate_condition(entity, lookup_key)

    value = nested_entity_get(entity, lookup_key) if isinstance(lookup_key, list) else entity.get(lookup_key)
    # Return J or N when the value is a boolean
    if isinstance(value, bool):
        value = 'J' if value else 'N'
    return value


def update_entity_value(entity, lookup_key, value):
    """Update the value from the entity using a key or a list of keys

    :param entity: The API entity to get the value from
    :param lookup_key: A attribute name or a list of attribute names
    :param new_value: The value to assign
    :return:
    """
    if isinstance(lookup_key, list):
        inside = entity
        for key in lookup_key:
            if isinstance(inside.get(key), dict):
                inside = inside[key]
            else:
                inside[key] = value
    else:
        entity[lookup_key] = value


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
