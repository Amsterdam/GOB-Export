from unittest import mock, TestCase

from gobexport import __main__


class TestMain(TestCase):

    @mock.patch("gobexport.__main__.run_app")
    def test_messagedriven_service(self, mock_run_app):
        from gobexport import __main__ as module

        with mock.patch.object(module, '__name__', '__main__'):
            __main__.init()
            mock_run_app.assert_called_once()

