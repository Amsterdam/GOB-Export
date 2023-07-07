from typing import Any

from gobexport.exporter.config.brk2.utils import brk2_filename
from gobexport.exporter.csv import csv_exporter
from gobexport.exporter.shared.brk import format_timestamp
from gobexport.exporter.shared.zakelijkerechten import ZakelijkerechtenCsvFormat
from gobexport.filters.notempty_filter import NotEmptyFilter


class Brk2ZakelijkRechtCsvFormat(ZakelijkerechtenCsvFormat):

    asg_vve_key = 'vveIdentificatieBetrokkenBij'
    tng_key = 'invVanBrkZakelijkRechtBrk2Tenaamstellingen'
    sjt_key = 'vanBrkKadastraalsubject'
    rsin_key = 'heeftKvknummerVoorHrMaatschappelijkeactiviteit'
    kvk_key = 'heeftRsinVoorHrNietNatuurlijkepersoon'

    def get_format(self) -> dict[str, Any]:
        return {
            "BRK_ZRT_ID": "identificatie",
            "ZRT_AARDZAKELIJKRECHT_CODE": "aardZakelijkRecht.code",
            "ZRT_AARDZAKELIJKRECHT_OMS": "aardZakelijkRecht.omschrijving",
            "ZRT_AARDZAKELIJKRECHT_AKR_CODE": "akrAardZakelijkRecht",
            "ZRT_BELAST_AZT": "belastAzt",
            "ZRT_BELAST_MET_AZT": "belastMetAzt",
            "ZRT_ONTSTAAN_UIT": "vveIdentificatieOntstaanUit.[0].identificatie",
            "ZRT_BETROKKEN_BIJ": "betrokkenBij",
            "ZRT_ISBEPERKT_TOT_TNG": "",  # not available in brk2
            "ZRT_BETREKKING_OP_KOT": {
                "action": "concat",
                "fields": [
                    "aangeduidDoorBrkKadastralegemeentecode.[0].identificatie",
                    {
                        "action": "literal",
                        "value": "-"
                    },
                    "aangeduidDoorBrkKadastralesectie.[0].code",
                    {
                        "action": "literal",
                        "value": "-"
                    },
                    {
                        "action": "fill",
                        "length": 5,
                        "character": "0",
                        "value": "rustOpBrkKadastraalObject.[0].perceelnummer",
                        "fill_type": "rjust",
                    },
                    {
                        "action": "literal",
                        "value": "-"
                    },
                    "rustOpBrkKadastraalObject.[0].indexletter",
                    {
                        "action": "literal",
                        "value": "-"
                    },
                    {
                        "action": "fill",
                        "length": 4,
                        "character": "0",
                        "value": "rustOpBrkKadastraalObject.[0].indexnummer",
                        "fill_type": "rjust",
                    }
                ]
            },
            "BRK_KOT_ID": "rustOpBrkKadastraalObject.[0].identificatie",
            "KOT_STATUS_CODE": {
                "condition": "isempty",
                "reference": "rustOpBrkKadastraalObject.[0].identificatie",
                "negate": True,
                "trueval": {
                    "action": "literal",
                    "value": "B",
                },
            },
            "KOT_MODIFICATION": "",
            "BRK_TNG_ID": "invVanBrkZakelijkRechtBrk2Tenaamstellingen.[0].identificatie",
            "TNG_AANDEEL_TELLER": "invVanBrkZakelijkRechtBrk2Tenaamstellingen.[0].aandeel.teller",
            "TNG_AANDEEL_NOEMER": "invVanBrkZakelijkRechtBrk2Tenaamstellingen.[0].aandeel.noemer",
            "TNG_EINDDATUM": {
                "action": "format",
                "formatter": format_timestamp,
                "value": "invVanBrkZakelijkRechtBrk2Tenaamstellingen.[0].eindGeldigheid",
            },
            "TNG_ACTUEEL": {
                "condition": "isempty",
                "reference": "invVanBrkZakelijkRechtBrk2Tenaamstellingen.[0].identificatie",
                "negate": True,
                "trueval": {
                    "action": "literal",
                    "value": "TRUE",
                },
            },
            "ASG_APP_RECHTSPLITSTYPE_CODE": "appartementsrechtsplitsingType.code",
            "ASG_APP_RECHTSPLITSTYPE_OMS": "appartementsrechtsplitsingType.omschrijving",
            "ASG_EINDDATUM": "",  # Always empty
            "ASG_ACTUEEL": "TRUE",  # Always True
            "BRK_SJT_ID": self.if_vve(
                trueval="vveIdentificatieBetrokkenBij.[0].identificatie",
                falseval="vanBrkKadastraalsubject.[0].identificatie",
            ),
            "SJT_BSN": "",
            "SJT_BESCHIKKINGSBEVOEGDH_CODE": self.if_vve(
                trueval="vveIdentificatieBetrokkenBij.[0].beschikkingsbevoegdheid.code",
                falseval="vanBrkKadastraalsubject.[0].beschikkingsbevoegdheid.code",
            ),
            "SJT_BESCHIKKINGSBEVOEGDH_OMS": self.if_vve(
                trueval="vveIdentificatieBetrokkenBij.[0].beschikkingsbevoegdheid.omschrijving",
                falseval="vanBrkKadastraalsubject.[0].beschikkingsbevoegdheid.omschrijving",
            ),
            "SJT_NAAM": self.if_vve(
                trueval="vveIdentificatieBetrokkenBij.[0].statutaireNaam",
                falseval={
                    "condition": "isempty",
                    "reference": "vanBrkKadastraalsubject.[0].statutaireNaam",
                    "trueval": {
                        "action": "concat",
                        "fields": [
                            "vanBrkKadastraalsubject.[0].geslachtsnaam",
                            {
                                "action": "literal",
                                "value": ","
                            },
                            "vanBrkKadastraalsubject.[0].voornamen",
                            {
                                "action": "literal",
                                "value": ","
                            },
                            "vanBrkKadastraalsubject.[0].voorvoegsels",
                            {
                                "action": "literal",
                                "value": " ("
                            },
                            "vanBrkKadastraalsubject.[0].geslacht.code",
                            {
                                "action": "literal",
                                "value": ")"
                            },
                        ]
                    },
                    "falseval": "vanBrkKadastraalsubject.[0].statutaireNaam"
                }
            ),
            **self._get_np_attrs(),
            **self._get_nnp_attrs(),
        }


