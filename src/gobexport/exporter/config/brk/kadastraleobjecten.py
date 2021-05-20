from fractions import Fraction

from gobexport.exporter.csv import csv_exporter
from gobexport.exporter.esri import esri_exporter
from gobexport.exporter.utils import convert_format, get_entity_value
from gobexport.formatter.geometry import format_geometry
from gobexport.filters.notempty_filter import NotEmptyFilter
from gobexport.filters.entity_filter import EntityFilter
from gobexport.exporter.config.brk.utils import brk_filename, brk_directory, format_timestamp


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

    def row_formatter(self, row):
        """Merges all 'isOntstaanUitGPerceel' relations into one object, with identificatie column concatenated into
        one, separated by comma's.

        (Very) simplified example:
        in     = { isOntstaanUitGPerceel: [{identificatie: 'A'}, {identificatie: 'B'}, {identificatie: 'C'}]}
        result = { isOntstaanUitGPerceel: [{identificatie: 'A,B,C'}]}

        :param row:
        :return:
        """
        identificatie = ','.join([edge['node']['identificatie']
                                  for edge in row['node']['isOntstaanUitGPerceel'].get('edges')])

        row['node']['isOntstaanUitGPerceel'] = {
            'edges': [{
                'node': {
                    'identificatie': identificatie
                }
            }]
        }

        return row

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
            'KOT_RELATIE_G_PERCEEL': 'isOntstaanUitGPerceel.identificatie',
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


class PerceelnummerEsriFormat:

    def format_rotatie(self, value):
        assert not None and isinstance(value, (int, float))
        # Return rotatie with three decimal places
        return f'{value:.3f}'

    def get_format(self):
        return {
            'BRK_KOT_ID': 'identificatie',
            'GEMEENTE': 'aangeduidDoorGemeente.naam',
            'KADGEMCODE': 'aangeduidDoorKadastralegemeentecode.[0].broninfo.omschrijving',
            'KADGEM': 'aangeduidDoorKadastralegemeente.[0].broninfo.omschrijving',
            'SECTIE': 'aangeduidDoorKadastralesectie.[0].code',
            'PERCEELNR': 'perceelnummer',
            'INDEXLTR': 'indexletter',
            'INDEXNR': 'indexnummer',
            'ROTATIE': {
                'condition': 'isempty',
                'reference': 'perceelnummerRotatie',
                'falseval': {
                    'action': 'format',
                    'formatter': self.format_rotatie,
                    'value': 'perceelnummerRotatie',
                },
                'trueval': {
                    'action': 'literal',
                    'value': '0.000',
                }
            },
            'geometrie': {
                'action': 'format',
                'formatter': format_geometry,
                'value': 'plaatscoordinaten'
            },
        }


