"""BRK2 kadastraleobjecten exports."""


from fractions import Fraction

from gobexport.exporter.config.brk2.utils import brk2_filename
from gobexport.exporter.csv import csv_exporter
from gobexport.exporter.utils import get_entity_value
from gobexport.filters.entity_filter import EntityFilter
from gobexport.filters.notempty_filter import NotEmptyFilter


class Brk2BagCsvFormat:
    """CSV format class for BRK2 BAG export."""

    def if_vot_relation(self, trueval: str, falseval: str):
        """BAG verblijfsobjecten (VOT) relation dictionary."""
        return {
            "condition": "isempty",
            "reference": "heeftEenRelatieMetVerblijfsobject.[0].identificatie",
            "negate": True,
            "trueval": trueval,
            "falseval": falseval,
        }

    def get_format(self):
        """BRK2 BAG CSV format dictionary."""
        return {
            "BRK_KOT_ID": "identificatie",
            "KOT_AKRKADGEMEENTECODE_CODE": "aangeduidDoorKadastralegemeentecode.code",
            "KOT_AKRKADGEMEENTECODE_OMS": "aangeduidDoorKadastralegemeentecode.omschrijving",
            "KOT_SECTIE": "aangeduidDoorKadastralesectie",
            "KOT_PERCEELNUMMER": "perceelnummer",
            "KOT_INDEX_LETTER": "indexletter",
            "KOT_INDEX_NUMMER": "indexnummer",
            "KOT_STATUS_CODE": "status",
            "KOT_MODIFICATION": "",
            "BAG_VOT_ID": "heeftEenRelatieMetVerblijfsobject.[0].bronwaarde",
            "BAG_VOT_STATUS": "heeftEenRelatieMetVerblijfsobject.[0].status.omschrijving",
            "DIVA_VOT_ID": "",
            "AOT_OPENBARERUIMTENAAM": self.if_vot_relation(
                trueval="ligtAanOpenbareruimte.naam",
                falseval="heeftEenRelatieMetVerblijfsobject.[0].broninfo.openbareruimtenaam",
            ),
            "AOT_HUISNUMMER": self.if_vot_relation(
                trueval="heeftHoofdadres.huisnummer",
                falseval="heeftEenRelatieMetVerblijfsobject.[0].broninfo.huisnummer",
            ),
            "AOT_HUISLETTER": self.if_vot_relation(
                trueval="heeftHoofdadres.huisletter",
                falseval="heeftEenRelatieMetVerblijfsobject.[0].broninfo.huisletter",
            ),
            "AOT_HUISNUMMERTOEVOEGING": self.if_vot_relation(
                trueval="heeftHoofdadres.huisnummertoevoeging",
                falseval="heeftEenRelatieMetVerblijfsobject.[0].broninfo.huisnummertoevoeging",
            ),
            "AOT_POSTCODE": self.if_vot_relation(
                trueval="heeftHoofdadres.postcode",
                falseval="heeftEenRelatieMetVerblijfsobject.[0].broninfo.postcode",
            ),
            "AOT_WOONPLAATSNAAM": self.if_vot_relation(
                trueval="heeftEenRelatieMetVerblijfsobject.[0].heeftHoofdadres.[0]."
                "ligtAanOpenbareruimte.[0].ligtInWoonplaats.[0].naam",
                falseval="heeftEenRelatieMetVerblijfsobject.[0].broninfo.woonplaatsnaam",
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


class KadastraleobjectenExportConfig:
    """Kadastraleobjecten export configuration."""

    brk2_bag_format = Brk2BagCsvFormat()
    brk2_bag_query = """
{
  brk2Kadastraleobjecten {
    edges {
      node {
        identificatie
        aangeduidDoorKadastralegemeente
        aangeduidDoorKadastralegemeentecode
        aangeduidDoorKadastralesectie
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
"""

    class VotFilter(EntityFilter):
        """Only include rows if vot identificatie is not set and city is not Amsterdam or Weesp."""

        vot_identificatie = "heeftEenRelatieMetVerblijfsobject.[0].identificatie"
        city = "heeftEenRelatieMetVerblijfsobject.[0].broninfo.woonplaatsnaam"

        def filter(self, entity: dict):
            if not get_entity_value(
                entity, self.vot_identificatie
            ) and get_entity_value(entity, self.city):
                return (
                    not get_entity_value(entity, self.city)
                    .lower()
                    .startswith(("amsterdam", "weesp"))
                )

            return True

    sort = {
        "invRustOpKadastraalobjectBrkZakelijkerechten"
        ".invVanZakelijkrechtBrkTenaamstellingen"
        ".aandeel": aandeel_sort,
        "invRustOpKadastraalobjectBrkZakelijkerechten"
        ".invVanZakelijkrechtBrkTenaamstellingen"
        ".vanKadastraalsubject"
        ".identificatie":
        # Take subject ID with highest number (which is the last part of the . separated string)
        lambda x, y: int(x.split(".")[-1]) > int(y.split(".")[-1]),
    }

    products = {
        "brk2_bag_csv": {
            "exporter": csv_exporter,
            "entity_filters": [
                NotEmptyFilter("heeftEenRelatieMetVerblijfsobject.[0].bronwaarde"),
                VotFilter(),
            ],
            "api_type": "graphql_streaming",
            "secure_user": "gob",
            "unfold": True,
            "query": brk2_bag_query,
            "filename": lambda: brk2_filename("BRK_BAG", use_sensitive_dir=False),
            "mime_type": "text/csv",
            "format": brk2_bag_format.get_format(),
        }
    }
