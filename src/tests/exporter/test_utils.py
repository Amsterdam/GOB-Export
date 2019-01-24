from gobexport.exporter.utils import nested_entity_get


def test_nested_entity_get():
    # Test nested dict
    result = nested_entity_get({'a': {'b': {'c': 1}}}, ['a', 'b', 'c'])
    assert(result == 1)

    # Test nested dict with list
    result = nested_entity_get({'a': [{'b': 1}, {'c':2}]}, ['a', 0, 'b'])
    assert(result == 1)

    # Test default missing value
    result = nested_entity_get({'a': {'b': {'c': 1}}}, ['a', 'b', 'd'])
    assert(result == None)

    # Test missing list index value
    result = nested_entity_get({'a': [{'b': 1}, {'c':2}]}, ['a', 2, 'b'])
    assert(result == None)

    # Test missing value
    result = nested_entity_get({'a': {'b': {'c': 1}}}, ['a', 'b', 'd'], 'missing')
    assert(result == 'missing')
