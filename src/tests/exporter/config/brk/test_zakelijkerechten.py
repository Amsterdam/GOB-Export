from unittest import TestCase

from gobexport.exporter.config.brk.zakelijkerechten import ZakelijkerechtenCsvFormat


class TestBrkZakelijkerechtenCsvFormat(TestCase):

    def setUp(self) -> None:
        self.format = ZakelijkerechtenCsvFormat()

    def test_take_nested(self):
        entity = {
            'node': {
                'relA': {
                    'edges': [
                        {
                            'node': {
                                'requestedFieldA': 'requestedValueA1',
                                'relB': {
                                    'edges': [
                                        {
                                            'node': {
                                                'requestedFieldB': 'requestedValueB1',
                                                'relC': {
                                                    'edges': [
                                                        {
                                                            'node': {
                                                                'requestedFieldC': 'requestedValueC1',
                                                            }
                                                        },
                                                    ]
                                                }
                                            },
                                        }
                                    ]
                                }
                            }
                        },
                        {
                            'node': {
                                'requestedFieldA': 'requestedValueA2',
                                'relB': {
                                    'edges': [
                                        {
                                            'node': {
                                                'requestedFieldB': 'requestedValueB2',
                                                'relC': {
                                                    'edges': [
                                                        {
                                                            'node': {
                                                                'requestedFieldC': 'requestedValueC2'
                                                            }
                                                        },
                                                    ]
                                                }
                                            }
                                        }
                                    ]
                                }
                            }
                        },
                        {
                            'node': {
                                'requestedFieldA': 'requestedValueA3',
                            }
                        },
                        {
                            'node': {
                                'requestedFieldA': 'requestedValueA4',
                                'relB': {
                                    'edges': [
                                        {
                                            'node': {
                                                'requestedFieldB': 'requestedValueB3',
                                                'relC': {
                                                    'edges': [
                                                        {
                                                            'node': {
                                                                'requestedFieldC': 'requestedValueC3',
                                                            }
                                                        },
                                                        {
                                                            'node': {
                                                                'requestedFieldC': 'requestedValueC4',
                                                            }
                                                        }
                                                    ]
                                                }
                                            }
                                        },
                                        {
                                            'node': {
                                                'requestedFieldB': 'requestedValueB4',
                                                'relC': {

                                                    'edges': [
                                                        {
                                                            'node': {
                                                                'requestedFieldC': 'requestedValueC5',
                                                            }
                                                        },
                                                        {
                                                            'node': {
                                                                'requestedFieldC': 'requestedValueC6',
                                                            }
                                                        }
                                                    ]
                                                }
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    ]
                }
            }
        }

        take = [
            ('relA', 'requestedFieldA'),
            ('relB', 'requestedFieldB'),
            ('relC', 'requestedFieldC'),
        ]

        expected_result = [
            ['requestedValueA1', ['requestedValueB1', ['requestedValueC1']]],
            ['requestedValueA2', ['requestedValueB2', ['requestedValueC2']]],
            ['requestedValueA3'],
            ['requestedValueA4', ['requestedValueB3', ['requestedValueC3'], ['requestedValueC4']],
             ['requestedValueB4', ['requestedValueC5'], ['requestedValueC6']]]
        ]

        result = self.format._take_nested(take, entity)
        self.assertEqual(expected_result, result)

    def test_format_azt_values(self):
        testcases = [
            ([['A1', ['B1', ['C1']]]], '[A1-B1-C1]'),
            ([['A1', ['B1', ['C1']]], ['A2', ['B2', ['C2']]]], '[A1-B1-C1]+[A2-B2-C2]'),
            ([['A1', ['B1', ['C1'], ['C2']]], ['A2']], '[* A1-B1-C1-C2]+[A2]')
        ]

        for testcase, expected_result in testcases:
            result = self.format._format_azt_values(testcase)

            self.assertEqual(expected_result, result)

    def test_zrt_belast_met_azt_valuebuilder(self):
        self.format._take_nested = lambda take, entity: 'taken_' + entity
        self.format._format_azt_values = lambda x: 'formatted_' + x

        self.assertEqual('formatted_taken_entity', self.format.zrt_belast_met_azt_valuebuilder('entity'))

    def test_zrt_belast_azt_valuebuilder(self):
        self.format._take_nested = lambda take, entity: 'taken_' + entity
        self.format._format_azt_values = lambda x: 'formatted_' + x

        self.assertEqual('formatted_taken_entity', self.format.zrt_belast_azt_valuebuilder('entity'))

    def test_row_formatter(self):
        row = {
            'node': {
                'belastMetZrt1': 'something',
                'belastZrt1': 'something else',
                'betrokkenBijAppartementsrechtsplitsingVve': {
                    'edges': [],
                },
                'invVanZakelijkrechtBrkTenaamstellingen': {
                    'edges': [],
                }
            },
        }

        self.format.zrt_belast_azt_valuebuilder = lambda x: 'new belastAzt value'
        self.format.zrt_belast_met_azt_valuebuilder = lambda x: 'new belastMetAzt value'

        self.assertEqual({
            'node': {
                'belastAzt': 'new belastAzt value',
                'belastMetAzt': 'new belastMetAzt value',
                'betrokkenBijAppartementsrechtsplitsingVve': {
                    'edges': [],
                },
                'invVanZakelijkrechtBrkTenaamstellingen': {
                    'edges': [],
                },
                'betrokkenBij': None,
            }
        }, self.format.row_formatter(row))

        emptyrow = {
            'node': {}
        }
        self.assertEqual({
            'node': {
                'belastAzt': 'new belastAzt value',
                'belastMetAzt': 'new belastMetAzt value',
                'betrokkenBij': None,
            }
        }, self.format.row_formatter(emptyrow))

        row_tng_asg = {
            'node': {
                'belastMetZrt1': 'something',
                'belastZrt1': 'something else',
                'betrokkenBijAppartementsrechtsplitsingVve': {
                    'edges': [
                        {'node': {'identificatie': 'vve 1'}},
                    ],
                },
                'invVanZakelijkrechtBrkTenaamstellingen': {
                    'edges': [
                        {'node': {'identificatie': 'tng 1'}},
                        {'node': {'identificatie': 'tng 2'}},
                        {'node': {'identificatie': 'tng 3'}},
                    ],
                }
            },
        }

        self.assertEqual([{
            'node': {
                'belastAzt': 'new belastAzt value',
                'belastMetAzt': 'new belastMetAzt value',
                'betrokkenBijAppartementsrechtsplitsingVve': {
                    'edges': [
                        {'node': {'identificatie': 'vve 1'}},
                    ],
                },
                'invVanZakelijkrechtBrkTenaamstellingen': {
                    'edges': [],
                },
                'betrokkenBij': 'vve 1',
            }
        }, {
            'node': {
                'belastAzt': 'new belastAzt value',
                'belastMetAzt': 'new belastMetAzt value',
                'betrokkenBijAppartementsrechtsplitsingVve': {
                    'edges': [],
                },
                'invVanZakelijkrechtBrkTenaamstellingen': {
                    'edges': [
                        {'node': {'identificatie': 'tng 1'}},
                        {'node': {'identificatie': 'tng 2'}},
                        {'node': {'identificatie': 'tng 3'}},
                    ],
                },
                'betrokkenBij': 'vve 1',
            }
        }
        ], self.format.row_formatter(row_tng_asg), "Row with both ASG and TNG should be split in two rows")

