"""BRK2 aantekeningenrechten exports."""


from gobexport.exporter.config.brk2.utils import brk2_filename
from gobexport.exporter.csv import csv_exporter
from gobexport.exporter.shared.brk import format_timestamp
from gobexport.filters.notempty_filter import NotEmptyFilter


class AantekeningenExportConfig:
    """Aantekeningenrechten/Aantekeningenkadastraleobjecten export configuration."""

    art_query = """
{
  brk2Aantekeningenrechten {
    edges {
      node {
        identificatie
        einddatumRecht
        aard
        omschrijving
        heeftBrkBetrokkenPersoon {
          edges {
            node {
              identificatie
            }
          }
        }
        betrokkenBrkTenaamstelling {
          edges {
            node {
              identificatie
              vanBrkZakelijkRecht {
                edges {
                  node {
                    aardZakelijkRecht
                    rustOpBrkKadastraalObject {
                      edges {
                        node {
                          identificatie
                          perceelnummer
                          indexletter
                          indexnummer
                          aangeduidDoorBrkKadastralegemeentecode {
                            edges {
                              node {
                                identificatie
                              }
                            }
                          }
                          aangeduidDoorBrkKadastralesectie {
                            edges {
                              node {
                                code
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
          }
        }
      }
    }
  }
}
"""

    art_format = {
        "BRK_ATG_ID": "identificatie",
        "ATG_AARDAANTEKENING_CODE": "aard.code",
        "ATG_AARDAANTEKENING_OMS": "aard.omschrijving",
        "ATG_OMSCHRIJVING": "omschrijving",
        "ATG_EINDDATUM": {
            "action": "format",
            "formatter": format_timestamp,
            "value": "einddatumRecht",
        },
        "ATG_TYPE": {"action": "literal", "value": "Aantekening Zakelijk Recht (R)"},
        "BRK_KOT_ID": "rustOpBrkKadastraalObject.[0].identificatie",
        "KOT_KADASTRALEGEMCODE_CODE": "aangeduidDoorBrkKadastralegemeentecode.identificatie",
        "KOT_SECTIE": "aangeduidDoorBrkKadastralesectie.code",
        "KOT_PERCEELNUMMER": "rustOpBrkKadastraalObject.[0].perceelnummer",
        "KOT_INDEX_LETTER": "rustOpBrkKadastraalObject.[0].indexletter",
        "KOT_INDEX_NUMMER": "rustOpBrkKadastraalObject.[0].indexnummer",
        "BRK_TNG_ID": "betrokkenBrkTenaamstelling.[0].identificatie",
        "ZRT_AARD_ZAKELIJKRECHT_CODE": "vanBrkZakelijkRecht.[0].aardZakelijkRecht.code",
        "ZRT_AARD_ZAKELIJKRECHT_OMS": "vanBrkZakelijkRecht.[0].aardZakelijkRecht.omschrijving",
        "BRK_SJT_ID": "heeftBrkBetrokkenPersoon.[0].identificatie",
    }

    akt_query = """
{
  brk2Aantekeningenkadastraleobjecten {
    edges {
      node {
        identificatie
        einddatumRecht
        aard
        omschrijving
        heeftBrkBetrokkenPersoon {
          edges {
            node {
              identificatie
            }
          }
        }
        heeftBetrekkingOpBrkKadastraalObject {
          edges {
            node {
              identificatie
              perceelnummer
              indexletter
              indexnummer
              aangeduidDoorBrkKadastralegemeentecode {
                edges {
                  node {
                    identificatie
                  }
                }
              }
              aangeduidDoorBrkKadastralesectie {
                edges {
                  node {
                    code
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

    akt_format = {
        "BRK_ATG_ID": "identificatie",
        "ATG_AARDAANTEKENING_CODE": "aard.code",
        "ATG_AARDAANTEKENING_OMS": "aard.omschrijving",
        "ATG_OMSCHRIJVING": "omschrijving",
        "ATG_EINDDATUM": {
            "action": "format",
            "formatter": format_timestamp,
            "value": "einddatumRecht",
        },
        "ATG_TYPE": {"action": "literal", "value": "Aantekening Kadastraal object (O)"},
        "BRK_KOT_ID": "heeftBetrekkingOpBrkKadastraalObject.[0].identificatie",
        "KOT_KADASTRALEGEMCODE_CODE": "aangeduidDoorBrkKadastralegemeentecode.identificatie",
        "KOT_SECTIE": "aangeduidDoorBrkKadastralesectie.code",
        "KOT_PERCEELNUMMER": "heeftBetrekkingOpBrkKadastraalObject.[0].perceelnummer",
        "KOT_INDEX_LETTER": "heeftBetrekkingOpBrkKadastraalObject.[0].indexletter",
        "KOT_INDEX_NUMMER": "heeftBetrekkingOpBrkKadastraalObject.[0].indexnummer",
        "BRK_TNG_ID": "",
        "ZRT_AARD_ZAKELIJKRECHT_CODE": "",
        "ZRT_AARD_ZAKELIJKRECHT_OMS": "",
        "BRK_SJT_ID": "heeftBrkBetrokkenPersoon.[0].identificatie",
    }

    products = {
        "csv_art": {
            "api_type": "graphql_streaming",
            "secure_user": "gob",
            "unfold": True,
            "cross_relations": True,
            "entity_filters": [
                NotEmptyFilter("betrokkenBrkTenaamstelling.[0].identificatie"),
                NotEmptyFilter("rustOpBrkKadastraalObject.[0].identificatie"),
            ],
            "exporter": csv_exporter,
            "query": art_query,
            "filename": lambda: brk2_filename("aantekening", use_sensitive_dir=True),
            "mime_type": "text/csv",
            "format": art_format,
        },
        "csv_akt": {
            "api_type": "graphql_streaming",
            "secure_user": "gob",
            "unfold": True,
            "entity_filters": [
                NotEmptyFilter("heeftBetrekkingOpBrkKadastraalObject.[0].identificatie"),
            ],
            "exporter": csv_exporter,
            "query": akt_query,
            "filename": lambda: brk2_filename("aantekening", use_sensitive_dir=True),
            "mime_type": "text/csv",
            "format": akt_format,
            "append": True,
            "unique_csv_id": "BRK_ATG_ID",
        },
    }
