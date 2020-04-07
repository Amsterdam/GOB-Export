from unittest import mock

@mock.patch('gobcore.logging.logger.logger', mock.MagicMock())
@mock.patch('gobcore.message_broker.notifications.listen_to_notifications', mock.MagicMock())
@mock.patch('gobcore.message_broker.notifications.get_notification')
@mock.patch('gobcore.workflow.start_workflow.start_workflow')
@mock.patch('gobexport.test.test')
@mock.patch('gobexport.export.export')
@mock.patch('gobexport.dump.Dumper')
@mock.patch('gobcore.message_broker.messagedriven_service.messagedriven_service')
def test_main(mocked_messagedriven_service, mocked_dump, mocked_export, mocked_test, mock_start_workflow, mock_get_notification):

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

    header = {
        'catalogue': 'any catalogue',
        'collection': 'any collection'
    }

    mock_notification = mock.MagicMock()
    mock_notification.contents = {
        'last_event': [1, 1]
    }
    mock_get_notification.return_value = mock_notification
    mock_notification.header = header

    msg = 'any msg'
    __main__.dump_on_new_events(msg)
    expected_arguments = {
        'catalogue': 'any catalogue',
        'collection': 'any collection',
        'destination': 'Database',
        'include_relations': False,
        'wait_if_job_already_runs': True
    }
    mock_start_workflow.assert_not_called()
    mock_notification.contents = {
        'last_event': [1, 2]
    }
    __main__.dump_on_new_events(msg)
    mock_start_workflow.assert_called_with({'workflow_name': 'export'}, expected_arguments)

