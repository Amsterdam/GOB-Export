from unittest import TestCase

from gobexport.exporter.config.brk.perceelnummer import PerceelnummerEsriFormat


class TestPerceelnummerEsriFormat(TestCase):

    def setUp(self) -> None:
        self.format = PerceelnummerEsriFormat()

    def test_format_rotatie(self):
        testcases = [
            (0, '0.000'),
            (-0.234435345, '-0.234'),
            (0.1299999999, '0.130'),
        ]

        for inp, outp in testcases:
            self.assertEqual(self.format.format_rotatie(inp), outp)

        invalid_testcases = [None, '']

        for testcase in invalid_testcases:
            with self.assertRaises(AssertionError):
                self.format.format_rotatie(testcase)
