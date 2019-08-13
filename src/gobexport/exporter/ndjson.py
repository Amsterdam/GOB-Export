import json

from gobcore.utils import ProgressTicker
from gobexport.filters.entity_filter import EntityFilter


def ndjson_exporter(api, file, format=None, append=False, filter: EntityFilter=None):
    """
    Exports a single entity in Newline Delimited JSON format

    :param api: API reader instance
    :param file: name of the file to write results
    :param format: NA
    :param append: NA
    :return: number of rows exported
    """
    if append:
        raise NotImplementedError("Appending not implemented for this exporter")

    row_count = 0
    with open(file, 'w') as fp, ProgressTicker(f"Export entities", 10000) as progress:
        for entity in api:
            if filter and not filter.filter(entity):
                continue

            result = json.dumps(entity)

            fp.write(result + '\n')

            row_count += 1
            progress.tick()

    return row_count
