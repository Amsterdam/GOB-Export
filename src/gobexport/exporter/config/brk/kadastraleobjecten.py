from fractions import Fraction

from gobexport.exporter.csv import csv_exporter
from gobexport.exporter.esri import esri_exporter
from gobexport.exporter.utils import convert_format
from gobexport.formatter.geometry import format_geometry
from gobexport.exporter.config.brk.utils import brk_filename, format_timestamp


class KadastraleobjectenCsvFormat:

    def if_vve(self, trueval, falseval):
        return {
            'condition': 'isempty',
            'reference': 'betrokkenBijAppartementsrechtsplitsingVve.[0].identificatie',
            'negate': True,
            'trueval': trueval,
            'falseval': falseval,
        }

    def if_sjt(self, trueval, falseval=None):
        val = {
            'condition': 'isempty',
            'reference': 'vanKadastraalsubject.[0].identificatie',
            'negate': True,
            'trueval': trueval,
        }

        if falseval:
            val['falseval'] = falseval

        return val

    def if_empty_geenWaarde(self, reference):
        return {
            'condition': 'isempty',
            'reference': reference,
            'negate': True,
            'trueval': reference,
            'falseval': {
                'action': 'literal',
                'value': 'geenWaarde'
            }
        }

    def comma_concatter(self, value):
        return value.replace('|', ', ')

    def comma_no_space_concatter(self, value):
        return value.replace('|', ',')

    def concat_with_comma(self, reference, with_space=True):
        return {
            'action': 'format',
            'value': reference,
            'formatter': self.comma_concatter if with_space else self.comma_no_space_concatter
        }

    def format_kadgrootte(self, value):
        floatval = float(value)

        if floatval < 1:
            return str(floatval)
        else:
            return str(int(floatval))

    def vve_or_subj(self, attribute):
        return self.if_vve(
            trueval=f"betrokkenBijAppartementsrechtsplitsingVve.[0].{attribute}",
            falseval=f"vanKadastraalsubject.[0].{attribute}",
        )

    def get_format(self):
        return {
            'BRK_KOT_ID': 'identificatie',
            'KOT_GEMEENTENAAM': 'aangeduidDoorGemeente.naam',
            'KOT_AKRKADGEMCODE_CODE': 'aangeduidDoorKadastralegemeentecode.[0].broninfo.code',
            'KOT_KADASTRALEGEMEENTE_CODE': 'aangeduidDoorKadastralegemeentecode.[0].broninfo.omschrijving',
            'KOT_KAD_GEMEENTECODE': 'aangeduidDoorKadastralegemeente.[0].broninfo.code',
            'KOT_KAD_GEMEENTE_OMS': 'aangeduidDoorKadastralegemeente.[0].broninfo.omschrijving',
            'KOT_SECTIE': 'aangeduidDoorKadastralesectie.[0].code',
            'KOT_PERCEELNUMMER': 'perceelnummer',
            'KOT_INDEX_LETTER': 'indexletter',
            'KOT_INDEX_NUMMER': 'indexnummer',
            'KOT_SOORTGROOTTE_CODE': 'soortGrootte.code',
            'KOT_SOORTGROOTTE_OMS': 'soortGrootte.omschrijving',
            'KOT_KADGROOTTE': {
                'action': 'format',
                'value': 'grootte',
                'formatter': self.format_kadgrootte,
            },
            'KOT_RELATIE_G_PERCEEL': self.concat_with_comma('isOntstaanUitGPerceel.identificatie', False),
            'KOT_KOOPSOM': 'koopsom',
            'KOT_KOOPSOM_VALUTA': 'koopsomValutacode',
            'KOT_KOOPJAAR': 'koopjaar',
            'KOT_INDICATIE_MEER_OBJECTEN': 'indicatieMeerObjecten',
            'KOT_CULTUURCODEONBEBOUWD_CODE': 'soortCultuurOnbebouwd.code',
            'KOT_CULTUURCODEONBEBOUWD_OMS': 'soortCultuurOnbebouwd.omschrijving',
            'KOT_CULTUURCODEBEBOUWD_CODE': self.if_empty_geenWaarde(
                self.concat_with_comma('soortCultuurBebouwd.code')
            ),
            'KOT_CULTUURCODEBEBOUWD_OMS': self.if_empty_geenWaarde(
                self.concat_with_comma('soortCultuurBebouwd.omschrijving')
            ),
            'KOT_AKRREGISTER9TEKST': '',
            'KOT_STATUS_CODE': 'status',
            'KOT_TOESTANDSDATUM': {
                'action': 'format',
                'formatter': format_timestamp,
                'value': 'toestandsdatum',
            },
            'KOT_IND_VOORLOPIGE_KADGRENS': {
                'reference': 'indicatieVoorlopigeGeometrie',
                'action': 'case',
                'values': {
                    'J': 'Voorlopige grens',
                    'N': 'Definitieve grens',
                },
            },
            'BRK_SJT_ID': self.vve_or_subj('identificatie'),
            'SJT_NAAM': self.if_vve(
                trueval='betrokkenBijAppartementsrechtsplitsingVve.[0].statutaireNaam',
                falseval=self.if_sjt(
                    trueval={
                        'condition': 'isempty',
                        'reference': 'vanKadastraalsubject.[0].statutaireNaam',
                        'trueval': {
                            'action': 'concat',
                            'fields': [
                                'vanKadastraalsubject.[0].geslachtsnaam',
                                {
                                    'action': 'literal',
                                    'value': ','
                                },
                                'vanKadastraalsubject.[0].voornamen',
                                {
                                    'action': 'literal',
                                    'value': ','
                                },
                                'vanKadastraalsubject.[0].voorvoegsels',
                                {
                                    'action': 'literal',
                                    'value': ' ('
                                },
                                'vanKadastraalsubject.[0].geslacht.code',
                                {
                                    'action': 'literal',
                                    'value': ')'
                                },
                            ]
                        },
                        'falseval': 'vanKadastraalsubject.[0].statutaireNaam'
                    }
                )
            ),
            'SJT_TYPE': self.vve_or_subj('typeSubject'),
            'SJT_NP_GEBOORTEDATUM': 'vanKadastraalsubject.[0].geboortedatum',
            'SJT_NP_GEBOORTEPLAATS': 'vanKadastraalsubject.[0].geboorteplaats',
            'SJT_NP_GEBOORTELAND_CODE': 'vanKadastraalsubject.[0].geboorteland.code',
            'SJT_NP_GEBOORTELAND_OMS': 'vanKadastraalsubject.[0].geboorteland.omschrijving',
            'SJT_NP_DATUMOVERLIJDEN': 'vanKadastraalsubject.[0].datumOverlijden',
            'SJT_NNP_RSIN': self.vve_or_subj('heeftRsinVoor.bronwaarde'),
            'SJT_NNP_KVKNUMMER': self.vve_or_subj('heeftKvknummerVoor.bronwaarde'),
            'SJT_NNP_RECHTSVORM_CODE': self.vve_or_subj('rechtsvorm.code'),
            'SJT_NNP_RECHTSVORM_OMS': self.vve_or_subj('rechtsvorm.omschrijving'),
            'SJT_NNP_STATUTAIRE_NAAM': self.vve_or_subj('statutaireNaam'),
            'SJT_NNP_STATUTAIRE_ZETEL': self.vve_or_subj('statutaireZetel'),
            'SJT_ZRT': 'invRustOpKadastraalobjectBrkZakelijkerechten.[0].aardZakelijkRecht.omschrijving',
            'SJT_AANDEEL': self.if_vve(
                trueval={
                    'action': 'literal',
                    'value': '1/1'
                },
                falseval={
                    'condition': 'isempty',
                    'reference': 'invVanZakelijkrechtBrkTenaamstellingen.[0].aandeel.teller',
                    'negate': True,
                    'trueval': {
                        'action': 'concat',
                        'fields': [
                            'invVanZakelijkrechtBrkTenaamstellingen.[0].aandeel.teller',
                            {
                                'action': 'literal',
                                'value': '/',
                            },
                            'invVanZakelijkrechtBrkTenaamstellingen.[0].aandeel.noemer'
                        ]
                    },
                    'falseval': {
                        'action': 'literal',
                        'value': 'ONBEKEND',
                    }
                }
            ),
            'SJT_VVE_SJT_ID': 'betrokkenBijAppartementsrechtsplitsingVve.[0].identificatie',
            'SJT_VVE_UIT_EIGENDOM': 'betrokkenBijAppartementsrechtsplitsingVve.[0].statutaireNaam',
            'KOT_INONDERZOEK': 'inOnderzoek',
            'KOT_MODIFICATION': '',
            'GEOMETRIE': {
                'action': 'format',
                'formatter': format_geometry,
                'value': 'geometrie'
            },
        }


