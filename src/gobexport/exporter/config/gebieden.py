from gobexport.exporter.csv import csv_exporter
from gobexport.exporter.esri import esri_exporter


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
                'naam': 'naam',
                'code': 'code',
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
                'naam': 'naam',
                'code': 'code',
                'datumBeginGeldigheid': 'begindatum',
                'datumEindeGeldigheid': 'einddatum',
                'documentdatum': 'docdatum',
                'documentnummer': 'docnummer',
                'ggwIdentificatie': 'ggw_id',
                'ggwNaam': 'ggw_naam',
                'ggwCode': 'ggw_code',
                'stadsdeelidentificatie': 'sdl_id',
                'stadsdeelnaam': 'sdl_naam',
                'stadsdeelcode': 'sdl_code',
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
                'naam': 'naam',
                'code': 'code',
                'datumBeginGeldigheid': 'begindatum',
                'datumEindeGeldigheid': 'einddatum',
                'documentdatum': 'docdatum',
                'documentnummer': 'docnummer',
                'wijkidentificatie': 'wijk_id',
                'wijknaam': 'wijk_naam',
                'wijkcode': 'wijk_code',
                'ggwIdentificatie': 'ggw_id',
                'ggwNaam': 'ggw_naam',
                'ggwCode': 'ggw_code',
                'stadsdeelidentificatie': 'sdl_id',
                'stadsdeelnaam': 'sdl_naam',
                'stadsdeelcode': 'sdl_code',
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
                'buurtnaam': 'brt_naam',
                'buurtcode': 'brt_code',
                'wijkidentificatie': 'wijk_id',
                'wijknaam': 'wijk_naam',
                'wijkcode': 'wijk_code',
                'ggwIdentificatie': 'ggw_id',
                'ggwNaam': 'ggw_naam',
                'ggwCode': 'ggw_code',
                'ggpIdentificatie': 'ggp_id',
                'ggpNaam': 'ggp_naam',
                'ggpCode': 'ggp_code',
                'stadsdeelidentificatie': 'sdl_id',
                'stadsdeelnaam': 'sdl_naam',
                'stadsdeelcode': 'sdl_code',
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
        }
    }
