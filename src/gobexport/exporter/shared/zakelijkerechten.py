import copy
from abc import abstractmethod
from typing import Any

from gobexport.exporter.shared.brk import BrkCsvFormat


class ZakelijkerechtenCsvFormat(BrkCsvFormat):

    asg_vve_key: str
    tng_key: str
    sjt_key: str
    rsin_key: str
    kvk_key: str

    def if_vve(self, trueval, falseval):
        return {
            'condition': 'isempty',
            'reference': self.asg_vve_key + '.[0].identificatie',
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

    def _flatten_list(self, lst: list):
        flatlist = []

        for item in lst:
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
            'SJT_NP_GEBOORTEDATUM': f'{self.sjt_key}.[0].geboortedatum',
            'SJT_NP_GEBOORTEPLAATS': f'{self.sjt_key}.[0].geboorteplaats',
            'SJT_NP_GEBOORTELAND_CODE': f'{self.sjt_key}.[0].geboorteland.code',
            'SJT_NP_GEBOORTELAND_OMS': f'{self.sjt_key}.[0].geboorteland.omschrijving',
            'SJT_NP_DATUMOVERLIJDEN': f'{self.sjt_key}.[0].datumOverlijden',
        }

        return self._add_condition_to_attrs(
            self.show_when_field_empty_condition(f"{self.sjt_key}.[0].statutaireNaam"),
            attrs,
        )

    def _get_nnp_attrs(self):

        attrs = {
            'SJT_NNP_RSIN': self.if_vve(
                trueval=f'{self.asg_vve_key}.[0].{self.rsin_key}',
                falseval=f'{self.sjt_key}.[0].{self.rsin_key}'
            ),
            'SJT_NNP_KVKNUMMER': self.if_vve(
                trueval=f'{self.asg_vve_key}.[0].{self.kvk_key}',
                falseval=f'{self.sjt_key}.[0].{self.kvk_key}'
            ),
            'SJT_NNP_RECHTSVORM_CODE': self.if_vve(
                trueval=f'{self.asg_vve_key}.[0].rechtsvorm.code',
                falseval=f'{self.sjt_key}.[0].rechtsvorm.code'
            ),
            'SJT_NNP_RECHTSVORM_OMS': self.if_vve(
                trueval=f'{self.asg_vve_key}.[0].rechtsvorm.omschrijving',
                falseval=f'{self.sjt_key}.[0].rechtsvorm.omschrijving'
            ),
            'SJT_NNP_STATUTAIRE_NAAM': self.if_vve(
                trueval=f'{self.asg_vve_key}.[0].statutaireNaam',
                falseval=f'{self.sjt_key}.[0].statutaireNaam'
            ),
            'SJT_NNP_STATUTAIRE_ZETEL': self.if_vve(
                trueval=f'{self.asg_vve_key}.[0].statutaireZetel',
                falseval=f'{self.sjt_key}.[0].statutaireZetel'
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

        asg_vve_key = self.asg_vve_key
        tng_key = self.tng_key

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

    @abstractmethod
    def get_format(self) -> dict[str, Any]:  # pragma: no cover
        pass
