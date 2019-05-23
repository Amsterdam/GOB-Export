from unittest import TestCase

from gobexport.exporter.esri import esri_exporter


class TestEsriExporter(TestCase):

    def test_append_raises_notimplementederror(self):
        with self.assertRaises(NotImplementedError):
            esri_exporter([], '', append=True)
