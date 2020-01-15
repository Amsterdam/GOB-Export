from gobexport.exporter.csv import csv_exporter
from gobexport.exporter.config.brk.utils import brk_filename


class AardzakelijkerechtenExportConfig:
    format = {
        'AZT_CODE': 'code',
        'AZT_OMSCHRIJVING': 'waarde',
        'AZT_AARDZAKELIJKRECHT_AKR_CODE': 'akrCode',
    }

    query = '''
{
  brkAardzakelijkerechten(sort:code_asc) {
    edges {
      node {
        code
        waarde
        akrCode
      }
    }
  }
}
'''

    products = {
        'csv': {
            'exporter': csv_exporter,
            'api_type': 'graphql',
            'secure': True,
            'query': query,
            'filename': lambda: brk_filename("c_aard_zakelijkrecht"),
            'mime_type': 'plain/text',
            'format': format,
        }
    }
