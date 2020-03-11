from unittest import mock

@mock.patch('gobexport.__main__.logger', mock.MagicMock())
@mock.patch('gobexport.test.test')
@mock.patch('gobexport.export.export')
@mock.patch('gobexport.dump.Dumper')
@mock.patch('gobcore.message_broker.messagedriven_service.messagedriven_service')
def test_main(mocked_messagedriven_service, mocked_dump, mocked_export, mocked_test):

    from gobexport import __main__

    msg = {
        "header": {
            "catalogue": "catalogue",
            "collection": "collection",
            "product": "csv",
            "destination": "Objectstore",
        },
        "any other arg": "any other arg",
    }

    __main__.handle_export_msg(msg)

    mocked_messagedriven_service.assert_called_with(__main__.SERVICEDEFINITION, "Export")
    mocked_export.assert_called_with(
        catalogue="catalogue",
        collection="collection",
        product="csv",
        destination="Objectstore")

    msg['header']['destination'] = "Database"
    __main__.handle_export_msg(msg)
    mocked_dump.return_value.dump_catalog_assert_called_with(
        catalogue="catalogue",
        collection="collection")

    mocked_export.reset_mock()
    mocked_dump.return_value.dump_catalog.reset_mock()

    msg['header']['destination'] = "Unkown destination"
    __main__.handle_export_msg(msg)
    mocked_export.assert_not_called()
    mocked_dump.return_value.dump_catalog_assert_not_called()

    msg = {
        "header": {
            "catalogue": "catalogue",
        }
    }

    __main__.handle_export_test_msg(msg)

    mocked_test.assert_called_with("catalogue")
