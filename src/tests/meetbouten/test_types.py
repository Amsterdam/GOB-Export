import pytest

from gobexport.meetbouten.types import _to_string, _to_boolean, _to_number, _to_date, _to_geometry, _to_xcoord, _to_ycoord, type_convert


def test_to_string():
    assert(_to_string('a string') == '$$a string$$')
    assert(_to_string(None) == '$$$$')
    assert(_to_string('') == '$$$$')

    for v in [True, 5, 5.1, [], {}]:
        with pytest.raises(AssertionError):
            assert(_to_string(v))


def test_to_boolean():
    assert(_to_boolean(True) == '$$$$')
    assert(_to_boolean(False) == '$$N$$')
    assert(_to_boolean(None) == '$$N$$')

    for v in ['', 5, 5.1, [], {}]:
        with pytest.raises(AssertionError):
            assert(_to_boolean(v))


def test_to_number():
    assert(_to_number(5) == '5')
    assert(_to_number(5.1) == '5,1')
    assert(_to_number(None) == '')

    for v in ['', True, [], {}]:
        with pytest.raises(AssertionError):
            assert(_to_number(v))


def test_to_date():
    assert(_to_date('2020-05-20') == '$$20200520$$')
    assert(_to_date('2020-5-20') == '$$20200520$$')
    assert(_to_date(None) == '$$$$')

    with pytest.raises(ValueError):
        assert(_to_date('2020-5'))
    with pytest.raises(ValueError):
        assert(_to_date('2020-20-05'))

    for v in [5, 5.1, True, [], {}]:
        with pytest.raises(AssertionError):
            assert(_to_date(v))


def test_to_geometry():
    assert(_to_geometry({"type": "Point", "coordinates": [1, 2]}) == 'POINT (1 2)')
    assert(_to_geometry({"type": "Point", "coordinates": [1.1, 2.2]}) == 'POINT (1,1 2,2)')
    assert(_to_geometry({"type": "X", "coordinates": ["a", "b"]}) == 'X (a b)')
    assert(_to_geometry(None) == '')

    for v in [5, 5.1, True, [], ""]:
        with pytest.raises(AssertionError):
            assert(_to_geometry(v))


def test_to_xcoord():
    assert(_to_xcoord({"type": "Point", "coordinates": [1, 2]}) == '1')
    assert(_to_xcoord({"type": "Point", "coordinates": [1.1, 2.2]}) == '1,1')
    assert(_to_xcoord({"type": "X", "coordinates": ["a", "b"]}) == 'a')
    assert(_to_xcoord(None) == '')

    for v in [5, 5.1, True, [], ""]:
        with pytest.raises(AssertionError):
            assert(_to_xcoord(v))


def test_to_ycoord():
    assert(_to_ycoord({"type": "Point", "coordinates": [1, 2]}) == '2')
    assert(_to_ycoord({"type": "Point", "coordinates": [1.1, 2.2]}) == '2,2')
    assert(_to_ycoord({"type": "X", "coordinates": ["a", "b"]}) == 'b')
    assert(_to_ycoord(None) == '')

    for v in [5, 5.1, True, [], ""]:
        with pytest.raises(AssertionError):
            assert(_to_ycoord(v))


def test_type_convert():
    for s in ['str', None, '']:
        assert(type_convert('str', s) == _to_string(s))

    for b in [True, False, None]:
        assert(type_convert('bool', b) == _to_boolean(b))

    for n in [0, 1, 2.5, None]:
        assert(type_convert('num', n) == _to_number(n))

    for d in ['2030-09-25', None]:
        assert(type_convert('dat', d) == _to_date(d))

    for g in [{"type": "Point", "coordinates": [1, 2]}, {"type": "Point", "coordinates": [1.1, 2.2]}, None]:
        assert(type_convert('geo', g) == _to_geometry(g))
