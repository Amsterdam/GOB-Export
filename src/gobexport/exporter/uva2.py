from datetime import date

from gobcore.utils import ProgressTicker

from gobexport.exporter.csv import build_mapping_from_format
from gobexport.exporter.utils import get_entity_value
from gobexport.filters.entity_filter import EntityFilter


CRLF = "\r\n"
DELIMITER = ";"


def _get_uva2_headers():
    """Returns the headers required for the UVA2 files

    :return:
    """
    publish_date = date.today().strftime("%Y%m%d")
    return f"VAN;{publish_date}{CRLF}" \
           f"TM;{publish_date}{CRLF}" \
           f"HISTORISCHE_CYCLI;N{CRLF}"


def uva2_exporter(api, file, format=None, append=False, filter: EntityFilter=None):
    """UVA2 Exporter

    Exports the output of the API to a ; delimited ASCII file with additional header rows

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
    :param append:
    :return:
    """
    row_count = 0

    mapping = build_mapping_from_format(format)
    fieldnames = [*mapping.keys()]

    with open(file, 'a' if append else 'w', encoding='utf-8') as fp, \
            ProgressTicker(f"Export entities", 10000) as progress:

        # Write the headers
        fp.write(_get_uva2_headers())

        # Write the fieldnames
        fp.write(f"{DELIMITER}".join(fieldnames))
        fp.write(CRLF)

        for entity in api:
            if filter and not filter.filter(entity):
                continue

            row = f"{DELIMITER}".join([get_entity_value(entity, mapping[fieldname])
                                       if get_entity_value(entity, mapping[fieldname]) else ''
                                       for fieldname in fieldnames])
            row += CRLF

            fp.write(row)
            row_count += 1
            progress.tick()

    return row_count
