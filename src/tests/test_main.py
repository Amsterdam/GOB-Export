from unittest import mock

@mock.patch('gobexport.test.test')
@mock.patch('gobexport.export.export')
@mock.patch('gobcore.message_broker.messagedriven_service.messagedriven_service')
def test_main(mocked_messagedriven_service, mocked_export, mocked_test):

    from gobexport import __main__

    msg = {
        "catalogue": "catalogue",
        "collection": "collection",
        "any other arg": "any other arg",
        "destination": "Objectstore",
        "header": {}
    }

    __main__.handle_export_msg(msg)

    mocked_messagedriven_service.assert_called_with(__main__.SERVICEDEFINITION, "Export")
    mocked_export.assert_called_with("catalogue", "collection", "Objectstore")

    msg = {
        "catalogue": "catalogue",
        "header": {}
    }

    __main__.handle_export_test_msg(msg)

    mocked_test.assert_called_with("catalogue")
