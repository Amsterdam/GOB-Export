from gobexport.exporter.config.bgt import format_guid


def test_format_guid():
    assert format_guid("abc") == "{abc}"
