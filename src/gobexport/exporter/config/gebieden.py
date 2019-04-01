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
    format: Additional configuration or mapping (see the different exporters for examples of format)
    extra_files: Resulting extra files of an export which need to be uploaded as
                 well. For example the esri product creates .dbf, .shx and .prj
                 files.
"""


class StadsdelenExportConfig:

    products = {
        'csv_actueel': {
            'exporter': csv_exporter,
            'endpoint': '/gob/gebieden/stadsdelen/?view=enhanced',
            'filename': 'CSV_Actueel/GBD_stadsdeel.csv',
            'mime_type': 'plain/text',
            'format': {
                'columns': [
                    'identificatie',
                    'code',
                    'naam',
                    'beginGeldigheid',
                    'eindGeldigheid',
                    'documentdatum',
                    'documentnummer',
                    'geometrie',
                ],
                'references': {
                    'ligtInGemeente': {
                        'ref': 'BRK.GME',
                        'ref_name': 'ligtIn',
                        'columns': ['identificatie', 'naam'],
                    }
                }
            }
        },
        'esri_actueel': {
            'exporter': esri_exporter,
            'endpoint': '/gob/gebieden/stadsdelen/?view=enhanced',
            'filename': 'SHP/GBD_stadsdeel.shp',
            'mime_type': 'application/octet-stream',
            'format': {
                'mapping': {
                    'id': 'identificatie',
                    'code': 'code',
                    'naam': 'naam',
                    'begindatum': 'beginGeldigheid',
                    'einddatum': 'eindGeldigheid',
                    'docdatum': 'documentdatum',
                    'docnummer': 'documentnummer',
                    'gme_id': 'ligtInGemeente.identificatie',
                    'gme_naam': 'ligtInGemeente.naam',
                }
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
            ]
        },
        'csv_actueel_en_historie': {
            'exporter': csv_exporter,
            'endpoint': '/gob/toestanden/?collections=gebieden:stadsdelen',
            'filename': 'CSV_ActueelEnHistorie/GBD_stadsdeel.csv',
            'mime_type': 'plain/text',
            'format': {
                'columns': [
                    'identificatie',
                    'volgnummer',
                    'registratiedatum',
                    'code',
                    'naam',
                    'beginGeldigheid',
                    'eindGeldigheid',
                    'documentdatum',
                    'documentnummer',
                    'beginTijdvak',
                    'eindTijdvak',
                    'geometrie',
                ],
                'mapping': {
                    'ligtIn:BRK.GME.identificatie': 'brk:gemeentenIdentificatie',
                    'ligtIn:BRK.GME.volgnummer': 'brk:gemeentenVolgnummer',
                    'ligtIn:BRK.GME.naam': 'brk:gemeentenNaam',
                }
            }
        }
    }


class GGPGebiedenExportConfig:

    products = {
        'csv_actueel': {
            'exporter': csv_exporter,
            'endpoint': '/gob/gebieden/ggpgebieden/?view=enhanced',
            'filename': 'CSV_Actueel/GBD_ggw_praktijkgebieden.csv',
            'mime_type': 'plain/text',
            'format': {
                'columns': [
                    'identificatie',
                    'code',
                    'naam',
                    'beginGeldigheid',
                    'eindGeldigheid',
                    'documentdatum',
                    'documentnummer',
                    'geometrie',
                ],
                'references': {
                    'ligtInStadsdeel': {
                        'ref': 'GBD.SDL',
                        'ref_name': 'ligtIn',
                        'columns': ['identificatie', 'code', 'naam'],
                    },
                    'ligtInGemeente': {
                        'ref': 'BRK.GME',
                        'ref_name': 'ligtIn',
                        'columns': ['identificatie', 'naam'],
                    }
                }
            }
        },
        'esri_actueel': {
            'exporter': esri_exporter,
            'endpoint': '/gob/gebieden/ggpgebieden/?view=enhanced',
            'filename': 'SHP/GBD_ggw_praktijkgebieden.shp',
            'mime_type': 'application/octet-stream',
            'format': {
                'mapping': {
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
                }
            },
            'extra_files': [
                {
                    'filename': 'SHP/GBD_ggw_praktijkgebieden.dbf',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'SHP/GBD_ggw_praktijkgebieden.shx',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'SHP/GBD_ggw_praktijkgebieden.prj',
                    'mime_type': 'application/octet-stream'
                },
            ]
        },
        'csv_actueel_en_historie': {
            'exporter': csv_exporter,
            'endpoint': '/gob/toestanden/?collections=gebieden:ggpgebieden,gebieden:stadsdelen',
            'filename': 'CSV_ActueelEnHistorie/GBD_ggw_praktijkgebieden.csv',
            'mime_type': 'plain/text',
            'format': {
                'columns': [
                    'identificatie',
                    'volgnummer',
                    'registratiedatum',
                    'code',
                    'naam',
                    'beginGeldigheid',
                    'eindGeldigheid',
                    'documentdatum',
                    'documentnummer',
                    'beginTijdvak',
                    'eindTijdvak',
                    'geometrie',
                ],
                'mapping': {
                    'ligtIn:GBD.SDL.identificatie': 'gebieden:stadsdelenIdentificatie',
                    'ligtIn:GDB.SDL.volgnummer': 'gebieden:stadsdelenVolgnummer',
                    'ligtIn:GDB.SDL.code': 'gebieden:stadsdelenCode',
                    'ligtIn:GDB.SDL.naam': 'gebieden:stadsdelenNaam',
                    'ligtIn:BRK.GME.identificatie': 'brk:gemeentenIdentificatie',
                    'ligtIn:BRK.GME.volgnummer': 'brk:gemeentenVolgnummer',
                    'ligtIn:BRK.GME.naam': 'brk:gemeentenNaam',
                }
            }
        }
    }


class GGWGebiedenExportConfig:

    products = {
        'csv_actueel': {
            'exporter': csv_exporter,
            'endpoint': '/gob/gebieden/ggwgebieden/?view=enhanced',
            'filename': 'CSV_Actueel/GBD_ggw_gebieden.csv',
            'mime_type': 'plain/text',
            'format': {
                'columns': [
                    'identificatie',
                    'code',
                    'naam',
                    'beginGeldigheid',
                    'eindGeldigheid',
                    'documentdatum',
                    'documentnummer',
                    'geometrie',
                ],
                'references': {
                    'ligtInStadsdeel': {
                        'ref': 'GBD.SDL',
                        'ref_name': 'ligtIn',
                        'columns': ['identificatie', 'code', 'naam'],
                    },
                    'ligtInGemeente': {
                        'ref': 'BRK.GME',
                        'ref_name': 'ligtIn',
                        'columns': ['identificatie', 'naam'],
                    }
                }
            }
        },
        'esri_actueel': {
            'exporter': esri_exporter,
            'endpoint': '/gob/gebieden/ggwgebieden/?view=enhanced',
            'filename': 'SHP/GBD_ggw_gebieden.shp',
            'mime_type': 'application/octet-stream',
            'format': {
                'mapping': {
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
                }
            },
            'extra_files': [
                {
                    'filename': 'SHP/GBD_ggw_gebieden.dbf',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'SHP/GBD_ggw_gebieden.shx',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'SHP/GBD_ggw_gebieden.prj',
                    'mime_type': 'application/octet-stream'
                },
            ]
        },
        'csv_actueel_en_historie': {
            'exporter': csv_exporter,
            'endpoint': '/gob/toestanden/?collections=gebieden:ggwgebieden,gebieden:stadsdelen',
            'filename': 'CSV_ActueelEnHistorie/GBD_ggw_gebieden.csv',
            'mime_type': 'plain/text',
            'format': {
                'columns': [
                    'identificatie',
                    'volgnummer',
                    'registratiedatum',
                    'code',
                    'naam',
                    'beginGeldigheid',
                    'eindGeldigheid',
                    'documentdatum',
                    'documentnummer',
                    'beginTijdvak',
                    'eindTijdvak',
                    'geometrie',
                ],
                'mapping': {
                    'ligtIn:GBD.SDL.identificatie': 'gebieden:stadsdelenIdentificatie',
                    'ligtIn:GDB.SDL.volgnummer': 'gebieden:stadsdelenVolgnummer',
                    'ligtIn:GDB.SDL.code': 'gebieden:stadsdelenCode',
                    'ligtIn:GDB.SDL.naam': 'gebieden:stadsdelenNaam',
                    'ligtIn:BRK.GME.identificatie': 'brk:gemeentenIdentificatie',
                    'ligtIn:BRK.GME.volgnummer': 'brk:gemeentenVolgnummer',
                    'ligtIn:BRK.GME.naam': 'brk:gemeentenNaam',
                }
            }
        }
    }


class WijkenExportConfig:

    products = {
        'csv_actueel': {
            'exporter': csv_exporter,
            'endpoint': '/gob/gebieden/wijken/?view=enhanced',
            'filename': 'CSV_Actueel/GBD_wijk.csv',
            'mime_type': 'plain/text',
            'format': {
                'columns': [
                    'identificatie',
                    'code',
                    'naam',
                    'beginGeldigheid',
                    'eindGeldigheid',
                    'documentdatum',
                    'documentnummer',
                    'cbsCode',
                    'geometrie',
                ],
                'references': {
                    'ligtInGgwgebied': {
                        'ref': 'GBD.GGW',
                        'ref_name': 'ligtIn',
                        'columns': ['identificatie', 'code', 'naam'],
                    },
                    'ligtInStadsdeel': {
                        'ref': 'GBD.SDL',
                        'ref_name': 'ligtIn',
                        'columns': ['identificatie', 'code', 'naam'],
                    },
                    'ligtInGemeente': {
                        'ref': 'BRK.GME',
                        'ref_name': 'ligtIn',
                        'columns': ['identificatie', 'naam'],
                    }
                }
            }
        },
        'esri_actueel': {
            'exporter': esri_exporter,
            'endpoint': '/gob/gebieden/wijken/?view=enhanced',
            'filename': 'SHP/GBD_wijk.shp',
            'mime_type': 'application/octet-stream',
            'format': {
                'mapping': {
                    'id': 'identificatie',
                    'code': 'code',
                    'naam': 'naam',
                    'begindatum': 'beginGeldigheid',
                    'einddatum': 'eindGeldigheid',
                    'docdatum': 'documentdatum',
                    'docnummer': 'documentnummer',
                    'CBS_code': 'cbsCode',
                    'ggw_id': 'ligtInGgwgebied.identificatie',
                    'ggw_code': 'ligtInGgwgebied.code',
                    'ggw_naam': 'ligtInGgwgebied.naam',
                    'sdl_id': 'ligtInStadsdeel.identificatie',
                    'sdl_code': 'ligtInStadsdeel.code',
                    'sdl_naam': 'ligtInStadsdeel.naam',
                    'gme_id': 'ligtInGemeente.identificatie',
                    'gme_naam': 'ligtInGemeente.naam',
                }
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
            ]
        },
        'csv_actueel_en_historie': {
            'exporter': csv_exporter,
            'endpoint': '/gob/toestanden/?collections=gebieden:wijken,gebieden:ggwgebieden,gebieden:stadsdelen',
            'filename': 'CSV_ActueelEnHistorie/GBD_wijk.csv',
            'mime_type': 'plain/text',
            'format': {
                'columns': [
                    'identificatie',
                    'volgnummer',
                    'registratiedatum',
                    'code',
                    'naam',
                    'beginGeldigheid',
                    'eindGeldigheid',
                    'documentdatum',
                    'documentnummer',
                    'cbsCode',
                    'beginTijdvak',
                    'eindTijdvak',
                    'geometrie',
                ],
                'mapping': {
                    'ligtIn:GBD.GGW.identificatie': 'gebieden:stadsdelenIdentificatie',
                    'ligtIn:GDB.GGW.volgnummer': 'gebieden:stadsdelenVolgnummer',
                    'ligtIn:GDB.GGW.code': 'gebieden:stadsdelenCode',
                    'ligtIn:GDB.GGW.naam': 'gebieden:ggwgebiedenNaam',
                    'ligtIn:GBD.SDL.identificatie': 'gebieden:stadsdelenIdentificatie',
                    'ligtIn:GDB.SDL.volgnummer': 'gebieden:stadsdelenVolgnummer',
                    'ligtIn:GDB.SDL.code': 'gebieden:stadsdelenCode',
                    'ligtIn:GDB.SDL.naam': 'gebieden:stadsdelenNaam',
                    'ligtIn:BRK.GME.identificatie': 'brk:gemeentenIdentificatie',
                    'ligtIn:BRK.GME.volgnummer': 'brk:gemeentenVolgnummer',
                    'ligtIn:BRK.GME.naam': 'brk:gemeentenNaam',
                }
            }
        }
    }


class BuurtenExportConfig:

    products = {
        'csv_actueel': {
            'exporter': csv_exporter,
            'endpoint': '/gob/gebieden/buurten/?view=enhanced',
            'filename': 'CSV_Actueel/GBD_buurt.csv',
            'mime_type': 'plain/text',
            'format': {
                'columns': [
                    'identificatie',
                    'code',
                    'naam',
                    'beginGeldigheid',
                    'eindGeldigheid',
                    'documentdatum',
                    'documentnummer',
                    'cbsCode',
                    'geometrie',
                ],
                'references': {
                    'ligtInWijk': {
                        'ref': 'GBD.WIJK',
                        'ref_name': 'ligtIn',
                        'columns': ['identificatie', 'code', 'naam'],
                    },
                    'ligtInGgwgebied': {
                        'ref': 'GBD.GGW',
                        'ref_name': 'ligtIn',
                        'columns': ['identificatie', 'code', 'naam'],
                    },
                    'ligtInGgpgebied': {
                        'ref': 'GBD.GGP',
                        'ref_name': 'ligtIn',
                        'columns': ['identificatie', 'code', 'naam'],
                    },
                    'ligtInStadsdeel': {
                        'ref': 'GBD.SDL',
                        'ref_name': 'ligtIn',
                        'columns': ['identificatie', 'code', 'naam'],
                    },
                    'ligtInGemeente': {
                        'ref': 'BRK.GME',
                        'ref_name': 'ligtIn',
                        'columns': ['identificatie', 'naam'],
                    }
                }
            }
        },
        'esri_actueel': {
            'exporter': esri_exporter,
            'endpoint': '/gob/gebieden/buurten/?view=enhanced',
            'filename': 'SHP/GBD_buurt.shp',
            'mime_type': 'application/octet-stream',
            'format': {
                'mapping': {
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
                    'ggw_id': 'ligtInGgwgebied.identificatie',
                    'ggw_code': 'ligtInGgwgebied.code',
                    'ggw_naam': 'ligtInGgwgebied.naam',
                    'ggp_id': 'ligtInGgpgebied.identificatie',
                    'ggp_code': 'ligtInGgpgebied.code',
                    'ggp_naam': 'ligtInGgpgebied.naam',
                    'sdl_id': 'ligtInStadsdeel.identificatie',
                    'sdl_code': 'ligtInStadsdeel.code',
                    'sdl_naam': 'ligtInStadsdeel.naam',
                    'gme_id': 'ligtInGemeente.identificatie',
                    'gme_naam': 'ligtInGemeente.naam',
                }
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
            ]
        },
        'csv_actueel_en_historie': {
            'exporter': csv_exporter,
            'endpoint': '/gob/toestanden/?collections=gebieden:buurten,gebieden:wijken,'
            'gebieden:ggwgebieden,gebieden:ggpgebieden,gebieden:stadsdelen',
            'filename': 'CSV_ActueelEnHistorie/GBD_buurt.csv',
            'mime_type': 'plain/text',
            'format': {
                'columns': [
                    'identificatie',
                    'volgnummer',
                    'registratiedatum',
                    'code',
                    'naam',
                    'beginGeldigheid',
                    'eindGeldigheid',
                    'documentdatum',
                    'documentnummer',
                    'cbsCode',
                    'beginTijdvak',
                    'eindTijdvak',
                    'geometrie',
                ],
                'mapping': {
                    'ligtIn:GBD.WIJK.identificatie': 'gebieden:wijkenIdentificatie',
                    'ligtIn:GDB.WIJK.volgnummer': 'gebieden:wijkenVolgnummer',
                    'ligtIn:GDB.WIJK.code': 'gebieden:wijkenCode',
                    'ligtIn:GDB.WIJK.naam': 'gebieden:wijkenNaam',
                    'ligtIn:GBD.GGW.identificatie': 'gebieden:ggwgebiedenIdentificatie',
                    'ligtIn:GDB.GGW.volgnummer': 'gebieden:ggwgebiedenVolgnummer',
                    'ligtIn:GDB.GGW.code': 'gebieden:ggwgebiedenCode',
                    'ligtIn:GDB.GGW.naam': 'gebieden:ggwgebiedenNaam',
                    'ligtIn:GBD.GGP.identificatie': 'gebieden:ggpgebiedenIdentificatie',
                    'ligtIn:GDB.GGP.volgnummer': 'gebieden:ggpgebiedenVolgnummer',
                    'ligtIn:GDB.GGP.code': 'gebieden:ggpgebiedenCode',
                    'ligtIn:GDB.GGP.naam': 'gebieden:ggpgebiedenNaam',
                    'ligtIn:GBD.SDL.identificatie': 'gebieden:stadsdelenIdentificatie',
                    'ligtIn:GDB.SDL.volgnummer': 'gebieden:stadsdelenVolgnummer',
                    'ligtIn:GDB.SDL.code': 'gebieden:stadsdelenCode',
                    'ligtIn:GDB.SDL.naam': 'gebieden:stadsdelenNaam',
                    'ligtIn:BRK.GME.identificatie': 'brk:gemeentenIdentificatie',
                    'ligtIn:BRK.GME.volgnummer': 'brk:gemeentenVolgnummer',
                    'ligtIn:BRK.GME.naam': 'brk:gemeentenNaam',
                }
            }
        }
    }


class BouwblokkenExportConfig:

    products = {
        'csv_actueel': {
            'exporter': csv_exporter,
            'endpoint': '/gob/gebieden/bouwblokken/?view=enhanced',
            'filename': 'CSV_Actueel/GBD_bouwblok.csv',
            'mime_type': 'plain/text',
            'format': {
                'columns': [
                    'identificatie',
                    'code',
                    'beginGeldigheid',
                    'eindGeldigheid',
                    'geometrie',
                ],
                'references': {
                    'ligtInBuurt': {
                        'ref': 'GBD.BRT',
                        'ref_name': 'ligtIn',
                        'columns': ['identificatie', 'code', 'naam'],
                    },
                    'ligtInWijk': {
                        'ref': 'GBD.WIJK',
                        'ref_name': 'ligtIn',
                        'columns': ['identificatie', 'code', 'naam'],
                    },
                    'ligtInGgwgebied': {
                        'ref': 'GBD.GGW',
                        'ref_name': 'ligtIn',
                        'columns': ['identificatie', 'code', 'naam'],
                    },
                    'ligtInGgpgebied': {
                        'ref': 'GBD.GGP',
                        'ref_name': 'ligtIn',
                        'columns': ['identificatie', 'code', 'naam'],
                    },
                    'ligtInStadsdeel': {
                        'ref': 'GBD.SDL',
                        'ref_name': 'ligtIn',
                        'columns': ['identificatie', 'code', 'naam'],
                    },
                    'ligtInGemeente': {
                        'ref': 'BRK.GME',
                        'ref_name': 'ligtIn',
                        'columns': ['identificatie', 'naam'],
                    }
                }
            }
        },
        'esri_actueel': {
            'exporter': esri_exporter,
            'endpoint': '/gob/gebieden/bouwblokken/?view=enhanced',
            'filename': 'SHP/GBD_bouwblok.shp',
            'mime_type': 'application/octet-stream',
            'format': {
                'mapping': {
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
                    'ggw_id': 'ligtInGgwgebied.identificatie',
                    'ggw_code': 'ligtInGgwgebied.code',
                    'ggw_naam': 'ligtInGgwgebied.naam',
                    'ggp_id': 'ligtInGgpgebied.identificatie',
                    'ggp_code': 'ligtInGgpgebied.code',
                    'ggp_naam': 'ligtInGgpgebied.naam',
                    'sdl_id': 'ligtInStadsdeel.identificatie',
                    'sdl_code': 'ligtInStadsdeel.code',
                    'sdl_naam': 'ligtInStadsdeel.naam',
                    'gme_id': 'ligtInGemeente.identificatie',
                    'gme_naam': 'ligtInGemeente.naam',
                }
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
            ]
        },
        'csv_actueel_en_historie': {
            'exporter': csv_exporter,
            'endpoint': '/gob/toestanden/?collections=gebieden:bouwblokken,'
                        'gebieden:buurten,gebieden:wijken,gebieden:ggwgebieden,'
                        'gebieden:ggpgebieden,gebieden:stadsdelen',
            'filename': 'CSV_ActueelEnHistorie/GBD_bouwblok.csv',
            'mime_type': 'plain/text',
            'format': {
                'columns': [
                    'identificatie',
                    'volgnummer',
                    'registratiedatum',
                    'code',
                    'beginGeldigheid',
                    'eindGeldigheid',
                    'beginTijdvak',
                    'eindTijdvak',
                    'geometrie',
                ],
                'mapping': {
                    'ligtIn:GBD.BRT.identificatie': 'gebieden:buurtenIdentificatie',
                    'ligtIn:GDB.BRT.volgnummer': 'gebieden:buurtenVolgnummer',
                    'ligtIn:GDB.BRT.code': 'gebieden:buurtenCode',
                    'ligtIn:GDB.BRT.naam': 'gebieden:buurtenNaam',
                    'ligtIn:GBD.WIJK.identificatie': 'gebieden:wijkenIdentificatie',
                    'ligtIn:GDB.WIJK.volgnummer': 'gebieden:wijkenVolgnummer',
                    'ligtIn:GDB.WIJK.code': 'gebieden:wijkenCode',
                    'ligtIn:GDB.WIJK.naam': 'gebieden:wijkenNaam',
                    'ligtIn:GBD.GGW.identificatie': 'gebieden:ggwgebiedenIdentificatie',
                    'ligtIn:GDB.GGW.volgnummer': 'gebieden:ggwgebiedenVolgnummer',
                    'ligtIn:GDB.GGW.code': 'gebieden:ggwgebiedenCode',
                    'ligtIn:GDB.GGW.naam': 'gebieden:ggwgebiedenNaam',
                    'ligtIn:GBD.GGP.identificatie': 'gebieden:ggpgebiedenIdentificatie',
                    'ligtIn:GDB.GGP.volgnummer': 'gebieden:ggpgebiedenVolgnummer',
                    'ligtIn:GDB.GGP.code': 'gebieden:ggpgebiedenCode',
                    'ligtIn:GDB.GGP.naam': 'gebieden:ggpgebiedenNaam',
                    'ligtIn:GBD.SDL.identificatie': 'gebieden:stadsdelenIdentificatie',
                    'ligtIn:GDB.SDL.volgnummer': 'gebieden:stadsdelenVolgnummer',
                    'ligtIn:GDB.SDL.code': 'gebieden:stadsdelenCode',
                    'ligtIn:GDB.SDL.naam': 'gebieden:stadsdelenNaam',
                    'ligtIn:BRK.GME.identificatie': 'brk:gemeentenIdentificatie',
                    'ligtIn:BRK.GME.volgnummer': 'brk:gemeentenVolgnummer',
                    'ligtIn:BRK.GME.naam': 'brk:gemeentenNaam',
                }
            }
        }
    }
