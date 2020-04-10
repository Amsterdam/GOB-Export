from unittest import TestCase
from unittest.mock import patch, MagicMock

from gobexport.exporter.config.bag import (
    format_date,
)


def test_format_timestamp():
    assert(format_date('2035-03-31') == '2035-03-31T00:00:00')
    assert(format_date('') == None)

    for dat in ['2035-03-31T10:30:30','2035-03-31T10:30:30.0000']:
        assert(format_date(dat) == '2035-03-31T10:30:30')

    for inp in [None, 'Invalid date']:
        assert(format_date(inp) == inp)
