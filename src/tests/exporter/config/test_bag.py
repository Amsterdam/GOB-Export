from unittest import TestCase

from gobexport.exporter.config.bag import format_date


class TestFormatDate(TestCase):

    def test_format_date(self):
        dt_str = '2013-02-04T11:58:29.000'

        self.assertEqual('2013-02-04', format_date(dt_str))
        self.assertEqual('nonsense', format_date('nonsense'))
        self.assertEqual(None, format_date(None))