class ZakelijkerechtenExportConfig:
    format = Brk2ZakelijkRechtCsvFormat()

    query = '''
{
  brk2Zakelijkerechten {
    edges {
      node {
        identificatie
        aardZakelijkRecht
        akrAardZakelijkRecht
        belastZrt1: belastBrkZakelijkeRechten {
          edges {
            node {
              akrAardZakelijkRecht
              belastZrt2: belastBrkZakelijkeRechten {
                edges {
                  node {
                    akrAardZakelijkRecht
                    belastZrt3: belastBrkZakelijkeRechten {
                      edges {
                        node {
                          akrAardZakelijkRecht
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
        belastMetZrt1: belastMetBrkZakelijkeRechten {
          edges {
            node {
              akrAardZakelijkRecht
              belastMetZrt2: belastMetBrkZakelijkeRechten {
                edges {
                  node {
                    akrAardZakelijkRecht
                    belastMetZrt3: belastMetBrkZakelijkeRechten {
                      edges {
                        node {
                          akrAardZakelijkRecht
                          belastMetZrt4: belastMetBrkZakelijkeRechten {
                            edges {
                              node {
                                akrAardZakelijkRecht
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
        vveIdentificatieOntstaanUit {
          edges {
            node {
              identificatie
            }
          }
        }
        vveIdentificatieBetrokkenBij {
          edges {
            node {
              identificatie
              rechtsvorm
              statutaireNaam
              statutaireZetel
              heeftKvknummerVoorHrMaatschappelijkeactiviteit
              heeftRsinVoorHrNietNatuurlijkepersoon
              beschikkingsbevoegdheid
            }
          }
        }
        rustOpBrkKadastraalObject {
          edges {
            node {
              perceelnummer
              indexletter
              indexnummer
              identificatie
              aangeduidDoorBrkKadastralegemeentecode {
                edges {
                  node {
                    identificatie
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
            }
          }
        }
        appartementsrechtsplitsingType
        invVanBrkZakelijkRechtBrk2Tenaamstellingen {
          edges {
            node {
              identificatie
              aandeel
              eindGeldigheid
              vanBrkKadastraalsubject {
                edges {
                  node {
                    identificatie
                    beschikkingsbevoegdheid
                    geslachtsnaam
                    voornamen
                    geslacht
                    voorvoegsels
                    geboortedatum
                    geboorteplaats
                    geboorteland
                    datumOverlijden
                    rechtsvorm
                    statutaireNaam
                    statutaireZetel
                    heeftBsnVoorBrpPersoon
                    heeftKvknummerVoorHrMaatschappelijkeactiviteit
                    heeftRsinVoorHrNietNatuurlijkepersoon
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
        'csv': {
            'exporter': csv_exporter,
            'api_type': 'graphql_streaming',
            'secure_user': 'gob',
            'unfold': True,
            'row_formatter': format.row_formatter,
            'entity_filters': [
                NotEmptyFilter(
                    f'{format.tng_key}.[0].identificatie',
                    f'{format.asg_vve_key}.[0].identificatie'
                ),
            ],
            'query': query,
            'filename': lambda: brk2_filename("zakelijk_recht", use_sensitive_dir=True),
            'mime_type': 'plain/text',
            'format': format.get_format(),
        }
    }
