from unittest import TestCase
from gobexport.sorter.graphql import GraphQlResultSorter


class TestGraphQlResultSorter(TestCase):

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

        sorter = GraphQlResultSorter({})
        result = sorter._box_item(item)
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

        self.maxDiff = None
        sorter = GraphQlResultSorter({})
        result = sorter._box_item(item)
        self.assertEqual(expected_result, result)

    def test_sort_item_simple(self):
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
        expected_result = {
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
                            },
                        }
                    ]
                }
            }
        }
        sorters = {
            'reference.sortkey': lambda x, y: x < y
        }
        sorter = GraphQlResultSorter(sorters)
        self.assertEqual(expected_result, sorter.sort_item(item))

    def test_sort_item_multiple_with_none(self):
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
                                'sort2key': None
                            },
                        },
                        {
                            'node': {
                                'rk1': 'rv1',
                                'rk2': 'rv2',
                                'sortkey': 'A',
                                'sort2key': 'c'
                            },
                        },
                        {
                            'node': {
                                'rk1': 'rv1',
                                'rk2': 'rv2',
                                'sortkey': 'A',
                                'sort2key': 'b'
                            },
                        }
                    ]
                }
            }
        }
        expected_result = {
            'node': {
                'k1': 'v1',
                'k2': 'v2',
                'reference': {
                    'edges': [
                        {
                            'node': {
                                'rk1': 'rv1',
                                'rk2': 'rv2',
                                'sortkey': 'A',
                                'sort2key': 'b'
                            },
                        }
                    ]
                }
            }
        }

        sorters = {
            'reference.sortkey': lambda x, y: x < y,
            'reference.sort2key': lambda x, y: x < y,
        }
        sorter = GraphQlResultSorter(sorters)
        self.assertEqual(expected_result, sorter.sort_item(item))

    def test_sort_item_nested(self):
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
                                'nestedreference': {
                                    'edges': [
                                        {
                                            'node': {
                                                'sort2key': 'C'
                                            }
                                        },
                                        {
                                            'node': {
                                                'sort2key': 'A'
                                            }
                                        },
                                        {
                                            'node': {
                                                'sort2key': 'B'
                                            }
                                        },

                                    ]
                                }
                            },
                        },
                        {
                            'node': {
                                'rk11': 'rv1',
                                'rk22': 'rv2',
                                'sortkey': 'A',
                                'nestedreference': {
                                    'edges': [
                                        {
                                            'node': {
                                                'sort2key': 'F'
                                            }
                                        },
                                        {
                                            'node': {
                                                'sort2key': 'D'
                                            }
                                        },
                                        {
                                            'node': {
                                                'sort2key': 'E'
                                            }
                                        },

                                    ]
                                }
                            },
                        },
                        {
                            'node': {
                                'rk111': 'rv1',
                                'rk222': 'rv2',
                                'sortkey': 'A',
                                'nestedreference': {
                                    'edges': [
                                        {
                                            'node': {
                                                'sort2key': 'H'
                                            }
                                        },
                                        {
                                            'node': {
                                                'sort2key': 'I'
                                            }
                                        },
                                        {
                                            'node': {
                                                'sort2key': 'G'
                                            }
                                        },

                                    ]
                                }
                            },
                        }
                    ]
                }
            }
        }

        expected_result = {
            'node': {
                'k1': 'v1',
                'k2': 'v2',
                'reference': {
                    'edges': [
                        {
                            'node': {
                                'rk111': 'rv1',
                                'rk222': 'rv2',
                                'sortkey': 'A',
                                'nestedreference': {
                                    'edges': [
                                        {
                                            'node': {
                                                'sort2key': 'I'
                                            }
                                        },
                                    ]
                                }
                            },
                        }
                    ]
                }
            }
        }

        sorters = {
            'reference.sortkey': lambda x, y: x < y,
            'reference.nestedreference.sort2key': lambda x, y: x > y,
        }
        sorter = GraphQlResultSorter(sorters)
        self.assertEqual(expected_result, sorter.sort_item(item))

    def test_set_value_for_all(self):
        sorter = GraphQlResultSorter({})
        lst = [{
            'item': 'A',
            'value': 'someval',
        }, {
            'item': 'B',
            'value': 'some other val'
        }]

        sorter._set_value_for_all(lst, 'value', 'new value')

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

    def test_extract_value_from_item_no_recursion(self):
        item = {
            'node': {
                'key': 'value'
            }
        }

        sorter = GraphQlResultSorter({})
        self.assertEqual('value', sorter._extract_value_from_item(item, 'key'))

    def test_extract_value_from_item_recursive(self):
        key = 'a.b'
        item = {
            'node': {
                'a': {
                    'edges': [
                        {
                            'node': {
                                'b': 'b value'
                            }
                        }
                    ]
                }
            }
        }

        sorter = GraphQlResultSorter({})
        self.assertEqual('b value', sorter._extract_value_from_item(item, key))

    def test_extract_value_empty_list(self):
        key = 'a.b'
        item = {
            'node': {
                'a': {
                    'edges': [
                    ]
                }
            }
        }

        sorter = GraphQlResultSorter({})
        self.assertEqual(None, sorter._extract_value_from_item(item, key))
