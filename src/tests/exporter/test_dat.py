from unittest import TestCase

from gobexport.exporter.dat import dat_exporter


class TestDatExporter(TestCase):

    def test_append_raises_notimplementederror(self):

        with self.assertRaises(NotImplementedError):
            dat_exporter([], '', append=True)
