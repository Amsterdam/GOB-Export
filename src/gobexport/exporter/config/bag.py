from gobexport.exporter.csv import csv_exporter
from gobexport.exporter.esri import esri_exporter

from gobexport.formatter.geometry import format_geometry

import dateutil.parser as dt_parser

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

TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S'


class BAGDefaultFormat:

    default_values = {
        'aanduidingInOnderzoek': 'N',
        'onderzoek': 'N',
        'geconstateerd': 'N',
        'geconst': 'N',
    }

    def __init__(self, format):
        self.format = format
        self._update_attrs_with_default()

    def _update_attrs_with_default(self):
        for name, value in self.default_values.items():
            if name in self.format:
                reference = self.format[name]
                self.format[name] = {
                    'condition': 'isempty',
                    'trueval': {
                        'action': 'literal',
                        'value': value,
                    },
                    'falseval': reference,
                    'reference': reference,
                }

    def get_format(self):
        return self.format


def format_date(datetimestr):
    if not datetimestr:
        # Input variable may be empty
        return None

    try:
        dt = dt_parser.parse(datetimestr)
        return dt.strftime(TIMESTAMP_FORMAT)
    except ValueError:
        # If invalid datetimestr, just return the original string so that no data is lost
        return datetimestr


def format_soort_object(value):
    return '|'.join(dict.fromkeys(value.split('|')).keys()) if value else value


class WoonplaatsenExportConfig:

    query_actueel = '''
{
  bagWoonplaatsen {
    edges {
      node {
        identificatie
        heeftOnderzoeken(inOnderzoek: "J") {
          edges {
            node {
              identificatie
            }
          }
        }
        geconstateerd
        naam
        beginGeldigheid
        eindGeldigheid
        documentdatum
        documentnummer
        status
        ligtInGemeente {
          edges {
            node {
              identificatie
              naam
            }
          }
        }
        geometrie
      }
    }
  }
}
'''

    query_history = '''
{
  bagWoonplaatsen(active: false, sort: [identificatie_asc, volgnummer_asc]) {
    edges {
      node {
        identificatie
        volgnummer
        heeftOnderzoeken(inOnderzoek: "J", active: false) {
          edges {
            node {
              identificatie
            }
          }
        }
        geconstateerd
        naam
        beginGeldigheid
        eindGeldigheid
        documentdatum
        documentnummer
        registratiedatum
        status
        ligtInGemeente {
          edges {
            node {
              identificatie
              naam
            }
          }
        }
        geometrie
      }
    }
  }
}
'''

    format = BAGDefaultFormat({
        'identificatie': 'identificatie',
        'aanduidingInOnderzoek': {
            'condition': 'isempty',
            'reference': 'heeftOnderzoeken.[0].identificatie',
            'trueval': {
                'action': 'literal',
                'value': 'N',
            },
            'falseval': {
                'action': 'literal',
                'value': 'J'
            }
        },
        'geconstateerd': 'geconstateerd',
        'naam': 'naam',
        'beginGeldigheid': 'beginGeldigheid',
        'eindGeldigheid': 'eindGeldigheid',
        'documentdatum': 'documentdatum',
        'documentnummer': 'documentnummer',
        'status': 'status.omschrijving',
        'ligtIn:BRK.GME.identificatie': 'ligtInGemeente.identificatie',
        'ligtIn:BRK.GME.naam': 'ligtInGemeente.naam',
        'geometrie': {
            'action': 'format',
            'formatter': format_geometry,
            'value': 'geometrie'
        },
    })

    esri_format = BAGDefaultFormat({
        'id': 'identificatie',
        'onderzoek': {
            'condition': 'isempty',
            'reference': 'heeftOnderzoeken.[0].identificatie',
            'trueval': {
                'action': 'literal',
                'value': 'N',
            },
            'falseval': {
                'action': 'literal',
                'value': 'J'
            }
        },
        'geconst': 'geconstateerd',
        'naam': 'naam',
        'begindatum': 'beginGeldigheid',
        'einddatum': 'eindGeldigheid',
        'docdatum': 'documentdatum',
        'docnummer': 'documentnummer',
        'status': 'status.omschrijving',
        'gme_id': 'ligtInGemeente.identificatie',
        'gme_naam': 'ligtInGemeente.naam',
    })

    history_format = BAGDefaultFormat({
        'identificatie': 'identificatie',
        'volgnummer': 'volgnummer',
        'registratiedatum': 'registratiedatum',
        'aanduidingInOnderzoek': {
            'condition': 'isempty',
            'reference': 'heeftOnderzoeken.[0].identificatie',
            'trueval': {
                'action': 'literal',
                'value': 'N',
            },
            'falseval': {
                'action': 'literal',
                'value': 'J'
            }
        },
        'geconstateerd': 'geconstateerd',
        'naam': 'naam',
        'beginGeldigheid': 'beginGeldigheid',
        'eindGeldigheid': 'eindGeldigheid',
        'documentdatum': 'documentdatum',
        'documentnummer': 'documentnummer',
        'status': 'status.omschrijving',
        'ligtIn:BRK.GME.identificatie': 'ligtInGemeente.identificatie',
        'ligtIn:BRK.GME.volgnummer': '',
        'ligtIn:BRK.GME.naam': 'ligtInGemeente.naam',
        'geometrie': {
            'action': 'format',
            'formatter': format_geometry,
            'value': 'geometrie'
        },
    })

    products = {
        'csv_actueel': {
            'api_type': 'graphql',
            'exporter': csv_exporter,
            'filename': 'CSV_Actueel/BAG_woonplaats_Actueel.csv',
            'mime_type': 'plain/text',
            'format': format.get_format(),
            'query': query_actueel
        },
        'esri_actueel': {
            'api_type': 'graphql',
            'exporter': esri_exporter,
            'filename': 'SHP/BAG_woonplaats.shp',
            'mime_type': 'application/octet-stream',
            'format': esri_format.get_format(),
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
                {
                    'filename': 'SHP/BAG_woonplaats.cpg',
                    'mime_type': 'application/octet-stream'
                },
            ],
            'query': query_actueel
        },
        'csv_history': {
            'api_type': 'graphql',
            'exporter': csv_exporter,
            'filename': 'CSV_ActueelEnHistorie/BAG_woonplaats_ActueelEnHistorie.csv',
            'mime_type': 'plain/text',
            'format': history_format.get_format(),
            'query': query_history
        },
    }


