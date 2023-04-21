"""BRK2 gemeentes exports."""


from gobexport.exporter.config.brk2.utils import brk2_directory, brk2_filename
from gobexport.exporter.csv import csv_exporter
from gobexport.exporter.esri import esri_exporter
from gobexport.formatter.geometry import format_geometry


class GemeentesExportConfig:
    """Gemeentes export configuration."""

    query = """
{
  brk2Gemeentes(sort:naam_asc) {
    edges {
      node {
        identificatie
        naam
        geometrie
      }
    }
  }
}
"""

    shp_filename = "BRK_GEMEENTE"
    products = {
        "csv": {
            "exporter": csv_exporter,
            "api_type": "graphql",
            "secure_user": "gob",
            "query": query,
            "filename": lambda: brk2_filename("Gemeente", file_type="csv", use_sensitive_dir=False),
            "mime_type": "plain/text",
            "format": {
                "naam": "naam",
                "identificatie": "identificatie",
                "geometrie": {"action": "format", "formatter": format_geometry, "value": "geometrie"},
            },
        },
        "shape": {
            "exporter": esri_exporter,
            "api_type": "graphql",
            "secure_user": "gob",
            "filename": f'{brk2_directory("shp", use_sensitive_dir=False)}/{shp_filename}.shp',
            "mime_type": "application/octet-stream",
            "format": {
                "GEMEENTE": "naam",
            },
            "extra_files": [
                {
                    "filename": f'{brk2_directory("dbf", use_sensitive_dir=False)}/{shp_filename}.dbf',
                    "mime_type": "application/octet-stream",
                },
                {
                    "filename": f'{brk2_directory("shx", use_sensitive_dir=False)}/{shp_filename}.shx',
                    "mime_type": "application/octet-stream",
                },
                {
                    "filename": f'{brk2_directory("prj", use_sensitive_dir=False)}/{shp_filename}.prj',
                    "mime_type": "application/octet-stream",
                },
                {
                    "filename": f'{brk2_directory("cpg", use_sensitive_dir=False)}/{shp_filename}.cpg',
                    "mime_type": "application/octet-stream",
                },
            ],
            "query": query,
        },
    }
