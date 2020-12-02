import copy

from gobexport.exporter.csv import csv_exporter
from gobexport.filters.notempty_filter import NotEmptyFilter
from gobexport.exporter.config.brk.csv_format import BrkCsvFormat
from gobexport.exporter.config.brk.utils import brk_filename, format_timestamp


class ZakelijkerechtenCsvFormat(BrkCsvFormat):

    def if_vve(self, trueval, falseval):
        return {
            'condition': 'isempty',
            'reference': 'betrokkenBijAppartementsrechtsplitsingVve.[0].identificatie',
            'negate': True,
            'trueval': trueval,
            'falseval': falseval,
        }

    def zrt_belast_met_azt_valuebuilder(self, entity: dict):
        take = [
            ('belastMetZrt1', 'akrAardZakelijkRecht'),
            ('belastMetZrt2', 'akrAardZakelijkRecht'),
            ('belastMetZrt3', 'akrAardZakelijkRecht'),
            ('belastMetZrt4', 'akrAardZakelijkRecht'),
        ]

        values = self._take_nested(take, entity)
        return self._format_azt_values(values)

    def zrt_belast_azt_valuebuilder(self, entity: dict):
        take = [
            ('belastZrt1', 'akrAardZakelijkRecht'),
            ('belastZrt2', 'akrAardZakelijkRecht'),
            ('belastZrt3', 'akrAardZakelijkRecht'),
        ]
        values = self._take_nested(take, entity)
        return self._format_azt_values(values)

    def _take_nested(self, take, entity, depth=0):
        """Takes values from nested structure with relations. Serves as input for _format_azt_values

        Take is a list of 2-tuples (relation, fieldname). The list follows the relations hierarchy and the name of the
        field to extract from that level.

        Returns a structure of values as they appear in the take list, as a list of lists. In each list the first item
        is the value of the requested field. The subsequent items are lists for each next nested relation as requested
        in take.

        Example:

        entity = {
            relA: [{
              'fieldA': 'valA',
              'relB': [
                {
                    'fieldB': 'valB1',
                    'relC': [
                        {'fieldC': 'valC1'
                    ]
                },
                {
                    'fieldB': 'valB2'
                }
              ]
            }]
        }

        take = [
            ('relA', 'fieldA'),
            ('relB', 'fieldB'),
            ('relC', 'fieldC'),
        ]

        result = [
            ['valA', ['valB1', ['valC1']], ['valB2']]
        ]

        :param take:
        :param entity:
        :param depth:
        :return:
        """
        result = []
        node = entity.get('node')

        if depth > 0:
            # Add value of requested field to result
            field = take[depth - 1][1]
            value = node.get(field)
            result = [value] if value else []

        if depth < len(take):
            relation = take[depth][0]

            if relation in node and len(node[relation]['edges']) > 0:
                # Add any nested relations as list to result
                result += [self._take_nested(take, e, depth + 1) for e in node[relation]['edges']]

        return result

    def _flatten_list(self, l: list):
        flatlist = []

        for item in l:
            if isinstance(item, list):
                flatlist.extend(self._flatten_list(item))
            else:
                flatlist.append(item)
        return flatlist

    def _is_complex_branch(self, branch: list):
        """A branch is considered complex if it contains any further branches

        For example:

        branch = ['valA', ['valB1', ['valC1']], ['valB2']]

        is considered complex, as at the outermost list is of length 3; there are two branches, one with valB1 and one
        with valB2.

        branch = ['valA', ['valB1', ['valC1', ['valD1']]]]

        is not considered complex, as each item in the branch has only one child.

        :param branch:
        :return:
        """
        return len(branch) > 2 or any(
            self._is_complex_branch(subbranch) for subbranch in branch if isinstance(subbranch, list)
        )

    def _format_branch(self, branch: list):
        """Formats a branch. Nested items in the branch are separated by a "-". If at some level the branch branches
        again, this branch is considered "complex". For a complex branch an "*" is added.

        :param branch:
        :return:
        """
        return f'[{"* " if self._is_complex_branch(branch) else ""}{"-".join(self._flatten_list(branch))}]'

    def _format_azt_values(self, values: list):
        """Separates branches bij the "+" character.

        :param values:
        :return:
        """
        return "+".join([self._format_branch(branch) for branch in values])

    def _get_np_attrs(self):
        attrs = {
            'SJT_NP_GEBOORTEDATUM': 'vanKadastraalsubject.[0].geboortedatum',
            'SJT_NP_GEBOORTEPLAATS': 'vanKadastraalsubject.[0].geboorteplaats',
            'SJT_NP_GEBOORTELAND_CODE': 'vanKadastraalsubject.[0].geboorteland.code',
            'SJT_NP_GEBOORTELAND_OMS': 'vanKadastraalsubject.[0].geboorteland.omschrijving',
            'SJT_NP_DATUMOVERLIJDEN': 'vanKadastraalsubject.[0].datumOverlijden',
        }

        return self._add_condition_to_attrs(
            self.show_when_field_empty_condition("vanKadastraalsubject.[0].statutaireNaam"),
            attrs,
        )

    def _get_nnp_attrs(self):

        attrs = {
            'SJT_NNP_RSIN': self.if_vve(
                trueval='betrokkenBijAppartementsrechtsplitsingVve.[0].heeftRsinVoor.bronwaarde',
                falseval='vanKadastraalsubject.[0].heeftRsinVoor.bronwaarde'
            ),
            'SJT_NNP_KVKNUMMER': self.if_vve(
                trueval='betrokkenBijAppartementsrechtsplitsingVve.[0].heeftKvknummerVoor.bronwaarde',
                falseval='vanKadastraalsubject.[0].heeftKvknummerVoor.bronwaarde'
            ),
            'SJT_NNP_RECHTSVORM_CODE': self.if_vve(
                trueval='betrokkenBijAppartementsrechtsplitsingVve.[0].rechtsvorm.code',
                falseval='vanKadastraalsubject.[0].rechtsvorm.code'
            ),
            'SJT_NNP_RECHTSVORM_OMS': self.if_vve(
                trueval='betrokkenBijAppartementsrechtsplitsingVve.[0].rechtsvorm.omschrijving',
                falseval='vanKadastraalsubject.[0].rechtsvorm.omschrijving'
            ),
            'SJT_NNP_STATUTAIRE_NAAM': self.if_vve(
                trueval='betrokkenBijAppartementsrechtsplitsingVve.[0].statutaireNaam',
                falseval='vanKadastraalsubject.[0].statutaireNaam'
            ),
            'SJT_NNP_STATUTAIRE_ZETEL': self.if_vve(
                trueval='betrokkenBijAppartementsrechtsplitsingVve.[0].statutaireZetel',
                falseval='vanKadastraalsubject.[0].statutaireZetel'
            )
        }

        return attrs

    def row_formatter(self, row):
        """Performs actions:
        1. Creates belastMet and belast keys in row from belastMetZrtN and belastZrtN relations.
        2. Creates betrokkenBij key
        3. Creates separate rows for TNG relations and VVE relations (so that TNG data is not linked with VVE data in
        the export)

        :param row:
        :return:
        """
        row['node']['belastMetAzt'] = self.zrt_belast_met_azt_valuebuilder(row)
        row['node']['belastAzt'] = self.zrt_belast_azt_valuebuilder(row)

        if 'belastMetZrt1' in row['node']:
            del row['node']['belastMetZrt1']

        if 'belastZrt1' in row['node']:
            del row['node']['belastZrt1']

        asg_vve_key = 'betrokkenBijAppartementsrechtsplitsingVve'
        tng_key = 'invVanZakelijkrechtBrkTenaamstellingen'

        # Set betrokkenBij
        if asg_vve_key in row['node'] and len(row['node'][asg_vve_key]['edges']):
            row['node']['betrokkenBij'] = row['node'][asg_vve_key]['edges'][0]['node']['identificatie']
        else:
            row['node']['betrokkenBij'] = None

        if asg_vve_key in row['node'] and tng_key in row['node'] and \
                len(row['node'][asg_vve_key]['edges']) and len(row['node'][tng_key]['edges']):
            # Both relations asg_vve_key and tng_key exist in row. Split row into two rows, with in one row only the
            # asg objects and the other row with only the tng objects.
            asg_row = copy.deepcopy(row)
            asg_row['node'][asg_vve_key]['edges'] = []

            row['node'][tng_key]['edges'] = []

            return [row, asg_row]

        return row

    def get_format(self):

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
    format = ZakelijkerechtenCsvFormat()

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
            'filename': lambda: brk_filename("zakelijk_recht"),
            'mime_type': 'plain/text',
            'format': format.get_format(),
        }
    }
