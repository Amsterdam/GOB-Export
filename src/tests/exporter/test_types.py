import pytest

from gobexport.exporter.dat import _to_plain, _to_string, _to_boolean, _to_number, _to_number_zero, _to_number_string, _to_date, _to_geometry, _to_coord, type_convert


def test_to_string():
    assert(_to_string('a string') == '$$a string$$')
    assert(_to_string(None) == '')
    assert(_to_string('') == '')

    for v in [True, 5, 5.1, [], {}]:
        with pytest.raises(AssertionError):
            assert(_to_string(v))


def test_to_boolean():
    assert(_to_boolean(True) == '')
    assert(_to_boolean(False) == '$$N$$')
    assert(_to_boolean(None) == '$$N$$')

    for v in ['', 5, 5.1, [], {}]:
        with pytest.raises(AssertionError):
            assert(_to_boolean(v))


def test_to_number():
    assert(_to_number(5) == '5')
    assert(_to_number(-5) == '-5')
    assert(_to_number(5.1) == '5,1')
    assert(_to_number('5.1') == '5,1')
    assert(_to_number('-5') == '-5')
    assert(_to_number(None) == '')

    # Test with precision
    assert(_to_number(5, 2) == '5,00')
    assert(_to_number(5.1324234, 1) == '5,1')
    assert(_to_number(5.1324234, 2) == '5,13')
    assert(_to_number(-5.1324234, 2) == '-5,13')
    assert(_to_number('5', 2) == '5,00')
    assert(_to_number('5.1324234', 2) == '5,13')
    assert(_to_number('-5.1324234', 2) == '-5,13')
    assert(_to_number('0.0', 1) == '0,0')
    assert(_to_number(0.0, 1) == '0,0')

    for v in ['', True, [], {}]:
        with pytest.raises(AssertionError):
            assert(_to_number(v))
    
    # Test
    with pytest.raises(ValueError):
        assert(_to_number('geen nummer', 1))
    with pytest.raises(ValueError):
        assert(_to_number('', 1))

def test_to_number_zero():
    # Test to export '' when input is 0
    for v in [0, 0.0, .0, "0", "0.0", "0.00", ".0", ".00"]:
        for p in [0, 1, 2, 3]:
            assert(_to_number_zero(v, p) == '')

    # Test to export _to_number when input is not 0
    for v in [1, 5, 0.001, .01, "01", "0.001", "0.001", "0.010", ".01", ".001"]:
        for p in [3, 4, 5]:
            assert(_to_number_zero(v, p) == _to_number(v, p))

def test_to_number_string():
    assert(_to_number_string(5) == '$$5$$')
    assert(_to_number_string(5.1) == '$$5,1$$')
    assert(_to_number_string('5.1') == '$$5,1$$')
    assert(_to_number_string('0.1') == '$$,1$$')
    assert(_to_number_string(None) == '')

    # Test with precision
    assert(_to_number_string(5, 2) == '$$5,00$$')
    assert(_to_number_string(5.1235353, 2) == '$$5,12$$')
    assert(_to_number_string(0.1235353, 2) == '$$,12$$')
    assert(_to_number_string(-5.1235353, 2) == '$$-5,12$$')
    assert(_to_number_string(-0.1235353, 2) == '$$-,12$$')
    assert(_to_number_string('5.1',1) == '$$5,1$$')

    for v in ['', True, [], {}]:
        with pytest.raises(AssertionError):
            assert(_to_number(v))

    # Test
    with pytest.raises(ValueError):
        assert(_to_number('geen nummer', 1))
    with pytest.raises(ValueError):
        assert(_to_number('', 1))

def test_to_date():
    assert(_to_date('2020-05-20') == '$$20200520$$')
    assert(_to_date('2020-5-20') == '$$20200520$$')
    assert(_to_date(None) == '')

    with pytest.raises(ValueError):
        assert(_to_date('2020-5'))
    with pytest.raises(ValueError):
        assert(_to_date('2020-20-05'))

    for v in [5, 5.1, True, [], {}]:
        with pytest.raises(AssertionError):
            assert(_to_date(v))


def test_to_geometry():
    assert(_to_geometry({"type": "Point", "coordinates": [1, 2]}) == 'POINT (1.0 2.0)')
    assert(_to_geometry({"type": "Point", "coordinates": [1.00, 2]}) == 'POINT (1.0 2.0)')
    assert(_to_geometry({"type": "Point", "coordinates": [1.1, 2.2]}) == 'POINT (1.1 2.2)')
    assert(_to_geometry({"type": "Point", "coordinates": [1.12, 2.21]}) == 'POINT (1.12 2.21)')
    assert(_to_geometry({"type": "Point", "coordinates": ['1,121.0', 2.21]}) == 'POINT (1121.0 2.21)')
    assert(_to_geometry({"type": "Point", "coordinates": [',5', 2.21]}) == 'POINT (5.0 2.21)')
    assert(_to_geometry(None) == '')

    with pytest.raises(ValueError):
        assert(_to_geometry({"type": "X", "coordinates": ["a", "b"]}) == 'X (a b)')

    for v in [5, 5.1, True, [], ""]:
        with pytest.raises(AssertionError):
            assert(_to_geometry(v))


def test_to_coord():
    assert(_to_coord({"type": "Point", "coordinates": [1, 2]}, 'x') == '1')
    assert(_to_coord({"type": "Point", "coordinates": [1.1, 2.2]}, 'x') == '1,1')
    assert(_to_coord({"type": "X", "coordinates": ["a", "b"]}, 'x') == 'a')
    assert(_to_coord(None, 'x') == '')

    assert(_to_coord({"type": "Point", "coordinates": [1, 2]}, 'y') == '2')
    assert(_to_coord({"type": "Point", "coordinates": [1.1, 2.2]}, 'y') == '2,2')
    assert(_to_coord({"type": "X", "coordinates": ["a", "b"]}, 'y') == 'b')
    assert(_to_coord(None, 'y') == '')

    for v in [(5, 'x'), (5.1, 'x'), (True, 'x'), ([], 'y'), ("", 'x')]:
        with pytest.raises(AssertionError):
            assert(_to_coord(*v))


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

def test_to_plain():
    assert(_to_plain(5) == '5')