class BrkBagCsvFormat:

    def if_vot_relation(self, trueval: str, falseval: str):
        return {
            'condition': 'isempty',
            'reference': 'heeftEenRelatieMetVerblijfsobject.[0].identificatie',
            'negate': True,
            'trueval': trueval,
            'falseval': falseval,
        }

    def get_format(self):
        return {
            'BRK_KOT_ID': 'identificatie',
            'KOT_AKRKADGEMEENTECODE_CODE': 'aangeduidDoorKadastralegemeentecode.[0].broninfo.code',
            'KOT_AKRKADGEMEENTECODE_OMS': 'aangeduidDoorKadastralegemeentecode.[0].broninfo.omschrijving',
            'KOT_SECTIE': 'aangeduidDoorKadastralesectie.[0].code',
            'KOT_PERCEELNUMMER': 'perceelnummer',
            'KOT_INDEX_LETTER': 'indexletter',
            'KOT_INDEX_NUMMER': 'indexnummer',
            'KOT_STATUS_CODE': 'status',
            'KOT_MODIFICATION': '',
            'BAG_VOT_ID': 'heeftEenRelatieMetVerblijfsobject.[0].bronwaarde',
            'DIVA_VOT_ID': '',
            'AOT_OPENBARERUIMTENAAM': self.if_vot_relation(
                trueval='ligtAanOpenbareruimte.naam',
                falseval='heeftEenRelatieMetVerblijfsobject.[0].broninfo.openbareruimtenaam'
            ),
            'AOT_HUISNUMMER': self.if_vot_relation(
                trueval='heeftHoofdadres.huisnummer',
                falseval='heeftEenRelatieMetVerblijfsobject.[0].broninfo.huisnummer'
            ),
            'AOT_HUISLETTER': self.if_vot_relation(
                trueval='heeftHoofdadres.huisletter',
                falseval='heeftEenRelatieMetVerblijfsobject.[0].broninfo.huisletter'
            ),
            'AOT_HUISNUMMERTOEVOEGING': self.if_vot_relation(
                trueval='heeftHoofdadres.huisnummertoevoeging',
                falseval='heeftEenRelatieMetVerblijfsobject.[0].broninfo.huisnummertoevoeging'
            ),
            'AOT_POSTCODE': self.if_vot_relation(
                trueval='heeftHoofdadres.postcode',
                falseval='heeftEenRelatieMetVerblijfsobject.[0].broninfo.postcode'
            ),
            'AOT_WOONPLAATSNAAM': self.if_vot_relation(
                trueval='heeftEenRelatieMetVerblijfsobject.[0].heeftHoofdadres.[0].'
                        'ligtAanOpenbareruimte.[0].ligtInWoonplaats.[0].naam',
                falseval='heeftEenRelatieMetVerblijfsobject.[0].broninfo.woonplaatsnaam'
            ),
            'BRON_RELATIE': {
                'action': 'literal',
                'value': 'BRK'
            }
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
    perceelnummer_esri_format = PerceelnummerEsriFormat()
    brk_bag_format = BrkBagCsvFormat()

    gperc_query = '''
{
  brkKadastraleobjecten {
    edges {
      node {
        identificatie
        volgnummer
        isOntstaanUitGPerceel {
          edges {
            node {
              identificatie
            }
          }
        }
      }
    }
  }
}
'''

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

    bijpijling_query = '''
{
  brkKadastraleobjecten(indexletter: "G") {
    edges {
      node {
        identificatie
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
        bijpijlingGeometrie
      }
    }
  }
}
'''

    perceelnummer_query = '''
{
  brkKadastraleobjecten(indexletter: "G") {
    edges {
      node {
        identificatie
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
        perceelnummerRotatie
        plaatscoordinaten
      }
    }
  }
}
'''

    brk_bag_query = '''
{
  brkKadastraleobjecten {
    edges {
      node {
        identificatie
        aangeduidDoorKadastralegemeente {
          edges {
            node {
              broninfo
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
        status
        heeftEenRelatieMetVerblijfsobject {
          edges {
            node {
              identificatie
              bronwaarde
              status
              broninfo
                heeftHoofdadres {
                edges {
                  node {
                    identificatie
                    ligtAanOpenbareruimte {
                      edges {
                        node {
                          naam
                          ligtInWoonplaats {
                            edges {
                              node {
                                naam
                              }
                            }
                          }
                        }
                      }
                    }
                    huisnummer
                    huisletter
                    huisnummertoevoeging
                    postcode
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

    class VotFilter(EntityFilter):
        """Only include rows with VOT statuses, for VOT's where status is defined:
        2   Niet gerealiseerd verblijfsobject
        3   Verblijfsobject in gebruik (niet ingemeten)
        4   Verblijfsobject in gebruik
        6   Verblijfsobject buiten gebruik

        """
        valid_status_codes = [2, 3, 4, 6]
        vot_identificatie = 'heeftEenRelatieMetVerblijfsobject.[0].identificatie'
        status_code = 'heeftEenRelatieMetVerblijfsobject.[0].status.code'
        city = 'heeftEenRelatieMetVerblijfsobject.[0].broninfo.woonplaatsnaam'

        def filter(self, entity: dict):
            if get_entity_value(entity, self.vot_identificatie):
                status_code = get_entity_value(entity, self.status_code)
                return status_code and int(status_code) in self.valid_status_codes
            elif get_entity_value(entity, self.city):
                return not get_entity_value(entity, self.city).lower().startswith('amsterdam')

            return True

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
        'kot_csv': {
            'merge_result': {
                'api_type': 'graphql_streaming',
                'attributes': ['isOntstaanUitGPerceel'],
                'query': gperc_query,
                'match_attributes': ['identificatie', 'volgnummer'],
                'row_formatter': csv_format.row_formatter,
                'secure_user': 'gob',
            },
            'exporter': csv_exporter,
            'api_type': 'graphql_streaming',
            'secure_user': 'gob',
            'query': csv_query,
            'filename': lambda: brk_filename('kadastraal_object', use_sensitive_dir=True),
            'mime_type': 'plain/text',
            'format': csv_format.get_format(),
            'sort': sort,
        },
        'kot_esri_actueel': {
            'api_type': 'graphql_streaming',
            'secure_user': 'gob',
            'exporter': esri_exporter,
            'filename': f'{brk_directory("shp", use_sensitive_dir=True)}/BRK_Adam_totaal_G.shp',
            'mime_type': 'application/octet-stream',
            'format': esri_format.get_format(),
            'sort': sort,
            'extra_files': [
                {
                    'filename': f'{brk_directory("dbf", use_sensitive_dir=True)}/BRK_Adam_totaal_G.dbf',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': f'{brk_directory("shx", use_sensitive_dir=True)}/BRK_Adam_totaal_G.shx',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': f'{brk_directory("prj", use_sensitive_dir=True)}/BRK_Adam_totaal_G.prj',
                    'mime_type': 'application/octet-stream'
                },
            ],
            'query': esri_query,
        },
        'kot_esri_actueel_no_subjects': {
            'api_type': 'graphql_streaming',
            'secure_user': 'gob',
            'exporter': esri_exporter,
            'filename': f'{brk_directory("shp", use_sensitive_dir=False)}/BRK_Adam_totaal_G_zonderSubjecten.shp',
            'mime_type': 'application/octet-stream',
            'format': esri_format_no_subjects.get_format(),
            'extra_files': [
                {
                    'filename': f'{brk_directory("dbf", use_sensitive_dir=False)}'
                                '/BRK_Adam_totaal_G_zonderSubjecten.dbf',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': f'{brk_directory("shx", use_sensitive_dir=False)}'
                                '/BRK_Adam_totaal_G_zonderSubjecten.shx',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': f'{brk_directory("prj", use_sensitive_dir=False)}'
                                '/BRK_Adam_totaal_G_zonderSubjecten.prj',
                    'mime_type': 'application/octet-stream'
                },
            ],
            'query': esri_query,
        },
        'bijpijling_shape': {
            'exporter': esri_exporter,
            'api_type': 'graphql_streaming',
            'secure_user': 'gob',
            'filename': f'{brk_directory("shp", use_sensitive_dir=False)}/BRK_bijpijling.shp',
            'entity_filters': [
                NotEmptyFilter('bijpijlingGeometrie'),
            ],
            'mime_type': 'application/octet-stream',
            'format': {
                'BRK_KOT_ID': 'identificatie',
                'GEMEENTE': 'aangeduidDoorGemeente.naam',
                'KADGEMCODE': 'aangeduidDoorKadastralegemeentecode.[0].broninfo.omschrijving',
                'KADGEM': 'aangeduidDoorKadastralegemeente.[0].broninfo.omschrijving',
                'SECTIE': 'aangeduidDoorKadastralesectie.[0].code',
                'PERCEELNR': 'perceelnummer',
                'INDEXLTR': 'indexletter',
                'INDEXNR': 'indexnummer',
                'geometrie': {
                    'action': 'format',
                    'formatter': format_geometry,
                    'value': 'bijpijlingGeometrie'
                },
            },
            'extra_files': [
                {
                    'filename': f'{brk_directory("dbf", use_sensitive_dir=False)}/BRK_bijpijling.dbf',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': f'{brk_directory("shx", use_sensitive_dir=False)}/BRK_bijpijling.shx',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': f'{brk_directory("prj", use_sensitive_dir=False)}/BRK_bijpijling.prj',
                    'mime_type': 'application/octet-stream'
                },
            ],
            'query': bijpijling_query
        },
        'perceel_shape': {
            'exporter': esri_exporter,
            'api_type': 'graphql_streaming',
            'secure_user': 'gob',
            'filename': f'{brk_directory("shp", use_sensitive_dir=False)}/BRK_perceelnummer.shp',
            'entity_filters': [
                NotEmptyFilter('plaatscoordinaten'),
            ],
            'mime_type': 'application/octet-stream',
            'format': perceelnummer_esri_format.get_format(),
            'extra_files': [
                {
                    'filename': f'{brk_directory("dbf", use_sensitive_dir=False)}/BRK_perceelnummer.dbf',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': f'{brk_directory("shx", use_sensitive_dir=False)}/BRK_perceelnummer.shx',
                    'mime_type': 'application/octet-stream'
                },
                {
                    'filename': f'{brk_directory("prj", use_sensitive_dir=False)}/BRK_perceelnummer.prj',
                    'mime_type': 'application/octet-stream'
                },
            ],
            'query': perceelnummer_query
        },
        'brk_bag_csv': {
            'exporter': csv_exporter,
            'entity_filters': [
                NotEmptyFilter('heeftEenRelatieMetVerblijfsobject.[0].bronwaarde'),
                VotFilter(),
            ],
            'api_type': 'graphql_streaming',
            'secure_user': 'gob',
            'unfold': True,
            'query': brk_bag_query,
            'filename': lambda: brk_filename("BRK_BAG", use_sensitive_dir=False),
            'mime_type': 'plain/text',
            'format': brk_bag_format.get_format(),
        }
    }
