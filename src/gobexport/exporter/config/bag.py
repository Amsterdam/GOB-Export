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
  woonplaatsen(active: true) {
    edges {
      node {
        identificatie
        volgnummer
        aanduidingInOnderzoek
        geconstateerd
        naam
        beginGeldigheid
        eindGeldigheid
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
            'filename': 'CSV_Actueel/BAG_woonplaats.csv',
            'mime_type': 'plain/text',
            'format': {
                'identificatie': 'identificatie',
                'volgnummer': 'volgnummer',
                'aanduidingInOnderzoek': 'aanduidingInOnderzoek',
                'geconstateerd': 'geconstateerd',
                'naam': 'naam',
                'beginGeldigheid': 'beginGeldigheid',
                'eindGeldigheid': 'eindGeldigheid',
                'documentdatum': 'documentdatum',
                'documentnummer': 'documentnummer',
                'status': 'status.omschrijving',
                'ligtIn:BRK.GME.identificatie': 'ligtInGemeente.identificatie',
                'ligtIn:BRK.GME.naam': 'ligtInGemeente.naam',
                'geometrie': 'geometrie',
            },
            'query': query_actueel
        },
        'esri_actueel': {
            'api_type': 'graphql',
            'exporter': esri_exporter,
            'filename': 'SHP/BAG_woonplaats.shp',
            'mime_type': 'application/octet-stream',
            'format': {
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
  openbareruimtes(active: true) {
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
                'identificatie': 'identificatie',
                'volgnummer': 'volgnummer',
                'aanduidingInOnderzoek': 'aanduidingInOnderzoek',
                'geconstateerd': 'geconstateerd',
                'naam': 'naam',
                'naamNen': 'naamNen',
                'beginGeldigheid': 'beginGeldigheid',
                'eindGeldigheid': 'eindGeldigheid',
                'type': 'type.omschrijving',
                'documentdatum': 'documentdatum',
                'documentnummer': 'documentnummer',
                'status': 'status.omschrijving',
                'ligtIn:BAG.WPL.identificatie': 'ligtInWoonplaats.identificatie',
                'ligtIn:BAG.WPL.volgnummer': 'ligtInWoonplaats.volgnummer',
                'geometrie': 'geometrie',
            },
            'query': query_actueel
        },
        'esri_actueel': {
            'api_type': 'graphql',
            'exporter': esri_exporter,
            'filename': 'SHP/BAG_openbare_ruimte.shp',
            'mime_type': 'application/octet-stream',
            'format': {
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
                'identificatie': 'identificatie',
                'volgnummer': 'volgnummer',
                'naam': 'naam',
                'beschrijvingNaam': 'beschrijvingNaam',
            },
            'query': '''
{
  openbareruimtes(active: true) {
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
        }
    }


class NummeraanduidingenExportConfig:

    query_actueel = '''
{
  nummeraanduidingen(active: true) {
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
                'identificatie': 'identificatie',
                'volgnummer': 'volgnummer',
                'aanduidingInOnderzoek': 'aanduidingInOnderzoek',
                'geconstateerd': 'geconstateerd',
                'huisnummer': 'huisnummer',
                'huisletter': 'huisletter',
                'huisnummertoevoeging': 'huisnummertoevoeging',
                'postcode': 'postcode',
                'ligtAan:BAG.ORE.identificatie': 'ligtAanOpenbareruimte.identificatie',
                'ligtAan:BAG.ORE.voglnummer': 'ligtAanOpenbareruimte.volgnummer',
                'ligtAan:BAG.ORE.naam': 'ligtAanOpenbareruimte.naam',
                'ligtIn:BAG.WPL.identificatie': 'ligtInWoonplaats.identificatie',
                'ligtIn:BAG.WPL.volgnummer': 'ligtInWoonplaats.volgnummer',
                'ligtIn:BAG.WPL.naam': 'ligtInWoonplaats.naam',
                'beginGeldigheid': 'beginGeldigheid',
                'eindGeldigheid': 'eindGeldigheid',
                'typeAdresseerbaarObject': 'typeAdresseerbaarObject',
                'documentdatum': 'documentdatum',
                'documentnummer': 'documentnummer',
                'status': 'status',
                'adresseert:BAG.VOT.identificatie': 'adresseertVerblijfsobject.identificatie',
                'adresseert:BAG.LPS.identificatie': 'adresseertLigplaats.identificatie',
                'adresseert:BAG.SPS.identificatie': 'adresseertStandplaats.identificatie',
                'adresseert:BAG.VOT.volgnummer': 'adresseertVerblijfsobject.volgnummer',
                'adresseert:BAG.LPS.volgnummer': 'adresseertLigplaats.volgnummer',
                'adresseert:BAG.SPS.volgnummer': 'adresseertStandplaats.volgnummer',
            },
            'query': query_actueel
        }
    }


class VerblijfsobjectenExportConfig:

    query_actueel = '''
{
  verblijfsobjecten(active: true) {
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
                'identificatie': 'identificatie',
                'volgnummer': 'volgnummer',
                'aanduidingInOnderzoek': 'aanduidingInOnderzoek',
                'geconstateerd': 'geconstateerd',
                'heeftIn:BAG.NAG.identificatieHoofdadres': 'heeftHoofdadres.identificatie',
                'heeftIn:BAG.NAG.volgnummerHoofdadres': 'heeftHoofdadres.volgnummer',
                'huisnummerHoofdadres': 'heeftHoofdadres.huisnummer',
                'huisletterHoofdadres': 'heeftHoofdadres.huisletter',
                'huisnummerToevoegingHoofdadres': 'heeftHoofdadres.huisnummerToevoeging',
                'postcodeHoofdadres': 'heeftHoofdadres.postcode',
                'ligtAan:BAG.ORE.identificatieHoofdadres': 'ligtAanOpenbareruimte.identificatie',
                'ligtAan:BAG.ORE.voglnummerHoofdadres': 'ligtAanOpenbareruimte.volgnummer',
                'ligtAan:BAG.ORE.naamHoofdadres': 'ligtAanOpenbareruimte.naam',
                'ligtIn:BAG.WPL.identificatieHoofdadres': 'ligtInWoonplaats.identificatie',
                'ligtIn:BAG.WPL.volgnummerHoofdadres': 'ligtInWoonplaats.volgnummer',
                'ligtIn:BAG.WPL.naamHoofdadres': 'ligtInWoonplaats.naam',
                'ligtIn:BRK.GME.identificatie': 'ligtInGemeente.identificatie',
                'ligtIn:BRK.GME.naam': 'ligtInGemeente.naam',
                'heeftIn:BAG.NAG.identificatieNevenadres': 'heeftNevenadres.identificatie',
                'heeftIn:BAG.NAG.volgnummerNevenadres': 'heeftNevenadres.volgnummer',
                'gebruiksdoel': 'gebruiksdoel',
                'gebruiksdoelWoonfunctie': 'gebruiksdoelWoonfunctie',
                'gebruiksdoelGezondheidszorgfunctie': 'gebruiksdoelGezondheidszorgfunctie',
                'aantalEenhedenComplex': 'aantalEenhedenComplex',
                'feitelijkGebruik': 'feitelijkGebruik.omschrijving',
                'oppervlakte': 'oppervlakte',
                'status': 'status.omschrijving',
                'beginGeldigheid': 'beginGeldigheid',
                'eindGeldigheid': 'eindGeldigheid',
                'documentdatum': 'documentdatum',
                'documentnummer': 'documentnummer',
                'verdiepingToegang': 'verdiepingToegang',
                'toegang': 'toegang',
                'aantalBouwlagen': 'aantalBouwlagen',
                'hoogsteBouwlaag': 'hoogsteBouwlaag',
                'laagsteBouwlaag': 'laagsteBouwlaag',
                'aantalKamers': 'aantalKamers',
                'eigendomsverhouding': 'eigendomsverhouding',
                'redenopvoer': 'redenopvoer',
                'redenafvoer': 'redenafvoer',
                'ligtIn:BAG.PND.identificatie': 'ligtInPanden.0.identificatie',
                'ligtIn:BAG.PND.volgnummer': 'ligtInPanden.0.volgnummer',
                'ligtIn:GBD.BBK.identificatie': 'ligtInBouwblok.identificatie',
                'ligtIn:GBD.BBK.volgnummer': 'ligtInBouwblok.volgnummer',
                'ligtIn:GBD.BBK.code': 'ligtInBouwblok.code',
                'ligtIn:GBD.BRT.identificatie': 'ligtInBuurt.identificatie',
                'ligtIn:GBD.BRT.volgnummer': 'ligtInBuurt.volgnummer',
                'ligtIn:GBD.BRT.naam': 'ligtInBuurt.naam',
                'ligtIn:GBD.BRT.code': 'ligtInBuurt.code',
                'ligtIn:GBD.WIJK.identificatie': 'ligtInWijk.identificatie',
                'ligtIn:GBD.WIJK.volgnummer': 'ligtInWijk.volgnummer',
                'ligtIn:GBD.WIJK.naam': 'ligtInWijk.naam',
                'ligtIn:GBD.WIJK.code': 'ligtInWijk.code',
                'ligtIn:GBD.GGW.identificatie': 'LigtInGgwgebied.identificatie',
                'ligtIn:GBD.GGW.volgnummer': 'LigtInGgwgebied.volgnummer',
                'ligtIn:GBD.GGW.naam': 'LigtInGgwgebied.naam',
                'ligtIn:GBD.GGW.code': 'LigtInGgwgebied.code',
                'ligtIn:GBD.GGP.identificatie': 'LigtInGgpgebied.identificatie',
                'ligtIn:GBD.GGP.volgnummer': 'LigtInGgpgebied.volgnummer',
                'ligtIn:GBD.GGP.naam': 'LigtInGgpgebied.naam',
                'ligtIn:GBD.GGP.code': 'LigtInGgpgebied.code',
                'ligtIn:GBD.SDL.identificatie': 'ligtInStadsdeel.identificatie',
                'ligtIn:GBD.SDL.volgnummer': 'ligtInStadsdeel.volgnummer',
                'ligtIn:GBD.SDL.naam': 'ligtInStadsdeel.naam',
                'ligtIn:GBD.SDL.code': 'ligtInStadsdeel.code',
                'geometrie': 'geometrie'
            },
            'query': query_actueel
        },
        'esri_actueel': {
            'api_type': 'graphql',
            'exporter': esri_exporter,
            'filename': 'SHP/BAG_verblijfsobject.shp',
            'mime_type': 'application/octet-stream',
            'format': {
                'id': 'identificatie',
                'volgnummer': 'volgnummer',
                'onderzoek': 'aanduidingInOnderzoek',
                'geconst': 'geconstateerd',
                'num_id_hfd': 'heeftHoofdadres.identificatie',
                'gme_id': 'ligtInGemeente.identificatie',
                'gm_naam': 'ligtInGemeente.naam',
                'num_id_nvn': 'heeftNevenadres.identificatie',
                'gebr_doel': 'gebruiksdoel',
                'gebr_wonen': 'gebruiksdoelWoonfunctie',
                'gebr_gezond': 'gebruiksdoelGezondheidszorgfunctie',
                'eenheden': 'aantalEenhedenComplex',
                'feit_gebr': 'feitelijkGebruik.omschrijving',
                'oppervlak': 'oppervlakte',
                'status': 'status.omschrijving',
                'begindatum': 'beginGeldigheid',
                'einddatum': 'eindGeldigheid',
                'docdatum': 'documentdatum',
                'docnummer': 'documentnummer',
                'verd_toe': 'verdiepingToegang',
                'toegang': 'toegang',
                'aant_bouwl': 'aantalBouwlagen',
                'hoog_bouwl': 'hoogsteBouwlaag',
                'laag_bouwl': 'laagsteBouwlaag',
                'aant_kamer': 'aantalKamers',
                'eigendom': 'eigendomsverhouding',
                'opvoer': 'redenopvoer',
                'afvoer': 'redenafvoer',
                'pnd_id': 'ligtInPanden.0.identificatie',
                'bbk_id': 'ligtInBouwblok.identificatie',
                'bbk_code': 'ligtInBouwblok.code',
                'brt_id': 'ligtInBuurt.identificatie',
                'brt_naam': 'ligtInBuurt.naam',
                'brt_code': 'ligtInBuurt.code',
                'wijk_id': 'ligtInWijk.identificatie',
                'wijk_naam': 'ligtInWijk.naam',
                'wijk_code': 'ligtInWijk.code',
                'ggw_id': 'LigtInGgwgebied.identificatie',
                'ggw_naam': 'LigtInGgwgebied.naam',
                'ggw_code': 'LigtInGgwgebied.code',
                'ggp_id': 'LigtInGgpgebied.identificatie',
                'ggp_naam': 'LigtInGgpgebied.naam',
                'ggp_code': 'LigtInGgpgebied.code',
                'sdl_id': 'ligtInStadsdeel.identificatie',
                'sdl_naam': 'ligtInStadsdeel.naam',
                'sdl_code': 'ligtInStadsdeel.code',
            },
            'extra_files': [
                {
                    'filename': 'SHP/BAG_verblijfsobject.dbf',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'SHP/BAG_verblijfsobject.shx',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'SHP/BAG_verblijfsobject.prj',
                    'mime_type': 'application/octet-stream'
                },
            ],
            'query': query_actueel
        },
    }


class StandplaatsenExportConfig:

    query_actueel = '''
{
  standplaatsen(active: true) {
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
                'identificatie': 'identificatie',
                'volgnummer': 'volgnummer',
                'aanduidingInOnderzoek': 'aanduidingInOnderzoek',
                'geconstateerd': 'geconstateerd',
                'heeftIn:BAG.NAG.identificatieHoofdadres': 'heeftHoofdadres.identificatie',
                'heeftIn:BAG.NAG.volgnummerHoofdadres': 'heeftHoofdadres.volgnummer',
                'huisnummerHoofdadres': 'heeftHoofdadres.huisnummer',
                'huisletterHoofdadres': 'heeftHoofdadres.huisletter',
                'huisnummerToevoegingHoofdadres': 'heeftHoofdadres.huisnummerToevoeging',
                'postcodeHoofdadres': 'heeftHoofdadres.postcode',
                'ligtAan:BAG.ORE.identificatieHoofdadres': 'ligtAanOpenbareruimte.identificatie',
                'ligtAan:BAG.ORE.voglnummerHoofdadres': 'ligtAanOpenbareruimte.volgnummer',
                'ligtAan:BAG.ORE.naamHoofdadres': 'ligtAanOpenbareruimte.naam',
                'ligtIn:BAG.WPL.identificatieHoofdadres': 'ligtInWoonplaats.identificatie',
                'ligtIn:BAG.WPL.volgnummerHoofdadres': 'ligtInWoonplaats.volgnummer',
                'ligtIn:BAG.WPL.naamHoofdadres': 'ligtInWoonplaats.naam',
                'ligtIn:BRK.GME.identificatie': 'ligtInGemeente.identificatie',
                'ligtIn:BRK.GME.naam': 'ligtInGemeente.naam',
                'heeftIn:BAG.NAG.identificatieNevenadres': 'heeftNevenadres.identificatie',
                'heeftIn:BAG.NAG.volgnummerNevenadres': 'heeftNevenadres.volgnummer',
                'status': 'status.omschrijving',
                'feitelijkGebruik': 'feitelijkGebruik.omschrijving',
                'beginGeldigheid': 'beginGeldigheid',
                'eindGeldigheid': 'eindGeldigheid',
                'documentdatum': 'documentdatum',
                'documentnummer': 'documentnummer',
                'ligtIn:GBD.BRT.identificatie': 'ligtInBuurt.identificatie',
                'ligtIn:GBD.BRT.volgnummer': 'ligtInBuurt.volgnummer',
                'ligtIn:GBD.BRT.naam': 'ligtInBuurt.naam',
                'ligtIn:GBD.BRT.code': 'ligtInBuurt.code',
                'ligtIn:GBD.WIJK.identificatie': 'ligtInWijk.identificatie',
                'ligtIn:GBD.WIJK.volgnummer': 'ligtInWijk.volgnummer',
                'ligtIn:GBD.WIJK.naam': 'ligtInWijk.naam',
                'ligtIn:GBD.WIJK.code': 'ligtInWijk.code',
                'ligtIn:GBD.GGW.identificatie': 'LigtInGgwgebied.identificatie',
                'ligtIn:GBD.GGW.volgnummer': 'LigtInGgwgebied.volgnummer',
                'ligtIn:GBD.GGW.naam': 'LigtInGgwgebied.naam',
                'ligtIn:GBD.GGW.code': 'LigtInGgwgebied.code',
                'ligtIn:GBD.GGP.identificatie': 'LigtInGgpgebied.identificatie',
                'ligtIn:GBD.GGP.volgnummer': 'LigtInGgpgebied.volgnummer',
                'ligtIn:GBD.GGP.naam': 'LigtInGgpgebied.naam',
                'ligtIn:GBD.GGP.code': 'LigtInGgpgebied.code',
                'ligtIn:GBD.SDL.identificatie': 'ligtInStadsdeel.identificatie',
                'ligtIn:GBD.SDL.volgnummer': 'ligtInStadsdeel.volgnummer',
                'ligtIn:GBD.SDL.naam': 'ligtInStadsdeel.naam',
                'ligtIn:GBD.SDL.code': 'ligtInStadsdeel.code',
                'geometrie': 'geometrie'
            },
            'query': query_actueel
        },
        'esri_actueel': {
            'api_type': 'graphql',
            'exporter': esri_exporter,
            'filename': 'SHP/BAG_standplaats.shp',
            'mime_type': 'application/octet-stream',
            'format': {
                'id': 'identificatie',
                'volgnummer': 'volgnummer',
                'onderzoek': 'aanduidingInOnderzoek',
                'geconst': 'geconstateerd',
                'num_id_hfd': 'heeftHoofdadres.identificatie',
                'gme_id': 'ligtInGemeente.identificatie',
                'gm_naam': 'ligtInGemeente.naam',
                'num_id_nvn': 'heeftNevenadres.identificatie',
                'status': 'status.omschrijving',
                'feit_gebr': 'feitelijkGebruik.omschrijving',
                'begindatum': 'beginGeldigheid',
                'einddatum': 'eindGeldigheid',
                'docdatum': 'documentdatum',
                'docnummer': 'documentnummer',
                'brt_id': 'ligtInBuurt.identificatie',
                'brt_naam': 'ligtInBuurt.naam',
                'brt_code': 'ligtInBuurt.code',
                'wijk_id': 'ligtInWijk.identificatie',
                'wijk_naam': 'ligtInWijk.naam',
                'wijk_code': 'ligtInWijk.code',
                'ggw_id': 'LigtInGgwgebied.identificatie',
                'ggw_naam': 'LigtInGgwgebied.naam',
                'ggw_code': 'LigtInGgwgebied.code',
                'ggp_id': 'LigtInGgpgebied.identificatie',
                'ggp_naam': 'LigtInGgpgebied.naam',
                'ggp_code': 'LigtInGgpgebied.code',
                'sdl_id': 'ligtInStadsdeel.identificatie',
                'sdl_naam': 'ligtInStadsdeel.naam',
                'sdl_code': 'ligtInStadsdeel.code',
            },
            'extra_files': [
                {
                    'filename': 'SHP/BAG_standplaats.dbf',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'SHP/BAG_standplaats.shx',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'SHP/BAG_standplaats.prj',
                    'mime_type': 'application/octet-stream'
                },
            ],
            'query': query_actueel
        },
    }


class LigplaatsenExportConfig:

    query_actueel = '''
{
  ligplaatsen(active: true) {
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
                'identificatie': 'identificatie',
                'volgnummer': 'volgnummer',
                'aanduidingInOnderzoek': 'aanduidingInOnderzoek',
                'geconstateerd': 'geconstateerd',
                'heeftIn:BAG.NAG.identificatieHoofdadres': 'heeftHoofdadres.identificatie',
                'heeftIn:BAG.NAG.volgnummerHoofdadres': 'heeftHoofdadres.volgnummer',
                'huisnummerHoofdadres': 'heeftHoofdadres.huisnummer',
                'huisletterHoofdadres': 'heeftHoofdadres.huisletter',
                'huisnummerToevoegingHoofdadres': 'heeftHoofdadres.huisnummerToevoeging',
                'postcodeHoofdadres': 'heeftHoofdadres.postcode',
                'ligtAan:BAG.ORE.identificatieHoofdadres': 'ligtAanOpenbareruimte.identificatie',
                'ligtAan:BAG.ORE.voglnummerHoofdadres': 'ligtAanOpenbareruimte.volgnummer',
                'ligtAan:BAG.ORE.naamHoofdadres': 'ligtAanOpenbareruimte.naam',
                'ligtIn:BAG.WPL.identificatieHoofdadres': 'ligtInWoonplaats.identificatie',
                'ligtIn:BAG.WPL.volgnummerHoofdadres': 'ligtInWoonplaats.volgnummer',
                'ligtIn:BAG.WPL.naamHoofdadres': 'ligtInWoonplaats.naam',
                'ligtIn:BRK.GME.identificatie': 'ligtInGemeente.identificatie',
                'ligtIn:BRK.GME.naam': 'ligtInGemeente.naam',
                'heeftIn:BAG.NAG.identificatieNevenadres': 'heeftNevenadres.identificatie',
                'heeftIn:BAG.NAG.volgnummerNevenadres': 'heeftNevenadres.volgnummer',
                'status': 'status.omschrijving',
                'feitelijkGebruik': 'feitelijkGebruik.omschrijving',
                'beginGeldigheid': 'beginGeldigheid',
                'eindGeldigheid': 'eindGeldigheid',
                'documentdatum': 'documentdatum',
                'documentnummer': 'documentnummer',
                'ligtIn:GBD.BRT.identificatie': 'ligtInBuurt.identificatie',
                'ligtIn:GBD.BRT.volgnummer': 'ligtInBuurt.volgnummer',
                'ligtIn:GBD.BRT.naam': 'ligtInBuurt.naam',
                'ligtIn:GBD.BRT.code': 'ligtInBuurt.code',
                'ligtIn:GBD.WIJK.identificatie': 'ligtInWijk.identificatie',
                'ligtIn:GBD.WIJK.volgnummer': 'ligtInWijk.volgnummer',
                'ligtIn:GBD.WIJK.naam': 'ligtInWijk.naam',
                'ligtIn:GBD.WIJK.code': 'ligtInWijk.code',
                'ligtIn:GBD.GGW.identificatie': 'LigtInGgwgebied.identificatie',
                'ligtIn:GBD.GGW.volgnummer': 'LigtInGgwgebied.volgnummer',
                'ligtIn:GBD.GGW.naam': 'LigtInGgwgebied.naam',
                'ligtIn:GBD.GGW.code': 'LigtInGgwgebied.code',
                'ligtIn:GBD.GGP.identificatie': 'LigtInGgpgebied.identificatie',
                'ligtIn:GBD.GGP.volgnummer': 'LigtInGgpgebied.volgnummer',
                'ligtIn:GBD.GGP.naam': 'LigtInGgpgebied.naam',
                'ligtIn:GBD.GGP.code': 'LigtInGgpgebied.code',
                'ligtIn:GBD.SDL.identificatie': 'ligtInStadsdeel.identificatie',
                'ligtIn:GBD.SDL.volgnummer': 'ligtInStadsdeel.volgnummer',
                'ligtIn:GBD.SDL.naam': 'ligtInStadsdeel.naam',
                'ligtIn:GBD.SDL.code': 'ligtInStadsdeel.code',
                'geometrie': 'geometrie'
            },
            'query': query_actueel
        },
        'esri_actueel': {
            'api_type': 'graphql',
            'exporter': esri_exporter,
            'filename': 'SHP/BAG_ligplaats.shp',
            'mime_type': 'application/octet-stream',
            'format': {
                'id': 'identificatie',
                'volgnummer': 'volgnummer',
                'onderzoek': 'aanduidingInOnderzoek',
                'geconst': 'geconstateerd',
                'num_id_hfd': 'heeftHoofdadres.identificatie',
                'gme_id': 'ligtInGemeente.identificatie',
                'gm_naam': 'ligtInGemeente.naam',
                'num_id_nvn': 'heeftNevenadres.identificatie',
                'status': 'status.omschrijving',
                'feit_gebr': 'feitelijkGebruik.omschrijving',
                'begindatum': 'beginGeldigheid',
                'einddatum': 'eindGeldigheid',
                'docdatum': 'documentdatum',
                'docnummer': 'documentnummer',
                'brt_id': 'ligtInBuurt.identificatie',
                'brt_naam': 'ligtInBuurt.naam',
                'brt_code': 'ligtInBuurt.code',
                'wijk_id': 'ligtInWijk.identificatie',
                'wijk_naam': 'ligtInWijk.naam',
                'wijk_code': 'ligtInWijk.code',
                'ggw_id': 'LigtInGgwgebied.identificatie',
                'ggw_naam': 'LigtInGgwgebied.naam',
                'ggw_code': 'LigtInGgwgebied.code',
                'ggp_id': 'LigtInGgpgebied.identificatie',
                'ggp_naam': 'LigtInGgpgebied.naam',
                'ggp_code': 'LigtInGgpgebied.code',
                'sdl_id': 'ligtInStadsdeel.identificatie',
                'sdl_naam': 'ligtInStadsdeel.naam',
                'sdl_code': 'ligtInStadsdeel.code',
            },
            'extra_files': [
                {
                    'filename': 'SHP/BAG_ligplaats.dbf',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'SHP/BAG_ligplaats.shx',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'SHP/BAG_ligplaats.prj',
                    'mime_type': 'application/octet-stream'
                },
            ],
            'query': query_actueel
        },
    }


class PandenExportConfig:

    query_actueel = '''
{
  panden(active: true) {
    edges {
      node {
        identificatie
        volgnummer
        aanduidingInOnderzoek
        geconstateerd
        oorspronkelijkBouwjaar
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
            'filename': 'CSV_Actueel/BAG_pand.csv',
            'mime_type': 'plain/text',
            'format': {
                'identificatie': 'identificatie',
                'volgnummer': 'volgnummer',
                'aanduidingInOnderzoek': 'aanduidingInOnderzoek',
                'geconstateerd': 'geconstateerd',
                'status': 'status',
                'oorspronkelijkBouwjaar': 'oorspronkelijkBouwjaar',
                'beginGeldigheid': 'beginGeldigheid',
                'eindGeldigheid': 'eindGeldigheid',
                'documentdatum': 'documentdatum',
                'documentnummer': 'documentnummer',
                'naam': 'naam',
                'ligging': 'ligging',
                'aantalBouwlagen': 'aantalBouwlagen',
                'hoogsteBouwlaag': 'hoogsteBouwlaag',
                'laagsteBouwlaag': 'laagsteBouwlaag',
                'ligtIn:GBD.BBK.identificatie': 'ligtInBouwblok.identificatie',
                'ligtIn:GBD.BBK.volgnummer': 'ligtInBouwblok.volgnummer',
                'ligtIn:GBD.BBK.code': 'ligtInBouwblok.code',
                'ligtIn:GBD.BRT.identificatie': 'ligtInBuurt.identificatie',
                'ligtIn:GBD.BRT.volgnummer': 'ligtInBuurt.volgnummer',
                'ligtIn:GBD.BRT.naam': 'ligtInBuurt.naam',
                'ligtIn:GBD.BRT.code': 'ligtInBuurt.code',
                'ligtIn:GBD.WIJK.identificatie': 'ligtInWijk.identificatie',
                'ligtIn:GBD.WIJK.volgnummer': 'ligtInWijk.volgnummer',
                'ligtIn:GBD.WIJK.naam': 'ligtInWijk.naam',
                'ligtIn:GBD.WIJK.code': 'ligtInWijk.code',
                'ligtIn:GBD.GGW.identificatie': 'LigtInGgwgebied.identificatie',
                'ligtIn:GBD.GGW.volgnummer': 'LigtInGgwgebied.volgnummer',
                'ligtIn:GBD.GGW.naam': 'LigtInGgwgebied.naam',
                'ligtIn:GBD.GGW.code': 'LigtInGgwgebied.code',
                'ligtIn:GBD.GGP.identificatie': 'LigtInGgpgebied.identificatie',
                'ligtIn:GBD.GGP.volgnummer': 'LigtInGgpgebied.volgnummer',
                'ligtIn:GBD.GGP.naam': 'LigtInGgpgebied.naam',
                'ligtIn:GBD.GGP.code': 'LigtInGgpgebied.code',
                'ligtIn:GBD.SDL.identificatie': 'ligtInStadsdeel.identificatie',
                'ligtIn:GBD.SDL.volgnummer': 'ligtInStadsdeel.volgnummer',
                'ligtIn:GBD.SDL.naam': 'ligtInStadsdeel.naam',
                'ligtIn:GBD.SDL.code': 'ligtInStadsdeel.code',
                'geometrie': 'geometrie'
            },
            'query': query_actueel
        },
        'esri_actueel': {
            'api_type': 'graphql',
            'exporter': esri_exporter,
            'filename': 'SHP/BAG_pand.shp',
            'mime_type': 'application/octet-stream',
            'format': {
                'pnd_id': 'identificatie',
                'volgnummer': 'volgnummer',
                'onderzoek': 'aanduidingInOnderzoek',
                'geconst': 'geconstateerd',
                'status': 'status',
                'bouwjaar': 'oorspronkelijkBouwjaar',
                'begindatum': 'beginGeldigheid',
                'einddatum': 'eindGeldigheid',
                'docdatum': 'documentdatum',
                'docnummer': 'documentnummer',
                'naam_pand': 'naam',
                'ligging': 'ligging',
                'aant_bouwl': 'aantalBouwlagen',
                'hoog_bouwl': 'hoogsteBouwlaag',
                'bbk_id': 'ligtInBouwblok.identificatie',
                'bbk_code': 'ligtInBouwblok.code',
                'brt_id': 'ligtInBuurt.identificatie',
                'brt_naam': 'ligtInBuurt.naam',
                'brt_code': 'ligtInBuurt.code',
                'wijk_id': 'ligtInWijk.identificatie',
                'wijk_naam': 'ligtInWijk.naam',
                'wijk_code': 'ligtInWijk.code',
                'ggw_id': 'LigtInGgwgebied.identificatie',
                'ggw_naam': 'LigtInGgwgebied.naam',
                'ggw_code': 'LigtInGgwgebied.code',
                'ggp_id': 'LigtInGgpgebied.identificatie',
                'ggp_naam': 'LigtInGgpgebied.naam',
                'ggp_code': 'LigtInGgpgebied.code',
                'sdl_id': 'ligtInStadsdeel.identificatie',
                'sdl_naam': 'ligtInStadsdeel.naam',
                'sdl_code': 'ligtInStadsdeel.code',
            },
            'extra_files': [
                {
                    'filename': 'SHP/BAG_pand.dbf',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'SHP/BAG_pand.shx',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'SHP/BAG_pand.prj',
                    'mime_type': 'application/octet-stream'
                },
            ],
            'query': query_actueel
        },
    }
