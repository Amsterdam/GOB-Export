from unittest import TestCase

from gobexport.exporter.config.brk2.stukdelen import format_bedrag


class TestStukdelenExportConfig(TestCase):

    def test_format_bedrag(self):
        self.assertEqual('100', format_bedrag('100.0'))
        self.assertEqual('125', format_bedrag('124.6'))
        self.assertEqual('124', format_bedrag('124.4'))
