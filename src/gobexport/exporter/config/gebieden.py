from gobexport.exporter.csv import csv_exporter
from gobexport.exporter.esri import esri_exporter

from gobexport.formatter.geometry import format_geometry


"""Gebieden export config

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


class StadsdelenExportConfig:

    query_actueel = '''
{
  gebiedenStadsdelen {
    edges {
      node {
        identificatie
        code
        naam
        beginGeldigheid
        eindGeldigheid
        documentdatum
        documentnummer
        geometrie
        ligtInGemeente {
          edges {
            node {
              identificatie
              naam
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
            'exporter': csv_exporter,
            'api_type': 'graphql',
            'filename': 'CSV_Actueel/GBD_stadsdeel_Actueel.csv',
            'mime_type': 'plain/text',
            'format': {
                'identificatie': 'identificatie',
                'code': 'code',
                'naam': 'naam',
                'beginGeldigheid': 'beginGeldigheid',
                'eindGeldigheid': 'eindGeldigheid',
                'documentdatum': 'documentdatum',
                'documentnummer': 'documentnummer',
                'ligtIn:BRK.GME.identificatie': 'ligtInGemeente.identificatie',
                'ligtIn:BRK.GME.naam': 'ligtInGemeente.naam',
                'geometrie': {
                    'action': 'format',
                    'formatter': format_geometry,
                    'value': 'geometrie'
                },
            },
            'query': query_actueel
        },
        'esri_actueel': {
            'exporter': esri_exporter,
            'api_type': 'graphql',
            'filename': 'SHP/GBD_stadsdeel.shp',
            'mime_type': 'application/octet-stream',
            'format': {
                'id': 'identificatie',
                'code': 'code',
                'naam': 'naam',
                'begindatum': 'beginGeldigheid',
                'einddatum': 'eindGeldigheid',
                'docdatum': 'documentdatum',
                'docnummer': 'documentnummer',
                'gme_id': 'ligtInGemeente.identificatie',
                'gme_naam': 'ligtInGemeente.naam',
            },
            'extra_files': [
                {
                    'filename': 'SHP/GBD_stadsdeel.dbf',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'SHP/GBD_stadsdeel.shx',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'SHP/GBD_stadsdeel.prj',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'SHP/GBD_stadsdeel.cpg',
                    'mime_type': 'application/octet-stream'
                },
            ],
            'query': query_actueel
        },
        'csv_actueel_en_historie': {
            'api_type': 'graphql',
            'exporter': csv_exporter,
            'filename': 'CSV_ActueelEnHistorie/GBD_stadsdeel_ActueelEnHistorie.csv',
            'mime_type': 'plain/text',
            'format': {
                'identificatie': 'identificatie',
                'volgnummer': 'volgnummer',
                'registratiedatum': 'registratiedatum',
                'code': 'code',
                'naam': 'naam',
                'beginGeldigheid': 'beginGeldigheid',
                'eindGeldigheid': 'eindGeldigheid',
                'documentdatum': 'documentdatum',
                'documentnummer': 'documentnummer',
                'ligtIn:BRK.GME.identificatie': 'ligtInGemeente.identificatie',
                'ligtIn:BRK.GME.volgnummer': 'ligtInGemeente.volgnummer',
                'ligtIn:BRK.GME.naam': 'ligtInGemeente.naam',
                'geometrie': {
                    'action': 'format',
                    'formatter': format_geometry,
                    'value': 'geometrie'
                },
            },
            'query': """
{
  gebiedenStadsdelen(sort: [identificatie_asc, volgnummer_asc], active: false) {
    edges {
      node {
        identificatie
        volgnummer
        registratiedatum
        code
        naam
        beginGeldigheid
        eindGeldigheid
        documentdatum
        documentnummer
        ligtInGemeente(active: false) {
          edges {
            node {
              identificatie
              naam
              beginGeldigheid
              eindGeldigheid
            }
          }
        }
        geometrie
      }
    }
  }
}
"""
        }
    }


class GGPGebiedenExportConfig:

    query_actueel = '''
{
  gebiedenGgpgebieden {
    edges {
      node {
        identificatie
        code
        naam
        beginGeldigheid
        eindGeldigheid
        documentdatum
        documentnummer
        geometrie
        ligtInStadsdeel {
          edges {
            node {
              identificatie
              code
              naam
              ligtInGemeente {
                edges {
                  node {
                    identificatie
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
'''

    products = {
        'csv_actueel': {
            'exporter': csv_exporter,
            'api_type': 'graphql',
            'filename': 'CSV_Actueel/GBD_ggw_praktijkgebied_Actueel.csv',
            'mime_type': 'plain/text',
            'format': {
                'identificatie': 'identificatie',
                'code': 'code',
                'naam': 'naam',
                'beginGeldigheid': 'beginGeldigheid',
                'eindGeldigheid': 'eindGeldigheid',
                'documentdatum': 'documentdatum',
                'documentnummer': 'documentnummer',
                'ligtIn:GBD.SDL.identificatie': 'ligtInStadsdeel.identificatie',
                'ligtIn:GBD.SDL.code': 'ligtInStadsdeel.code',
                'ligtIn:GBD.SDL.naam': 'ligtInStadsdeel.naam',
                'ligtIn:BRK.GME.identificatie': 'ligtInGemeente.identificatie',
                'ligtIn:BRK.GME.naam': 'ligtInGemeente.naam',
                'geometrie': {
                    'action': 'format',
                    'formatter': format_geometry,
                    'value': 'geometrie'
                },
            },
            'query': query_actueel
        },
        'esri_actueel': {
            'exporter': esri_exporter,
            'api_type': 'graphql',
            'filename': 'SHP/GBD_ggw_praktijkgebied.shp',
            'mime_type': 'application/octet-stream',
            'format': {
                'id': 'identificatie',
                'code': 'code',
                'naam': 'naam',
                'begindatum': 'beginGeldigheid',
                'einddatum': 'eindGeldigheid',
                'docdatum': 'documentdatum',
                'docnummer': 'documentnummer',
                'sdl_id': 'ligtInStadsdeel.identificatie',
                'sdl_code': 'ligtInStadsdeel.code',
                'sdl_naam': 'ligtInStadsdeel.naam',
                'gme_id': 'ligtInGemeente.identificatie',
                'gme_naam': 'ligtInGemeente.naam',
            },
            'extra_files': [
                {
                    'filename': 'SHP/GBD_ggw_praktijkgebied.dbf',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'SHP/GBD_ggw_praktijkgebied.shx',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'SHP/GBD_ggw_praktijkgebied.prj',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'SHP/GBD_ggw_praktijkgebied.cpg',
                    'mime_type': 'application/octet-stream'
                },
            ],
            'query': query_actueel
        },
        'csv_actueel_en_historie': {
            'api_type': 'graphql',
            'exporter': csv_exporter,
            'filename': 'CSV_ActueelEnHistorie/GBD_ggw_praktijkgebied_ActueelEnHistorie.csv',
            'mime_type': 'plain/text',
            'format': {
                'identificatie': 'identificatie',
                'volgnummer': 'volgnummer',
                'registratiedatum': 'registratiedatum',
                'code': 'code',
                'naam': 'naam',
                'beginGeldigheid': 'beginGeldigheid',
                'eindGeldigheid': 'eindGeldigheid',
                'documentdatum': 'documentdatum',
                'documentnummer': 'documentnummer',
                'ligtIn:GBD.SDL.identificatie': 'ligtInStadsdeel.identificatie',
                'ligtIn:GBD.SDL.volgnummer': 'ligtInStadsdeel.volgnummer',
                'ligtIn:GBD.SDL.code': 'ligtInStadsdeel.code',
                'ligtIn:GBD.SDL.naam': 'ligtInStadsdeel.naam',
                'ligtIn:BRK.GME.identificatie': 'ligtInGemeente.identificatie',
                'ligtIn:BRK.GME.volgnummer': 'ligtInGemeente.volgnummer',
                'ligtIn:BRK.GME.naam': 'ligtInGemeente.naam',
                'geometrie': {
                    'action': 'format',
                    'formatter': format_geometry,
                    'value': 'geometrie'
                },
            },
            'query': '''
{
  gebiedenGgpgebieden(sort: [identificatie_asc, volgnummer_asc], active: false) {
    edges {
      node {
        identificatie
        volgnummer
        registratiedatum
        code
        naam
        beginGeldigheid
        eindGeldigheid
        documentdatum
        documentnummer
        geometrie
        ligtInStadsdeel(active: false) {
          edges {
            node {
              identificatie
              volgnummer
              code
              naam
              beginGeldigheid
              eindGeldigheid
              ligtInGemeente(active: false) {
                edges {
                  node {
                    identificatie
                    naam
                    beginGeldigheid
                    eindGeldigheid
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
'''
        }
    }


class GGWGebiedenExportConfig:

    query_actueel = '''
{
  gebiedenGgwgebieden {
    edges {
      node {
        identificatie
        code
        naam
        beginGeldigheid
        eindGeldigheid
        documentdatum
        documentnummer
        geometrie
        ligtInStadsdeel {
          edges {
            node {
              identificatie
              code
              naam
              ligtInGemeente {
                edges {
                  node {
                    identificatie
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
'''

    products = {
        'csv_actueel': {
            'exporter': csv_exporter,
            'api_type': 'graphql',
            'filename': 'CSV_Actueel/GBD_ggw_gebied_Actueel.csv',
            'mime_type': 'plain/text',
            'format': {
                'identificatie': 'identificatie',
                'code': 'code',
                'naam': 'naam',
                'beginGeldigheid': 'beginGeldigheid',
                'eindGeldigheid': 'eindGeldigheid',
                'documentdatum': 'documentdatum',
                'documentnummer': 'documentnummer',
                'ligtIn:GBD.SDL.identificatie': 'ligtInStadsdeel.identificatie',
                'ligtIn:GBD.SDL.code': 'ligtInStadsdeel.code',
                'ligtIn:GBD.SDL.naam': 'ligtInStadsdeel.naam',
                'ligtIn:BRK.GME.identificatie': 'ligtInGemeente.identificatie',
                'ligtIn:BRK.GME.naam': 'ligtInGemeente.naam',
                'geometrie': {
                    'action': 'format',
                    'formatter': format_geometry,
                    'value': 'geometrie'
                },
            },
            'query': query_actueel
        },
        'esri_actueel': {
            'exporter': esri_exporter,
            'api_type': 'graphql',
            'filename': 'SHP/GBD_ggw_gebied.shp',
            'mime_type': 'application/octet-stream',
            'format': {
                'id': 'identificatie',
                'code': 'code',
                'naam': 'naam',
                'begindatum': 'beginGeldigheid',
                'einddatum': 'eindGeldigheid',
                'docdatum': 'documentdatum',
                'docnummer': 'documentnummer',
                'sdl_id': 'ligtInStadsdeel.identificatie',
                'sdl_code': 'ligtInStadsdeel.code',
                'sdl_naam': 'ligtInStadsdeel.naam',
                'gme_id': 'ligtInGemeente.identificatie',
                'gme_naam': 'ligtInGemeente.naam',
            },
            'extra_files': [
                {
                    'filename': 'SHP/GBD_ggw_gebied.dbf',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'SHP/GBD_ggw_gebied.shx',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'SHP/GBD_ggw_gebied.prj',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'SHP/GBD_ggw_gebied.cpg',
                    'mime_type': 'application/octet-stream'
                },
            ],
            'query': query_actueel
        },
        'csv_actueel_en_historie': {
            'api_type': 'graphql',
            'exporter': csv_exporter,
            'filename': 'CSV_ActueelEnHistorie/GBD_ggw_gebied_ActueelEnHistorie.csv',
            'mime_type': 'plain/text',
            'format': {
                'identificatie': 'identificatie',
                'volgnummer': 'volgnummer',
                'registratiedatum': 'registratiedatum',
                'code': 'code',
                'naam': 'naam',
                'beginGeldigheid': 'beginGeldigheid',
                'eindGeldigheid': 'eindGeldigheid',
                'documentdatum': 'documentdatum',
                'documentnummer': 'documentnummer',
                'ligtIn:GBD.SDL.identificatie': 'ligtInStadsdeel.identificatie',
                'ligtIn:GBD.SDL.volgnummer': 'ligtInStadsdeel.volgnummer',
                'ligtIn:GBD.SDL.code': 'ligtInStadsdeel.code',
                'ligtIn:GBD.SDL.naam': 'ligtInStadsdeel.naam',
                'ligtIn:BRK.GME.identificatie': 'ligtInGemeente.identificatie',
                'ligtIn:BRK.GME.volgnummer': 'ligtInGemeente.volgnummer',
                'ligtIn:BRK.GME.naam': 'ligtInGemeente.naam',
                'geometrie': {
                    'action': 'format',
                    'formatter': format_geometry,
                    'value': 'geometrie'
                },
            },
            'query': '''
{
  gebiedenGgwgebieden(sort: [identificatie_asc, volgnummer_asc], active: false) {
    edges {
      node {
        identificatie
        volgnummer
        registratiedatum
        code
        naam
        beginGeldigheid
        eindGeldigheid
        documentdatum
        documentnummer
        geometrie
        ligtInStadsdeel(active: false) {
          edges {
            node {
              identificatie
              volgnummer
              code
              naam
              beginGeldigheid
              eindGeldigheid
              ligtInGemeente(active: false) {
                edges {
                  node {
                    identificatie
                    naam
                    beginGeldigheid
                    eindGeldigheid
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
'''
        }
    }


class WijkenExportConfig:

    query_actueel = '''
{
  gebiedenWijken {
    edges {
      node {
        identificatie
        code
        naam
        beginGeldigheid
        eindGeldigheid
        documentdatum
        documentnummer
        cbsCode
        geometrie
        LigtInGgwgebied {
          edges {
            node {
              identificatie
              code
              naam
            }
          }
        }
        ligtInStadsdeel {
          edges {
            node {
              identificatie
              code
              naam
              ligtInGemeente {
                edges {
                  node {
                    identificatie
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
'''

    products = {
        'csv_actueel': {
            'exporter': csv_exporter,
            'api_type': 'graphql',
            'filename': 'CSV_Actueel/GBD_wijk_Actueel.csv',
            'mime_type': 'plain/text',
            'format': {
                'identificatie': 'identificatie',
                'code': 'code',
                'naam': 'naam',
                'beginGeldigheid': 'beginGeldigheid',
                'eindGeldigheid': 'eindGeldigheid',
                'documentdatum': 'documentdatum',
                'documentnummer': 'documentnummer',
                'cbsCode': 'cbsCode',
                'ligtIn:GBD.GGW.identificatie': 'LigtInGgwgebied.identificatie',
                'ligtIn:GBD.GGW.code': 'LigtInGgwgebied.code',
                'ligtIn:GBD.GGW.naam': 'LigtInGgwgebied.naam',
                'ligtIn:GBD.SDL.identificatie': 'ligtInStadsdeel.identificatie',
                'ligtIn:GBD.SDL.code': 'ligtInStadsdeel.code',
                'ligtIn:GBD.SDL.naam': 'ligtInStadsdeel.naam',
                'ligtIn:BRK.GME.identificatie': 'ligtInGemeente.identificatie',
                'ligtIn:BRK.GME.naam': 'ligtInGemeente.naam',
                'geometrie': {
                    'action': 'format',
                    'formatter': format_geometry,
                    'value': 'geometrie'
                },
            },
            'query': query_actueel
        },
        'esri_actueel': {
            'exporter': esri_exporter,
            'api_type': 'graphql',
            'filename': 'SHP/GBD_wijk.shp',
            'mime_type': 'application/octet-stream',
            'format': {
                'id': 'identificatie',
                'code': 'code',
                'naam': 'naam',
                'begindatum': 'beginGeldigheid',
                'einddatum': 'eindGeldigheid',
                'docdatum': 'documentdatum',
                'docnummer': 'documentnummer',
                'CBS_code': 'cbsCode',
                'ggw_id': 'LigtInGgwgebied.identificatie',
                'ggw_code': 'LigtInGgwgebied.code',
                'ggw_naam': 'LigtInGgwgebied.naam',
                'sdl_id': 'ligtInStadsdeel.identificatie',
                'sdl_code': 'ligtInStadsdeel.code',
                'sdl_naam': 'ligtInStadsdeel.naam',
                'gme_id': 'ligtInGemeente.identificatie',
                'gme_naam': 'ligtInGemeente.naam',
            },
            'extra_files': [
                {
                    'filename': 'SHP/GBD_wijk.dbf',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'SHP/GBD_wijk.shx',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'SHP/GBD_wijk.prj',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'SHP/GBD_wijk.cpg',
                    'mime_type': 'application/octet-stream'
                },
            ],
            'query': query_actueel
        },
        'csv_actueel_en_historie': {
            'api_type': 'graphql',
            'exporter': csv_exporter,
            'filename': 'CSV_ActueelEnHistorie/GBD_wijk_ActueelEnHistorie.csv',
            'mime_type': 'plain/text',
            'format': {
                'identificatie': 'identificatie',
                'volgnummer': 'volgnummer',
                'registratiedatum': 'registratiedatum',
                'code': 'code',
                'naam': 'naam',
                'beginGeldigheid': 'beginGeldigheid',
                'eindGeldigheid': 'eindGeldigheid',
                'documentdatum': 'documentdatum',
                'documentnummer': 'documentnummer',
                'cbsCode': 'cbsCode',
                'ligtIn:GBD.GGW.identificatie': 'LigtInGgwgebied.identificatie',
                'ligtIn:GBD.GGW.volgnummer': 'LigtInGgwgebied.volgnummer',
                'ligtIn:GBD.GGW.code': 'LigtInGgwgebied.code',
                'ligtIn:GBD.GGW.naam': 'LigtInGgwgebied.naam',
                'ligtIn:GBD.SDL.identificatie': 'ligtInStadsdeel.identificatie',
                'ligtIn:GBD.SDL.volgnummer': 'ligtInStadsdeel.volgnummer',
                'ligtIn:GBD.SDL.code': 'ligtInStadsdeel.code',
                'ligtIn:GBD.SDL.naam': 'ligtInStadsdeel.naam',
                'ligtIn:BRK.GME.identificatie': 'ligtInGemeente.identificatie',
                'ligtIn:BRK.GME.volgnummer': 'ligtInGemeente.volgnummer',
                'ligtIn:BRK.GME.naam': 'ligtInGemeente.naam',
                'geometrie': {
                    'action': 'format',
                    'formatter': format_geometry,
                    'value': 'geometrie'
                },
            },
            'query': '''
{
  gebiedenWijken(sort: [identificatie_asc, volgnummer_asc], active: false) {
    edges {
      node {
        identificatie
        volgnummer
        registratiedatum
        code
        naam
        beginGeldigheid
        eindGeldigheid
        documentdatum
        documentnummer
        cbsCode
        geometrie
        LigtInGgwgebied(active: false) {
          edges {
            node {
              identificatie
              volgnummer
              code
              naam
              beginGeldigheid
              eindGeldigheid
            }
          }
        }
        ligtInStadsdeel(active: false) {
          edges {
            node {
              identificatie
              volgnummer
              code
              naam
              beginGeldigheid
              eindGeldigheid
              ligtInGemeente(active: false) {
                edges {
                  node {
                    identificatie
                    naam
                    beginGeldigheid
                    eindGeldigheid
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
'''
        }
    }


class BuurtenExportConfig:

    query_actueel = '''
{
  gebiedenBuurten {
    edges {
      node {
        identificatie
        code
        naam
        cbsCode
        beginGeldigheid
        eindGeldigheid
        documentdatum
        documentnummer
        geometrie
        LigtInGgpgebied {
          edges {
            node {
              identificatie
              code
              naam
            }
          }
        }
        ligtInWijk {
          edges {
            node {
              identificatie
              code
              naam
              LigtInGgwgebied {
                edges {
                  node {
                    identificatie
                    code
                    naam
                  }
                }
              }
              ligtInStadsdeel {
                edges {
                  node {
                    identificatie
                    code
                    naam
                    ligtInGemeente {
                      edges {
                        node {
                          identificatie
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
    }
  }
}
'''

    products = {
        'csv_actueel': {
            'api_type': 'graphql',
            'exporter': csv_exporter,
            'filename': 'CSV_Actueel/GBD_buurt_Actueel.csv',
            'mime_type': 'plain/text',
            'format': {
                'identificatie': 'identificatie',
                'code': 'code',
                'naam': 'naam',
                'beginGeldigheid': 'beginGeldigheid',
                'eindGeldigheid': 'eindGeldigheid',
                'documentdatum': 'documentdatum',
                'documentnummer': 'documentnummer',
                'cbsCode': 'cbsCode',
                'ligtIn:GBD.WIJK.identificatie': 'ligtInWijk.identificatie',
                'ligtIn:GBD.WIJK.code': 'ligtInWijk.code',
                'ligtIn:GBD.WIJK.naam': 'ligtInWijk.naam',
                'ligtIn:GBD.GGW.identificatie': 'LigtInGgwgebied.identificatie',
                'ligtIn:GBD.GGW.code': 'LigtInGgwgebied.code',
                'ligtIn:GBD.GGW.naam': 'LigtInGgwgebied.naam',
                'ligtIn:GBD.GGP.identificatie': 'LigtInGgpgebied.identificatie',
                'ligtIn:GBD.GGP.code': 'LigtInGgpgebied.code',
                'ligtIn:GBD.GGP.naam': 'LigtInGgpgebied.naam',
                'ligtIn:GBD.SDL.identificatie': 'ligtInStadsdeel.identificatie',
                'ligtIn:GBD.SDL.code': 'ligtInStadsdeel.code',
                'ligtIn:GBD.SDL.naam': 'ligtInStadsdeel.naam',
                'ligtIn:BRK.GME.identificatie': 'ligtInGemeente.identificatie',
                'ligtIn:BRK.GME.naam': 'ligtInGemeente.naam',
                'geometrie': {
                    'action': 'format',
                    'formatter': format_geometry,
                    'value': 'geometrie'
                },
            },
            'query': query_actueel
        },
        'esri_actueel': {
            'api_type': 'graphql_streaming',
            'exporter': esri_exporter,
            'filename': 'SHP/GBD_buurt.shp',
            'mime_type': 'application/octet-stream',
            'format': {
                'id': 'identificatie',
                'code': 'code',
                'naam': 'naam',
                'begindatum': 'beginGeldigheid',
                'einddatum': 'eindGeldigheid',
                'docdatum': 'documentdatum',
                'docnummer': 'documentnummer',
                'CBS_code': 'cbsCode',
                'wijk_id': 'ligtInWijk.identificatie',
                'wijk_code': 'ligtInWijk.code',
                'wijk_naam': 'ligtInWijk.naam',
                'ggw_id': 'LigtInGgwgebied.identificatie',
                'ggw_code': 'LigtInGgwgebied.code',
                'ggw_naam': 'LigtInGgwgebied.naam',
                'ggp_id': 'LigtInGgpgebied.identificatie',
                'ggp_code': 'LigtInGgpgebied.code',
                'ggp_naam': 'LigtInGgpgebied.naam',
                'sdl_id': 'ligtInStadsdeel.identificatie',
                'sdl_code': 'ligtInStadsdeel.code',
                'sdl_naam': 'ligtInStadsdeel.naam',
                'gme_id': 'ligtInGemeente.identificatie',
                'gme_naam': 'ligtInGemeente.naam',
            },
            'extra_files': [
                {
                    'filename': 'SHP/GBD_buurt.dbf',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'SHP/GBD_buurt.shx',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'SHP/GBD_buurt.prj',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'SHP/GBD_buurt.cpg',
                    'mime_type': 'application/octet-stream'
                },
            ],
            'query': query_actueel
        },
        'csv_actueel_en_historie': {
            'api_type': 'graphql',
            'exporter': csv_exporter,
            'filename': 'CSV_ActueelEnHistorie/GBD_buurt_ActueelEnHistorie.csv',
            'mime_type': 'plain/text',
            'format': {
                'identificatie': 'identificatie',
                'volgnummer': 'volgnummer',
                'registratiedatum': 'registratiedatum',
                'code': 'code',
                'naam': 'naam',
                'beginGeldigheid': 'beginGeldigheid',
                'eindGeldigheid': 'eindGeldigheid',
                'documentdatum': 'documentdatum',
                'documentnummer': 'documentnummer',
                'cbsCode': 'cbsCode',
                'ligtIn:GBD.WIJK.identificatie': 'ligtInWijk.identificatie',
                'ligtIn:GBD.WIJK.volgnummer': 'ligtInWijk.volgnummer',
                'ligtIn:GBD.WIJK.code': 'ligtInWijk.code',
                'ligtIn:GBD.WIJK.naam': 'ligtInWijk.naam',
                'ligtIn:GBD.GGW.identificatie': 'LigtInGgwgebied.identificatie',
                'ligtIn:GBD.GGW.volgnummer': 'LigtInGgwgebied.volgnummer',
                'ligtIn:GBD.GGW.code': 'LigtInGgwgebied.code',
                'ligtIn:GBD.GGW.naam': 'LigtInGgwgebied.naam',
                'ligtIn:GBD.GGP.identificatie': 'LigtInGgpgebied.identificatie',
                'ligtIn:GBD.GGP.volgnummer': 'LigtInGgpgebied.volgnummer',
                'ligtIn:GBD.GGP.code': 'LigtInGgpgebied.code',
                'ligtIn:GBD.GGP.naam': 'LigtInGgpgebied.naam',
                'ligtIn:GBD.SDL.identificatie': 'ligtInStadsdeel.identificatie',
                'ligtIn:GBD.SDL.volgnummer': 'ligtInStadsdeel.volgnummer',
                'ligtIn:GBD.SDL.code': 'ligtInStadsdeel.code',
                'ligtIn:GBD.SDL.naam': 'ligtInStadsdeel.naam',
                'ligtIn:BRK.GME.identificatie': 'ligtInGemeente.identificatie',
                'ligtIn:BRK.GME.volgnummer': 'ligtInGemeente.volgnummer',
                'ligtIn:BRK.GME.naam': 'ligtInGemeente.naam',
                'geometrie': {
                    'action': 'format',
                    'formatter': format_geometry,
                    'value': 'geometrie'
                },
            },
            'query': '''
{
  gebiedenBuurten(sort: [identificatie_asc, volgnummer_asc], active: false) {
    edges {
      node {
        identificatie
        volgnummer
        registratiedatum
        code
        naam
        beginGeldigheid
        eindGeldigheid
        documentdatum
        documentnummer
        cbsCode
        geometrie
        LigtInGgwgebied(active: false) {
          edges {
            node {
              identificatie
              volgnummer
              code
              naam
              beginGeldigheid
              eindGeldigheid
            }
          }
        }
        LigtInGgpgebied(active: false) {
          edges {
            node {
              identificatie
              volgnummer
              code
              naam
              beginGeldigheid
              eindGeldigheid
            }
          }
        }
        ligtInWijk(active: false) {
          edges {
            node {
              identificatie
              volgnummer
              code
              naam
              beginGeldigheid
              eindGeldigheid
              ligtInStadsdeel(active: false) {
                edges {
                  node {
                    identificatie
                    volgnummer
                    code
                    naam
                    beginGeldigheid
                    eindGeldigheid
                    ligtInGemeente(active: false) {
                      edges {
                        node {
                          identificatie
                          naam
                          beginGeldigheid
                          eindGeldigheid
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
'''
        }
    }


class BouwblokkenExportConfig:

    query_actueel = """
{
  gebiedenBouwblokken(sort:code_asc) {
    edges {
      node {
        identificatie
        code
        beginGeldigheid
        eindGeldigheid
        geometrie
        ligtInBuurt {
          edges {
            node {
              identificatie
              code
              naam
              LigtInGgpgebied {
                edges {
                  node {
                    identificatie
                    code
                    naam
                  }
                }
              }
              LigtInGgwgebied {
                edges {
                  node {
                    identificatie
                    code
                    naam
                  }
                }
              }
              ligtInWijk {
                edges {
                  node {
                    identificatie
                    code
                    naam
                    ligtInStadsdeel {
                      edges {
                        node {
                          identificatie
                          code
                          naam
                          ligtInGemeente {
                            edges {
                              node {
                                identificatie
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
          }
        }
      }
    }
  }
}
"""

    products = {
        'csv_actueel': {
            'api_type': 'graphql',
            'exporter': csv_exporter,
            'filename': 'CSV_Actueel/GBD_bouwblok_Actueel.csv',
            'mime_type': 'plain/text',
            'format': {
                'identificatie': 'identificatie',
                'code': 'code',
                'beginGeldigheid': 'beginGeldigheid',
                'eindGeldigheid': 'eindGeldigheid',
                'ligtIn:GBD.BRT.identificatie': 'ligtInBuurt.identificatie',
                'ligtIn:GBD.BRT.code': 'ligtInBuurt.code',
                'ligtIn:GBD.BRT.naam': 'ligtInBuurt.naam',
                'ligtIn:GBD.WIJK.identificatie': 'ligtInWijk.identificatie',
                'ligtIn:GBD.WIJK.code': 'ligtInWijk.code',
                'ligtIn:GBD.WIJK.naam': 'ligtInWijk.naam',
                'ligtIn:GBD.GGW.identificatie': 'LigtInGgwgebied.identificatie',
                'ligtIn:GBD.GGW.code': 'LigtInGgwgebied.code',
                'ligtIn:GBD.GGW.naam': 'LigtInGgwgebied.naam',
                'ligtIn:GBD.GGP.identificatie': 'LigtInGgpgebied.identificatie',
                'ligtIn:GBD.GGP.code': 'LigtInGgpgebied.code',
                'ligtIn:GBD.GGP.naam': 'LigtInGgpgebied.naam',
                'ligtIn:GBD.SDL.identificatie': 'ligtInStadsdeel.identificatie',
                'ligtIn:GBD.SDL.code': 'ligtInStadsdeel.code',
                'ligtIn:GBD.SDL.naam': 'ligtInStadsdeel.naam',
                'ligtIn:BRK.GME.identificatie': 'ligtInGemeente.identificatie',
                'ligtIn:BRK.GME.naam': 'ligtInGemeente.naam',
                'geometrie': {
                    'action': 'format',
                    'formatter': format_geometry,
                    'value': 'geometrie'
                },
            },
            'query': query_actueel
        },
        'esri_actueel': {
            'api_type': 'graphql',
            'exporter': esri_exporter,
            'filename': 'SHP/GBD_bouwblok.shp',
            'mime_type': 'application/octet-stream',
            'format': {
                'id': 'identificatie',
                'code': 'code',
                'begindatum': 'beginGeldigheid',
                'einddatum': 'eindGeldigheid',
                'brt_id': 'ligtInBuurt.identificatie',
                'brt_code': 'ligtInBuurt.code',
                'brt_naam': 'ligtInBuurt.naam',
                'wijk_id': 'ligtInWijk.identificatie',
                'wijk_code': 'ligtInWijk.code',
                'wijk_naam': 'ligtInWijk.naam',
                'ggw_id': 'LigtInGgwgebied.identificatie',
                'ggw_code': 'LigtInGgwgebied.code',
                'ggw_naam': 'LigtInGgwgebied.naam',
                'ggp_id': 'LigtInGgpgebied.identificatie',
                'ggp_code': 'LigtInGgpgebied.code',
                'ggp_naam': 'LigtInGgpgebied.naam',
                'sdl_id': 'ligtInStadsdeel.identificatie',
                'sdl_code': 'ligtInStadsdeel.code',
                'sdl_naam': 'ligtInStadsdeel.naam',
                'gme_id': 'ligtInGemeente.identificatie',
                'gme_naam': 'ligtInGemeente.naam',
            },
            'extra_files': [
                {
                    'filename': 'SHP/GBD_bouwblok.dbf',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'SHP/GBD_bouwblok.shx',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'SHP/GBD_bouwblok.prj',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'SHP/GBD_bouwblok.cpg',
                    'mime_type': 'application/octet-stream'
                },
            ],
            'query': query_actueel
        },
        'csv_actueel_en_historie': {
            'api_type': 'graphql',
            'exporter': csv_exporter,
            'filename': 'CSV_ActueelEnHistorie/GBD_bouwblok_ActueelEnHistorie.csv',
            'mime_type': 'plain/text',
            'format': {
                'identificatie': 'identificatie',
                'volgnummer': 'volgnummer',
                'registratiedatum': 'registratiedatum',
                'code': 'code',
                'beginGeldigheid': 'beginGeldigheid',
                'eindGeldigheid': 'eindGeldigheid',
                'ligtIn:GBD.BRT.identificatie': 'ligtInBuurt.identificatie',
                'ligtIn:GBD.BRT.volgnummer': 'ligtInBuurt.volgnummer',
                'ligtIn:GBD.BRT.code': 'ligtInBuurt.code',
                'ligtIn:GBD.BRT.naam': 'ligtInBuurt.naam',
                'ligtIn:GBD.WIJK.identificatie': 'ligtInWijk.identificatie',
                'ligtIn:GBD.WIJK.volgnummer': 'ligtInWijk.volgnummer',
                'ligtIn:GBD.WIJK.code': 'ligtInWijk.code',
                'ligtIn:GBD.WIJK.naam': 'ligtInWijk.naam',
                'ligtIn:GBD.GGW.identificatie': 'LigtInGgwgebied.identificatie',
                'ligtIn:GBD.GGW.volgnummer': 'LigtInGgwgebied.volgnummer',
                'ligtIn:GBD.GGW.code': 'LigtInGgwgebied.code',
                'ligtIn:GBD.GGW.naam': 'LigtInGgwgebied.naam',
                'ligtIn:GBD.GGP.identificatie': 'LigtInGgpgebied.identificatie',
                'ligtIn:GBD.GGP.volgnummer': 'LigtInGgpgebied.volgnummer',
                'ligtIn:GBD.GGP.code': 'LigtInGgpgebied.code',
                'ligtIn:GBD.GGP.naam': 'LigtInGgpgebied.naam',
                'ligtIn:GBD.SDL.identificatie': 'ligtInStadsdeel.identificatie',
                'ligtIn:GBD.SDL.volgnummer': 'ligtInStadsdeel.volgnummer',
                'ligtIn:GBD.SDL.code': 'ligtInStadsdeel.code',
                'ligtIn:GBD.SDL.naam': 'ligtInStadsdeel.naam',
                'ligtIn:BRK.GME.identificatie': 'ligtInGemeente.identificatie',
                'ligtIn:BRK.GME.volgnummer': 'ligtInGemeente.volgnummer',
                'ligtIn:BRK.GME.naam': 'ligtInGemeente.naam',
                'geometrie': {
                    'action': 'format',
                    'formatter': format_geometry,
                    'value': 'geometrie'
                },
            },
            'query': '''
{
  gebiedenBouwblokken(sort: [identificatie_asc, volgnummer_asc], active: false) {
    edges {
      node {
        identificatie
        volgnummer
        registratiedatum
        code
        beginGeldigheid
        eindGeldigheid
        geometrie
        ligtInBuurt(active: false) {
          edges {
            node {
              identificatie
              volgnummer
              code
              naam
              beginGeldigheid
              eindGeldigheid
              LigtInGgwgebied(active: false) {
                edges {
                  node {
                    identificatie
                    volgnummer
                    code
                    naam
                    beginGeldigheid
                    eindGeldigheid
                  }
                }
              }
              LigtInGgpgebied(active: false) {
                edges {
                  node {
                    identificatie
                    volgnummer
                    code
                    naam
                    beginGeldigheid
                    eindGeldigheid
                  }
                }
              }
              ligtInWijk(active: false) {
                edges {
                  node {
                    identificatie
                    volgnummer
                    code
                    naam
                    beginGeldigheid
                    eindGeldigheid
                    ligtInStadsdeel(active: false) {
                      edges {
                        node {
                          identificatie
                          volgnummer
                          code
                          naam
                          beginGeldigheid
                          eindGeldigheid
                          ligtInGemeente(active: false) {
                            edges {
                              node {
                                identificatie
                                naam
                                beginGeldigheid
                                eindGeldigheid
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
'''
        }
    }
