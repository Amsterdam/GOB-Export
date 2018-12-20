from gobexport.exporter.csv import csv_exporter


class StadsdelenExportConfig:

    products = {
        'csv_actueel': {
            'exporter': csv_exporter,
            'endpoint': '/gob/gebieden/stadsdelen/?view=enhanced',
            'filename': 'Actueel_CSV/GBD_stadsdeel.csv'
        },
        'csv_actueel_en_historie': {
            'exporter': csv_exporter,
            'endpoint': '/gob/toestanden/?collections=gebieden:stadsdelen',
            'filename': 'ActueelEnHistorie_CSV/GBD_stadsdeel.csv'
        }
    }


class WijkenExportConfig:

    products = {
        'csv_actueel': {
            'exporter': csv_exporter,
            'endpoint': '/gob/gebieden/wijken/?view=enhanced',
            'filename': 'Actueel_CSV/GBD_wijk.csv'
        },
        'csv_actueel_en_historie': {
            'exporter': csv_exporter,
            'endpoint': '/gob/toestanden/?collections=gebieden:wijken,gebieden:stadsdelen',
            'filename': 'ActueelEnHistorie_CSV/GBD_wijk.csv'
        }
    }


class BuurtenExportConfig:

    products = {
        'csv_actueel': {
            'exporter': csv_exporter,
            'endpoint': '/gob/gebieden/buurten/?view=enhanced',
            'filename': 'Actueel_CSV/GBD_buurt.csv'
        },
        'csv_actueel_en_historie': {
            'exporter': csv_exporter,
            'endpoint': '/gob/toestanden/?collections=gebieden:buurten,gebieden:wijken,gebieden:stadsdelen',
            'filename': 'ActueelEnHistorie_CSV/GBD_buurt.csv'
        }
    }


class BouwblokkenExportConfig:

    products = {
        'csv_actueel': {
            'exporter': csv_exporter,
            'endpoint': '/gob/gebieden/bouwblokken/?view=enhanced',
            'filename': 'Actueel_CSV/GBD_bouwblok.csv'
        },
        'csv_actueel_en_historie': {
            'exporter': csv_exporter,
            'endpoint': '/gob/toestanden/?collections=gebieden:bouwblokken,'
                        'gebieden:buurten,gebieden:wijken,gebieden:stadsdelen',
            'filename': 'ActueelEnHistorie_CSV/GBD_bouwblok.csv'
        }
    }
