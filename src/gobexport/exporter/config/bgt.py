from gobexport.exporter.csv import csv_exporter
from gobexport.formatter.geometry import format_geometry


def format_guid(value):
    return f"{{{value}}}"


class OnderbouwExportConfig:
    """Onderbouw export config."""

    products = {
        'csv_actueel': {
            'api_type': 'graphql',
            'exporter': csv_exporter,
            'filename': 'CSV_Actueel/CFT_onderbouw.csv',
            'mime_type': 'plain/text',
            'format': {
                'guid': {
                    'action': 'format',
                    'formatter': format_guid,
                    'value': 'identificatie',
                },
                'eindregistratie': 'eindGeldigheid',
                'relatievehoogteligging': 'relatieveHoogteligging',
                'geometrie': {
                    'action': 'format',
                    'formatter': format_geometry,
                    'value': 'geometrie'
                },
            },
            'query': """
{
    bgtOnderbouw {
    edges {
      node {
        identificatie
        eindGeldigheid
        relatieveHoogteligging
        geometrie
      }
    }
  }
}
"""
        }
    }


class OverbouwExportConfig:
    """Overbouw export config."""

    products = {
        'csv_actueel': {
            'api_type': 'graphql',
            'exporter': csv_exporter,
            'filename': 'CSV_Actueel/CFT_overbouw.csv',
            'mime_type': 'plain/text',
            'format': {
                'guid': {
                    'action': 'format',
                    'formatter': format_guid,
                    'value': 'identificatie',
                },
                'eindregistratie': 'eindGeldigheid',
                'relatievehoogteligging': 'relatieveHoogteligging',
                'geometrie': {
                    'action': 'format',
                    'formatter': format_geometry,
                    'value': 'geometrie'
                },
            },
            'query': """
{
    bgtOverbouw {
    edges {
      node {
        identificatie
        eindGeldigheid
        relatieveHoogteligging
        geometrie
      }
    }
  }
}
"""
        }
    }
