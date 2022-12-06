from unittest import TestCase, mock

from gobexport.app import handle_export_msg, handle_export_test_msg, \
    run_message_thread, get_app, SERVICEDEFINITION, run, LOG_HANDLERS


@mock.patch('gobexport.app.logger')
class TestApp(TestCase):

    @mock.patch('gobexport.app.test')
    @mock.patch('gobexport.app.export')
    def test_main(self, mocked_export, mocked_test, mock_logger):

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

        mocked_export.reset_mock()

        msg['header']['destination'] = "Unkown destination"
        handle_export_msg(msg)
        mocked_export.assert_not_called()

        msg = {
            "header": {
                "catalogue": "catalogue",
            }
        }

        handle_export_test_msg(msg)

        mocked_test.assert_called_with("catalogue")


    @mock.patch("gobexport.app.os._exit")
    @mock.patch("gobexport.app.messagedriven_service")
    def test_run_message_thread(self, mock_messagedriven_service, mock_os_exit, _):
        run_message_thread()

        mock_messagedriven_service.assert_called_with(SERVICEDEFINITION, "Export")

        mock_messagedriven_service.side_effect = Exception
        run_message_thread()

    @mock.patch("gobexport.app.Thread")
    @mock.patch("gobexport.app.get_flask_app")
    def test_get_app(self, mock_flask_app, mock_thread, _):
        self.assertEqual(mock_flask_app(), get_app())

        mock_thread.assert_called_with(target=run_message_thread)
        mock_thread().start.assert_called_once()

    @mock.patch("gobexport.app.GOB_EXPORT_API_PORT", 1234)
    @mock.patch("gobexport.app.get_app")
    def test_run(self, mock_get_app, _):
        mock_app = mock.MagicMock()
        mock_get_app.return_value = mock_app
        run()
        mock_app.run.assert_called_with(port=1234)