class KadastraleobjectenEsriFormat(KadastraleobjectenCsvFormat):
    inonderzk = {
        'condition': 'isempty',
        'reference': 'inOnderzoek',
        'trueval': {
            'action': 'literal',
            'value': 'N',
        },
        'falseval': {
            'action': 'literal',
            'value': 'J',
        }
    }

    toestd_dat = {
        'action': 'format',
        'formatter': format_timestamp,
        'value': 'toestandsdatum',
        'kwargs': {'format': '%Y-%m-%d'},
    }

    def get_mapping(self):
        return {
            'BRK_KOT_ID': 'BRK_KOT_ID',
            'GEMEENTE': 'KOT_GEMEENTENAAM',
            'KADGEMCODE': 'KOT_KADASTRALEGEMEENTE_CODE',
            'KADGEM': 'KOT_KAD_GEMEENTE_OMS',
            'SECTIE': 'KOT_SECTIE',
            'PERCEELNR': 'KOT_PERCEELNUMMER',
            'INDEXLTR': 'KOT_INDEX_LETTER',
            'INDEXNR': 'KOT_INDEX_NUMMER',
            'SOORTGCOD': 'KOT_SOORTGROOTTE_CODE',
            'SOORTGOMS': 'KOT_SOORTGROOTTE_OMS',
            'KADGROOTTE': 'KOT_KADGROOTTE',
            'REL_GPCL': 'KOT_RELATIE_G_PERCEEL',
            'KOOPSOM': 'KOT_KOOPSOM',
            'KOOPSOMVAL': 'KOT_KOOPSOM_VALUTA',
            'KOOPJAAR': 'KOT_KOOPJAAR',
            'MEEROB_IND': 'KOT_INDICATIE_MEER_OBJECTEN',
            'CULTONBCOD': 'KOT_CULTUURCODEONBEBOUWD_CODE',
            'CULTONBOMS': 'KOT_CULTUURCODEONBEBOUWD_OMS',
            'CULTBCOD': 'KOT_CULTUURCODEBEBOUWD_CODE',
            'CULTBOMS': 'KOT_CULTUURCODEBEBOUWD_OMS',
            'AKRREG9T': 'KOT_AKRREGISTER9TEKST',
            'STATUSCOD': 'KOT_STATUS_CODE',
            'TOESTD_DAT': self.toestd_dat,
            'VL_KGR_IND': 'KOT_IND_VOORLOPIGE_KADGRENS',
            'BRK_SJT_ID': 'BRK_SJT_ID',
            'VVE_SJT_ID': 'SJT_VVE_SJT_ID',
            'SJT_NAAM': 'SJT_NAAM',
            'SJT_TYPE': 'SJT_TYPE',
            'RSIN': 'SJT_NNP_RSIN',
            'KVKNUMMER': 'SJT_NNP_KVKNUMMER',
            'RECHTSVCOD': 'SJT_NNP_RECHTSVORM_CODE',
            'RECHTSVOMS': 'SJT_NNP_RECHTSVORM_OMS',
            'STAT_NAAM': 'SJT_NNP_STATUTAIRE_NAAM',
            'STAT_ZETEL': 'SJT_NNP_STATUTAIRE_ZETEL',
            'SJT_ZRT': 'SJT_ZRT',
            # SJT_AANDEE is not a typo. Will be truncated by GDAL, which breaks the mapping.
            'SJT_AANDEE': 'SJT_AANDEEL',
            'INONDERZK': self.inonderzk,
        }

    def get_format(self):
        csv_format = super().get_format()
        return convert_format(csv_format, self.get_mapping())