class OpenbareruimtesExportConfig:

    query_actueel = '''
{
  bagOpenbareruimtes {
    edges {
      node {
        identificatie
        heeftOnderzoeken(inOnderzoek: "J") {
          edges {
            node {
              identificatie
            }
          }
        }
        geconstateerd
        naam
        naamNen
        beginGeldigheid
        eindGeldigheid
        ligtInWoonplaats(active: false) {
          edges {
            node {
              identificatie
              naam
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

    query_history = '''
{
  bagOpenbareruimtes(active: false, sort: [identificatie_asc, volgnummer_asc]) {
    edges {
      node {
        identificatie
        registratiedatum
        volgnummer
        heeftOnderzoeken(inOnderzoek: "J", active: false) {
          edges {
            node {
              identificatie
            }
          }
        }
        geconstateerd
        naam
        naamNen
        beginGeldigheid
        eindGeldigheid
        ligtInWoonplaats(active: false) {
          edges {
            node {
              identificatie
              volgnummer
              naam
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

    format = BAGDefaultFormat({
        'identificatie': 'identificatie',
        'aanduidingInOnderzoek': {
            'condition': 'isempty',
            'reference': 'heeftOnderzoeken.[0].identificatie',
            'trueval': {
                'action': 'literal',
                'value': 'N',
            },
            'falseval': {
                'action': 'literal',
                'value': 'J'
            }
        },
        'geconstateerd': 'geconstateerd',
        'naam': 'naam',
        'naamNEN': 'naamNen',
        'beginGeldigheid': 'beginGeldigheid',
        'eindGeldigheid': 'eindGeldigheid',
        'type': 'type.omschrijving',
        'documentdatum': 'documentdatum',
        'documentnummer': 'documentnummer',
        'status': 'status.omschrijving',
        'ligtIn:BAG.WPS.identificatie': 'ligtInWoonplaats.identificatie',
        'ligtIn:BAG.WPS.naam': 'ligtInWoonplaats.naam',
        'geometrie': {
            'action': 'format',
            'formatter': format_geometry,
            'value': 'geometrie'
        },
    })

    esri_format = BAGDefaultFormat({
        'id': 'identificatie',
        'onderzoek': {
            'condition': 'isempty',
            'reference': 'heeftOnderzoeken.[0].identificatie',
            'trueval': {
                'action': 'literal',
                'value': 'N',
            },
            'falseval': {
                'action': 'literal',
                'value': 'J'
            }
        },
        'geconst': 'geconstateerd',
        'naam': 'naam',
        'naam_nen': 'naamNen',
        'begindatum': 'beginGeldigheid',
        'einddatum': 'eindGeldigheid',
        'type': 'type.omschrijving',
        'docdatum': 'documentdatum',
        'docnummer': 'documentnummer',
        'status': 'status.omschrijving',
        'wps_id': 'ligtInWoonplaats.identificatie',
        'wps_naam': 'ligtInWoonplaats.naam',
    })

    history_format = BAGDefaultFormat({
        'identificatie': 'identificatie',
        'volgnummer': 'volgnummer',
        'registratiedatum': 'registratiedatum',
        'aanduidingInOnderzoek': {
            'condition': 'isempty',
            'reference': 'heeftOnderzoeken.[0].identificatie',
            'trueval': {
                'action': 'literal',
                'value': 'N',
            },
            'falseval': {
                'action': 'literal',
                'value': 'J'
            }
        },
        'geconstateerd': 'geconstateerd',
        'naam': 'naam',
        'naamNEN': 'naamNen',
        'beginGeldigheid': 'beginGeldigheid',
        'eindGeldigheid': 'eindGeldigheid',
        'type': 'type.omschrijving',
        'documentdatum': 'documentdatum',
        'documentnummer': 'documentnummer',
        'status': 'status.omschrijving',
        'ligtIn:BAG.WPS.identificatie': 'ligtInWoonplaats.identificatie',
        'ligtIn:BAG.WPS.volgnummer': 'ligtInWoonplaats.volgnummer',
        'ligtIn:BAG.WPS.naam': 'ligtInWoonplaats.naam',
        'geometrie': {
            'action': 'format',
            'formatter': format_geometry,
            'value': 'geometrie'
        },
    })

    products = {
        'csv_actueel': {
            'api_type': 'graphql',
            'exporter': csv_exporter,
            'filename': 'CSV_Actueel/BAG_openbare_ruimte_Actueel.csv',
            'mime_type': 'plain/text',
            'format': format.get_format(),
            'query': query_actueel
        },
        'esri_actueel': {
            'api_type': 'graphql',
            'exporter': esri_exporter,
            'filename': 'SHP/BAG_openbare_ruimte.shp',
            'mime_type': 'application/octet-stream',
            'format': esri_format.get_format(),
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
                {
                    'filename': 'SHP/BAG_openbare_ruimte.cpg',
                    'mime_type': 'application/octet-stream'
                },
            ],
            'query': query_actueel
        },
        'csv_history': {
            'api_type': 'graphql',
            'exporter': csv_exporter,
            'filename': 'CSV_ActueelEnHistorie/BAG_openbare_ruimte_ActueelEnHistorie.csv',
            'mime_type': 'plain/text',
            'format': history_format.get_format(),
            'query': query_history
        },
        'csv_beschrijving_actueel': {
            'api_type': 'graphql',
            'exporter': csv_exporter,
            'filename': 'CSV_Actueel/BAG_openbare_ruimte_beschrijving_Actueel.csv',
            'mime_type': 'plain/text',
            'format': {
                'identificatie': 'identificatie',
                'naam': 'naam',
                'beschrijving': 'beschrijvingNaam',
            },
            'query': '''
{
  bagOpenbareruimtes(active: true) {
    edges {
      node {
        identificatie
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

    format = BAGDefaultFormat({
        'identificatie': 'identificatie',
        'aanduidingInOnderzoek': 'aanduidingInOnderzoek',
        'geconstateerd': 'geconstateerd',
        'huisnummer': 'huisnummer',
        'huisletter': 'huisletter',
        'huisnummertoevoeging': 'huisnummertoevoeging',
        'postcode': 'postcode',
        'ligtAan:BAG.ORE.identificatie': 'ligtAanOpenbareruimte.identificatie',
        'ligtAan:BAG.ORE.naam': 'ligtAanOpenbareruimte.naam',
        'ligtIn:BAG.WPS.identificatie': 'ligtInWoonplaats.identificatie',
        'ligtIn:BAG.WPS.naam': 'ligtInWoonplaats.naam',
        'beginGeldigheid': 'beginGeldigheid',
        'eindGeldigheid': 'eindGeldigheid',
        'typeAdresseerbaarObject': 'typeAdresseerbaarObject.omschrijving',
        'typeAdres': 'typeAdres',
        'documentdatum': 'documentdatum',
        'documentnummer': 'documentnummer',
        'status': 'status.omschrijving',
        'adresseert:BAG.VOT.identificatie': 'adresseertVerblijfsobject.identificatie',
        'adresseert:BAG.LPS.identificatie': 'adresseertLigplaats.identificatie',
        'adresseert:BAG.SPS.identificatie': 'adresseertStandplaats.identificatie',
    })

    history_format = BAGDefaultFormat({
        'identificatie': 'identificatie',
        'volgnummer': 'volgnummer',
        'registratiedatum': 'registratiedatum',
        'aanduidingInOnderzoek': 'aanduidingInOnderzoek',
        'geconstateerd': 'geconstateerd',
        'huisnummer': 'huisnummer',
        'huisletter': 'huisletter',
        'huisnummertoevoeging': 'huisnummertoevoeging',
        'postcode': 'postcode',
        'ligtAan:BAG.ORE.identificatie': 'ligtAanOpenbareruimte.identificatie',
        'ligtAan:BAG.ORE.volgnummer': 'ligtAanOpenbareruimte.volgnummer',
        'ligtAan:BAG.ORE.naam': 'ligtAanOpenbareruimte.naam',
        'ligtIn:BAG.WPS.identificatie': 'ligtInWoonplaats.identificatie',
        'ligtIn:BAG.WPS.volgnummer': 'ligtInWoonplaats.volgnummer',
        'ligtIn:BAG.WPS.naam': 'ligtInWoonplaats.naam',
        'beginGeldigheid': 'beginGeldigheid',
        'eindGeldigheid': 'eindGeldigheid',
        'typeAdresseerbaarObject': 'typeAdresseerbaarObject.omschrijving',
        'typeAdres': 'typeAdres',
        'documentdatum': 'documentdatum',
        'documentnummer': 'documentnummer',
        'status': 'status.omschrijving',
        'adresseert:BAG.VOT.identificatie': 'adresseertVerblijfsobject.identificatie',
        'adresseert:BAG.VOT.volgnummer': 'adresseertVerblijfsobject.volgnummer',
        'adresseert:BAG.LPS.identificatie': 'adresseertLigplaats.identificatie',
        'adresseert:BAG.LPS.volgnummer': 'adresseertLigplaats.volgnummer',
        'adresseert:BAG.SPS.identificatie': 'adresseertStandplaats.identificatie',
        'adresseert:BAG.SPS.volgnummer': 'adresseertStandplaats.volgnummer',
    })

    products = {
        'csv_actueel': {
            'endpoint': '/gob/public/bag/nummeraanduidingen/?view=enhanced&ndjson=true',
            'exporter': csv_exporter,
            'filename': 'CSV_Actueel/BAG_nummeraanduiding_Actueel.csv',
            'mime_type': 'plain/text',
            'format': format.get_format(),
        },
        'csv_history': {
            'endpoint': '/gob/public/bag/nummeraanduidingen/?view=enhanced_history&ndjson=true',
            'exporter': csv_exporter,
            'filename': 'CSV_ActueelEnHistorie/BAG_nummeraanduiding_ActueelEnHistorie.csv',
            'mime_type': 'plain/text',
            'format': history_format.get_format(),
        },

    }


class VerblijfsobjectenExportConfig:

    format = BAGDefaultFormat({
        'identificatie': 'identificatie',
        'aanduidingInOnderzoek': 'aanduidingInOnderzoek',
        'geconstateerd': 'geconstateerd',
        'heeftIn:BAG.NAG.identificatieHoofdadres': 'heeftHoofdadres.identificatie',
        'huisnummerHoofdadres': 'heeftHoofdadres.huisnummer',
        'huisletterHoofdadres': 'heeftHoofdadres.huisletter',
        'huisnummertoevoegingHoofdadres': 'heeftHoofdadres.huisnummertoevoeging',
        'postcodeHoofdadres': 'heeftHoofdadres.postcode',
        'ligtAan:BAG.ORE.identificatieHoofdadres': 'ligtAanOpenbareruimte.identificatie',
        'ligtAan:BAG.ORE.naamHoofdadres': 'ligtAanOpenbareruimte.naam',
        'ligtIn:BAG.WPS.identificatieHoofdadres': 'ligtInWoonplaats.identificatie',
        'ligtIn:BAG.WPS.naamHoofdadres': 'ligtInWoonplaats.naam',
        'ligtIn:BRK.GME.identificatie': 'ligtInGemeente.identificatie',
        'ligtIn:BRK.GME.naam': 'ligtInGemeente.naam',
        'heeftIn:BAG.NAG.identificatieNevenadres': 'heeftNevenadres.identificatie',
        'gebruiksdoel': 'gebruiksdoel.omschrijving',
        'gebruiksdoelWoonfunctie': 'gebruiksdoelWoonfunctie.omschrijving',
        'gebruiksdoelGezondheidszorgfunctie': 'gebruiksdoelGezondheidszorgfunctie.omschrijving',
        'aantalEenhedenComplex': 'aantalEenhedenComplex',
        'is:WOZ.WOB.soortObject': 'soortobject.omschrijving',
        'oppervlakte': 'oppervlakte',
        'status': 'status.omschrijving',
        'beginGeldigheid': 'beginGeldigheid',
        'eindGeldigheid': 'eindGeldigheid',
        'documentdatum': 'documentdatum',
        'documentnummer': 'documentnummer',
        'verdiepingToegang': 'verdiepingToegang',
        'toegang': 'toegang.omschrijving',
        'aantalBouwlagen': 'aantalBouwlagen',
        'hoogsteBouwlaag': 'hoogsteBouwlaag',
        'laagsteBouwlaag': 'laagsteBouwlaag',
        'aantalKamers': 'aantalKamers',
        'eigendomsverhouding': 'eigendomsverhouding.omschrijving',
        'redenopvoer': 'redenopvoer.omschrijving',
        'redenafvoer': 'redenafvoer.omschrijving',
        'ligtIn:BAG.PND.identificatie': 'ligtInPanden.identificatie',
        'ligtIn:GBD.BBK.identificatie': 'ligtInBouwblok.identificatie',
        'ligtIn:GBD.BBK.code': 'ligtInBouwblok.code',
        'ligtIn:GBD.BRT.identificatie': 'ligtInBuurt.identificatie',
        'ligtIn:GBD.BRT.code': 'ligtInBuurt.code',
        'ligtIn:GBD.BRT.naam': 'ligtInBuurt.naam',
        'ligtIn:GBD.WIJK.identificatie': 'ligtInWijk.identificatie',
        'ligtIn:GBD.WIJK.code': 'ligtInWijk.code',
        'ligtIn:GBD.WIJK.naam': 'ligtInWijk.naam',
        'ligtIn:GBD.GGW.identificatie': 'ligtInGgwgebied.identificatie',
        'ligtIn:GBD.GGW.code': 'ligtInGgwgebied.code',
        'ligtIn:GBD.GGW.naam': 'ligtInGgwgebied.naam',
        'ligtIn:GBD.GGP.identificatie': 'ligtInGgpgebied.identificatie',
        'ligtIn:GBD.GGP.code': 'ligtInGgpgebied.code',
        'ligtIn:GBD.GGP.naam': 'ligtInGgpgebied.naam',
        'ligtIn:GBD.SDL.identificatie': 'ligtInStadsdeel.identificatie',
        'ligtIn:GBD.SDL.code': 'ligtInStadsdeel.code',
        'ligtIn:GBD.SDL.naam': 'ligtInStadsdeel.naam',
        'geometrie': {
            'action': 'format',
            'formatter': format_geometry,
            'value': 'geometrie'
        },
    })

    esri_format = BAGDefaultFormat({
        'id': 'identificatie',
        'onderzoek': 'aanduidingInOnderzoek',
        'geconst': 'geconstateerd',
        'num_id_hfd': 'heeftHoofdadres.identificatie',
        'huisnr_hfd': 'heeftHoofdadres.huisnummer',
        'huislt_hfd': 'heeftHoofdadres.huisletter',
        'huis_t_hfd': 'heeftHoofdadres.huisnummertoevoeging',
        'pc_hfd': 'heeftHoofdadres.postcode',
        'ore_id_hfd': 'ligtAanOpenbareruimte.identificatie',
        'ore_nm_hfd': 'ligtAanOpenbareruimte.naam',
        'wps_id_hfd': 'ligtInWoonplaats.identificatie',
        'wps_nm_hfd': 'ligtInWoonplaats.naam',
        'gme_id': 'ligtInGemeente.identificatie',
        'gme_naam': 'ligtInGemeente.naam',
        'num_id_nvn': 'heeftNevenadres.identificatie',
        'gebr_doel': 'gebruiksdoel.omschrijving',
        'gdl_wonen': 'gebruiksdoelWoonfunctie.omschrijving',
        'gdl_gezond': 'gebruiksdoelGezondheidszorgfunctie.omschrijving',
        'eenheden': 'aantalEenhedenComplex',
        'soort_obj': 'soortobject.omschrijving',
        'oppervlak': 'oppervlakte',
        'status': 'status.omschrijving',
        'begindatum': 'beginGeldigheid',
        'einddatum': 'eindGeldigheid',
        'docdatum': 'documentdatum',
        'docnummer': 'documentnummer',
        'verd_toe': 'verdiepingToegang',
        'toegang': 'toegang.omschrijving',
        'aant_bouwl': 'aantalBouwlagen',
        'hoog_bouwl': 'hoogsteBouwlaag',
        'laag_bouwl': 'laagsteBouwlaag',
        'aant_kamer': 'aantalKamers',
        'eigendom': 'eigendomsverhouding.omschrijving',
        'opvoer': 'redenopvoer.omschrijving',
        'afvoer': 'redenafvoer.omschrijving',
        'pnd_id': 'ligtInPanden.identificatie',
        'bbk_id': 'ligtInBouwblok.identificatie',
        'bbk_code': 'ligtInBouwblok.code',
        'brt_id': 'ligtInBuurt.identificatie',
        'brt_code': 'ligtInBuurt.code',
        'brt_naam': 'ligtInBuurt.naam',
        'wijk_id': 'ligtInWijk.identificatie',
        'wijk_code': 'ligtInWijk.code',
        'wijk_naam': 'ligtInWijk.naam',
        'ggw_id': 'ligtInGgwgebied.identificatie',
        'ggw_code': 'ligtInGgwgebied.code',
        'ggw_naam': 'ligtInGgwgebied.naam',
        'ggp_id': 'ligtInGgpgebied.identificatie',
        'ggp_code': 'ligtInGgpgebied.code',
        'ggp_naam': 'ligtInGgpgebied.naam',
        'sdl_id': 'ligtInStadsdeel.identificatie',
        'sdl_code': 'ligtInStadsdeel.code',
        'sdl_naam': 'ligtInStadsdeel.naam',
    })

    history_format = BAGDefaultFormat({
        'identificatie': 'identificatie',
        'volgnummer': 'volgnummer',
        'registratiedatum': 'registratiedatum',
        'aanduidingInOnderzoek': 'aanduidingInOnderzoek',
        'geconstateerd': 'geconstateerd',
        'heeftIn:BAG.NAG.identificatieHoofdadres': 'heeftHoofdadres.identificatie',
        'heeftIn:BAG.NAG.volgnummerHoofdadres': 'heeftHoofdadres.volgnummer',
        'huisnummerHoofdadres': 'heeftHoofdadres.huisnummer',
        'huisletterHoofdadres': 'heeftHoofdadres.huisletter',
        'huisnummertoevoegingHoofdadres': 'heeftHoofdadres.huisnummertoevoeging',
        'postcodeHoofdadres': 'heeftHoofdadres.postcode',
        'ligtAan:BAG.ORE.identificatieHoofdadres': 'ligtAanOpenbareruimte.identificatie',
        'ligtAan:BAG.ORE.volgnummerHoofdadres': 'ligtAanOpenbareruimte.volgnummer',
        'ligtAan:BAG.ORE.naamHoofdadres': 'ligtAanOpenbareruimte.naam',
        'ligtIn:BAG.WPS.identificatieHoofdadres': 'ligtInWoonplaats.identificatie',
        'ligtIn:BAG.WPS.volgnummerHoofdadres': 'ligtInWoonplaats.volgnummer',
        'ligtIn:BAG.WPS.naamHoofdadres': 'ligtInWoonplaats.naam',
        'ligtIn:BRK.GME.identificatie': 'ligtInGemeente.identificatie',
        'ligtIn:BRK.GME.volgnummer': 'ligtInGemeente.volgnummer',
        'ligtIn:BRK.GME.naam': 'ligtInGemeente.naam',
        'heeftIn:BAG.NAG.identificatieNevenadres': 'heeftNevenadres.identificatie',
        'heeftIn:BAG.NAG.volgnummerNevenadres': 'heeftNevenadres.volgnummer',
        'gebruiksdoel': 'gebruiksdoel.omschrijving',
        'gebruiksdoelWoonfunctie': 'gebruiksdoelWoonfunctie.omschrijving',
        'gebruiksdoelGezondheidszorgfunctie': 'gebruiksdoelGezondheidszorgfunctie.omschrijving',
        'aantalEenhedenComplex': 'aantalEenhedenComplex',
        'is:WOZ.WOB.soortObject': 'soortobject.omschrijving',
        'oppervlakte': 'oppervlakte',
        'status': 'status.omschrijving',
        'beginGeldigheid': 'beginGeldigheid',
        'eindGeldigheid': 'eindGeldigheid',
        'documentdatum': 'documentdatum',
        'documentnummer': 'documentnummer',
        'verdiepingToegang': 'verdiepingToegang',
        'toegang': 'toegang.omschrijving',
        'aantalBouwlagen': 'aantalBouwlagen',
        'hoogsteBouwlaag': 'hoogsteBouwlaag',
        'laagsteBouwlaag': 'laagsteBouwlaag',
        'aantalKamers': 'aantalKamers',
        'eigendomsverhouding': 'eigendomsverhouding.omschrijving',
        'redenopvoer': 'redenopvoer.omschrijving',
        'redenafvoer': 'redenafvoer.omschrijving',
        'ligtIn:BAG.PND.identificatie': 'ligtInPanden.identificatie',
        'ligtIn:BAG.PND.volgnummer': 'ligtInPanden.volgnummer',
        'ligtIn:GBD.BBK.identificatie': 'ligtInBouwblok.identificatie',
        'ligtIn:GBD.BBK.volgnummer': 'ligtInBouwblok.volgnummer',
        'ligtIn:GBD.BBK.code': 'ligtInBouwblok.code',
        'ligtIn:GBD.BRT.identificatie': 'ligtInBuurt.identificatie',
        'ligtIn:GBD.BRT.volgnummer': 'ligtInBuurt.volgnummer',
        'ligtIn:GBD.BRT.code': 'ligtInBuurt.code',
        'ligtIn:GBD.BRT.naam': 'ligtInBuurt.naam',
        'ligtIn:GBD.WIJK.identificatie': 'ligtInWijk.identificatie',
        'ligtIn:GBD.WIJK.volgnummer': 'ligtInWijk.volgnummer',
        'ligtIn:GBD.WIJK.code': 'ligtInWijk.code',
        'ligtIn:GBD.WIJK.naam': 'ligtInWijk.naam',
        'ligtIn:GBD.GGW.identificatie': 'ligtInGgwgebied.identificatie',
        'ligtIn:GBD.GGW.volgnummer': 'ligtInGgwgebied.volgnummer',
        'ligtIn:GBD.GGW.code': 'ligtInGgwgebied.code',
        'ligtIn:GBD.GGW.naam': 'ligtInGgwgebied.naam',
        'ligtIn:GBD.GGP.identificatie': 'ligtInGgpgebied.identificatie',
        'ligtIn:GBD.GGP.volgnummer': 'ligtInGgpgebied.volgnummer',
        'ligtIn:GBD.GGP.code': 'ligtInGgpgebied.code',
        'ligtIn:GBD.GGP.naam': 'ligtInGgpgebied.naam',
        'ligtIn:GBD.SDL.identificatie': 'ligtInStadsdeel.identificatie',
        'ligtIn:GBD.SDL.volgnummer': 'ligtInStadsdeel.volgnummer',
        'ligtIn:GBD.SDL.code': 'ligtInStadsdeel.code',
        'ligtIn:GBD.SDL.naam': 'ligtInStadsdeel.naam',
        'geometrie': {
            'action': 'format',
            'formatter': format_geometry,
            'value': 'geometrie'
        },
    })

    products = {
        'csv_actueel': {
            'endpoint': '/gob/public/bag/verblijfsobjecten/?view=enhanced&ndjson=true',
            'exporter': csv_exporter,
            'filename': 'CSV_Actueel/BAG_verblijfsobject_Actueel.csv',
            'mime_type': 'plain/text',
            'format': format.get_format(),
        },
        'esri_actueel': {
            'endpoint': '/gob/public/bag/verblijfsobjecten/?view=enhanced&ndjson=true',
            'exporter': esri_exporter,
            'filename': 'SHP/BAG_verblijfsobject.shp',
            'mime_type': 'application/octet-stream',
            'format': esri_format.get_format(),
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
                {
                    'filename': 'SHP/BAG_verblijfsobject.cpg',
                    'mime_type': 'application/octet-stream'
                },
            ],
        },
        'csv_history': {
            'endpoint': '/gob/public/bag/verblijfsobjecten/?view=enhanced_history&ndjson=true',
            'exporter': csv_exporter,
            'filename': 'CSV_ActueelEnHistorie/BAG_verblijfsobject_ActueelEnHistorie.csv',
            'mime_type': 'plain/text',
            'format': history_format.get_format(),
        },

    }


class StandplaatsenExportConfig:

    query_actueel = '''
{
  bagStandplaatsen {
    edges {
      node {
        identificatie
        geconstateerd
        heeftOnderzoeken(inOnderzoek: "J") {
          edges {
            node {
              identificatie
            }
          }
        }
        heeftHoofdadres {
          edges {
            node {
              identificatie
              huisnummer
              huisletter
              huisnummertoevoeging
              postcode
              ligtAanOpenbareruimte {
                edges {
                  node {
                    identificatie
                    naam
                    ligtInWoonplaats {
                      edges {
                        node {
                          identificatie
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
        heeftNevenadres {
          edges {
            node {
              identificatie
            }
          }
        }
        ligtInBuurt {
          edges {
            node {
              identificatie
              naam
              code
              ligtInWijk {
                edges {
                  node {
                    identificatie
                    naam
                    code
                    ligtInStadsdeel {
                      edges {
                        node {
                          identificatie
                          naam
                          code
                        }
                      }
                    }
                  }
                }
              }
              ligtInGgpgebied {
                edges {
                  node {
                    identificatie
                    naam
                    code
                  }
                }
              }
              ligtInGgwgebied {
                edges {
                  node {
                    identificatie
                    naam
                    code
                  }
                }
              }
            }
          }
        }
        invIsVerbondenMetStandplaatsWozWozdeelobjecten {
          edges {
            node {
              soortobject
            }
          }
        }
        status
        beginGeldigheid
        eindGeldigheid
        documentdatum
        documentnummer
        geometrie
        gebruiksdoel
      }
    }
  }
}
'''

    query_history = '''
{
  bagStandplaatsen(active: false, sort: [identificatie_asc, volgnummer_asc]) {
    edges {
      node {
        identificatie
        volgnummer
        registratiedatum
        heeftOnderzoeken(inOnderzoek: "J", active: false) {
          edges {
            node {
              identificatie
            }
          }
        }
        geconstateerd
        heeftHoofdadres(active: false) {
          edges {
            node {
              identificatie
              volgnummer
              huisnummer
              huisletter
              huisnummertoevoeging
              postcode
              ligtAanOpenbareruimte(active: false) {
                edges {
                  node {
                    identificatie
                    volgnummer
                    naam
                    ligtInWoonplaats(active: false) {
                      edges {
                        node {
                          identificatie
                          volgnummer
                          naam
                          ligtInGemeente(active: false) {
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
        heeftNevenadres(active: false) {
          edges {
            node {
              identificatie
              volgnummer
            }
          }
        }
        ligtInBuurt(active: false) {
          edges {
            node {
              identificatie
              volgnummer
              naam
              code
              ligtInWijk(active: false) {
                edges {
                  node {
                    identificatie
                    volgnummer
                    naam
                    code
                    ligtInStadsdeel(active: false) {
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
              ligtInGgpgebied(active: false) {
                edges {
                  node {
                    identificatie
                    volgnummer
                    naam
                    code
                  }
                }
              }
              ligtInGgwgebied(active: false) {
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
        invIsVerbondenMetStandplaatsWozWozdeelobjecten {
          edges {
            node {
              soortobject
            }
          }
        }
        status
        beginGeldigheid
        eindGeldigheid
        documentdatum
        documentnummer
        geometrie
        gebruiksdoel
      }
    }
  }
}
'''

    format = BAGDefaultFormat({
        'identificatie': 'identificatie',
        'aanduidingInOnderzoek': {
            'condition': 'isempty',
            'reference': 'heeftOnderzoeken.[0].identificatie',
            'trueval': {
                'action': 'literal',
                'value': 'N',
            },
            'falseval': {
                'action': 'literal',
                'value': 'J'
            }
        },
        'geconstateerd': 'geconstateerd',
        'heeftIn:BAG.NAG.identificatieHoofdadres': 'heeftHoofdadres.identificatie',
        'huisnummerHoofdadres': 'heeftHoofdadres.huisnummer',
        'huisletterHoofdadres': 'heeftHoofdadres.huisletter',
        'huisnummertoevoegingHoofdadres': 'heeftHoofdadres.huisnummertoevoeging',
        'postcodeHoofdadres': 'heeftHoofdadres.postcode',
        'ligtAan:BAG.ORE.identificatieHoofdadres': 'ligtAanOpenbareruimte.identificatie',
        'ligtAan:BAG.ORE.naamHoofdadres': 'ligtAanOpenbareruimte.naam',
        'ligtIn:BAG.WPS.identificatieHoofdadres': 'ligtInWoonplaats.identificatie',
        'ligtIn:BAG.WPS.naamHoofdadres': 'ligtInWoonplaats.naam',
        'ligtIn:BRK.GME.identificatie': 'ligtInGemeente.identificatie',
        'ligtIn:BRK.GME.naam': 'ligtInGemeente.naam',
        'heeftIn:BAG.NAG.identificatieNevenadres': 'heeftNevenadres.[0].identificatie',
        'gebruiksdoel': 'gebruiksdoel.omschrijving',
        'status': 'status.omschrijving',
        'is:WOZ.WOB.soortObject': {
            'action': 'format',
            'formatter': format_soort_object,
            'value': 'invIsVerbondenMetStandplaatsWozWozdeelobjecten.soortobject.omschrijving',
        },
        'beginGeldigheid': 'beginGeldigheid',
        'eindGeldigheid': 'eindGeldigheid',
        'documentdatum': 'documentdatum',
        'documentnummer': 'documentnummer',
        'ligtIn:GBD.BRT.identificatie': 'ligtInBuurt.identificatie',
        'ligtIn:GBD.BRT.code': 'ligtInBuurt.code',
        'ligtIn:GBD.BRT.naam': 'ligtInBuurt.naam',
        'ligtIn:GBD.WIJK.identificatie': 'ligtInWijk.identificatie',
        'ligtIn:GBD.WIJK.code': 'ligtInWijk.code',
        'ligtIn:GBD.WIJK.naam': 'ligtInWijk.naam',
        'ligtIn:GBD.GGW.identificatie': 'ligtInGgwgebied.identificatie',
        'ligtIn:GBD.GGW.code': 'ligtInGgwgebied.code',
        'ligtIn:GBD.GGW.naam': 'ligtInGgwgebied.naam',
        'ligtIn:GBD.GGP.identificatie': 'ligtInGgpgebied.identificatie',
        'ligtIn:GBD.GGP.code': 'ligtInGgpgebied.code',
        'ligtIn:GBD.GGP.naam': 'ligtInGgpgebied.naam',
        'ligtIn:GBD.SDL.identificatie': 'ligtInStadsdeel.identificatie',
        'ligtIn:GBD.SDL.code': 'ligtInStadsdeel.code',
        'ligtIn:GBD.SDL.naam': 'ligtInStadsdeel.naam',
        'geometrie': {
            'action': 'format',
            'formatter': format_geometry,
            'value': 'geometrie'
        },
    })

    esri_format = BAGDefaultFormat({
        'id': 'identificatie',
        'onderzoek': {
            'condition': 'isempty',
            'reference': 'heeftOnderzoeken.[0].identificatie',
            'trueval': {
                'action': 'literal',
                'value': 'N',
            },
            'falseval': {
                'action': 'literal',
                'value': 'J'
            }
        },
        'geconst': 'geconstateerd',
        'num_id_hfd': 'heeftHoofdadres.identificatie',
        'huisnr_hfd': 'heeftHoofdadres.huisnummer',
        'huislt_hfd': 'heeftHoofdadres.huisletter',
        'huis_t_hfd': 'heeftHoofdadres.huisnummertoevoeging',
        'pc_hfd': 'heeftHoofdadres.postcode',
        'ore_id_hfd': 'ligtAanOpenbareruimte.identificatie',
        'ore_nm_hfd': 'ligtAanOpenbareruimte.naam',
        'wps_id_hfd': 'ligtInWoonplaats.identificatie',
        'wps_nm_hfd': 'ligtInWoonplaats.naam',
        'gme_id': 'ligtInGemeente.identificatie',
        'gme_naam': 'ligtInGemeente.naam',
        'num_id_nvn': 'heeftNevenadres.identificatie',
        'gebr_doel': 'gebruiksdoel.omschrijving',
        'status': 'status.omschrijving',
        'soort_obj': {
            'action': 'format',
            'formatter': format_soort_object,
            'value': 'invIsVerbondenMetStandplaatsWozWozdeelobjecten.soortobject.omschrijving',
        },
        'begindatum': 'beginGeldigheid',
        'einddatum': 'eindGeldigheid',
        'docdatum': 'documentdatum',
        'docnummer': 'documentnummer',
        'brt_id': 'ligtInBuurt.identificatie',
        'brt_code': 'ligtInBuurt.code',
        'brt_naam': 'ligtInBuurt.naam',
        'wijk_id': 'ligtInWijk.identificatie',
        'wijk_code': 'ligtInWijk.code',
        'wijk_naam': 'ligtInWijk.naam',
        'ggw_id': 'ligtInGgwgebied.identificatie',
        'ggw_code': 'ligtInGgwgebied.code',
        'ggw_naam': 'ligtInGgwgebied.naam',
        'ggp_id': 'ligtInGgpgebied.identificatie',
        'ggp_code': 'ligtInGgpgebied.code',
        'ggp_naam': 'ligtInGgpgebied.naam',
        'sdl_id': 'ligtInStadsdeel.identificatie',
        'sdl_code': 'ligtInStadsdeel.code',
        'sdl_naam': 'ligtInStadsdeel.naam',
    })

    history_format = BAGDefaultFormat({
        'identificatie': 'identificatie',
        'volgnummer': 'volgnummer',
        'registratiedatum': 'registratiedatum',
        'aanduidingInOnderzoek': {
            'condition': 'isempty',
            'reference': 'heeftOnderzoeken.[0].identificatie',
            'trueval': {
                'action': 'literal',
                'value': 'N',
            },
            'falseval': {
                'action': 'literal',
                'value': 'J'
            }
        },
        'geconstateerd': 'geconstateerd',
        'heeftIn:BAG.NAG.identificatieHoofdadres': 'heeftHoofdadres.identificatie',
        'heeftIn:BAG.NAG.volgnummerHoofdadres': 'heeftHoofdadres.volgnummer',
        'huisnummerHoofdadres': 'heeftHoofdadres.huisnummer',
        'huisletterHoofdadres': 'heeftHoofdadres.huisletter',
        'huisnummertoevoegingHoofdadres': 'heeftHoofdadres.huisnummertoevoeging',
        'postcodeHoofdadres': 'heeftHoofdadres.postcode',
        'ligtAan:BAG.ORE.identificatieHoofdadres': 'ligtAanOpenbareruimte.identificatie',
        'ligtAan:BAG.ORE.volgnummerHoofdadres': 'ligtAanOpenbareruimte.volgnummer',
        'ligtAan:BAG.ORE.naamHoofdadres': 'ligtAanOpenbareruimte.naam',
        'ligtIn:BAG.WPS.identificatieHoofdadres': 'ligtInWoonplaats.identificatie',
        'ligtIn:BAG.WPS.volgnummerHoofdadres': 'ligtInWoonplaats.volgnummer',
        'ligtIn:BAG.WPS.naamHoofdadres': 'ligtInWoonplaats.naam',
        'ligtIn:BRK.GME.identificatie': 'ligtInGemeente.identificatie',
        'ligtIn:BRK.GME.volgnummer': 'ligtInGemeente.volgnummer',
        'ligtIn:BRK.GME.naam': 'ligtInGemeente.naam',
        'heeftIn:BAG.NAG.identificatieNevenadres': 'heeftNevenadres.identificatie',
        'heeftIn:BAG.NAG.volgnummerNevenadres': 'heeftNevenadres.volgnummer',
        'gebruiksdoel': 'gebruiksdoel.omschrijving',
        'status': 'status.omschrijving',
        'is:WOZ.WOB.soortObject': {
            'action': 'format',
            'formatter': format_soort_object,
            'value': 'invIsVerbondenMetStandplaatsWozWozdeelobjecten.soortobject.omschrijving',
        },
        'beginGeldigheid': 'beginGeldigheid',
        'eindGeldigheid': 'eindGeldigheid',
        'documentdatum': 'documentdatum',
        'documentnummer': 'documentnummer',
        'ligtIn:GBD.BRT.identificatie': 'ligtInBuurt.identificatie',
        'ligtIn:GBD.BRT.volgnummer': 'ligtInBuurt.volgnummer',
        'ligtIn:GBD.BRT.code': 'ligtInBuurt.code',
        'ligtIn:GBD.BRT.naam': 'ligtInBuurt.naam',
        'ligtIn:GBD.WIJK.identificatie': 'ligtInWijk.identificatie',
        'ligtIn:GBD.WIJK.volgnummer': 'ligtInWijk.volgnummer',
        'ligtIn:GBD.WIJK.code': 'ligtInWijk.code',
        'ligtIn:GBD.WIJK.naam': 'ligtInWijk.naam',
        'ligtIn:GBD.GGW.identificatie': 'ligtInGgwgebied.identificatie',
        'ligtIn:GBD.GGW.volgnummer': 'ligtInGgwgebied.volgnummer',
        'ligtIn:GBD.GGW.code': 'ligtInGgwgebied.code',
        'ligtIn:GBD.GGW.naam': 'ligtInGgwgebied.naam',
        'ligtIn:GBD.GGP.identificatie': 'ligtInGgpgebied.identificatie',
        'ligtIn:GBD.GGP.volgnummer': 'ligtInGgpgebied.volgnummer',
        'ligtIn:GBD.GGP.code': 'ligtInGgpgebied.code',
        'ligtIn:GBD.GGP.naam': 'ligtInGgpgebied.naam',
        'ligtIn:GBD.SDL.identificatie': 'ligtInStadsdeel.identificatie',
        'ligtIn:GBD.SDL.volgnummer': 'ligtInStadsdeel.volgnummer',
        'ligtIn:GBD.SDL.code': 'ligtInStadsdeel.code',
        'ligtIn:GBD.SDL.naam': 'ligtInStadsdeel.naam',
        'geometrie': {
            'action': 'format',
            'formatter': format_geometry,
            'value': 'geometrie'
        },
    })

    products = {
        'csv_actueel': {
            'api_type': 'graphql',
            'exporter': csv_exporter,
            'filename': 'CSV_Actueel/BAG_standplaats_Actueel.csv',
            'mime_type': 'plain/text',
            'format': format.get_format(),
            'query': query_actueel
        },
        'esri_actueel': {
            'api_type': 'graphql',
            'exporter': esri_exporter,
            'filename': 'SHP/BAG_standplaats.shp',
            'mime_type': 'application/octet-stream',
            'format': esri_format.get_format(),
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
                {
                    'filename': 'SHP/BAG_standplaats.cpg',
                    'mime_type': 'application/octet-stream'
                },
            ],
            'query': query_actueel
        },
        'csv_history': {
            'api_type': 'graphql',
            'exporter': csv_exporter,
            'filename': 'CSV_ActueelEnHistorie/BAG_standplaats_ActueelEnHistorie.csv',
            'mime_type': 'plain/text',
            'format': history_format.get_format(),
            'query': query_history
        },
    }


class LigplaatsenExportConfig:

    query_actueel = '''
{
  bagLigplaatsen {
    edges {
      node {
        identificatie
        heeftOnderzoeken(inOnderzoek: "J") {
          edges {
            node {
              identificatie
            }
          }
        }
        geconstateerd
        heeftHoofdadres {
          edges {
            node {
              identificatie
              huisnummer
              huisletter
              huisnummertoevoeging
              postcode
              ligtAanOpenbareruimte {
                edges {
                  node {
                    identificatie
                    naam
                    ligtInWoonplaats {
                      edges {
                        node {
                          identificatie
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
        heeftNevenadres {
          edges {
            node {
              identificatie
            }
          }
        }
        ligtInBuurt {
          edges {
            node {
              identificatie
              naam
              code
              ligtInWijk {
                edges {
                  node {
                    identificatie
                    naam
                    code
                    ligtInStadsdeel {
                      edges {
                        node {
                          identificatie
                          naam
                          code
                        }
                      }
                    }
                  }
                }
              }
              ligtInGgpgebied {
                edges {
                  node {
                    identificatie
                    naam
                    code
                  }
                }
              }
              ligtInGgwgebied {
                edges {
                  node {
                    identificatie
                    naam
                    code
                  }
                }
              }
            }
          }
        }
        invIsVerbondenMetLigplaatsWozWozdeelobjecten {
          edges {
            node {
              soortobject
            }
          }
        }
        status
        beginGeldigheid
        eindGeldigheid
        documentdatum
        documentnummer
        geometrie
        gebruiksdoel
      }
    }
  }
}
'''

    query_history = '''
{
  bagLigplaatsen(active: false, sort: [identificatie_asc, volgnummer_asc]) {
    edges {
      node {
        identificatie
        volgnummer
        registratiedatum
        heeftOnderzoeken(inOnderzoek: "J", active: false) {
          edges {
            node {
              identificatie
            }
          }
        }
        geconstateerd
        heeftHoofdadres(active: false) {
          edges {
            node {
              identificatie
              volgnummer
              huisnummer
              huisletter
              huisnummertoevoeging
              postcode
              ligtAanOpenbareruimte(active: false) {
                edges {
                  node {
                    identificatie
                    volgnummer
                    naam
                    ligtInWoonplaats(active: false) {
                      edges {
                        node {
                          identificatie
                          volgnummer
                          naam
                          ligtInGemeente(active: false) {
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
        heeftNevenadres(active: false) {
          edges {
            node {
              identificatie
              volgnummer
            }
          }
        }
        ligtInBuurt(active: false) {
          edges {
            node {
              identificatie
              volgnummer
              naam
              code
              ligtInWijk(active: false) {
                edges {
                  node {
                    identificatie
                    volgnummer
                    naam
                    code
                    ligtInStadsdeel(active: false) {
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
              ligtInGgpgebied(active: false) {
                edges {
                  node {
                    identificatie
                    volgnummer
                    naam
                    code
                  }
                }
              }
              ligtInGgwgebied(active: false) {
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
        invIsVerbondenMetLigplaatsWozWozdeelobjecten {
          edges {
            node {
              soortobject
            }
          }
        }
        status
        beginGeldigheid
        eindGeldigheid
        documentdatum
        documentnummer
        geometrie
        gebruiksdoel
      }
    }
  }
}
'''

    format = BAGDefaultFormat({
        'identificatie': 'identificatie',
        'aanduidingInOnderzoek': {
            'condition': 'isempty',
            'reference': 'heeftOnderzoeken.[0].identificatie',
            'trueval': {
                'action': 'literal',
                'value': 'N',
            },
            'falseval': {
                'action': 'literal',
                'value': 'J'
            }
        },
        'geconstateerd': 'geconstateerd',
        'heeftIn:BAG.NAG.identificatieHoofdadres': 'heeftHoofdadres.identificatie',
        'huisnummerHoofdadres': 'heeftHoofdadres.huisnummer',
        'huisletterHoofdadres': 'heeftHoofdadres.huisletter',
        'huisnummertoevoegingHoofdadres': 'heeftHoofdadres.huisnummertoevoeging',
        'postcodeHoofdadres': 'heeftHoofdadres.postcode',
        'ligtAan:BAG.ORE.identificatieHoofdadres': 'ligtAanOpenbareruimte.identificatie',
        'ligtAan:BAG.ORE.naamHoofdadres': 'ligtAanOpenbareruimte.naam',
        'ligtIn:BAG.WPS.identificatieHoofdadres': 'ligtInWoonplaats.identificatie',
        'ligtIn:BAG.WPS.naamHoofdadres': 'ligtInWoonplaats.naam',
        'ligtIn:BRK.GME.identificatie': 'ligtInGemeente.identificatie',
        'ligtIn:BRK.GME.naam': 'ligtInGemeente.naam',
        'heeftIn:BAG.NAG.identificatieNevenadres': 'heeftNevenadres.identificatie',
        'gebruiksdoel': 'gebruiksdoel.omschrijving',
        'status': 'status.omschrijving',
        'is:WOZ.WOB.soortObject': {
            'action': 'format',
            'formatter': format_soort_object,
            'value': 'invIsVerbondenMetLigplaatsWozWozdeelobjecten.soortobject.omschrijving',
        },
        'beginGeldigheid': 'beginGeldigheid',
        'eindGeldigheid': 'eindGeldigheid',
        'documentdatum': 'documentdatum',
        'documentnummer': 'documentnummer',
        'ligtIn:GBD.BRT.identificatie': 'ligtInBuurt.identificatie',
        'ligtIn:GBD.BRT.code': 'ligtInBuurt.code',
        'ligtIn:GBD.BRT.naam': 'ligtInBuurt.naam',
        'ligtIn:GBD.WIJK.identificatie': 'ligtInWijk.identificatie',
        'ligtIn:GBD.WIJK.code': 'ligtInWijk.code',
        'ligtIn:GBD.WIJK.naam': 'ligtInWijk.naam',
        'ligtIn:GBD.GGW.identificatie': 'ligtInGgwgebied.identificatie',
        'ligtIn:GBD.GGW.code': 'ligtInGgwgebied.code',
        'ligtIn:GBD.GGW.naam': 'ligtInGgwgebied.naam',
        'ligtIn:GBD.GGP.identificatie': 'ligtInGgpgebied.identificatie',
        'ligtIn:GBD.GGP.code': 'ligtInGgpgebied.code',
        'ligtIn:GBD.GGP.naam': 'ligtInGgpgebied.naam',
        'ligtIn:GBD.SDL.identificatie': 'ligtInStadsdeel.identificatie',
        'ligtIn:GBD.SDL.code': 'ligtInStadsdeel.code',
        'ligtIn:GBD.SDL.naam': 'ligtInStadsdeel.naam',
        'geometrie': {
            'action': 'format',
            'formatter': format_geometry,
            'value': 'geometrie'
        },
    })

    esri_format = BAGDefaultFormat({
        'id': 'identificatie',
        'onderzoek': {
            'condition': 'isempty',
            'reference': 'heeftOnderzoeken.[0].identificatie',
            'trueval': {
                'action': 'literal',
                'value': 'N',
            },
            'falseval': {
                'action': 'literal',
                'value': 'J'
            }
        },
        'geconst': 'geconstateerd',
        'num_id_hfd': 'heeftHoofdadres.identificatie',
        'huisnr_hfd': 'heeftHoofdadres.huisnummer',
        'huislt_hfd': 'heeftHoofdadres.huisletter',
        'huis_t_hfd': 'heeftHoofdadres.huisnummertoevoeging',
        'pc_hfd': 'heeftHoofdadres.postcode',
        'ore_id_hfd': 'ligtAanOpenbareruimte.identificatie',
        'ore_nm_hfd': 'ligtAanOpenbareruimte.naam',
        'wps_id_hfd': 'ligtInWoonplaats.identificatie',
        'wps_nm_hfd': 'ligtInWoonplaats.naam',
        'gme_id': 'ligtInGemeente.identificatie',
        'gme_naam': 'ligtInGemeente.naam',
        'num_id_nvn': 'heeftNevenadres.identificatie',
        'gebr_doel': 'gebruiksdoel.omschrijving',
        'status': 'status.omschrijving',
        'soort_obj': {
            'action': 'format',
            'formatter': format_soort_object,
            'value': 'invIsVerbondenMetLigplaatsWozWozdeelobjecten.soortobject.omschrijving',
        },
        'begindatum': 'beginGeldigheid',
        'einddatum': 'eindGeldigheid',
        'docdatum': 'documentdatum',
        'docnummer': 'documentnummer',
        'brt_id': 'ligtInBuurt.identificatie',
        'brt_code': 'ligtInBuurt.code',
        'brt_naam': 'ligtInBuurt.naam',
        'wijk_id': 'ligtInWijk.identificatie',
        'wijk_code': 'ligtInWijk.code',
        'wijk_naam': 'ligtInWijk.naam',
        'ggw_id': 'ligtInGgwgebied.identificatie',
        'ggw_code': 'ligtInGgwgebied.code',
        'ggw_naam': 'ligtInGgwgebied.naam',
        'ggp_id': 'ligtInGgpgebied.identificatie',
        'ggp_code': 'ligtInGgpgebied.code',
        'ggp_naam': 'ligtInGgpgebied.naam',
        'sdl_id': 'ligtInStadsdeel.identificatie',
        'sdl_code': 'ligtInStadsdeel.code',
        'sdl_naam': 'ligtInStadsdeel.naam',
    })

    history_format = BAGDefaultFormat({
        'identificatie': 'identificatie',
        'volgnummer': 'volgnummer',
        'registratiedatum': 'registratiedatum',
        'aanduidingInOnderzoek': {
            'condition': 'isempty',
            'reference': 'heeftOnderzoeken.[0].identificatie',
            'trueval': {
                'action': 'literal',
                'value': 'N',
            },
            'falseval': {
                'action': 'literal',
                'value': 'J'
            }
        },
        'geconstateerd': 'geconstateerd',
        'heeftIn:BAG.NAG.identificatieHoofdadres': 'heeftHoofdadres.identificatie',
        'heeftIn:BAG.NAG.volgnummerHoofdadres': 'heeftHoofdadres.volgnummer',
        'huisnummerHoofdadres': 'heeftHoofdadres.huisnummer',
        'huisletterHoofdadres': 'heeftHoofdadres.huisletter',
        'huisnummertoevoegingHoofdadres': 'heeftHoofdadres.huisnummertoevoeging',
        'postcodeHoofdadres': 'heeftHoofdadres.postcode',
        'ligtAan:BAG.ORE.identificatieHoofdadres': 'ligtAanOpenbareruimte.identificatie',
        'ligtAan:BAG.ORE.volgnummerHoofdadres': 'ligtAanOpenbareruimte.volgnummer',
        'ligtAan:BAG.ORE.naamHoofdadres': 'ligtAanOpenbareruimte.naam',
        'ligtIn:BAG.WPS.identificatieHoofdadres': 'ligtInWoonplaats.identificatie',
        'ligtIn:BAG.WPS.volgnummerHoofdadres': 'ligtInWoonplaats.volgnummer',
        'ligtIn:BAG.WPS.naamHoofdadres': 'ligtInWoonplaats.naam',
        'ligtIn:BRK.GME.identificatie': 'ligtInGemeente.identificatie',
        'ligtIn:BRK.GME.volgnummer': 'ligtInGemeente.volgnummer',
        'ligtIn:BRK.GME.naam': 'ligtInGemeente.naam',
        'heeftIn:BAG.NAG.identificatieNevenadres': 'heeftNevenadres.identificatie',
        'heeftIn:BAG.NAG.volgnummerNevenadres': 'heeftNevenadres.volgnummer',
        'gebruiksdoel': 'gebruiksdoel.omschrijving',
        'status': 'status.omschrijving',
        'is:WOZ.WOB.soortObject': {
            'action': 'format',
            'formatter': format_soort_object,
            'value': 'invIsVerbondenMetLigplaatsWozWozdeelobjecten.soortobject.omschrijving',
        },
        'beginGeldigheid': 'beginGeldigheid',
        'eindGeldigheid': 'eindGeldigheid',
        'documentdatum': 'documentdatum',
        'documentnummer': 'documentnummer',
        'ligtIn:GBD.BRT.identificatie': 'ligtInBuurt.identificatie',
        'ligtIn:GBD.BRT.volgnummer': 'ligtInBuurt.volgnummer',
        'ligtIn:GBD.BRT.code': 'ligtInBuurt.code',
        'ligtIn:GBD.BRT.naam': 'ligtInBuurt.naam',
        'ligtIn:GBD.WIJK.identificatie': 'ligtInWijk.identificatie',
        'ligtIn:GBD.WIJK.volgnummer': 'ligtInWijk.volgnummer',
        'ligtIn:GBD.WIJK.code': 'ligtInWijk.code',
        'ligtIn:GBD.WIJK.naam': 'ligtInWijk.naam',
        'ligtIn:GBD.GGW.identificatie': 'ligtInGgwgebied.identificatie',
        'ligtIn:GBD.GGW.volgnummer': 'ligtInGgwgebied.volgnummer',
        'ligtIn:GBD.GGW.code': 'ligtInGgwgebied.code',
        'ligtIn:GBD.GGW.naam': 'ligtInGgwgebied.naam',
        'ligtIn:GBD.GGP.identificatie': 'ligtInGgpgebied.identificatie',
        'ligtIn:GBD.GGP.volgnummer': 'ligtInGgpgebied.volgnummer',
        'ligtIn:GBD.GGP.code': 'ligtInGgpgebied.code',
        'ligtIn:GBD.GGP.naam': 'ligtInGgpgebied.naam',
        'ligtIn:GBD.SDL.identificatie': 'ligtInStadsdeel.identificatie',
        'ligtIn:GBD.SDL.volgnummer': 'ligtInStadsdeel.volgnummer',
        'ligtIn:GBD.SDL.code': 'ligtInStadsdeel.code',
        'ligtIn:GBD.SDL.naam': 'ligtInStadsdeel.naam',
        'geometrie': {
            'action': 'format',
            'formatter': format_geometry,
            'value': 'geometrie'
        },
    })

    products = {
        'csv_actueel': {
            'api_type': 'graphql',
            'exporter': csv_exporter,
            'filename': 'CSV_Actueel/BAG_ligplaats_Actueel.csv',
            'mime_type': 'plain/text',
            'format': format.get_format(),
            'query': query_actueel
        },
        'esri_actueel': {
            'api_type': 'graphql',
            'exporter': esri_exporter,
            'filename': 'SHP/BAG_ligplaats.shp',
            'mime_type': 'application/octet-stream',
            'format': esri_format.get_format(),
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
                {
                    'filename': 'SHP/BAG_ligplaats.cpg',
                    'mime_type': 'application/octet-stream'
                },
            ],
            'query': query_actueel
        },
        'csv_history': {
            'api_type': 'graphql',
            'exporter': csv_exporter,
            'filename': 'CSV_ActueelEnHistorie/BAG_ligplaats_ActueelEnHistorie.csv',
            'mime_type': 'plain/text',
            'format': history_format.get_format(),
            'query': query_history
        },
    }


class PandenExportConfig:

    format = BAGDefaultFormat({
        'identificatie': 'identificatie',
        'aanduidingInOnderzoek': 'aanduidingInOnderzoek',
        'geconstateerd': 'geconstateerd',
        'status': 'status.omschrijving',
        'oorspronkelijkBouwjaar': 'oorspronkelijkBouwjaar',
        'beginGeldigheid': 'beginGeldigheid',
        'eindGeldigheid': 'eindGeldigheid',
        'documentdatum': 'documentdatum',
        'documentnummer': 'documentnummer',
        'naam': 'naam',
        'ligging': 'ligging.omschrijving',
        'typeWoonobject': 'typeWoonobject',
        'aantalBouwlagen': 'aantalBouwlagen',
        'hoogsteBouwlaag': 'hoogsteBouwlaag',
        'laagsteBouwlaag': 'laagsteBouwlaag',
        'ligtIn:GBD.BBK.identificatie': 'ligtInBouwblok.identificatie',
        'ligtIn:GBD.BBK.code': 'ligtInBouwblok.code',
        'ligtIn:GBD.BRT.identificatie': 'ligtInBuurt.identificatie',
        'ligtIn:GBD.BRT.code': 'ligtInBuurt.code',
        'ligtIn:GBD.BRT.naam': 'ligtInBuurt.naam',
        'ligtIn:GBD.WIJK.identificatie': 'ligtInWijk.identificatie',
        'ligtIn:GBD.WIJK.code': 'ligtInWijk.code',
        'ligtIn:GBD.WIJK.naam': 'ligtInWijk.naam',
        'ligtIn:GBD.GGW.identificatie': 'ligtInGgwgebied.identificatie',
        'ligtIn:GBD.GGW.code': 'ligtInGgwgebied.code',
        'ligtIn:GBD.GGW.naam': 'ligtInGgwgebied.naam',
        'ligtIn:GBD.GGP.identificatie': 'ligtInGgpgebied.identificatie',
        'ligtIn:GBD.GGP.code': 'ligtInGgpgebied.code',
        'ligtIn:GBD.GGP.naam': 'ligtInGgpgebied.naam',
        'ligtIn:GBD.SDL.identificatie': 'ligtInStadsdeel.identificatie',
        'ligtIn:GBD.SDL.code': 'ligtInStadsdeel.code',
        'ligtIn:GBD.SDL.naam': 'ligtInStadsdeel.naam',
        'geometrie': {
            'action': 'format',
            'formatter': format_geometry,
            'value': 'geometrie'
        },
    })

    esri_format = BAGDefaultFormat({
        'id': 'identificatie',
        'onderzoek': 'aanduidingInOnderzoek',
        'geconst': 'geconstateerd',
        'status': 'status.omschrijving',
        'bouwjaar': 'oorspronkelijkBouwjaar',
        'begindatum': 'beginGeldigheid',
        'einddatum': 'eindGeldigheid',
        'docdatum': 'documentdatum',
        'docnummer': 'documentnummer',
        'naam_pand': 'naam',
        'ligging': 'ligging.omschrijving',
        'type_oms': 'typeWoonobject',
        'aant_bouwl': 'aantalBouwlagen',
        'hoog_bouwl': 'hoogsteBouwlaag',
        'laag_bouwl': 'laagsteBouwlaag',
        'bbk_id': 'ligtInBouwblok.identificatie',
        'bbk_code': 'ligtInBouwblok.code',
        'brt_id': 'ligtInBuurt.identificatie',
        'brt_code': 'ligtInBuurt.code',
        'brt_naam': 'ligtInBuurt.naam',
        'wijk_id': 'ligtInWijk.identificatie',
        'wijk_code': 'ligtInWijk.code',
        'wijk_naam': 'ligtInWijk.naam',
        'ggw_id': 'ligtInGgwgebied.identificatie',
        'ggw_code': 'ligtInGgwgebied.code',
        'ggw_naam': 'ligtInGgwgebied.naam',
        'ggp_id': 'ligtInGgpgebied.identificatie',
        'ggp_code': 'ligtInGgpgebied.code',
        'ggp_naam': 'ligtInGgpgebied.naam',
        'sdl_id': 'ligtInStadsdeel.identificatie',
        'sdl_code': 'ligtInStadsdeel.code',
        'sdl_naam': 'ligtInStadsdeel.naam',
    })

    history_format = BAGDefaultFormat({
        'identificatie': 'identificatie',
        'volgnummer': 'volgnummer',
        'registratiedatum': 'registratiedatum',
        'aanduidingInOnderzoek': 'aanduidingInOnderzoek',
        'geconstateerd': 'geconstateerd',
        'status': 'status.omschrijving',
        'oorspronkelijkBouwjaar': 'oorspronkelijkBouwjaar',
        'beginGeldigheid': 'beginGeldigheid',
        'eindGeldigheid': 'eindGeldigheid',
        'documentdatum': 'documentdatum',
        'documentnummer': 'documentnummer',
        'naam': 'naam',
        'ligging': 'ligging.omschrijving',
        'typeWoonobject': 'typeWoonobject',
        'aantalBouwlagen': 'aantalBouwlagen',
        'hoogsteBouwlaag': 'hoogsteBouwlaag',
        'laagsteBouwlaag': 'laagsteBouwlaag',
        'ligtIn:GBD.BBK.identificatie': 'ligtInBouwblok.identificatie',
        'ligtIn:GBD.BBK.volgnummer': 'ligtInBouwblok.volgnummer',
        'ligtIn:GBD.BBK.code': 'ligtInBouwblok.code',
        'ligtIn:GBD.BRT.identificatie': 'ligtInBuurt.identificatie',
        'ligtIn:GBD.BRT.volgnummer': 'ligtInBuurt.volgnummer',
        'ligtIn:GBD.BRT.code': 'ligtInBuurt.code',
        'ligtIn:GBD.BRT.naam': 'ligtInBuurt.naam',
        'ligtIn:GBD.WIJK.identificatie': 'ligtInWijk.identificatie',
        'ligtIn:GBD.WIJK.volgnummer': 'ligtInWijk.volgnummer',
        'ligtIn:GBD.WIJK.code': 'ligtInWijk.code',
        'ligtIn:GBD.WIJK.naam': 'ligtInWijk.naam',
        'ligtIn:GBD.GGW.identificatie': 'ligtInGgwgebied.identificatie',
        'ligtIn:GBD.GGW.volgnummer': 'ligtInGgwgebied.volgnummer',
        'ligtIn:GBD.GGW.code': 'ligtInGgwgebied.code',
        'ligtIn:GBD.GGW.naam': 'ligtInGgwgebied.naam',
        'ligtIn:GBD.GGP.identificatie': 'ligtInGgpgebied.identificatie',
        'ligtIn:GBD.GGP.volgnummer': 'ligtInGgpgebied.volgnummer',
        'ligtIn:GBD.GGP.code': 'ligtInGgpgebied.code',
        'ligtIn:GBD.GGP.naam': 'ligtInGgpgebied.naam',
        'ligtIn:GBD.SDL.identificatie': 'ligtInStadsdeel.identificatie',
        'ligtIn:GBD.SDL.volgnummer': 'ligtInStadsdeel.volgnummer',
        'ligtIn:GBD.SDL.code': 'ligtInStadsdeel.code',
        'ligtIn:GBD.SDL.naam': 'ligtInStadsdeel.naam',
        'geometrie': {
            'action': 'format',
            'formatter': format_geometry,
            'value': 'geometrie'
        },
    })

    products = {
        'csv_actueel': {
            'endpoint': '/gob/public/bag/panden/?view=enhanced&ndjson=true',
            'exporter': csv_exporter,
            'filename': 'CSV_Actueel/BAG_pand_Actueel.csv',
            'mime_type': 'plain/text',
            'format': format.get_format(),
        },
        'esri_actueel': {
            'endpoint': '/gob/public/bag/panden/?view=enhanced&ndjson=true',
            'exporter': esri_exporter,
            'filename': 'SHP/BAG_pand.shp',
            'mime_type': 'application/octet-stream',
            'format': esri_format.get_format(),
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
                {
                    'filename': 'SHP/BAG_pand.cpg',
                    'mime_type': 'application/octet-stream'
                },
            ],
        },
        'csv_history': {
            'endpoint': '/gob/public/bag/panden/?view=enhanced_history&ndjson=true',
            'exporter': csv_exporter,
            'filename': 'CSV_ActueelEnHistorie/BAG_pand_ActueelEnHistorie.csv',
            'mime_type': 'plain/text',
            'format': history_format.get_format(),
        },

    }


class BrondocumentenExportConfig:

    products = {
        'csv_actueel': {
            'endpoint': '/gob/public/bag/brondocumenten/?view=enhanced&ndjson=true',
            'exporter': csv_exporter,
            'filename': 'CSV_Actueel/BAG_brondocument_Actueel.csv',
            'mime_type': 'plain/text',
            'format': {
                'dossier': 'dossier',
                'documentnummer': 'documentnummer',
                'documentdatum': 'registratiedatum',
                'bronleverancier': 'bronleverancier',
                'typeDossier': 'typeDossier',
                'typeBrondocument': 'typeBrondocument',
            }
        },
        'csv_history': {
            'endpoint': '/gob/public/bag/brondocumenten/?view=enhanced_history&ndjson=true',
            'exporter': csv_exporter,
            'filename': 'CSV_ActueelEnHistorie/BAG_brondocument_ActueelEnHistorie.csv',
            'mime_type': 'plain/text',
            'format': {
                'dossier': 'dossier',
                'documentnummer': 'documentnummer',
                'documentdatum': 'registratiedatum',
                'bronleverancier': 'bronleverancier',
                'typeDossier': 'typeDossier',
                'typeBrondocument': 'typeBrondocument',
            }
        },
    }


class OnderzoekenExportConfig:

    actueel_query = '''
{
    bagOnderzoeken(inOnderzoek:"J") {
        edges {
          node {
            objectIdentificatie
            objecttype
            kenmerk
            inOnderzoek
            documentnummer
            documentdatum
            beginGeldigheid
            eindGeldigheid
            tijdstipRegistratie
            eindRegistratie
          }
        }
    }
}
'''

    history_query = '''
{
    bagOnderzoeken(active: false) {
        edges {
          node {
            objectIdentificatie
            volgnummer
            objecttype
            kenmerk
            inOnderzoek
            documentnummer
            documentdatum
            beginGeldigheid
            eindGeldigheid
            tijdstipRegistratie
            eindRegistratie
          }
        }
    }
}
'''

    format = {
        'gerelateerdAan:BAG.identificatie': 'objectIdentificatie',
        'objecttype': 'objecttype',
        'kenmerk': 'kenmerk',
        'inOnderzoek': 'inOnderzoek',
        'documentnummer': 'documentnummer',
        'documentdatum': 'documentdatum',
        'beginGeldigheid': {
            'action': 'format',
            'formatter': format_date,
            'value': 'beginGeldigheid',
        },
        'eindGeldigheid': {
            'action': 'format',
            'formatter': format_date,
            'value': 'eindGeldigheid',
        },
        'tijdstipRegistratie': {
            'action': 'format',
            'formatter': format_date,
            'value': 'tijdstipRegistratie',
        },
        'eindRegistratie': {
            'action': 'format',
            'formatter': format_date,
            'value': 'eindRegistratie',
        },
    }

    history_format = {
        'gerelateerdAan:BAG.identificatie': 'objectIdentificatie',
        'volgnummer': 'volgnummer',
        'objecttype': 'objecttype',
        'kenmerk': 'kenmerk',
        'inOnderzoek': 'inOnderzoek',
        'documentnummer': 'documentnummer',
        'documentdatum': 'documentdatum',
        'beginGeldigheid': {
            'action': 'format',
            'formatter': format_date,
            'value': 'beginGeldigheid',
        },
        'eindGeldigheid': {
            'action': 'format',
            'formatter': format_date,
            'value': 'eindGeldigheid',
        },
        'tijdstipRegistratie': {
            'action': 'format',
            'formatter': format_date,
            'value': 'tijdstipRegistratie',
        },
        'eindRegistratie': {
            'action': 'format',
            'formatter': format_date,
            'value': 'eindRegistratie',
        },
    }

    products = {
        'csv_actueel': {
            'exporter': csv_exporter,
            'api_type': 'graphql_streaming',
            'filename': 'CSV_Actueel/BAG_onderzoek_Actueel.csv',
            'mime_type': 'plain/text',
            'query': actueel_query,
            'format': format
        },
        'csv_history': {
            'exporter': csv_exporter,
            'api_type': 'graphql_streaming',
            'filename': 'CSV_ActueelEnHistorie/BAG_onderzoek_ActueelEnHistorie.csv',
            'mime_type': 'plain/text',
            'query': history_query,
            'format': history_format
        }
    }
