"""BRK2 kadastraleobjecten exports."""


from fractions import Fraction

from gobexport.exporter.config.brk2.utils import brk2_directory, brk2_filename, format_timestamp
from gobexport.exporter.csv import csv_exporter
from gobexport.exporter.esri import esri_exporter
from gobexport.exporter.utils import convert_format, get_entity_value
from gobexport.filters.entity_filter import EntityFilter
from gobexport.filters.notempty_filter import NotEmptyFilter
from gobexport.formatter.geometry import format_geometry


class Brk2BagCsvFormat:
    """CSV format class for BRK2 BAG export."""

    def if_vot_relation(self, trueval: str, falseval: str):
        """BAG verblijfsobjecten (VOT) relation dictionary."""
        return {
            "condition": "isempty",
            "reference": "heeftEenRelatieMetBagVerblijfsobject.[0].identificatie",
            "negate": True,
            "trueval": trueval,
            "falseval": falseval,
        }

    def get_format(self):
        """BRK2 BAG CSV format dictionary."""
        return {
            "BRK_KOT_ID": "identificatie",
            "KOT_AKRKADGEMEENTECODE_CODE": "aangeduidDoorBrkKadastralegemeentecode.code",
            "KOT_AKRKADGEMEENTECODE_OMS": "aangeduidDoorBrkKadastralegemeentecode.identificatie",
            "KOT_SECTIE": "aangeduidDoorBrkKadastralesectie.code",
            "KOT_PERCEELNUMMER": "perceelnummer",
            "KOT_INDEX_LETTER": "indexletter",
            "KOT_INDEX_NUMMER": "indexnummer",
            "KOT_MODIFICATION": "",
            "BAG_VOT_ID": "heeftEenRelatieMetBagVerblijfsobject.[0].bronwaarde",
            "BAG_VOT_STATUS": "heeftEenRelatieMetBagVerblijfsobject.[0].status.omschrijving",
            "DIVA_VOT_ID": "",
            "AOT_OPENBARERUIMTENAAM": self.if_vot_relation(
                trueval="ligtAanOpenbareruimte.naam",
                falseval="heeftEenRelatieMetBagVerblijfsobject.[0].broninfo.openbareruimtenaam",
            ),
            "AOT_HUISNUMMER": self.if_vot_relation(
                trueval="heeftHoofdadres.huisnummer",
                falseval="heeftEenRelatieMetBagVerblijfsobject.[0].broninfo.huisnummer",
            ),
            "AOT_HUISLETTER": self.if_vot_relation(
                trueval="heeftHoofdadres.huisletter",
                falseval="heeftEenRelatieMetBagVerblijfsobject.[0].broninfo.huisletter",
            ),
            "AOT_HUISNUMMERTOEVOEGING": self.if_vot_relation(
                trueval="heeftHoofdadres.huisnummertoevoeging",
                falseval="heeftEenRelatieMetBagVerblijfsobject.[0].broninfo.huisnummertoevoeging",
            ),
            "AOT_POSTCODE": self.if_vot_relation(
                trueval="heeftHoofdadres.postcode",
                falseval="heeftEenRelatieMetBagVerblijfsobject.[0].broninfo.postcode",
            ),
            "AOT_WOONPLAATSNAAM": self.if_vot_relation(
                trueval="heeftEenRelatieMetBagVerblijfsobject.[0].heeftHoofdadres.[0]."
                "ligtAanOpenbareruimte.[0].ligtInWoonplaats.[0].naam",
                falseval="heeftEenRelatieMetBagVerblijfsobject.[0].broninfo.woonplaatsnaam",
            ),
            "BRON_RELATIE": {"action": "literal", "value": "BRK2"},
        }


def aandeel_sort(a: dict, b: dict):
    """Returns True if aandeel a takes preference over b.

    :param a:
    :param b:
    :return:
    """

    def is_valid(aandeel: dict):
        return (
            aandeel is not None
            and isinstance(aandeel, dict)
            and aandeel.get("teller") is not None
            and aandeel.get("noemer") is not None
        )

    if not is_valid(a):
        return False

    if not is_valid(b):
        return True

    return Fraction(a["teller"], a["noemer"]) > Fraction(b["teller"], b["noemer"])


