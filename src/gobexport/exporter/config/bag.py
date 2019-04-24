from gobexport.exporter.csv import csv_exporter
from gobexport.exporter.esri import esri_exporter


"""BAG export config

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


class WoonplaatsenExportConfig:

    query_actueel = '''
{
  woonplaatsen(eindGeldigheid: "null", status: "{\\"code\\": 1, \\"omschrijving\\": \\"Woonplaats aangewezen\\"}") {
    edges {
      node {
        identificatie,
        volgnummer,
        aanduidingInOnderzoek,
        geconstateerd,
        naam,
        beginGeldigheid,
        eindGeldigheid,
        documentdatum,
        documentnummer,
        status,
        ligtInGemeente,
        geometrie
      }
    }
  }
}
'''

    products = {
        'csv_actueel': {
            'api_type': 'graphql',
            'exporter': csv_exporter,
            'filename': 'CSV_Actueel/BAG_woonplaats.csv',
            'mime_type': 'plain/text',
            'format': {
                'columns': [
                    'identificatie',
                    'volgnummer',
                    'aanduidingInOnderzoek',
                    'geconstateerd',
                    'naam',
                    'beginGeldigheid',
                    'eindGeldigheid',
                    'documentdatum',
                    'documentnummer',
                    'status.omschrijving',
                    'geometrie',
                ],
                'references': {
                    'ligtInGemeente': {
                        'ref': 'BRK.GME',
                        'ref_name': 'ligtIn',
                        'columns': ['identificatie', 'naam'],
                    }
                }
            },
            'query': query_actueel
        },
        'esri_actueel': {
            'api_type': 'graphql',
            'exporter': esri_exporter,
            'filename': 'SHP/BAG_woonplaats.shp',
            'mime_type': 'application/octet-stream',
            'format': {
                'mapping': {
                    'id': 'identificatie',
                    'volgnummer': 'volgnummer',
                    'onderzoek': 'aanduidingInOnderzoek',
                    'geconst': 'geconstateerd',
                    'naam': 'naam',
                    'begindatum': 'beginGeldigheid',
                    'einddatum': 'eindGeldigheid',
                    'docdatum': 'documentdatum',
                    'docnummer': 'documentnummer',
                    'status': 'status.omschrijving',
                    'gme_id': 'ligtInGemeente.identificatie',
                    'gme_naam': 'ligtInGemeente.naam',
                }
            },
            'extra_files': [
                {
                    'filename': 'SHP/BAG_woonplaats.dbf',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'SHP/BAG_woonplaats.shx',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'SHP/BAG_woonplaats.prj',
                    'mime_type': 'application/octet-stream'
                },
            ],
            'query': query_actueel
        }
    }


class OpenbareruimtesExportConfig:

    query_actueel = '''
{
  openbareruimtes(eindGeldigheid: "null", status: "{\\"code\\": 1, \\"omschrijving\\": \\"Naamgeving uitgegeven\\"}") {
    edges {
      node {
        identificatie
        volgnummer
        aanduidingInOnderzoek
        geconstateerd
        naam
        naamNen
        beginGeldigheid
        eindGeldigheid
        ligtInWoonplaats {
          edges {
            node {
              identificatie
              volgnummer
            }
          }
        }
        type
        documentdatum
        documentnummer
        status
        geometrie
      }
    }
  }
}
'''
    products = {
        'csv_actueel': {
            'api_type': 'graphql',
            'exporter': csv_exporter,
            'filename': 'CSV_Actueel/BAG_openbare_ruimte.csv',
            'mime_type': 'plain/text',
            'format': {
                'columns': [
                    'identificatie',
                    'volgnummer',
                    'aanduidingInOnderzoek',
                    'geconstateerd',
                    'naam',
                    'naamNen',
                    'beginGeldigheid',
                    'eindGeldigheid',
                    'type.omschrijving',
                    'documentdatum',
                    'documentnummer',
                    'status.omschrijving',
                    'geometrie',
                ],
                'references': {
                    'ligtInWoonplaats': {
                        'ref': 'BAG.WPL',
                        'ref_name': 'ligtIn',
                        'columns': ['identificatie', 'volgnummer'],
                    }
                }
            },
            'query': query_actueel
        },
        'esri_actueel': {
            'api_type': 'graphql',
            'exporter': esri_exporter,
            'filename': 'SHP/BAG_openbare_ruimte.shp',
            'mime_type': 'application/octet-stream',
            'format': {
                'mapping': {
                    'id': 'identificatie',
                    'volgnummer': 'volgnummer',
                    'onderzoek': 'aanduidingInOnderzoek',
                    'geconst': 'geconstateerd',
                    'naam': 'naam',
                    'naam_nen': 'naamNen',
                    'begindatum': 'beginGeldigheid',
                    'einddatum': 'eindGeldigheid',
                    'wpl_id': 'ligtInWoonplaats.identificatie',
                    'type': 'type.omschrijving',
                    'docdatum': 'documentdatum',
                    'docnummer': 'documentnummer',
                    'status': 'status.omschrijving',
                }
            },
            'extra_files': [
                {
                    'filename': 'SHP/BAG_openbare_ruimte.dbf',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'SHP/BAG_openbare_ruimte.shx',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'SHP/BAG_openbare_ruimte.prj',
                    'mime_type': 'application/octet-stream'
                },
            ],
            'query': query_actueel
        },
        'csv_beschrijving_actueel': {
            'api_type': 'graphql',
            'exporter': csv_exporter,
            'filename': 'CSV_Actueel/BAG_ORE_beschrijving.csv',
            'mime_type': 'plain/text',
            'format': {
                'columns': [
                    'identificatie',
                    'volgnummer',
                    'naam',
                    'beschrijvingNaam'
                ],
            },
            'query': '''
{
  openbareruimtes(eindGeldigheid: "null", status: "{\\"code\\": 1, \\"omschrijving\\": \\"Naamgeving uitgegeven\\"}") {
    edges {
      node {
        identificatie
        volgnummer
        naam
        beschrijvingNaam
      }
    }
  }
}
'''
        },
    }


class NummeraanduidingenExportConfig:

    query_actueel = '''
{
  nummeraanduidingen(eindGeldigheid: "null", status: "{\\"code\\": 1, \\"omschrijving\\": \\"Naamgeving uitgegeven\\"}") {
    edges {
      node {
        identificatie
        volgnummer
        aanduidingInOnderzoek
        geconstateerd
        huisnummer
        huisletter
        huisnummertoevoeging
        postcode
        ligtAanOpenbareruimte {
          edges {
            node {
              identificatie
              volgnummer
              naam
            }
          }
        }
        ligtInWoonplaats {
          edges {
            node {
              identificatie
              volgnummer
              naam
            }
          }
        }
        beginGeldigheid
        eindGeldigheid
        typeAdresseerbaarObject
        documentdatum
        documentnummer
        status
        adresseertVerblijfsobject {
          edges {
            node {
              identificatie
              volgnummer
            }
          }
        }
        adresseertLigplaats {
          edges {
            node {
              identificatie
              volgnummer
            }
          }
        }
        adresseertStandplaats {
          edges {
            node {
              identificatie
              volgnummer
            }
          }
        }
      }
    }
  }
}
'''
    products = {
        'csv_actueel': {
            'api_type': 'graphql',
            'exporter': csv_exporter,
            'filename': 'CSV_Actueel/BAG_nummeraanduiding.csv',
            'mime_type': 'plain/text',
            'format': {
                'columns': [
                    'identificatie',
                    'volgnummer',
                    'aanduidingInOnderzoek',
                    'geconstateerd',
                    'huisnummer',
                    'huisletter',
                    'huisnummertoevoeging',
                    'postcode',
                    'beginGeldigheid',
                    'eindGeldigheid',
                    'typeAdresseerbaarObject.omschrijving',
                    'documentdatum',
                    'documentnummer',
                    'status.omschrijving',
                    'geometrie',
                ],
                'references': {
                    'ligtAanOpenbareruimte': {
                        'ref': 'BAG.ORE',
                        'ref_name': 'ligtAan',
                        'columns': ['identificatie', 'volgnummer', 'naam'],
                    },
                    'ligtInWoonplaats': {
                        'ref': 'BAG.WPL',
                        'ref_name': 'ligtIn',
                        'columns': ['identificatie', 'volgnummer', 'naam'],
                    },
                    'adresseertVerblijfsobject': {
                        'ref': 'BAG.VOT',
                        'ref_name': 'adresseert',
                        'columns': ['identificatie', 'volgnummer'],
                    },
                    'adresseertLigplaats': {
                        'ref': 'BAG.LPS',
                        'ref_name': 'adresseert',
                        'columns': ['identificatie', 'volgnummer'],
                    },
                    'adresseertStandplaats': {
                        'ref': 'BAG.SPS',
                        'ref_name': 'adresseert',
                        'columns': ['identificatie', 'volgnummer'],
                    }
                }
            },
            'query': query_actueel
        }
    }


class VerblijfsobjectenExportConfig:

    query_actueel = '''
{
  verblijfsobjecten(eindGeldigheid: "null", status: "{\\"code\\": 1, \\"omschrijving\\": \\"Naamgeving uitgegeven\\"}") {
    edges {
      node {
        identificatie
        volgnummer
        aanduidingInOnderzoek
        geconstateerd
        heeftHoofdadres {
          edges {
            node {
              identificatie
              volgnummer
              huisnummer
              huisletter
              huisnummertoevoeging
              postcode
              ligtAanOpenbareruimte {
                edges {
                  node {
                    identificatie
                    volgnummer
                    naam
                  }
                }
              }
              ligtInWoonplaats {
                edges {
                  node {
                    identificatie
                    volgnummer
                    naam
                  }
                }
              }
            }
          }
        }
        heeftNevenadres {
          edges {
            node {
              identificatie
              volgnummer
            }
          }
        }
        ligtInPanden {
          edges {
            node {
              identificatie
              volgnummer
              ligtInBouwblok {
                edges {
                  node {
                    identificatie
                    volgnummer
                    code
                  }
                }
              }
            }
          }
        }
        ligtInBuurt {
          edges {
            node {
              identificatie
              volgnummer
              naam
              code
              ligtInWijk {
                edges {
                  node {
                    identificatie
                    volgnummer
                    naam
                    code
                    ligtInStadsdeel {
                      edges {
                        node {
                          identificatie
                          volgnummer
                          naam
                          code
                          ligtInGemeente
                        }
                      }
                    }
                  }
                }
              }
              LigtInGgpgebied {
                edges {
                  node {
                    identificatie
                    volgnummer
                    naam
                    code
                  }
                }
              }
              LigtInGgwgebied {
                edges {
                  node {
                    identificatie
                    volgnummer
                    naam
                    code
                  }
                }
              }
            }
          }
        }
        gebruiksdoel
        gebruiksdoelWoonfunctie
        gebruiksdoelGezondheidszorgfunctie
        aantalEenhedenComplex
        feitelijkGebruik
        oppervlakte
        status
        beginGeldigheid
        eindGeldigheid
        documentdatum
        documentnummer
        verdiepingToegang
        toegang
        aantalBouwlagen
        hoogsteBouwlaag
        laagsteBouwlaag
        aantalKamers
        eigendomsverhouding
        redenopvoer
        redenafvoer
        geometrie
      }
    }
  }
}
'''
    products = {
        'csv_actueel': {
            'api_type': 'graphql',
            'exporter': csv_exporter,
            'filename': 'CSV_Actueel/BAG_verblijfsobject.csv',
            'mime_type': 'plain/text',
            'format': {
                'columns': [
                    'identificatie',
                    'volgnummer',
                    'aanduidingInOnderzoek',
                    'geconstateerd',
                    'huisnummer',
                    'huisletter',
                    'huisnummertoevoeging',
                    'postcode',
                    'beginGeldigheid',
                    'eindGeldigheid',
                    'typeAdresseerbaarObject.omschrijving',
                    'documentdatum',
                    'documentnummer',
                    'status.omschrijving',
                    'geometrie',
                ],
                'references': {
                    'ligtAanOpenbareruimte': {
                        'ref': 'BAG.ORE',
                        'ref_name': 'ligtAan',
                        'columns': ['identificatie', 'volgnummer', 'naam'],
                    },
                    'ligtInWoonplaats': {
                        'ref': 'BAG.WPL',
                        'ref_name': 'ligtIn',
                        'columns': ['identificatie', 'volgnummer', 'naam'],
                    },
                    'adresseertVerblijfsobject': {
                        'ref': 'BAG.VOT',
                        'ref_name': 'adresseert',
                        'columns': ['identificatie', 'volgnummer'],
                    },
                    'adresseertLigplaats': {
                        'ref': 'BAG.LPS',
                        'ref_name': 'adresseert',
                        'columns': ['identificatie', 'volgnummer'],
                    },
                    'adresseertStandplaats': {
                        'ref': 'BAG.SPS',
                        'ref_name': 'adresseert',
                        'columns': ['identificatie', 'volgnummer'],
                    }
                }
            },
            'query': query_actueel
        }
    }


class StandplaatsenExportConfig:

    query_actueel = '''
{
  standplaatsen(eindGeldigheid: "null", status: "{\\"code\\": 1, \\"omschrijving\\": \\"Naamgeving uitgegeven\\"}") {
    edges {
      node {
        identificatie
        volgnummer
        aanduidingInOnderzoek
        geconstateerd
        heeftHoofdadres {
          edges {
            node {
              identificatie
              volgnummer
              huisnummer
              huisletter
              huisnummertoevoeging
              postcode
              ligtAanOpenbareruimte {
                edges {
                  node {
                    identificatie
                    volgnummer
                    naam
                  }
                }
              }
              ligtInWoonplaats {
                edges {
                  node {
                    identificatie
                    volgnummer
                    naam
                  }
                }
              }
            }
          }
        }
        heeftNevenadres {
          edges {
            node {
              identificatie
              volgnummer
            }
          }
        }
        ligtInPanden {
          edges {
            node {
              identificatie
              volgnummer
              ligtInBouwblok {
                edges {
                  node {
                    identificatie
                    volgnummer
                    code
                  }
                }
              }
            }
          }
        }
        ligtInBuurt {
          edges {
            node {
              identificatie
              volgnummer
              naam
              code
              ligtInWijk {
                edges {
                  node {
                    identificatie
                    volgnummer
                    naam
                    code
                    ligtInStadsdeel {
                      edges {
                        node {
                          identificatie
                          volgnummer
                          naam
                          code
                          ligtInGemeente
                        }
                      }
                    }
                  }
                }
              }
              LigtInGgpgebied {
                edges {
                  node {
                    identificatie
                    volgnummer
                    naam
                    code
                  }
                }
              }
              LigtInGgwgebied {
                edges {
                  node {
                    identificatie
                    volgnummer
                    naam
                    code
                  }
                }
              }
            }
          }
        }
        feitelijkGebruik
        status
        beginGeldigheid
        eindGeldigheid
        documentdatum
        documentnummer
        geometrie
      }
    }
  }
}
'''
    products = {
        'csv_actueel': {
            'api_type': 'graphql',
            'exporter': csv_exporter,
            'filename': 'CSV_Actueel/BAG_standplaats.csv',
            'mime_type': 'plain/text',
            'format': {
                'columns': [
                    'identificatie',
                    'volgnummer',
                    'aanduidingInOnderzoek',
                    'geconstateerd',
                    'huisnummer',
                    'huisletter',
                    'huisnummertoevoeging',
                    'postcode',
                    'beginGeldigheid',
                    'eindGeldigheid',
                    'typeAdresseerbaarObject.omschrijving',
                    'documentdatum',
                    'documentnummer',
                    'status.omschrijving',
                    'geometrie',
                ],
                'references': {
                    'ligtAanOpenbareruimte': {
                        'ref': 'BAG.ORE',
                        'ref_name': 'ligtAan',
                        'columns': ['identificatie', 'volgnummer', 'naam'],
                    },
                    'ligtInWoonplaats': {
                        'ref': 'BAG.WPL',
                        'ref_name': 'ligtIn',
                        'columns': ['identificatie', 'volgnummer', 'naam'],
                    },
                    'adresseertVerblijfsobject': {
                        'ref': 'BAG.VOT',
                        'ref_name': 'adresseert',
                        'columns': ['identificatie', 'volgnummer'],
                    },
                    'adresseertLigplaats': {
                        'ref': 'BAG.LPS',
                        'ref_name': 'adresseert',
                        'columns': ['identificatie', 'volgnummer'],
                    },
                    'adresseertStandplaats': {
                        'ref': 'BAG.SPS',
                        'ref_name': 'adresseert',
                        'columns': ['identificatie', 'volgnummer'],
                    }
                }
            },
            'query': query_actueel
        }
    }


class LigplaatsenExportConfig:

    query_actueel = '''
{
  ligplaatsen(eindGeldigheid: "null", status: "{\\"code\\": 1, \\"omschrijving\\": \\"Naamgeving uitgegeven\\"}") {
    edges {
      node {
        identificatie
        volgnummer
        aanduidingInOnderzoek
        geconstateerd
        heeftHoofdadres {
          edges {
            node {
              identificatie
              volgnummer
              huisnummer
              huisletter
              huisnummertoevoeging
              postcode
              ligtAanOpenbareruimte {
                edges {
                  node {
                    identificatie
                    volgnummer
                    naam
                  }
                }
              }
              ligtInWoonplaats {
                edges {
                  node {
                    identificatie
                    volgnummer
                    naam
                  }
                }
              }
            }
          }
        }
        heeftNevenadres {
          edges {
            node {
              identificatie
              volgnummer
            }
          }
        }
        ligtInPanden {
          edges {
            node {
              identificatie
              volgnummer
              ligtInBouwblok {
                edges {
                  node {
                    identificatie
                    volgnummer
                    code
                  }
                }
              }
            }
          }
        }
        ligtInBuurt {
          edges {
            node {
              identificatie
              volgnummer
              naam
              code
              ligtInWijk {
                edges {
                  node {
                    identificatie
                    volgnummer
                    naam
                    code
                    ligtInStadsdeel {
                      edges {
                        node {
                          identificatie
                          volgnummer
                          naam
                          code
                          ligtInGemeente
                        }
                      }
                    }
                  }
                }
              }
              LigtInGgpgebied {
                edges {
                  node {
                    identificatie
                    volgnummer
                    naam
                    code
                  }
                }
              }
              LigtInGgwgebied {
                edges {
                  node {
                    identificatie
                    volgnummer
                    naam
                    code
                  }
                }
              }
            }
          }
        }
        feitelijkGebruik
        status
        beginGeldigheid
        eindGeldigheid
        documentdatum
        documentnummer
        geometrie
      }
    }
  }
}
'''
    products = {
        'csv_actueel': {
            'api_type': 'graphql',
            'exporter': csv_exporter,
            'filename': 'CSV_Actueel/BAG_ligplaats.csv',
            'mime_type': 'plain/text',
            'format': {
                'columns': [
                    'identificatie',
                    'volgnummer',
                    'aanduidingInOnderzoek',
                    'geconstateerd',
                    'huisnummer',
                    'huisletter',
                    'huisnummertoevoeging',
                    'postcode',
                    'beginGeldigheid',
                    'eindGeldigheid',
                    'typeAdresseerbaarObject.omschrijving',
                    'documentdatum',
                    'documentnummer',
                    'status.omschrijving',
                    'geometrie',
                ],
                'references': {
                    'ligtAanOpenbareruimte': {
                        'ref': 'BAG.ORE',
                        'ref_name': 'ligtAan',
                        'columns': ['identificatie', 'volgnummer', 'naam'],
                    },
                    'ligtInWoonplaats': {
                        'ref': 'BAG.WPL',
                        'ref_name': 'ligtIn',
                        'columns': ['identificatie', 'volgnummer', 'naam'],
                    },
                    'adresseertVerblijfsobject': {
                        'ref': 'BAG.VOT',
                        'ref_name': 'adresseert',
                        'columns': ['identificatie', 'volgnummer'],
                    },
                    'adresseertLigplaats': {
                        'ref': 'BAG.LPS',
                        'ref_name': 'adresseert',
                        'columns': ['identificatie', 'volgnummer'],
                    },
                    'adresseertStandplaats': {
                        'ref': 'BAG.SPS',
                        'ref_name': 'adresseert',
                        'columns': ['identificatie', 'volgnummer'],
                    }
                }
            },
            'query': query_actueel
        }
    }


class PandenExportConfig:

    query_actueel = '''
{
  panden(eindGeldigheid: "null", status: "{\\"code\\": 1, \\"omschrijving\\": \\"Naamgeving uitgegeven\\"}") {
    edges {
      node {
        identificatie
        volgnummer
        aanduidingInOnderzoek
        geconstateerd
        oorspronkelijkBouwjaar
        ligtInBouwblok {
          edges {
            node {
            ligtInBuurt {
              edges {
                node {
                  identificatie
                  volgnummer
                  naam
                  code
                  ligtInWijk {
                    edges {
                      node {
                        identificatie
                        volgnummer
                        naam
                        code
                        ligtInStadsdeel {
                          edges {
                            node {
                              identificatie
                              volgnummer
                              naam
                              code
                              ligtInGemeente
                            }
                          }
                        }
                      }
                    }
                  }
                  LigtInGgpgebied {
                    edges {
                      node {
                        identificatie
                        volgnummer
                        naam
                        code
                      }
                    }
                  }
                  LigtInGgwgebied {
                    edges {
                      node {
                        identificatie
                        volgnummer
                        naam
                        code
                      }
                    }
                  }
                }
              }
            }
          }
        }
        status
        beginGeldigheid
        eindGeldigheid
        documentdatum
        documentnummer
        naam
        ligging
        aantalBouwlagen
        hoogsteBouwlaag
        laagsteBouwlaag
        geometrie
      }
    }
  }
}
'''
    products = {
        'csv_actueel': {
            'api_type': 'graphql',
            'exporter': csv_exporter,
            'filename': 'CSV_Actueel/BAG_ligplaats.csv',
            'mime_type': 'plain/text',
            'format': {
                'columns': [
                    'identificatie',
                    'volgnummer',
                    'aanduidingInOnderzoek',
                    'geconstateerd',
                    'huisnummer',
                    'huisletter',
                    'huisnummertoevoeging',
                    'postcode',
                    'beginGeldigheid',
                    'eindGeldigheid',
                    'typeAdresseerbaarObject.omschrijving',
                    'documentdatum',
                    'documentnummer',
                    'status.omschrijving',
                    'geometrie',
                ],
                'references': {
                    'ligtAanOpenbareruimte': {
                        'ref': 'BAG.ORE',
                        'ref_name': 'ligtAan',
                        'columns': ['identificatie', 'volgnummer', 'naam'],
                    },
                    'ligtInWoonplaats': {
                        'ref': 'BAG.WPL',
                        'ref_name': 'ligtIn',
                        'columns': ['identificatie', 'volgnummer', 'naam'],
                    },
                    'adresseertVerblijfsobject': {
                        'ref': 'BAG.VOT',
                        'ref_name': 'adresseert',
                        'columns': ['identificatie', 'volgnummer'],
                    },
                    'adresseertLigplaats': {
                        'ref': 'BAG.LPS',
                        'ref_name': 'adresseert',
                        'columns': ['identificatie', 'volgnummer'],
                    },
                    'adresseertStandplaats': {
                        'ref': 'BAG.SPS',
                        'ref_name': 'adresseert',
                        'columns': ['identificatie', 'volgnummer'],
                    }
                }
            },
            'query': query_actueel
        }
    }
