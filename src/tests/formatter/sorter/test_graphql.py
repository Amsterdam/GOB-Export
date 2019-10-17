from unittest import TestCase
from unittest.mock import MagicMock
from gobexport.formatter.sorter.graphql import GraphQlResultSorter
from gobexport.formatter.graphql import GraphQLResultFormatter


class TestGraphQlResultSorter(TestCase):

    def test_sort_item_simple(self):
        items = [
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
                                    'sortkey': 'C'
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
                                    'sortkey': 'A'
                                },
                            }
                        ]
                    }
                }
            }

        ]
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
        self.assertEqual(expected_result, sorter.sort_items(items))

    def test_sort_item_multiple_with_none(self):
        items = [
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
                                    'sort2key': None
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
                                    'sortkey': 'A',
                                    'sort2key': 'c'
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
                                    'sortkey': 'A',
                                    'sort2key': 'b'
                                },
                            }
                        ]
                    }
                }
            }
        ]
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
        self.assertEqual(expected_result, sorter.sort_items(items))

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

        # Use formatter to box item; otherwise the argument would be very long
        formatter = GraphQLResultFormatter()
        items = formatter._box_item(item)

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
        self.assertEqual(expected_result, sorter.sort_items(items))

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

    def test_extract_value_missing_key(self):
        key = 'a.b'
        item = {
            'node': {
                'a': {
                    'edges': [{
                        'node': {}
                    }]
                }
            }
        }

        sorter = GraphQlResultSorter({})
        self.assertEqual(None, sorter._extract_value_from_item(item, key))

    def test_sort_and_eliminate_non_values(self):
        sorter_func = MagicMock()
        sorter = GraphQlResultSorter({})
        sorter._extract_value_from_item = MagicMock(return_value=None)
        res = sorter._sort_and_eliminate([1, 2, 3], 'a.b.c.', sorter_func)

        sorter_func.assert_not_called()
        self.assertEqual([1, 2, 3], res)