class KadastraleobjectenCsvFormat:
    """CSV format class for BRK2 Kadastraleobjecten exports."""

    def if_vve(self, trueval, falseval):
        return {
            "condition": "isempty",
            "reference": "vveIdentificatieBetrokkenBij.[0].identificatie",
            "negate": True,
            "trueval": trueval,
            "falseval": falseval,
        }

    def if_sjt(self, trueval, falseval=None):
        val = {
            "condition": "isempty",
            "reference": "vanBrkKadastraalsubject.[0].identificatie",
            "negate": True,
            "trueval": trueval,
        }

        if falseval:
            val["falseval"] = falseval

        return val

    def if_empty_geen_waarde(self, reference):
        return {
            "condition": "isempty",
            "reference": reference,
            "negate": True,
            "trueval": reference,
            "falseval": {"action": "literal", "value": "geenWaarde"},
        }

    def comma_concatter(self, value):
        return value.replace("|", ", ")

    def concat_with_comma(self, reference):
        """Replace occurrences of '|' in `reference` with commas."""
        return {
            "action": "format",
            "value": reference,
            "formatter": self.comma_concatter,
        }

    def format_kadgrootte(self, value):
        floatval = float(value)

        if floatval < 1:
            return str(floatval)
        return str(int(floatval))

    def vve_or_subj(self, attribute):
        return self.if_vve(
            trueval=f"vveIdentificatieBetrokkenBij.[0].{attribute}",
            falseval=f"vanBrkKadastraalsubject.[0].{attribute}",
        )

    def get_format(self):
        """Kadastraleobjecten CSV format dictionary."""
        return {
            "BRK_KOT_ID": "identificatie",
            "KOT_GEMEENTENAAM": "aangeduidDoorBrkGemeente.naam",
            "KOT_AKRKADGEMCODE_CODE": "aangeduidDoorBrkKadastralegemeentecode.code",
            "KOT_KADASTRALEGEMEENTE_CODE": "aangeduidDoorBrkKadastralegemeentecode.identificatie",
            "KOT_KAD_GEMEENTECODE": "aangeduidDoorBrkKadastralegemeente.code",
            "KOT_KAD_GEMEENTE_OMS": "aangeduidDoorBrkKadastralegemeente.identificatie",
            "KOT_SECTIE": "aangeduidDoorBrkKadastralesectie.code",
            "KOT_PERCEELNUMMER": "perceelnummer",
            "KOT_INDEX_LETTER": "indexletter",
            "KOT_INDEX_NUMMER": "indexnummer",
            "KOT_SOORTGROOTTE_CODE": "soortGrootte.code",
            "KOT_SOORTGROOTTE_OMS": "soortGrootte.omschrijving",
            "KOT_KADGROOTTE": {
                "action": "format",
                "value": "grootte",
                "formatter": self.format_kadgrootte,
            },
            "KOT_RELATIE_G_PERCEEL": "isOntstaanUitBrkGPerceel.identificatie",
            "KOT_KOOPSOM": "koopsom",
            "KOT_KOOPSOM_VALUTA": "koopsomValutacode",
            "KOT_KOOPJAAR": "koopjaar",
            "KOT_INDICATIE_MEER_OBJECTEN": "indicatieMeerObjecten",
            "KOT_CULTUURCODEONBEBOUWD_CODE": "soortCultuurOnbebouwd.code",
            "KOT_CULTUURCODEONBEBOUWD_OMS": "soortCultuurOnbebouwd.omschrijving",
            "KOT_CULTUURCODEBEBOUWD_CODE": self.if_empty_geen_waarde(
                self.concat_with_comma("soortCultuurBebouwd.code")
            ),
            "KOT_CULTUURCODEBEBOUWD_OMS": self.if_empty_geen_waarde(
                self.concat_with_comma("soortCultuurBebouwd.omschrijving")
            ),
            "KOT_AKRREGISTER9TEKST": "",
            "KOT_STATUS_CODE": "status",
            "KOT_TOESTANDSDATUM": {
                "action": "format",
                "formatter": format_timestamp,
                "value": "toestandsdatum",
            },
            "KOT_IND_VOORLOPIGE_KADGRENS": {
                "reference": "indicatieVoorlopigeKadastraleGrens",
                "action": "case",
                "values": {
                    True: "Voorlopige grens",
                    False: "Definitieve grens",
                },
            },
            "BRK_SJT_ID": self.vve_or_subj("identificatie"),
            "SJT_NAAM": self.if_vve(
                trueval="vveIdentificatieBetrokkenBij.[0].statutaireNaam",
                falseval=self.if_sjt(
                    trueval={
                        "condition": "isempty",
                        "reference": "vanBrkKadastraalsubject.[0].statutaireNaam",
                        "trueval": {
                            "action": "concat",
                            "fields": [
                                "vanBrkKadastraalsubject.[0].geslachtsnaam",
                                {"action": "literal", "value": ","},
                                "vanBrkKadastraalsubject.[0].voornamen",
                                {"action": "literal", "value": ","},
                                "vanBrkKadastraalsubject.[0].voorvoegsels",
                                {"action": "literal", "value": " ("},
                                "vanBrkKadastraalsubject.[0].geslacht.code",
                                {"action": "literal", "value": ")"},
                            ],
                        },
                        "falseval": "vanBrkKadastraalsubject.[0].statutaireNaam",
                    }
                ),
            ),
            "SJT_TYPE": self.vve_or_subj("typeSubject"),
            "SJT_NP_GEBOORTEDATUM": "vanBrkKadastraalsubject.[0].geboortedatum",
            "SJT_NP_GEBOORTEPLAATS": "vanBrkKadastraalsubject.[0].geboorteplaats",
            "SJT_NP_GEBOORTELAND_CODE": "vanBrkKadastraalsubject.[0].geboorteland.code",
            "SJT_NP_GEBOORTELAND_OMS": "vanBrkKadastraalsubject.[0].geboorteland.omschrijving",
            "SJT_NP_DATUMOVERLIJDEN": "vanBrkKadastraalsubject.[0].datumOverlijden",
            "SJT_NNP_RSIN": self.vve_or_subj("heeftRsinVoorHrNietNatuurlijkepersoon.bronwaarde"),
            "SJT_NNP_KVKNUMMER": self.vve_or_subj("heeftKvknummerVoorHrMaatschappelijkeactiviteit.bronwaarde"),
            "SJT_NNP_RECHTSVORM_CODE": self.vve_or_subj("rechtsvorm.code"),
            "SJT_NNP_RECHTSVORM_OMS": self.vve_or_subj("rechtsvorm.omschrijving"),
            "SJT_NNP_STATUTAIRE_NAAM": self.vve_or_subj("statutaireNaam"),
            "SJT_NNP_STATUTAIRE_ZETEL": self.vve_or_subj("statutaireZetel"),
            "SJT_ZRT": "invRustOpBrkKadastraalObjectBrk2Zakelijkerechten.[0].aardZakelijkRecht.omschrijving",
            "SJT_AANDEEL": self.if_vve(
                trueval={"action": "literal", "value": "1/1"},
                falseval={
                    "condition": "isempty",
                    "reference": "invVanBrkZakelijkRechtBrk2Tenaamstellingen.[0].aandeel.teller",
                    "negate": True,
                    "trueval": {
                        "action": "concat",
                        "fields": [
                            "invVanBrkZakelijkRechtBrk2Tenaamstellingen.[0].aandeel.teller",
                            {
                                "action": "literal",
                                "value": "/",
                            },
                            "invVanBrkZakelijkRechtBrk2Tenaamstellingen.[0].aandeel.noemer",
                        ],
                    },
                    "falseval": {
                        "action": "literal",
                        "value": "ONBEKEND",
                    },
                },
            ),
            "SJT_VVE_SJT_ID": "vveIdentificatieBetrokkenBij.[0].identificatie",
            "SJT_VVE_UIT_EIGENDOM": "vveIdentificatieBetrokkenBij.[0].statutaireNaam",
            "KOT_INONDERZOEK": "inOnderzoek",
            "KOT_MODIFICATION": "",
            "GEOMETRIE": {
                "action": "format",
                "formatter": format_geometry,
                "value": "geometrie",
            },
        }


