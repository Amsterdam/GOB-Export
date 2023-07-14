import csv
from typing import Optional, Sequence

from gobcore.exceptions import GOBException
from gobcore.utils import ProgressTicker
from gobexport.exporter.utils import get_entity_value, split_field_reference
from gobexport.filters.entity_filter import EntityFilter


def build_mapping_from_format(format):
    """Builds a mapping dictionary with csv column name and the lookup key

    :param format: A format description, see csv exporter for examples of format
    :return: the mapping
    """
    mapping = {}
    for key, value in format.items():
        mapping[key] = split_field_reference(value)

    return mapping


def _get_headers_from_file(file: str) -> Optional[Sequence[str]]:
    """Returns existing column names from a CSV file

    :param file:
    :return:
    """

    # utf-8-sig encoding handles UTF-8 BOM character correctly
    with open(file, 'r', encoding='utf-8-sig') as fp:
        reader = csv.DictReader(fp, delimiter=';')
        headers = reader.fieldnames

    return headers


def _ensure_fieldnames_match_existing_file(fieldnames, file):
    """Raises GOBException if fieldnames don't match the header names present in file

    :param fieldnames:
    :param file:
    :return:
    """
    existing_headers = _get_headers_from_file(file)

    if existing_headers != fieldnames:
        raise GOBException('Fields from existing file do not match fields to append')


def _get_csv_ids(csv_file: str, csv_id: str) -> list[str]:
    """Return list with all csv_id's in csv_file.

    :param csv_file:
    :param csv_id:
    :return:
    """
    csv_ids = []
    with open(csv_file, 'r', encoding='utf-8-sig') as fp:
        reader = csv.DictReader(fp, delimiter=';')
        for row in reader:
            csv_ids.append(row[csv_id])
    return csv_ids


def csv_exporter(
    api, file, format=None, append=False, filter: Optional[EntityFilter] = None, unique_csv_id: Optional[str] = None
):
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



    :param filter:
    :param api: the API wrapper which can be iterated through
    :param file: the local file to write to
    :param format: format definition, see above for examples
    :param append: the file the result of this export will be appended to, or False
    :return:
    """
    row_count = 0

    mapping = build_mapping_from_format(format)
    fieldnames = [*mapping.keys()]

    if append:
        _ensure_fieldnames_match_existing_file(fieldnames, append)
        csv_ids = _get_csv_ids(file.removesuffix(".to_append"), unique_csv_id) if unique_csv_id else []

    with open(file, 'a' if append else 'w', encoding='utf-8-sig') as fp, \
            ProgressTicker("Export entities", 10000) as progress:
        # Get the fieldnames from the mapping
        writer = csv.DictWriter(fp, fieldnames=fieldnames, delimiter=';')

        if not append:
            writer.writeheader()

        for entity in api:
            if filter and not filter.filter(entity):
                continue

            if unique_csv_id and entity[mapping[unique_csv_id]] in csv_ids:
                continue

            row = {}
            for attribute_name, lookup_key in mapping.items():
                row[attribute_name] = get_entity_value(entity, lookup_key)

            writer.writerow(row)
            row_count += 1
            progress.tick()

    return row_count
