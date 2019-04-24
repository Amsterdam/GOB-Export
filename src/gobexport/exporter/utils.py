def nested_entity_get(entity, keys, default=None):
    """
    Tries to get a value from a nested entity by a list of keys to look into.
    This can also be used to lookup indexes in a list.

    Example:
        entity = {'a': {'b': {'c': 1}}
        nested_get(entity, ['a', 'b', 'c']) => 1
        nested_get(entity, ['a', 'd', 'c']) => None
        nested_get(entity, ['a', 'd', 'c'], 'missing') => 'missing'

        entity = {'a': [{'b': 1}, {'c':2}]}
        nested_get(entity, ['a', '0', 'b']) => 1
        nested_get(entity, ['a', '1', 'c']) => 2
        nested_get(entity, ['a', '2', 'c'], 'missing') => 'missing'
    """
    # If the first key is not in the entity, try to find it in _embedded
    if not keys[0] in entity:
        keys = keys.copy()
        keys.insert(0, '_embedded')
    # Loop through all keys to find the nested value
    for key in keys:
        if isinstance(entity, dict):
            entity = entity.get(key, default)
        elif isinstance(entity, list):
            entity = _get_value_from_list(entity, key, default)
        else:
            return default
    return entity


def _get_value_from_list(entity, key, default):
    """
    Tries to get the value from a list based on a key. Can be a string or integer.
    """
    if isinstance(key, str):
        entity = _get_value_from_list_by_string(entity, key, default)
    else:
        # Use the key as an index
        try:
            entity = entity[key]
        except IndexError:
            entity = default
    return entity


def _get_value_from_list_by_string(entity, key, default):
    """
    Tries to get the value from a list based on a key. Will first try to find the
    key as the index of the list. If the key can't be cast into an int, it will
    try to get the value from the first item in the list.
    """
    # First try to convert the key to an int and use as index
    try:
        entity = entity[int(key)]
    except ValueError:
        # Try to find the key in the first item of the list
        try:
            entity = entity[0].get(key, default)
        except IndexError:
            entity = default
    except IndexError:
        entity = default
    return entity
