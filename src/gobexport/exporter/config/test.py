from gobexport.exporter.ndjson import ndjson_exporter


class TestEntityExportConfig:
    """TestEntity config

    """
    products = {
        'dat': {
            'exporter': ndjson_exporter,
            'endpoint': '/gob/test_catalogue/test_entity/',
            'filename': 'test_output.ndjson',
            'mime_type': 'application/x-ndjson',
            'format': None
        }
    }


configs = [TestEntityExportConfig]
