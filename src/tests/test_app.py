from unittest import TestCase, mock

from gobexport.app import handle_export_msg, handle_export_test_msg, dump_on_new_events, handle_export_dump_msg, \
    run_message_thread, get_app, SERVICEDEFINITION, run


@mock.patch('gobexport.app.logger', mock.MagicMock())
class TestApp(TestCase):

    @mock.patch('gobexport.app.get_notification')
    @mock.patch('gobexport.app.start_workflow')
    @mock.patch('gobexport.app.test')
    @mock.patch('gobexport.app.export')
    @mock.patch('gobexport.app.Dumper')
    def test_main(self, mocked_dump, mocked_export, mocked_test, mock_start_workflow, mock_get_notification):

        msg = {
            "header": {
                "catalogue": "catalogue",
                "collection": "collection",
                "product": "csv",
                "destination": "Objectstore",
            },
            "any other arg": "any other arg",
        }

        handle_export_msg(msg)

        mocked_export.assert_called_with(
            catalogue="catalogue",
            collection="collection",
            product="csv",
            destination="Objectstore")

        msg['header']['destination'] = "Database"
        handle_export_msg(msg)
        mocked_dump.return_value.dump_catalog_assert_called_with(
            catalogue="catalogue",
            collection="collection")

        mocked_export.reset_mock()
        mocked_dump.return_value.dump_catalog.reset_mock()

        msg['header']['destination'] = "Unkown destination"
        handle_export_msg(msg)
        mocked_export.assert_not_called()
        mocked_dump.return_value.dump_catalog_assert_not_called()

        msg = {
            "header": {
                "catalogue": "catalogue",
            }
        }

        handle_export_test_msg(msg)

        mocked_test.assert_called_with("catalogue")

        header = {
            'catalogue': 'any catalogue',
            'collection': 'any collection',
            'application': 'any application',
            'process_id': 'the process id',
        }

        mock_notification = mock.MagicMock()
        mock_notification.contents = {
            'last_event': [1, 1]
        }
        mock_get_notification.return_value = mock_notification
        mock_notification.header = header

        msg = 'any msg'
        dump_on_new_events(msg)
        expected_arguments = {
            'catalogue': 'any catalogue',
            'collection': 'any collection',
            'application': 'any application',
            'process_id': 'the process id',
            'destination': 'Database',
            'include_relations': False,
            'retry_time': mock.ANY
        }
        # workflow is also started if nothing has changed
        mock_start_workflow.assert_called()
        mock_start_workflow.reset_mock()
        mock_notification.contents = {
            'last_event': [1, 2]
        }
        dump_on_new_events(msg)
        mock_start_workflow.assert_called_with({'workflow_name': 'export'}, expected_arguments)

    @mock.patch("gobexport.app.Dumper")
    @mock.patch("gobexport.app.DumpNotification")
    @mock.patch("gobexport.app.add_notification")
    def test_handle_export_dump_msg(self, mock_add_notification, mock_dump_notification, mock_dumper):

        msg = {
            'header': {
                'catalogue': 'CAT',
                'collection': 'COLL',
            }
        }

        # With default values for include_relations and force_full
        handle_export_dump_msg(msg)

        mock_dumper().dump_catalog.assert_called_with(catalog_name='CAT',
                                                      collection_name='COLL',
                                                      include_relations=True,
                                                      force_full=False)

        mock_add_notification.assert_called_with(msg, mock_dump_notification.return_value)
        mock_dump_notification.assert_called_with('CAT', 'COLL')

        # Check that force_full and include_relations are passed with provided values
        msg['header']['full'] = True
        msg['header']['include_relations'] = False

        handle_export_dump_msg(msg)
        mock_dumper().dump_catalog.assert_called_with(catalog_name='CAT',
                                                      collection_name='COLL',
                                                      include_relations=False,
                                                      force_full=True)

    @mock.patch("gobexport.app.os._exit")
    @mock.patch("gobexport.app.messagedriven_service")
    def test_run_message_thread(self, mock_messagedriven_service, mock_os_exit):
        run_message_thread()

        mock_messagedriven_service.assert_called_with(SERVICEDEFINITION, "Export")

        mock_messagedriven_service.side_effect = Exception
        run_message_thread()

    @mock.patch("gobexport.app.Thread")
    @mock.patch("gobexport.app.get_flask_app")
    def test_get_app(self, mock_flask_app, mock_thread):
        self.assertEqual(mock_flask_app(), get_app())

        mock_thread.assert_called_with(target=run_message_thread)
        mock_thread().start.assert_called_once()

    @mock.patch("gobexport.app.GOB_EXPORT_API_PORT", 1234)
    @mock.patch("gobexport.app.get_app")
    def test_run(self, mock_get_app):
        mock_app = mock.MagicMock()
        mock_get_app.return_value = mock_app
        run()
        mock_app.run.assert_called_with(port=1234)
