from gobexport.exporter.csv import csv_exporter
from gobexport.exporter.esri import esri_exporter


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
    format: Additional configuration or mapping
    extra_files: Resulting extra files of an export which need to be uploaded as
                 well. For example the esri product creates .dbf, .shx and .prj
                 files.


"""


class StadsdelenExportConfig:

    products = {
        'csv_actueel': {
            'exporter': csv_exporter,
            'endpoint': '/gob/gebieden/stadsdelen/?view=enhanced',
            'filename': 'Actueel_CSV/GBD_stadsdeel.csv',
            'mime_type': 'plain/text',
        },
        'esri_actueel': {
            'exporter': esri_exporter,
            'endpoint': '/gob/gebieden/stadsdelen/?view=enhanced',
            'filename': 'Actueel_SHP/GBD_stadsdeel.shp',
            'mime_type': 'application/octet-stream',
            'format': {
                'identificatie': 'id',
                'code': 'code',
                'naam': 'naam',
                'datumBeginGeldigheid': 'begindatum',
                'datumEindeGeldigheid': 'einddatum',
                'documentdatum': 'docdatum',
                'documentnummer': 'docnummer',
                'brkGemeenteidentificatie': 'gme_id',
                'brkGemeentenaam': 'gme_naam',
            },
            'extra_files': [
                {
                    'filename': 'Actueel_SHP/GBD_stadsdeel.dbf',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'Actueel_SHP/GBD_stadsdeel.shx',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'Actueel_SHP/GBD_stadsdeel.prj',
                    'mime_type': 'application/octet-stream'
                },
            ]
        },
        'csv_actueel_en_historie': {
            'exporter': csv_exporter,
            'endpoint': '/gob/toestanden/?collections=gebieden:stadsdelen',
            'filename': 'ActueelEnHistorie_CSV/GBD_stadsdeel.csv',
            'mime_type': 'plain/text',
            'format': 'identificatie,volgnummer,registratiedatum,code,naam,'
                      'datumBeginGeldigheid,datumEindeGeldigheid,documentdatum,'
                      'documentnummer,datumBeginTijdvak,datumEindeTijdvak,'
                      'geometrie'
        }
    }


class WijkenExportConfig:

    products = {
        'csv_actueel': {
            'exporter': csv_exporter,
            'endpoint': '/gob/gebieden/wijken/?view=enhanced',
            'filename': 'Actueel_CSV/GBD_wijk.csv',
            'mime_type': 'plain/text',
        },
        'esri_actueel': {
            'exporter': esri_exporter,
            'endpoint': '/gob/gebieden/wijken/?view=enhanced',
            'filename': 'Actueel_SHP/GBD_wijk.shp',
            'mime_type': 'application/octet-stream',
            'format': {
                'identificatie': 'id',
                'code': 'code',
                'naam': 'naam',
                'datumBeginGeldigheid': 'begindatum',
                'datumEindeGeldigheid': 'einddatum',
                'documentdatum': 'docdatum',
                'documentnummer': 'docnummer',
                'cbsCode': 'CBS_code',
                'ggwIdentificatie': 'ggw_id',
                'ggwCode': 'ggw_code',
                'ggwNaam': 'ggw_naam',
                'stadsdeelidentificatie': 'sdl_id',
                'stadsdeelcode': 'sdl_code',
                'stadsdeelnaam': 'sdl_naam',
                'brkGemeenteidentificatie': 'gme_id',
                'brkGemeentenaam': 'gme_naam',
            },
            'extra_files': [
                {
                    'filename': 'Actueel_SHP/GBD_wijk.dbf',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'Actueel_SHP/GBD_wijk.shx',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'Actueel_SHP/GBD_wijk.prj',
                    'mime_type': 'application/octet-stream'
                },
            ]
        },
        'csv_actueel_en_historie': {
            'exporter': csv_exporter,
            'endpoint': '/gob/toestanden/?collections=gebieden:wijken,gebieden:stadsdelen',
            'filename': 'ActueelEnHistorie_CSV/GBD_wijk.csv',
            'mime_type': 'plain/text',
            'format': 'identificatie,volgnummer,registratiedatum,code,naam,'
                      'datumBeginGeldigheid,datumEindeGeldigheid,documentdatum,'
                      'documentnummer,cbsCode,datumBeginTijdvak,datumEindeTijdvak,'
                      'gebieden:stadsdelenVolgnummer,gebieden:stadsdelenIdentificatie,'
                      'gebieden:stadsdelenCode,gebieden:stadsdelenNaam,geometrie'
        }
    }


class BuurtenExportConfig:

    products = {
        'csv_actueel': {
            'exporter': csv_exporter,
            'endpoint': '/gob/gebieden/buurten/?view=enhanced',
            'filename': 'Actueel_CSV/GBD_buurt.csv',
            'mime_type': 'plain/text',
        },
        'esri_actueel': {
            'exporter': esri_exporter,
            'endpoint': '/gob/gebieden/buurten/?view=enhanced',
            'filename': 'Actueel_SHP/GBD_buurt.shp',
            'mime_type': 'application/octet-stream',
            'format': {
                'identificatie': 'id',
                'code': 'code',
                'naam': 'naam',
                'datumBeginGeldigheid': 'begindatum',
                'datumEindeGeldigheid': 'einddatum',
                'documentdatum': 'docdatum',
                'documentnummer': 'docnummer',
                'cbsCode': 'CBS_code',
                'wijkidentificatie': 'wijk_id',
                'wijkcode': 'wijk_code',
                'wijknaam': 'wijk_naam',
                'ggwIdentificatie': 'ggw_id',
                'ggwCode': 'ggw_code',
                'ggwNaam': 'ggw_naam',
                'stadsdeelidentificatie': 'sdl_id',
                'stadsdeelcode': 'sdl_code',
                'stadsdeelnaam': 'sdl_naam',
                'brkGemeenteidentificatie': 'gme_id',
                'brkGemeentenaam': 'gme_naam',
            },
            'extra_files': [
                {
                    'filename': 'Actueel_SHP/GBD_buurt.dbf',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'Actueel_SHP/GBD_buurt.shx',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'Actueel_SHP/GBD_buurt.prj',
                    'mime_type': 'application/octet-stream'
                },
            ]
        },
        'csv_actueel_en_historie': {
            'exporter': csv_exporter,
            'endpoint': '/gob/toestanden/?collections=gebieden:buurten,gebieden:wijken,gebieden:stadsdelen',
            'filename': 'ActueelEnHistorie_CSV/GBD_buurt.csv',
            'mime_type': 'plain/text',
            'format': 'identificatie,volgnummer,registratiedatum,code,naam,'
                      'datumBeginGeldigheid,datumEindeGeldigheid,documentdatum,'
                      'documentnummer,cbsCode,datumBeginTijdvak,datumEindeTijdvak,'
                      'gebieden:wijkenVolgnummer,gebieden:wijkenIdentificatie,'
                      'gebieden:wijkenCode,gebieden:wijkenNaam,'
                      'gebieden:stadsdelenVolgnummer,gebieden:stadsdelenIdentificatie,'
                      'gebieden:stadsdelenCode,gebieden:stadsdelenNaam,geometrie'
        }
    }


class BouwblokkenExportConfig:

    products = {
        'csv_actueel': {
            'exporter': csv_exporter,
            'endpoint': '/gob/gebieden/bouwblokken/?view=enhanced',
            'filename': 'Actueel_CSV/GBD_bouwblok.csv',
            'mime_type': 'plain/text',
        },
        'esri_actueel': {
            'exporter': esri_exporter,
            'endpoint': '/gob/gebieden/bouwblokken/?view=enhanced',
            'filename': 'Actueel_SHP/GBD_bouwblok.shp',
            'mime_type': 'application/octet-stream',
            'format': {
                'identificatie': 'id',
                'code': 'code',
                'datumBeginGeldigheid': 'begindatum',
                'datumEindeGeldigheid': 'einddatum',
                'buurtidentificatie': 'brt_id',
                'buurtcode': 'brt_code',
                'buurtnaam': 'brt_naam',
                'wijkidentificatie': 'wijk_id',
                'wijkcode': 'wijk_code',
                'wijknaam': 'wijk_naam',
                'ggwIdentificatie': 'ggw_id',
                'ggwCode': 'ggw_code',
                'ggwNaam': 'ggw_naam',
                'ggpIdentificatie': 'ggp_id',
                'ggpCode': 'ggp_code',
                'ggpNaam': 'ggp_naam',
                'stadsdeelidentificatie': 'sdl_id',
                'stadsdeelcode': 'sdl_code',
                'stadsdeelnaam': 'sdl_naam',
                'brkGemeenteidentificatie': 'gme_id',
                'brkGemeentenaam': 'gme_naam',
            },
            'extra_files': [
                {
                    'filename': 'Actueel_SHP/GBD_bouwblok.dbf',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'Actueel_SHP/GBD_bouwblok.shx',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'Actueel_SHP/GBD_bouwblok.prj',
                    'mime_type': 'application/octet-stream'
                },
            ]
        },
        'csv_actueel_en_historie': {
            'exporter': csv_exporter,
            'endpoint': '/gob/toestanden/?collections=gebieden:bouwblokken,'
                        'gebieden:buurten,gebieden:wijken,gebieden:stadsdelen',
            'filename': 'ActueelEnHistorie_CSV/GBD_bouwblok.csv',
            'mime_type': 'plain/text',
            'format': 'identificatie,volgnummer,registratiedatum,code,naam,'
                      'datumBeginGeldigheid,datumEindeGeldigheid,documentdatum,'
                      'documentnummer,cbsCode,datumBeginTijdvak,datumEindeTijdvak,'
                      'gebieden:buurtenVolgnummer,gebieden:buurtenIdentificatie,'
                      'gebieden:buurtenCode,gebieden:buurtenNaam,'
                      'gebieden:wijkenVolgnummer,gebieden:wijkenIdentificatie,'
                      'gebieden:wijkenCode,gebieden:wijkenNaam,'
                      'gebieden:stadsdelenVolgnummer,gebieden:stadsdelenIdentificatie,'
                      'gebieden:stadsdelenCode,gebieden:stadsdelenNaam,geometrie'
        }
    }
