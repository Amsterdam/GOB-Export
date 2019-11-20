from unittest import TestCase
from unittest.mock import MagicMock, patch

from gobexport.formatter.graphql import GraphQLResultFormatter


class TestGraphQLResultFormatter(TestCase):

    @patch("gobexport.formatter.graphql.convert_to_history_rows")
    def test_expand_history(self, mock_convert_to_history_rows):
        expected_result = [i for i in range(5)]
        mock_convert_to_history_rows.return_value = expected_result

        formatter = GraphQLResultFormatter()
        formatter._flatten_edge = MagicMock()
        result = list(formatter._expand_history('edge'))

        formatter._flatten_edge.assert_called_with('edge')
        mock_convert_to_history_rows.assert_called_with(formatter._flatten_edge.return_value)
        self.assertEqual(expected_result, result)

    def test_format_item_no_special_formatting(self):
        formatter = GraphQLResultFormatter(expand_history=False)
        formatter._flatten_edge = MagicMock()

        result = list(formatter.format_item('item'))
        formatter._flatten_edge.assert_called_with('item')
        self.assertEqual([formatter._flatten_edge.return_value], result)

    def test_format_item_with_sorter(self):
        formatter = GraphQLResultFormatter(sort=True)
        formatter._box_item = MagicMock(return_value=['a', 'b', 'c'])
        formatter.sorter = MagicMock()
        formatter.sorter.sort_items = lambda x: x[1]
        formatter._flatten_edge = lambda x: 'flattened_' + x

        result = next(formatter.format_item('item'))

        self.assertEqual('flattened_b', result)

    def test_format_item_with_unfold(self):
        formatter = GraphQLResultFormatter(unfold=True)
        formatter._box_item = MagicMock()
        formatter._box_item.return_value = ['a', 'b', 'c']
        formatter._flatten_edge = lambda x: 'flattened_' + x

        result = list(formatter.format_item('item'))
        self.assertEqual(['flattened_a', 'flattened_b', 'flattened_c'], result)

    def test_format_item_expand_history(self):
        formatter = GraphQLResultFormatter(expand_history=True)
        formatter._expand_history = MagicMock(return_value=iter(['a', 'b']))

        result = list(formatter.format_item('item'))
        self.assertEqual(['a', 'b'], result)
        formatter._expand_history.assert_called_with('item')

    def test_format_item_with_row_formatter(self):
        row_formatter = lambda x: 'formatted_row(' + x + ')'
        formatter = GraphQLResultFormatter(row_formatter=row_formatter)
        formatter._flatten_edge = lambda x: 'flattened(' + x + ')'

        self.assertEqual(['flattened(formatted_row(a))'], list(formatter.format_item('a')))

    def test_flatten_edge(self):
        formatter = GraphQLResultFormatter()
        edge = {
            'node': {
                'reference': {
                    'edges': [
                        {
                            'node': {
                                'value': 'value'
                            }
                        }
                    ]
                }
            }
        }

        nested_edge = {
            "node": {
                "value": "value",
                "reference": {
                    "edges": [
                        {
                            "node": {
                                "value": "value",
                                "nested_reference": {
                                    "edges": [
                                        {
                                            "node": {
                                                "nested_value": "value"
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    ]
                },
                "empty_reference": {
                    "edges": [
                        {
                            "node": {
                                "empty_nested_reference": {
                                    "edges": []
                                }
                            }
                        }
                    ]
                }
            }
        }

        expected_result = {'reference': [{'value': 'value'}]}
        result = formatter._flatten_edge(edge)
        assert (expected_result == result)

        expected_result = {
            'value': 'value',
            'reference': [{
                'value': 'value',
                'nested_reference': [{'nested_value': 'value'}]
            }],
            'nested_reference': [{'nested_value': 'value'}],
            'empty_reference': [{'empty_nested_reference': []}],
            'empty_nested_reference': [],
        }
        result = formatter._flatten_edge(nested_edge)
        assert (expected_result == result)

    def test_box_item(self):
        item = {
            'node': {
                'k1': 'v1',
                'k2': 'v2',
                'reference': {
                    'edges': [
                        {
                            'node': {
                                'rk1': 'rv1',
                                'rk2': 'rv2',
                                'sortkey': 'B'
                            },
                        },
                        {
                            'node': {
                                'rk1': 'rv1',
                                'rk2': 'rv2',
                                'sortkey': 'C'
                            },
                        },
                        {
                            'node': {
                                'rk1': 'rv1',
                                'rk2': 'rv2',
                                'sortkey': 'A'
                            },
                        }
                    ]
                }
            }
        }

        expected_result = [
            {
                'node': {
                    'k1': 'v1',
                    'k2': 'v2',
                    'reference': {
                        'edges': [
                            {
                                'node': {
                                    'rk1': 'rv1',
                                    'rk2': 'rv2',
                                    'sortkey': 'B'
                                }
                            }
                        ]
                    }
                },
            },
            {
                'node': {
                    'k1': 'v1',
                    'k2': 'v2',
                    'reference': {
                        'edges': [
                            {
                                'node': {
                                    'rk1': 'rv1',
                                    'rk2': 'rv2',
                                    'sortkey': 'C'
                                }
                            }
                        ]
                    }
                },
            },
            {
                'node': {
                    'k1': 'v1',
                    'k2': 'v2',
                    'reference': {
                        'edges': [
                            {
                                'node': {
                                    'rk1': 'rv1',
                                    'rk2': 'rv2',
                                    'sortkey': 'A'
                                }
                            }
                        ]
                    }
                },
            }
        ]

        formatter = GraphQLResultFormatter()
        result = formatter._box_item(item)
        self.assertEqual(expected_result, result)

    def test_box_item_specific(self):

        item = {
            'node': {
                'identificatie': '0363200000403263',
                'huisnummer': 17,
                'huisletter': None,
                'huisnummertoevoeging': None,
                'postcode': '1015NR',
                'ligtAanOpenbareruimte': {
                    'edges': [
                        {
                            'node': {
                                'naam': 'Eerste Anjeliersdwarsstraat'
                            }
                        }
                    ]
                },
                'ligtInWoonplaats': {
                    'edges': [
                        {
                            'node': {
                                'naam': 'Amsterdam'
                            }
                        }
                    ]
                }
            }
        }

        expected_result = [{
            'node': {
                'identificatie': '0363200000403263',
                'huisnummer': 17,
                'huisletter': None,
                'huisnummertoevoeging': None,
                'postcode': '1015NR',
                'ligtAanOpenbareruimte': {
                    'edges': [
                        {
                            'node': {
                                'naam': 'Eerste Anjeliersdwarsstraat'
                            }
                        }
                    ]
                },
                'ligtInWoonplaats': {
                    'edges': [
                        {
                            'node': {
                                'naam': 'Amsterdam'
                            }
                        }
                    ]
                }
            }
        }]

        formatter = GraphQLResultFormatter()
        formatter._undouble = MagicMock(side_effect=lambda x: x)
        result = formatter._box_item(item)
        self.assertEqual(len(expected_result), len(result))
        self.assertEqual(expected_result, result)

    def test_box_item_nested_references(self):
        item = {
            'node': {
                'k1': 'v1',
                'k2': 'v2',
                'reference': {
                    'edges': [
                        {
                            'node': {
                                'rk1': 'rv1',
                                'rk2': 'rv2',
                                'sortkey': 'B',
                                'reference': {
                                    'edges': [
                                        {
                                            'node': {
                                                'rrk1': 'rrv1',
                                                'rrk2': 'rrv2',
                                                'sortkey': 'rrB',
                                            }
                                        },
                                        {
                                            'node': {
                                                'rrk1': 'rrv1',
                                                'rrk2': 'rrv2',
                                                'sortkey': 'rrA',
                                            }
                                        }
                                    ]
                                }
                            },
                        },
                        {
                            'node': {
                                'rk1': 'rv1',
                                'rk2': 'rv2',
                                'sortkey': 'C'
                            },
                        },
                        {
                            'node': {
                                'rk1': 'rv1',
                                'rk2': 'rv2',
                                'sortkey': 'A'
                            },
                        }
                    ]
                }
            }
        }

        expected_result = [
            {
                'node': {
                    'k1': 'v1',
                    'k2': 'v2',
                    'reference': {
                        'edges': [
                            {
                                'node': {
                                    'rk1': 'rv1',
                                    'rk2': 'rv2',
                                    'sortkey': 'B',
                                    'reference': {
                                        'edges': [
                                            {
                                                'node': {
                                                    'rrk1': 'rrv1',
                                                    'rrk2': 'rrv2',
                                                    'sortkey': 'rrB',
                                                }
                                            },
                                        ]
                                    }
                                }
                            }
                        ]
                    }
                },
            },
            {
                'node': {
                    'k1': 'v1',
                    'k2': 'v2',
                    'reference': {
                        'edges': [
                            {
                                'node': {
                                    'rk1': 'rv1',
                                    'rk2': 'rv2',
                                    'sortkey': 'B',
                                    'reference': {
                                        'edges': [
                                            {
                                                'node': {
                                                    'rrk1': 'rrv1',
                                                    'rrk2': 'rrv2',
                                                    'sortkey': 'rrA',
                                                }
                                            },
                                        ]
                                    }
                                }
                            }
                        ]
                    }
                },
            },
            {
                'node': {
                    'k1': 'v1',
                    'k2': 'v2',
                    'reference': {
                        'edges': [
                            {
                                'node': {
                                    'rk1': 'rv1',
                                    'rk2': 'rv2',
                                    'sortkey': 'C'
                                }
                            }
                        ]
                    }
                },
            },
            {
                'node': {
                    'k1': 'v1',
                    'k2': 'v2',
                    'reference': {
                        'edges': [
                            {
                                'node': {
                                    'rk1': 'rv1',
                                    'rk2': 'rv2',
                                    'sortkey': 'A'
                                }
                            }
                        ]
                    }
                },
            }
        ]

        formatter = GraphQLResultFormatter()
        formatter._undouble = MagicMock(side_effect=lambda x: x)
        result = formatter._box_item(item)
        self.assertEqual(expected_result, result)

    def test_box_item_nested_references_same_level(self):
        item = {
            'node': {
                'k1': 'v1',
                'k2': 'v2',
                'reference': {
                    'edges': [
                        {
                            'node': {
                                'rk1': 'rv1',
                                'rk2': 'rv2',
                                'sortkey': 'B',
                                'reference': {
                                    'edges': [
                                        {
                                            'node': {
                                                'rrk1': 'rrv1',
                                                'rrk2': 'rrv2',
                                                'sortkey': 'rrB',
                                            }
                                        },
                                        {
                                            'node': {
                                                'rrk1': 'rrv1',
                                                'rrk2': 'rrv2',
                                                'sortkey': 'rrA',
                                            }
                                        }
                                    ]
                                },
                                'reference2': {
                                    'edges': [
                                        {
                                            'node': {
                                                'r2k1': 'r2v1'
                                            }
                                        }
                                    ]
                                }
                            },
                        },
                    ]
                }
            }
        }

        expected_result = [
            {
                'node': {
                    'k1': 'v1',
                    'k2': 'v2',
                    'reference': {
                        'edges': [
                            {
                                'node': {
                                    'rk1': 'rv1',
                                    'rk2': 'rv2',
                                    'sortkey': 'B',
                                    'reference': {
                                        'edges': [
                                            {
                                                'node': {
                                                    'rrk1': 'rrv1',
                                                    'rrk2': 'rrv2',
                                                    'sortkey': 'rrB',
                                                }
                                            },
                                        ]
                                    },
                                    'reference2': {
                                        'edges': [
                                            {
                                                'node': {
                                                    'r2k1': 'r2v1'
                                                }
                                            }
                                        ]
                                    }
                                }
                            }
                        ]
                    }
                },
            },
            {
                'node': {
                    'k1': 'v1',
                    'k2': 'v2',
                    'reference': {
                        'edges': [
                            {
                                'node': {
                                    'rk1': 'rv1',
                                    'rk2': 'rv2',
                                    'sortkey': 'B',
                                    'reference': {
                                        'edges': [
                                            {
                                                'node': {
                                                    'rrk1': 'rrv1',
                                                    'rrk2': 'rrv2',
                                                    'sortkey': 'rrA',
                                                }
                                            },
                                        ]
                                    },
                                    'reference2': {
                                        'edges': [
                                            {
                                                'node': {
                                                    'r2k1': 'r2v1'
                                                }
                                            }
                                        ]
                                    }
                                }
                            }
                        ]
                    }
                },
            },
        ]
        formatter = GraphQLResultFormatter()
        formatter._undouble = MagicMock(side_effect=lambda x: x)
        result = formatter._box_item(item)
        self.assertEqual(expected_result, result)

    def test_box_item_nested_references_same_level_cross_relations(self):
        item = {
            'node': {
                'k1': 'v1',
                'k2': 'v2',
                'reference': {
                    'edges': [
                        {
                            'node': {
                                'rk1': 'rv1',
                                'rk2': 'rv2',
                                'sortkey': 'B',
                                'reference': {
                                    'edges': [
                                        {
                                            'node': {
                                                'rrk1': 'rrv1',
                                                'rrk2': 'rrv2',
                                                'sortkey': 'rrB',
                                            }
                                        },
                                        {
                                            'node': {
                                                'rrk1': 'rrv1',
                                                'rrk2': 'rrv2',
                                                'sortkey': 'rrA',
                                            }
                                        }
                                    ]
                                },
                                'reference2': {
                                    'edges': [
                                        {
                                            'node': {
                                                'r2k1': 'r2v1'
                                            }
                                        },
                                        {
                                            'node': {
                                                'r2k2': 'r2v2',
                                            }
                                        }
                                    ]
                                }
                            },
                        },
                    ]
                }
            }
        }

        expected_result = [
            {
                'node': {
                    'k1': 'v1',
                    'k2': 'v2',
                    'reference': {
                        'edges': [
                            {
                                'node': {
                                    'rk1': 'rv1',
                                    'rk2': 'rv2',
                                    'sortkey': 'B',
                                    'reference': {
                                        'edges': [
                                            {
                                                'node': {
                                                    'rrk1': 'rrv1',
                                                    'rrk2': 'rrv2',
                                                    'sortkey': 'rrB',
                                                }
                                            },
                                        ]
                                    },
                                    'reference2': {
                                        'edges': [
                                            {
                                                'node': {
                                                    'r2k1': 'r2v1'
                                                }
                                            },
                                        ]
                                    }
                                },
                            },
                        ]
                    }
                }
            },
            {
                'node': {
                    'k1': 'v1',
                    'k2': 'v2',
                    'reference': {
                        'edges': [
                            {
                                'node': {
                                    'rk1': 'rv1',
                                    'rk2': 'rv2',
                                    'sortkey': 'B',
                                    'reference': {
                                        'edges': [
                                            {
                                                'node': {
                                                    'rrk1': 'rrv1',
                                                    'rrk2': 'rrv2',
                                                    'sortkey': 'rrA',
                                                }
                                            }
                                        ]
                                    },
                                    'reference2': {
                                        'edges': [
                                            {
                                                'node': {
                                                    'r2k1': 'r2v1'
                                                }
                                            },
                                        ]
                                    }
                                },
                            },
                        ]
                    }
                }
            },
            {
                'node': {
                    'k1': 'v1',
                    'k2': 'v2',
                    'reference': {
                        'edges': [
                            {
                                'node': {
                                    'rk1': 'rv1',
                                    'rk2': 'rv2',
                                    'sortkey': 'B',
                                    'reference': {
                                        'edges': [
                                            {
                                                'node': {
                                                    'rrk1': 'rrv1',
                                                    'rrk2': 'rrv2',
                                                    'sortkey': 'rrB',
                                                }
                                            },
                                        ]
                                    },
                                    'reference2': {
                                        'edges': [
                                            {
                                                'node': {
                                                    'r2k2': 'r2v2',
                                                }
                                            }
                                        ]
                                    }
                                },
                            },
                        ]
                    }
                }
            },
            {
                'node': {
                    'k1': 'v1',
                    'k2': 'v2',
                    'reference': {
                        'edges': [
                            {
                                'node': {
                                    'rk1': 'rv1',
                                    'rk2': 'rv2',
                                    'sortkey': 'B',
                                    'reference': {
                                        'edges': [
                                            {
                                                'node': {
                                                    'rrk1': 'rrv1',
                                                    'rrk2': 'rrv2',
                                                    'sortkey': 'rrA',
                                                }
                                            }
                                        ]
                                    },
                                    'reference2': {
                                        'edges': [
                                            {
                                                'node': {
                                                    'r2k2': 'r2v2',
                                                }
                                            }
                                        ]
                                    }
                                },
                            },
                        ]
                    }
                }
            },

        ]
        formatter = GraphQLResultFormatter(cross_relations=True)
        formatter._undouble = MagicMock(side_effect=lambda x: x)
        result = formatter._box_item(item)
        self.assertEqual(expected_result, result)

    def test_set_value_for_all(self):
        formatter = GraphQLResultFormatter()
        lst = [{
            'item': 'A',
            'value': 'someval',
        }, {
            'item': 'B',
            'value': 'some other val'
        }]

        formatter._set_value_for_all(lst, 'value', 'new value')

        self.assertEqual(
            [{
                'item': 'A',
                'value': 'new value',
            }, {
                'item': 'B',
                'value': 'new value'
            }],
            lst
        )
