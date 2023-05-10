"""BRK2 kadastralegemeentecodes exports."""


from gobexport.exporter.config.brk2.utils import brk2_directory
from gobexport.exporter.esri import esri_exporter


class KadastralegemeentecodesExportConfig:
    """Kadastralegemeentecodes export configuration."""

    query = """
{
  brk2Kadastralegemeentecodes {
    edges {
      node {
        identificatie
        geometrie
        isOnderdeelVanBrkKadastraleGemeente {
          edges {
            node {
              identificatie
              ligtInBrkGemeente {
                edges {
                  node {
                    naam
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
"""

    filename = "BRK_KAD_GEMEENTE"
    products = {
        "shape": {
            "exporter": esri_exporter,
            "api_type": "graphql_streaming",
            "secure_user": "gob",
            "filename": f'{brk2_directory("shp", use_sensitive_dir = False)}/{filename}.shp',
            "mime_type": "application/octet-stream",
            "format": {
                "GEMEENTE": "ligtInBrkGemeente.[0].naam",
                "KADGEMCODE": "identificatie",
                "KADGEM": "isOnderdeelVanBrkKadastraleGemeente.[0].identificatie",
            },
            "extra_files": [
                {
                    "filename": f'{brk2_directory("dbf", use_sensitive_dir = False)}/{filename}.dbf',
                    "mime_type": "application/octet-stream",
                },
                {
                    "filename": f'{brk2_directory("shx", use_sensitive_dir = False)}/{filename}.shx',
                    "mime_type": "application/octet-stream",
                },
                {
                    "filename": f'{brk2_directory("prj", use_sensitive_dir = False)}/{filename}.prj',
                    "mime_type": "application/octet-stream",
                },
                {
                    "filename": f'{brk2_directory("cpg", use_sensitive_dir=False)}/{filename}.cpg',
                    "mime_type": "application/octet-stream",
                },
            ],
            "query": query,
        },
    }
