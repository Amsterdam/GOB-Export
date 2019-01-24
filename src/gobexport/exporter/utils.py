def nested_entity_get(entity, keys, default=None):  # noqa: C901
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
        keys.insert(0, '_embedded')
    for key in keys:
        if isinstance(entity, dict):
            entity = entity.get(key, default)
        elif isinstance(entity, list):
            try:
                entity = entity[key]
            except IndexError:
                entity = default
        else:
            return default
    return entity
