import csv

from shapely.geometry import shape


def csv_exporter(api, file, format=None):
    row_count = 0
    with open(file, 'w') as fp:
        # Get the headers from the first record in the API
        for entity in api:
            if row_count == 0:
                writer = csv.DictWriter(fp, fieldnames=[k for k in entity.keys()], delimiter=';')
                writer.writeheader()

            # Convert geojson to wkt
            if 'geometrie' in entity:
                entity['geometrie'] = shape(entity['geometrie']).wkt

            writer.writerow(entity)
            row_count += 1
    return row_count
