from unittest import TestCase

from gobexport.exporter.config.brk2.stukdelen import StukdelenExportConfig


class TestStukdelenExportConfig(TestCase):

    def test_format_bedrag(self):
        exporter = StukdelenExportConfig()
        self.assertEqual('100', exporter.format_bedrag('100.0'))
        self.assertEqual('125', exporter.format_bedrag('124.6'))
        self.assertEqual('124', exporter.format_bedrag('124.4'))