class KadastraleobjectenEsriNoSubjectsFormat(KadastraleobjectenEsriFormat):
    def get_mapping(self):
        return {
            'BRK_KOT_ID': 'BRK_KOT_ID',
            'GEMEENTE': 'KOT_GEMEENTENAAM',
            'KADGEMCODE': 'KOT_KADASTRALEGEMEENTE_CODE',
            'KADGEM': 'KOT_KAD_GEMEENTE_OMS',
            'SECTIE': 'KOT_SECTIE',
            'PERCEELNR': 'KOT_PERCEELNUMMER',
            'INDEXLTR': 'KOT_INDEX_LETTER',
            'INDEXNR': 'KOT_INDEX_NUMMER',
            'SOORTGCOD': 'KOT_SOORTGROOTTE_CODE',
            'SOORTGOMS': 'KOT_SOORTGROOTTE_OMS',
            'KADGROOTTE': 'KOT_KADGROOTTE',
            'REL_GPCL': 'KOT_RELATIE_G_PERCEEL',
            'KOOPSOM': 'KOT_KOOPSOM',
            'KOOPSOMVAL': 'KOT_KOOPSOM_VALUTA',
            'KOOPJAAR': 'KOT_KOOPJAAR',
            'MEEROB_IND': 'KOT_INDICATIE_MEER_OBJECTEN',
            'CULTONBCOD': 'KOT_CULTUURCODEONBEBOUWD_CODE',
            'CULTONBOMS': 'KOT_CULTUURCODEONBEBOUWD_OMS',
            'CULTBCOD': 'KOT_CULTUURCODEBEBOUWD_CODE',
            'CULTBOMS': 'KOT_CULTUURCODEBEBOUWD_OMS',
            'AKRREG9T': 'KOT_AKRREGISTER9TEKST',
            'STATUSCOD': 'KOT_STATUS_CODE',
            'TOESTD_DAT': self.toestd_dat,
            'VL_KGR_IND': 'KOT_IND_VOORLOPIGE_KADGRENS',
            'INONDERZK': self.inonderzk,
        }