class KadastraleobjectenEsriNoSubjectsFormat(KadastraleobjectenCsvFormat):
    """ESRI (GIS) format class for KOT exports without subjects."""

    inonderzk = {
        "condition": "isempty",
        "reference": "inOnderzoek",
        "trueval": {
            "action": "literal",
            "value": "N",
        },
        "falseval": {
            "action": "literal",
            "value": "J",
        },
    }

    toestd_dat = {
        "action": "format",
        "formatter": format_timestamp,
        "value": "toestandsdatum",
        "kwargs": {"format": "%Y-%m-%d"},
    }

    def get_format(self):
        """Kadastraleobjecten ESRI format dictionary."""
        csv_format = super().get_format()
        return convert_format(csv_format, self.get_mapping())

    def get_mapping(self):
        """Kadastraleobjecten ESRI without subjects mapping."""
        return {
            "BRK_KOT_ID": "BRK_KOT_ID",
            "GEMEENTE": "KOT_GEMEENTENAAM",
            "KADGEMCODE": "KOT_KADASTRALEGEMEENTE_CODE",
            "KADGEM": "KOT_KAD_GEMEENTE_OMS",
            "SECTIE": "KOT_SECTIE",
            "PERCEELNR": "KOT_PERCEELNUMMER",
            "INDEXLTR": "KOT_INDEX_LETTER",
            "INDEXNR": "KOT_INDEX_NUMMER",
            "SOORTGCOD": "KOT_SOORTGROOTTE_CODE",
            "SOORTGOMS": "KOT_SOORTGROOTTE_OMS",
            "KADGROOTTE": "KOT_KADGROOTTE",
            "REL_GPCL": "KOT_RELATIE_G_PERCEEL",
            "KOOPSOM": "KOT_KOOPSOM",
            "KOOPSOMVAL": "KOT_KOOPSOM_VALUTA",
            "KOOPJAAR": "KOT_KOOPJAAR",
            "MEEROB_IND": "KOT_INDICATIE_MEER_OBJECTEN",
            "CULTONBCOD": "KOT_CULTUURCODEONBEBOUWD_CODE",
            "CULTONBOMS": "KOT_CULTUURCODEONBEBOUWD_OMS",
            "CULTBCOD": "KOT_CULTUURCODEBEBOUWD_CODE",
            "CULTBOMS": "KOT_CULTUURCODEBEBOUWD_OMS",
            "AKRREG9T": "KOT_AKRREGISTER9TEKST",
            "STATUSCOD": "KOT_STATUS_CODE",
            "TOESTD_DAT": self.toestd_dat,
            "VL_KGR_IND": "KOT_IND_VOORLOPIGE_KADGRENS",
            "INONDERZK": self.inonderzk,
        }


