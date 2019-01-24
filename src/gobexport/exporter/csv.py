import csv

from shapely.geometry import shape

from gobexport.exporter.utils import nested_entity_get


def build_mapping_from_format(format):
    """Builds a mapping dictionary with csv column name and the lookup key

    :param format: A format description, see csv exporter for examples of format
    :return: the mapping
    """
    # First add the regular columns
    mapping = {c: c for c in format['columns']}

    # Add references and their columns if supplied
    references = format.get('references', {})
    for key, reference in references.items():
        # Add all columns from this reference
        for column in reference['columns']:
            attribute_name = f"{reference['ref_name']}:{reference['ref']}.{column}"

            # Store the fieldname and an array of keys needed for lookup
            mapping[attribute_name] = [key, column]

    # Add a mapping if provided
    mapping.update(format.get('mapping', {}))

    return mapping


def get_entity_value(entity, lookup_key):
    """Get the value from the entity using a key or a list of keys

    :param entity: The API entity to get the value from
    :param lookup_key: A attribute name or a list of attribute names
    :return: the value of the entity's attribute or None
    """
    return nested_entity_get(entity, lookup_key) if isinstance(lookup_key, list) else entity.get(lookup_key)


def reorder_list(input_list, items_to_move, move_to_end=True):
    """Move a selection of items in a list to the front or back of the list

    Example [0,1,2,3,4,5], [2] ==> [0,1,3,4,5,2]
            [0,1,2,3,4,5], [2,4] ==> [0,1,3,5,2,4]
            [0,1,2,3,4,5], [4], False ==> [4,0,1,2,3,5]

    :param input_list: The list to apply the reorder on
    :param items_to_move: The items to be moved
    :param move_to_end: Default behaviour is to move to the end, can be overruled
    :return: the reorderd list
    """
    # Note that False<True and sort algorithm is stable, so:
    return sorted(input_list, key=lambda x: x in items_to_move) if move_to_end else \
           sorted(input_list, key=lambda x: x not in items_to_move)


def csv_exporter(api, file, format=None):
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
    :return:
    """
    row_count = 0

    mapping = build_mapping_from_format(format)

    with open(file, 'w') as fp:
        # Get the headers from the first record in the API
        for entity in api:
            if row_count == 0:
                # Get the fieldnames from the mapping
                fieldnames = [*mapping.keys()]

                # beginTijdvak, eindTijdvak and geometrie should always be the last columns
                items_to_move = ['beginTijdvak', 'eindTijdvak', 'geometrie']
                fieldnames = reorder_list(fieldnames, items_to_move)

                writer = csv.DictWriter(fp, fieldnames=fieldnames, delimiter=';')
                writer.writeheader()

            row = {}
            for attribute_name, lookup_key in mapping.items():
                row[attribute_name] = get_entity_value(entity, lookup_key)

            # Convert geojson to wkt
            row['geometrie'] = shape(entity['geometrie']).wkt if entity['geometrie'] else ''

            writer.writerow(row)
            row_count += 1

    return row_count
