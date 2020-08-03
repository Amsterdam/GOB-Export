from unittest import mock, TestCase

from freezegun import freeze_time
from gobexport import __main__


@mock.patch('gobexport.__main__.logger', mock.MagicMock())
class TestMain(TestCase):

    @mock.patch("gobexport.__main__.messagedriven_service")
    def test_messagedriven_service(self, mocked_messagedriven_service):
        from gobexport import __main__ as module

        with mock.patch.object(module, '__name__', '__main__'):
            __main__.init()
            mocked_messagedriven_service.assert_called_with(__main__.SERVICEDEFINITION, "Export")


    @mock.patch('gobexport.__main__.get_notification')
    @mock.patch('gobexport.__main__.start_workflow')
    @mock.patch('gobexport.__main__.test')
    @mock.patch('gobexport.__main__.export')
    @mock.patch('gobexport.__main__.Dumper')
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

        __main__.handle_export_msg(msg)

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
        __main__.dump_on_new_events(msg)
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
        __main__.dump_on_new_events(msg)
        mock_start_workflow.assert_called_with({'workflow_name': 'export'}, expected_arguments)

    @mock.patch("gobexport.__main__.Dumper")
    @mock.patch("gobexport.__main__.DumpNotification")
    @mock.patch("gobexport.__main__.add_notification")
    def test_handle_export_dump_msg(self, mock_add_notification, mock_dump_notification, mock_dumper):

        msg = {
            'header': {
                'catalogue': 'CAT',
                'collection': 'COLL',
                'include_relations': 'TrueOrFalse'
            }
        }

        __main__.handle_export_dump_msg(msg)

        mock_dumper().dump_catalog.assert_called_with(catalog_name='CAT',
                                                      collection_name='COLL',
                                                      include_relations='TrueOrFalse')

        mock_add_notification.assert_called_with(msg, mock_dump_notification.return_value)
        mock_dump_notification.assert_called_with('CAT', 'COLL')