class PerceelnummerEsriFormat:
    def format_rotation(self, value):
        """Return rotation with three decimal places."""
        assert isinstance(value, (int, float))
        return f"{value:.3f}"

    def get_format(self):
        """Kadastraleobjecten Perceelnummer ESRI format dictionary."""
        return {
            "BRK_KOT_ID": "identificatie",
            "GEMEENTE": "aangeduidDoorBrkGemeente.naam",
            "KADGEMCODE": "aangeduidDoorBrkKadastralegemeentecode.identificatie",
            "KADGEM": "aangeduidDoorBrkKadastralegemeente.identificatie",
            "SECTIE": "aangeduidDoorBrkKadastralesectie.code",
            "PERCEELNR": "perceelnummer",
            "INDEXLTR": "indexletter",
            "INDEXNR": "indexnummer",
            "ROTATIE": {
                "condition": "isempty",
                "reference": "perceelnummerRotatie",
                "falseval": {
                    "action": "format",
                    "formatter": self.format_rotation,
                    "value": "perceelnummerRotatie",
                },
                "trueval": {
                    "action": "literal",
                    "value": "0.000",
                },
            },
            "geometrie": {
                "action": "format",
                "formatter": format_geometry,
                "value": "plaatscoordinaten",
            },
        }


class KadastraleobjectenExportConfig:
    """Kadastraleobjecten export configuration."""

    brk2_bag_format = Brk2BagCsvFormat()
    brk2_bag_query = """
{
  brk2Kadastraleobjecten {
    edges {
      node {
        identificatie
        aangeduidDoorBrkKadastralegemeentecode {
          edges {
            node {
              identificatie
              code
            }
          }
        }
        aangeduidDoorBrkKadastralegemeente {
          edges {
            node {
              identificatie
              code
            }
          }
        }
        aangeduidDoorBrkKadastralesectie {
          edges {
            node {
              code
            }
          }
        }
        perceelnummer
        indexletter
        indexnummer
        heeftEenRelatieMetBagVerblijfsobject {
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
"""

    esri_format_no_subjects = KadastraleobjectenEsriNoSubjectsFormat()
    esri_query = """
{
  brk2Kadastraleobjecten(indexletter:"G") {
    edges {
      node {
        identificatie
        volgnummer
        aangeduidDoorBrkGemeente {
          edges {
            node {
              naam
            }
          }
        }
        aangeduidDoorBrkKadastralegemeentecode {
          edges {
            node {
              identificatie
              code
            }
          }
        }
        aangeduidDoorBrkKadastralegemeente {
          edges {
            node {
              identificatie
              code
            }
          }
        }
        aangeduidDoorBrkKadastralesectie {
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
        isOntstaanUitBrkGPerceel {
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
        toestandsdatum
        indicatieVoorlopigeKadastraleGrens
        inOnderzoek
        geometrie
        invRustOpBrkKadastraalObjectBrk2Zakelijkerechten(akrAardZakelijkRecht:"VE") {
          edges {
            node {
              identificatie
              aardZakelijkRecht
              vveIdentificatieBetrokkenBij {
                edges {
                  node {
                    identificatie
                    statutaireNaam
                    typeSubject
                    heeftRsinVoorHrNietNatuurlijkepersoon
                    heeftKvknummerVoorHrMaatschappelijkeactiviteit
                    heeftBsnVoorBrpPersoon
                    rechtsvorm
                    statutaireNaam
                    statutaireZetel
                  }
                }
              }
              invVanBrkZakelijkRechtBrk2Tenaamstellingen {
                edges {
                  node {
                    aandeel
                    vanBrkKadastraalsubject {
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
                          heeftRsinVoorHrNietNatuurlijkepersoon
                          heeftKvknummerVoorHrMaatschappelijkeactiviteit
                          heeftBsnVoorBrpPersoon
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
"""

    bijpijling_query = """
{
  brk2Kadastraleobjecten(indexletter:"G") {
    edges {
      node {
        identificatie
        aangeduidDoorBrkGemeente {
          edges {
            node {
              naam
            }
          }
        }
        aangeduidDoorBrkKadastralegemeentecode {
          edges {
            node {
              identificatie
              code
            }
          }
        }
        aangeduidDoorBrkKadastralegemeente {
          edges {
            node {
              identificatie
              code
            }
          }
        }
        aangeduidDoorBrkKadastralesectie {
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
"""

    perceelnummer_esri_format = PerceelnummerEsriFormat()
    perceelnummer_query = """
{
  brk2Kadastraleobjecten(indexletter: "G") {
    edges {
      node {
        identificatie
        aangeduidDoorBrkGemeente {
          edges {
            node {
              naam
            }
          }
        }
        aangeduidDoorBrkKadastralegemeentecode {
          edges {
            node {
              identificatie
              code
            }
          }
        }
        aangeduidDoorBrkKadastralegemeente {
          edges {
            node {
              identificatie
              code
            }
          }
        }
        aangeduidDoorBrkKadastralesectie {
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
"""

    class VotFilter(EntityFilter):
        """Only include rows if vot identificatie is not set and city is not Amsterdam or Weesp."""

        vot_identificatie = "heeftEenRelatieMetBagVerblijfsobject.[0].identificatie"
        city = "heeftEenRelatieMetBagVerblijfsobject.[0].broninfo.woonplaatsnaam"

        def filter(self, entity: dict):
            if not get_entity_value(entity, self.vot_identificatie) and get_entity_value(entity, self.city):
                return not get_entity_value(entity, self.city).lower().startswith(("amsterdam", "weesp"))

            return True

    sort = {
        "invRustOpBrkKadastraalObjectBrk2Zakelijkerechten"
        ".invVanBrkZakelijkRechtBrk2Tenaamstellingen"
        ".aandeel": aandeel_sort,
        "invRustOpBrkKadastraalObjectBrk2Zakelijkerechten"
        ".invVanBrkZakelijkRechtBrk2Tenaamstellingen"
        ".vanBrkKadastraalsubject"
        ".identificatie":
        # Take subject ID with highest number (which is the last part of the . separated string)
        lambda x, y: int(x.split(".")[-1]) > int(y.split(".")[-1]),
    }

    products = {
        "brk2_bag_csv": {
            "exporter": csv_exporter,
            "entity_filters": [
                NotEmptyFilter("heeftEenRelatieMetBagVerblijfsobject.[0].bronwaarde"),
                VotFilter(),
            ],
            "api_type": "graphql_streaming",
            "secure_user": "gob",
            "unfold": True,
            "query": brk2_bag_query,
            "filename": lambda: brk2_filename("BRK_BAG", use_sensitive_dir=False),
            "mime_type": "text/csv",
            "format": brk2_bag_format.get_format(),
        },
        "kot_esri_actueel_no_subjects": {
            "exporter": esri_exporter,
            "api_type": "graphql_streaming",
            "secure_user": "gob",
            "query": esri_query,
            "filename": (f"{brk2_directory('shp', use_sensitive_dir=False)}" "/BRK_Adam_totaal_G_zonderSubjecten.shp"),
            "mime_type": "application/octet-stream",
            "format": esri_format_no_subjects.get_format(),
            "extra_files": [
                {
                    "filename": (
                        f'{brk2_directory("dbf", use_sensitive_dir=False)}' "/BRK_Adam_totaal_G_zonderSubjecten.dbf"
                    ),
                    "mime_type": "application/octet-stream",
                },
                {
                    "filename": (
                        f'{brk2_directory("shx", use_sensitive_dir=False)}' "/BRK_Adam_totaal_G_zonderSubjecten.shx"
                    ),
                    "mime_type": "application/octet-stream",
                },
                {
                    "filename": (
                        f'{brk2_directory("prj", use_sensitive_dir=False)}' "/BRK_Adam_totaal_G_zonderSubjecten.prj"
                    ),
                    "mime_type": "application/octet-stream",
                },
                {
                    "filename": (
                        f'{brk2_directory("cpg", use_sensitive_dir=False)}' "/BRK_Adam_totaal_G_zonderSubjecten.cpg"
                    ),
                    "mime_type": "application/octet-stream",
                },
            ],
        },
        "bijpijling_shape": {
            "exporter": esri_exporter,
            "api_type": "graphql_streaming",
            "secure_user": "gob",
            "filename": f'{brk2_directory("shp", use_sensitive_dir=False)}/BRK_bijpijling.shp',
            "entity_filters": [
                NotEmptyFilter("bijpijlingGeometrie"),
            ],
            "mime_type": "application/octet-stream",
            "format": {
                "BRK_KOT_ID": "identificatie",
                "GEMEENTE": "aangeduidDoorBrkGemeente.naam",
                "KADGEMCODE": "aangeduidDoorBrkKadastralegemeentecode.identificatie",
                "KADGEM": "aangeduidDoorBrkKadastralegemeente.identificatie",
                "SECTIE": "aangeduidDoorBrkKadastralesectie.code",
                "PERCEELNR": "perceelnummer",
                "INDEXLTR": "indexletter",
                "INDEXNR": "indexnummer",
                "geometrie": {
                    "action": "format",
                    "formatter": format_geometry,
                    "value": "bijpijlingGeometrie",
                },
            },
            "extra_files": [
                {
                    "filename": (f'{brk2_directory("dbf", use_sensitive_dir=False)}/BRK_bijpijling.dbf'),
                    "mime_type": "application/octet-stream",
                },
                {
                    "filename": (f'{brk2_directory("shx", use_sensitive_dir=False)}/BRK_bijpijling.shx'),
                    "mime_type": "application/octet-stream",
                },
                {
                    "filename": (f'{brk2_directory("prj", use_sensitive_dir=False)}/BRK_bijpijling.prj'),
                    "mime_type": "application/octet-stream",
                },
                {
                    "filename": (f'{brk2_directory("cpg", use_sensitive_dir=False)}/BRK_bijpijling.cpg'),
                    "mime_type": "application/octet-stream",
                },
            ],
            "query": bijpijling_query,
        },
        "perceel_shape": {
            "exporter": esri_exporter,
            "api_type": "graphql_streaming",
            "secure_user": "gob",
            "filename": f'{brk2_directory("shp", use_sensitive_dir=False)}/BRK_perceelnummer.shp',
            "entity_filters": [
                NotEmptyFilter("plaatscoordinaten"),
            ],
            "mime_type": "application/octet-stream",
            "format": perceelnummer_esri_format.get_format(),
            "extra_files": [
                {
                    "filename": (f'{brk2_directory("dbf", use_sensitive_dir=False)}/BRK_perceelnummer.dbf'),
                    "mime_type": "application/octet-stream",
                },
                {
                    "filename": (f'{brk2_directory("shx", use_sensitive_dir=False)}/BRK_perceelnummer.shx'),
                    "mime_type": "application/octet-stream",
                },
                {
                    "filename": (f'{brk2_directory("prj", use_sensitive_dir=False)}/BRK_perceelnummer.prj'),
                    "mime_type": "application/octet-stream",
                },
                {
                    "filename": (f'{brk2_directory("cpg", use_sensitive_dir=False)}/BRK_perceelnummer.cpg'),
                    "mime_type": "application/octet-stream",
                },
            ],
            "query": perceelnummer_query,
        },
    }
