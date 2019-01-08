from gobexport.exporter.dat import dat_exporter


class TestEntityExportConfig:
    """TestEntity config

    """
    products = {
        'dat': {
            'exporter': dat_exporter,
            'endpoint': '/gob/test_catalogue/test_entity/',
            'filename': 'NAP_PEILMERK.dat',
            'mime_type': 'plain/text',
            'format': '|integer:plain|decimal:plain|character:plain|string:plain|date:plain|point:plain|boolean:plain|'
        }
    }
