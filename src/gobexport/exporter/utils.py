import re


def split_field_reference(ref: str):
    return ref.split('.') if '.' in ref else ref


def evaluate_condition(entity: dict, condition: dict):
    """Expects an entity and a condition as dict, which has as keys:

    condition: for example 'isempty'
    reference: the field reference to which to apply the condition
    trueval: the value (field reference) to return if condition evaluates to true
    falseval: you get it

    negate:    optional. if true, negate the condition

    :param condition:
    :return:
    """
    assert all([k in condition for k in ['condition', 'reference', 'trueval']]), "Invalid condition definition"

    condition_type = condition.get('condition')
    reference = condition.get('reference')
    trueval = condition.get('trueval')
    falseval = condition.get('falseval')
    negate = condition.get('negate', False)
    condition_should_be = not negate

    onfield_value = get_entity_value(entity, split_field_reference(reference))

    if condition_type == 'isempty':
        condition_result = not bool(onfield_value)
    elif condition_type == 'isnone':
        condition_result = onfield_value is None
    else:
        raise NotImplementedError(f"Not implemented condition {condition_type}")

    if condition_result is condition_should_be:
        result = trueval
    else:
        result = falseval

    if result:
        return get_entity_value(entity, result)


def _evaluate_concat_action(entity: dict, action: dict):
    assert 'fields' in action
    return "".join([str(item) if item is not None else "" for
                    item in [get_entity_value(entity, field) for field in action['fields']]])


def _evaluate_literal_action(action: dict):
    return action.get('value')


def _evaluate_fill_action(entity: dict, action: dict):
    assert all([key in action for key in ['length', 'value', 'character', 'fill_type']])
    assert action['fill_type'] in ['rjust', 'ljust'], "A valid fill type must be supplied (rjust, ljust)"

    value = str(get_entity_value(entity, action['value']))

    if action['fill_type'] == 'rjust':
        return value.rjust(action['length'], action['character'])
    elif action['fill_type'] == 'ljust':
        return value.ljust(action['length'], action['character'])


def _evaluate_format_action(entity: dict, action: dict):
    assert all([key in action for key in ['formatter', 'value']])

    value = get_entity_value(entity, action['value'])

    if not value:
        return

    return action['formatter'](value, **action.get('kwargs', {}))


def _evaluate_build_value_action(entity: dict, action: dict):
    assert 'valuebuilder' in action
    return action['valuebuilder'](entity)


def _evaluate_case_action(entity: dict, action: dict):
    assert all([key in action for key in ['reference', 'values']])
    assert isinstance(action['values'], dict)

    value = get_entity_value(entity, action['reference'])
    return action['values'].get(value)


def evaluate_action(entity: dict, action: dict):
    if action.get('action') == 'concat':
        return _evaluate_concat_action(entity, action)
    elif action.get('action') == 'literal':
        return _evaluate_literal_action(action)
    elif action.get('action') == 'fill':
        return _evaluate_fill_action(entity, action)
    elif action.get('action') == 'format':
        return _evaluate_format_action(entity, action)
    elif action.get('action') == 'case':
        return _evaluate_case_action(entity, action)
    elif action.get('action') == 'build_value':
        return _evaluate_build_value_action(entity, action)
    else:
        raise NotImplementedError()


def _get_entity_value_dict_lookup_key(entity: dict, lookup_key: dict):
    if lookup_key.get('action'):
        return evaluate_action(entity, lookup_key)
    elif lookup_key.get('condition'):
        return evaluate_condition(entity, lookup_key)

    raise NotImplementedError()


def get_entity_value(entity, lookup_key):
    """Get the value from the entity using a key or a list of keys

    lookup_key can be of type dict, with either 'action' or 'condition' set.

    An action overrides the remainder of this function and returns the value immediately.
    A condition returns a new (or the same) lookup key/dict for further processing.

    If lookup_key is of type list or string, we perform a lookup on entity.

    :param entity: The API entity to get the value from
    :param lookup_key: A attribute name or a list of attribute names
    :return: the value of the entity's attribute or None
    """
    if not lookup_key:
        return None

    if isinstance(lookup_key, str):
        lookup_key = split_field_reference(lookup_key)

    if isinstance(lookup_key, dict):
        return _get_entity_value_dict_lookup_key(entity, lookup_key)

    assert isinstance(lookup_key, str) or isinstance(lookup_key, list)

    value = nested_entity_get(entity, lookup_key) if isinstance(lookup_key, list) else entity.get(lookup_key)
    # Return J or N when the value is a boolean
    if isinstance(value, bool):
        value = 'J' if value else 'N'
    return value


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
    Tries to get the value from a list based on a key.
    If the key is an index, which is defined by an integer wrapped in
    brackets e.g. [1], we select a single value. Otherwise a pipe delimited
    string is returned.
    If the list contains dict of dict, a remapped dict with unnested keys and
    values as pipe delimited strings is returned.
    """
    # If we've received an specific index, try to get the value
    index = re.match(r'\[(\d+)\]', key)
    if index:
        # Use the key as an index
        try:
            entity = entity[int(index.groups()[0])]
        except IndexError:
            entity = default
    else:
        if entity and isinstance(entity[0][key], dict):
            # Un-nest keys in dict of dict and join values as string, separated by '|'

            nested_objs = [ent[key] for ent in entity]
            res = {new_key: [] for nested in nested_objs for new_key in nested}

            for nested in nested_objs:
                for new_key in res:
                    value = nested[new_key]
                    res[new_key].append(str(value))

            entity = {new_key: '|'.join(res[new_key]) for new_key in res}

        else:
            # Return a pipe delimited string of the values by key
            entity = '|'.join([str(d[key]) if d[key] else "" for d in entity if key in d])

    return entity


def convert_format(format, mapping):
    """
    Converts one format to another one using mapping.
    """
    output_format = {}

    for key, value in mapping.items():
        if isinstance(value, str):
            output_format[key] = format[value]
        else:
            output_format[key] = value

    return output_format
