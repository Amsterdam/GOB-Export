from unittest import TestCase
from unittest.mock import patch, MagicMock
from datetime import datetime

from gobexport.exporter.config.brk import (
    KadastralesubjectenCsvFormat,
    brk_filename,
    sort_attributes,
    format_timestamp,
    ZakelijkerechtenCsvFormat,
    PerceelnummerEsriFormat,
    _get_filename_date,
    KadastraleobjectenEsriFormat,
    KadastraleobjectenCsvFormat,
)


class TestBrkConfigHelpers(TestCase):

    @patch("gobexport.exporter.config.brk._get_filename_date", datetime.now)
    def test_brk_filename(self):
        self.assertEqual(f"AmsterdamRegio/CSV_Actueel/BRK_FileName_{datetime.now().strftime('%Y%m%d')}.csv",
                         brk_filename('FileName'))

        self.assertEqual(f"AmsterdamRegio/SHP_Actueel/BRK_FileName_{datetime.now().strftime('%Y%m%d')}.shp",
                         brk_filename('FileName', type='shp'))

        self.assertEqual(f"AmsterdamRegio/SHP_Actueel/BRK_FileName.prj",
                         brk_filename('FileName', type='prj', append_date=False, ))

        # Assert undefined file type raises error
        with self.assertRaises(AssertionError):
            brk_filename('FileName', type='xxx')

    def test_sort_attributes(self):
        attrs = {
            'b': {
                'some': {
                    'nested': 'dict'
                }
            },
            'a': [1, 2, 3],
            'c': 'stringval'
        }

        expected_result = {
            'c': 'stringval',
            'a': [1, 2, 3],
            'b': {
                'some': {
                    'nested': 'dict'
                },
            },
        }

        self.assertEqual(expected_result, sort_attributes(attrs, ['c', 'a', 'b']))

        with self.assertRaises(AssertionError):
            sort_attributes(attrs, ['d', 'a', 'b'])

        with self.assertRaises(AssertionError):
            sort_attributes(attrs, ['c', 'a', 'b', 'c'])

        del attrs['a']
        with self.assertRaises(AssertionError):
            sort_attributes(attrs, ['c' 'a', 'b'])

    def test_format_timestamp(self):
        inp = '2035-03-31T01:02:03.000000'
        outp = '20350331010203'
        self.assertEqual(outp, format_timestamp(inp))

        for inp in ['invalid_str', None]:
            # These inputs should not change
            self.assertEqual(inp, format_timestamp(inp))

    @patch("gobexport.exporter.config.brk.requests.get")
    def test_get_filename_date(self, mock_request_get):
        mock_request_get.return_value.json.return_value = {
            'id': 1,
            'kennisgevingsdatum': "2019-09-03T00:00:00",
        }

        expected_date = datetime(year=2019, month=9, day=3)
        self.assertEqual(expected_date, _get_filename_date())


class TestBrkCsvFormat(TestCase):

    def setUp(self) -> None:
        self.format = KadastralesubjectenCsvFormat()

    def test_prefix_dict(self):
        inp_dict = {"key": "val"}
        res = self.format._prefix_dict(inp_dict, "key_prefix_", "val_prefix_")
        self.assertEqual({"key_prefix_key": "val_prefix_val"}, res)

    def test_add_condition_to_attrs(self):
        condition = {
            "condition": "isempty",
            "reference": "field.ref",
        }
        attrs = {
            'KEY1': 'val1',
            'KEY2': 'val2',
        }

        expected = {
            'KEY1': {
                'condition': 'isempty',
                'reference': 'field.ref',
                'trueval': 'val1',
            },
            'KEY2': {
                'condition': 'isempty',
                'reference': 'field.ref',
                'trueval': 'val2',
            }
        }
        res = self.format._add_condition_to_attrs(condition, attrs)
        self.assertEqual(expected, res)

    def test_show_when_field_notempty_condition(self):
        expected = {
            'condition': 'isempty',
            'reference': 'FIELDREF',
            'negate': True,
        }

        self.assertEqual(expected, self.format.show_when_field_notempty_condition('FIELDREF'))

    def test_hide_when_field_isempty_condition(self):
        expected = {
            'condition': 'isempty',
            'reference': 'FIELDREF',
        }

        self.assertEqual(expected, self.format.show_when_field_empty_condition('FIELDREF'))


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


class TestPerceelnummerEsriFormat(TestCase):

    def setUp(self) -> None:
        self.format = PerceelnummerEsriFormat()

    def test_format_rotatie(self):
        testcases = [
            (0, '0.000'),
            (-0.234435345, '-0.234'),
            (0.1299999999, '0.130'),
        ]

        for inp, outp in testcases:
            self.assertEqual(self.format.format_rotatie(inp), outp)

        invalid_testcases = [None, '']

        for testcase in invalid_testcases:
            with self.assertRaises(AssertionError):
                self.format.format_rotatie(testcase)


class TestKadastraleobjectenCsvFormat(TestCase):

    def setUp(self) -> None:
        self.format = KadastraleobjectenCsvFormat()

    def test_comma_concatter(self):
        testcases = [
            ('A|B', 'A, B'),
            ('A', 'A'),
        ]

        for inp, outp in testcases:
            self.assertEqual(outp, self.format.comma_concatter(inp))

    def test_comma_no_space_concatter(self):
        testcases = [
            ('A|B', 'A,B'),
            ('A', 'A'),
        ]

        for inp, outp in testcases:
            self.assertEqual(outp, self.format.comma_no_space_concatter(inp))

    def test_concat_with_comma(self):

        self.assertEqual({
            'action': 'format',
            'value': 'the reference',
            'formatter': self.format.comma_concatter,
        }, self.format.concat_with_comma('the reference'))

        self.assertEqual({
            'action': 'format',
            'value': 'the reference',
            'formatter': self.format.comma_no_space_concatter,
        }, self.format.concat_with_comma('the reference', False))

    def test_format_kadgrootte(self):
        testcases = [
            ('1.0', '1'),
            ('10.0', '10'),
            ('0.1', '0.1'),
            ('10', '10'),
        ]

        for inp, outp in testcases:
            self.assertEqual(outp, self.format.format_kadgrootte(inp))


class TestKadastraleobjectenEsriFormat(TestCase):

    def setUp(self) -> None:
        self.format = KadastraleobjectenEsriFormat()

    @patch("gobexport.exporter.config.brk.KadastraleobjectenCsvFormat.get_format",
           return_value={"a": "A", "b": {"x": "X"}, "c": "C"})
    @patch("gobexport.exporter.config.brk.KadastraleobjectenEsriFormat.esri_to_csv_mapping",
           {"A": "a", "B": "b"})
    def test_get_format(self, get_format_mock):
        output = {"A": "A", "B": {"x": "X"}}
        self.assertEqual(self.format.get_format(), output)
