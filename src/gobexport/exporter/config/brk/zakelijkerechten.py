from typing import Any

from gobexport.exporter.config.brk.utils import brk_filename
from gobexport.exporter.csv import csv_exporter
from gobexport.exporter.shared.brk import format_timestamp
from gobexport.exporter.shared.zakelijkerechten import ZakelijkerechtenCsvFormat
from gobexport.filters.notempty_filter import NotEmptyFilter


class BrkZakelijkRechtCsvFormat(ZakelijkerechtenCsvFormat):

    asg_vve_key = 'betrokkenBijAppartementsrechtsplitsingVve'
    tng_key = 'invVanZakelijkrechtBrkTenaamstellingen'
    sjt_key = 'vanKadastraalsubject'
    rsin_key = 'heeftRsinVoor.bronwaarde'  # defined as relation
    kvk_key = 'heeftKvknummerVoor.bronwaarde'  # defined as relation

    def get_format(self) -> dict[str, Any]:
        return {
            'BRK_ZRT_ID': 'identificatie',
            'ZRT_AARDZAKELIJKRECHT_CODE': 'aardZakelijkRecht.code',
            'ZRT_AARDZAKELIJKRECHT_OMS': 'aardZakelijkRecht.omschrijving',
            'ZRT_AARDZAKELIJKRECHT_AKR_CODE': 'akrAardZakelijkRecht',
            'ZRT_BELAST_AZT': 'belastAzt',
            'ZRT_BELAST_MET_AZT': 'belastMetAzt',
            'ZRT_ONTSTAAN_UIT': 'ontstaanUitAppartementsrechtsplitsingVve.[0].identificatie',
            'ZRT_BETROKKEN_BIJ': 'betrokkenBij',
            'ZRT_ISBEPERKT_TOT_TNG': 'isBeperktTot',
            'ZRT_BETREKKING_OP_KOT': {
                'action': 'concat',
                'fields': [
                    'aangeduidDoorKadastralegemeentecode.[0].broninfo.omschrijving',
                    {
                        'action': 'literal',
                        'value': '-'
                    },
                    'aangeduidDoorKadastralesectie.[0].code',
                    {
                        'action': 'literal',
                        'value': '-'
                    },
                    {
                        'action': 'fill',
                        'length': 5,
                        'character': '0',
                        'value': 'rustOpKadastraalobject.[0].perceelnummer',
                        'fill_type': 'rjust',
                    },
                    {
                        'action': 'literal',
                        'value': '-'
                    },
                    'rustOpKadastraalobject.[0].indexletter',
                    {
                        'action': 'literal',
                        'value': '-'
                    },
                    {
                        'action': 'fill',
                        'length': 4,
                        'character': '0',
                        'value': 'rustOpKadastraalobject.[0].indexnummer',
                        'fill_type': 'rjust',
                    }
                ]
            },
            'BRK_KOT_ID': 'rustOpKadastraalobject.[0].identificatie',
            'KOT_STATUS_CODE': 'rustOpKadastraalobject.[0].status',
            'KOT_MODIFICATION': '',
            'BRK_TNG_ID': 'invVanZakelijkrechtBrkTenaamstellingen.[0].identificatie',
            'TNG_AANDEEL_TELLER': 'invVanZakelijkrechtBrkTenaamstellingen.[0].aandeel.teller',
            'TNG_AANDEEL_NOEMER': 'invVanZakelijkrechtBrkTenaamstellingen.[0].aandeel.noemer',
            'TNG_EINDDATUM': {
                'action': 'format',
                'formatter': format_timestamp,
                'value': 'invVanZakelijkrechtBrkTenaamstellingen.[0].eindGeldigheid',
            },
            'TNG_ACTUEEL': {
                'condition': 'isempty',
                'reference': 'invVanZakelijkrechtBrkTenaamstellingen.[0].identificatie',
                'negate': True,
                'trueval': {
                    'action': 'literal',
                    'value': 'TRUE',
                },
            },
            'ASG_APP_RECHTSPLITSTYPE_CODE': 'appartementsrechtsplitsingtype.code',
            'ASG_APP_RECHTSPLITSTYPE_OMS': 'appartementsrechtsplitsingtype.omschrijving',
            'ASG_EINDDATUM': 'einddatumAppartementsrechtsplitsing',
            'ASG_ACTUEEL': 'indicatieActueelAppartementsrechtsplitsing',
            'BRK_SJT_ID': self.if_vve(
                trueval='betrokkenBijAppartementsrechtsplitsingVve.[0].identificatie',
                falseval='vanKadastraalsubject.[0].identificatie',
            ),
            'SJT_BSN': '',
            'SJT_BESCHIKKINGSBEVOEGDH_CODE': self.if_vve(
                trueval='betrokkenBijAppartementsrechtsplitsingVve.[0].beschikkingsbevoegdheid.code',
                falseval='vanKadastraalsubject.[0].beschikkingsbevoegdheid.code',
            ),
            'SJT_BESCHIKKINGSBEVOEGDH_OMS': self.if_vve(
                trueval='betrokkenBijAppartementsrechtsplitsingVve.[0].beschikkingsbevoegdheid.omschrijving',
                falseval='vanKadastraalsubject.[0].beschikkingsbevoegdheid.omschrijving',
            ),
            'SJT_NAAM': self.if_vve(
                trueval='betrokkenBijAppartementsrechtsplitsingVve.[0].statutaireNaam',
                falseval={
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
            ),
            **self._get_np_attrs(),
            **self._get_nnp_attrs(),
        }


class ZakelijkerechtenExportConfig:
    format = BrkZakelijkRechtCsvFormat()

    query = '''
{
  brkZakelijkerechten {
    edges {
      node {
        identificatie
        aardZakelijkRecht
        akrAardZakelijkRecht
        belastZrt1: belastZakelijkerechten {
          edges {
            node {
              akrAardZakelijkRecht
              belastZrt2: belastZakelijkerechten {
                edges {
                  node {
                    akrAardZakelijkRecht
                    belastZrt3: belastZakelijkerechten {
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
        belastMetZrt1: belastMetZakelijkerechten {
          edges {
            node {
              akrAardZakelijkRecht
              belastMetZrt2: belastMetZakelijkerechten {
                edges {
                  node {
                    akrAardZakelijkRecht
                    belastMetZrt3: belastMetZakelijkerechten {
                      edges {
                        node {
                          akrAardZakelijkRecht
                          belastMetZrt4: belastMetZakelijkerechten {
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
        ontstaanUitAppartementsrechtsplitsingVve {
          edges {
            node {
              identificatie
            }
          }
        }
        betrokkenBijAppartementsrechtsplitsingVve {
          edges {
            node {
              identificatie
              rechtsvorm
              statutaireNaam
              statutaireZetel
              heeftKvknummerVoor
              heeftRsinVoor
              beschikkingsbevoegdheid
            }
          }
        }
        isBeperktTot
        rustOpKadastraalobject {
          edges {
            node {
              perceelnummer
              indexletter
              indexnummer
              identificatie
              status
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
            }
          }
        }
        appartementsrechtsplitsingtype
        einddatumAppartementsrechtsplitsing
        indicatieActueelAppartementsrechtsplitsing
        invVanZakelijkrechtBrkTenaamstellingen {
          edges {
            node {
              identificatie
              aandeel
              eindGeldigheid
              vanKadastraalsubject {
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
                    heeftBsnVoor
                    heeftKvknummerVoor
                    heeftRsinVoor
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
                NotEmptyFilter('invVanZakelijkrechtBrkTenaamstellingen.[0].identificatie',
                               'betrokkenBijAppartementsrechtsplitsingVve.[0].identificatie'),
            ],
            'query': query,
            'filename': lambda: brk_filename("zakelijk_recht", use_sensitive_dir=True),
            'mime_type': 'plain/text',
            'format': format.get_format(),
        }
    }
