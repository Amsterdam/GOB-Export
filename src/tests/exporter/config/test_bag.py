from unittest import TestCase

from gobexport.exporter.config.bag import format_timestamp


class TestBagConfigHelpers(TestCase):

    def test_format_timestamp(self):
        inp = '2035-03-31T01:02:03.000000'
        outp = '2035-03-31'
        self.assertEqual(outp, format_timestamp(inp))

        for inp in ['invalid_str', None]:
            # These inputs should not change
            self.assertEqual(inp, format_timestamp(inp))
