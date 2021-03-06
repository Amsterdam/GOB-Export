from gobexport.exporter.ndjson import ndjson_exporter


class TestEntityExportConfig:
    """TestEntity config

    """
    products = {
        'dat': {
            'exporter': ndjson_exporter,
            'endpoint': '/gob/public/test_catalogue/test_entity/',
            'filename': 'test_output.ndjson',
            'mime_type': 'application/x-ndjson',
            'format': None
        },
        'sec': {
            'exporter': ndjson_exporter,
            'secure_user': 'gob',
            'endpoint': '/gob/test_catalogue/secure/',
            'filename': 'test_secure.ndjson',
            'mime_type': 'application/x-ndjson',
            'format': None
        }
    }
