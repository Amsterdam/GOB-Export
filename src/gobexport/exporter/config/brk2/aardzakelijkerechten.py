from gobexport.exporter.csv import csv_exporter
from gobexport.exporter.config.brk2.utils import brk2_filename


class AardzakelijkerechtenExportConfig:
    format = {
        'AZT_CODE': 'code',
        'AZT_OMSCHRIJVING': 'waarde',
        'AZT_AARDZAKELIJKRECHT_AKR_CODE': 'akrCode',
    }

    query = '''
{
  brk2Aardzakelijkerechten(sort: code_asc) {
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
            'secure_user': 'gob',
            'query': query,
            'filename': lambda: brk2_filename("c_aard_zakelijkrecht", use_sensitive_dir=True),
            'mime_type': 'plain/text',
            'format': format,
        }
    }