def aandeel_sort(a: dict, b: dict):
    """Returns True if a takes preference over b

    :param a:
    :param b:
    :return:
    """
    def is_valid(aandeel: dict):
        return aandeel is not None and isinstance(aandeel, dict) and aandeel.get('teller') is not None \
               and aandeel.get('noemer') is not None

    if not is_valid(a):
        return False

    if not is_valid(b):
        return True

    return Fraction(a['teller'], a['noemer']) > Fraction(b['teller'], b['noemer'])


class KadastraleobjectenExportConfig:
    csv_format = KadastraleobjectenCsvFormat()
    esri_format = KadastraleobjectenEsriFormat()
    esri_format_no_subjects = KadastraleobjectenEsriNoSubjectsFormat()

    csv_query = '''
{
  brkKadastraleobjecten {
    edges {
      node {
        identificatie
        volgnummer
        gemeente
        aangeduidDoorGemeente {
          edges {
            node {
              naam
            }
          }
        }
        aangeduidDoorKadastralegemeentecode {
          edges {
            node {
              broninfo
            }
          }
        }
        aangeduidDoorKadastralegemeente {
          edges {
            node {
              broninfo
            }
          }
        }
        aangeduidDoorKadastralesectie {
          edges {
            node {
              code
            }
          }
        }
        perceelnummer
        indexletter
        indexnummer
        soortGrootte
        grootte
        isOntstaanUitGPerceel {
          edges {
            node {
              identificatie
            }
          }
        }
        koopsom
        koopsomValutacode
        koopjaar
        indicatieMeerObjecten
        soortCultuurOnbebouwd
        soortCultuurBebouwd
        status
        toestandsdatum
        indicatieVoorlopigeGeometrie
        inOnderzoek
        geometrie
        invRustOpKadastraalobjectBrkZakelijkerechten(akrAardZakelijkRecht:"VE") {
          edges {
            node {
              identificatie
              aardZakelijkRecht
              betrokkenBijAppartementsrechtsplitsingVve {
                edges {
                  node {
                    identificatie
                    statutaireNaam
                    typeSubject
                    heeftRsinVoor
                    heeftKvknummerVoor
                    heeftBsnVoor
                    rechtsvorm
                    statutaireNaam
                    statutaireZetel
                  }
                }
              }
              invVanZakelijkrechtBrkTenaamstellingen {
                edges {
                  node {
                    aandeel
                    vanKadastraalsubject {
                      edges {
                        node {
                          identificatie
                          voornamen
                          voorvoegsels
                          geslachtsnaam
                          geslacht
                          statutaireNaam
                          typeSubject
                          geboortedatum
                          geboorteplaats
                          geboorteland
                          datumOverlijden
                          heeftRsinVoor
                          heeftKvknummerVoor
                          heeftBsnVoor
                          rechtsvorm
                          statutaireNaam
                          statutaireZetel
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

    esri_query = '''
{
  brkKadastraleobjecten(indexletter:"G") {
    edges {
      node {
        identificatie
        volgnummer
        gemeente
        aangeduidDoorGemeente {
          edges {
            node {
              naam
            }
          }
        }
        aangeduidDoorKadastralegemeentecode {
          edges {
            node {
              broninfo
            }
          }
        }
        aangeduidDoorKadastralegemeente {
          edges {
            node {
              broninfo
            }
          }
        }
        aangeduidDoorKadastralesectie {
          edges {
            node {
              code
            }
          }
        }
        perceelnummer
        indexletter
        indexnummer
        soortGrootte
        grootte
        isOntstaanUitGPerceel {
          edges {
            node {
              identificatie
            }
          }
        }
        koopsom
        koopsomValutacode
        koopjaar
        indicatieMeerObjecten
        soortCultuurOnbebouwd
        soortCultuurBebouwd
        status
        toestandsdatum
        indicatieVoorlopigeGeometrie
        inOnderzoek
        geometrie
        invRustOpKadastraalobjectBrkZakelijkerechten(akrAardZakelijkRecht:"VE") {
          edges {
            node {
              identificatie
              aardZakelijkRecht
              betrokkenBijAppartementsrechtsplitsingVve {
                edges {
                  node {
                    identificatie
                    statutaireNaam
                    typeSubject
                    heeftRsinVoor
                    heeftKvknummerVoor
                    heeftBsnVoor
                    rechtsvorm
                    statutaireNaam
                    statutaireZetel
                  }
                }
              }
              invVanZakelijkrechtBrkTenaamstellingen {
                edges {
                  node {
                    aandeel
                    vanKadastraalsubject {
                      edges {
                        node {
                          identificatie
                          voornamen
                          voorvoegsels
                          geslachtsnaam
                          geslacht
                          statutaireNaam
                          typeSubject
                          geboortedatum
                          geboorteplaats
                          geboorteland
                          datumOverlijden
                          heeftRsinVoor
                          heeftKvknummerVoor
                          heeftBsnVoor
                          rechtsvorm
                          statutaireNaam
                          statutaireZetel
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

    sort = {
        'invRustOpKadastraalobjectBrkZakelijkerechten'
        '.invVanZakelijkrechtBrkTenaamstellingen'
        '.aandeel': aandeel_sort,
        'invRustOpKadastraalobjectBrkZakelijkerechten'
        '.invVanZakelijkrechtBrkTenaamstellingen'
        '.vanKadastraalsubject'
        '.identificatie':
        # Take subject ID with highest number (which is the last part of the . separated string)
            lambda x, y: int(x.split('.')[-1]) > int(y.split('.')[-1])
    }

    """
    Tenaamstellingen/Subject: Return the tenaamstelling with the largest aandeel (teller/noemer). When multiple
    tenaamstellingen have an even aandeel, sort the tenaamstellingen by its subject's geslachtsnaam.
    """
    products = {
        'csv': {
            'exporter': csv_exporter,
            'api_type': 'graphql_streaming',
            'secure': True,
            'query': csv_query,
            'filename': lambda: brk_filename('kadastraal_object'),
            'mime_type': 'plain/text',
            'format': csv_format.get_format(),
            'sort': sort,
        },
        'esri_actueel': {
            'api_type': 'graphql_streaming',
            'secure': True,
            'exporter': esri_exporter,
            'filename': 'AmsterdamRegio/SHP_Actueel/BRK_Adam_totaal_G.shp',
            'mime_type': 'application/octet-stream',
            'format': esri_format.get_format(),
            'sort': sort,
            'extra_files': [
                {
                    'filename': 'AmsterdamRegio/SHP_Actueel/BRK_Adam_totaal_G.dbf',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'AmsterdamRegio/SHP_Actueel/BRK_Adam_totaal_G.shx',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'AmsterdamRegio/SHP_Actueel/BRK_Adam_totaal_G.prj',
                    'mime_type': 'application/octet-stream'
                },
            ],
            'query': esri_query,
        },
        'esri_actueel_no_subjects': {
            'api_type': 'graphql_streaming',
            'secure': True,
            'exporter': esri_exporter,
            'filename': 'AmsterdamRegio/SHP_Actueel/BRK_Adam_totaal_G_zonderSubjecten.shp',
            'mime_type': 'application/octet-stream',
            'format': esri_format_no_subjects.get_format(),
            'extra_files': [
                {
                    'filename': 'AmsterdamRegio/SHP_Actueel/BRK_Adam_totaal_G_zonderSubjecten.dbf',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'AmsterdamRegio/SHP_Actueel/BRK_Adam_totaal_G_zonderSubjecten.shx',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': 'AmsterdamRegio/SHP_Actueel/BRK_Adam_totaal_G_zonderSubjecten.prj',
                    'mime_type': 'application/octet-stream'
                },
            ],
            'query': esri_query,
        }
    }
