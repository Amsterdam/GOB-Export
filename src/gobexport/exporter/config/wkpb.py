from gobexport.exporter.csv import csv_exporter
from gobexport.filters.notempty_filter import NotEmptyFilter
from gobexport.filters.unique_filter import UniqueFilter


"""WKPB export config

In these configuration files it is possible to define all products that need
to be exported for a catalogue. Each product is defined by a unique name and the
following properties:

    exporter: The python module used for this product, current options include:
        - dat_exporter
        - csv_exporter
        - esri_exporter
    endpoint: The endpoint to the API used for getting the data
    filename: The resulting filename of the exported file
    mime_type: The mime_type for the product, needed for export to the objectstore
    format: Additional configuration or mapping (see the different exporters for examples of format)
    extra_files: Resulting extra files of an export which need to be uploaded as
                 well. For example the esri product creates .dbf, .shx and .prj
                 files.
"""


class BeperkingenExportConfig:

    query_actueel = '''
{
  beperkingen {
    edges {
      node {
        identificatie
        beperking
        beginGeldigheid
        eindGeldigheid
      }
    }
  }
}
'''

    query_type = '''
{
  beperkingen(sort: beperking_asc) {
    edges {
      node {
        beperking
      }
    }
  }
}
'''

    query_orgaan = '''
{
  beperkingen(sort: orgaan_asc) {
    edges {
      node {
        orgaan
      }
    }
  }
}
'''

    products = {
        'csv_actueel': {
            'api_type': 'graphql',
            'exporter': csv_exporter,
            'filename': 'CSV_Actueel/WKPB_beperking.csv',
            'mime_type': 'plain/text',
            'format': {
                'identificatie': 'identificatie',
                'typeCode': 'beperking.code',
                'beginGeldigheid': 'beginGeldigheid',
                'eindGeldigheid': 'eindGeldigheid',
            },
            'query': query_actueel
        },
        'csv_types': {
            'api_type': 'graphql',
            'exporter': csv_exporter,
            'entity_filters': [
                NotEmptyFilter('beperking.code'),
                UniqueFilter('beperking.code'),
            ],
            'filename': 'CSV_Actueel/WKPB_type.csv',
            'mime_type': 'plain/text',
            'format': {
                'typeCode': 'beperking.code',
                'typeOmschrijving': 'beperking.omschrijving',
            },
            'query': query_type
        },
        'csv_orgaan': {
            'api_type': 'graphql',
            'exporter': csv_exporter,
            'entity_filters': [
                NotEmptyFilter('orgaan.code'),
                UniqueFilter('orgaan.code'),
            ],
            'filename': 'CSV_Actueel/WKPB_orgaan.csv',
            'mime_type': 'plain/text',
            'format': {
                'orgaanCode': 'orgaan.code',
                'orgaanOmschrijving': 'orgaan.omschrijving',
            },
            'query': query_orgaan
        },
    }