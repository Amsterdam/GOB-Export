from unittest import TestCase, mock

from gobexport.export import _with_retries

class SucceedAfterNTimes():

    def __init__(self, n_tries):
        self.n_tries = n_tries
        self.n_exec = 0

    def f(self, value, exc):
        self.n_exec += 1
        self.n_tries -= 1
        if self.n_tries > 0:
            raise exc
        return value

class TestRetries(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_no_exec(self):
        # No execution
        result = _with_retries(lambda: 0, 0, 0, Exception)
        self.assertIsNone(result)

    def test_no_exception(self):
        result = _with_retries(lambda: 0, 1, 0, Exception)
        self.assertEqual(result, 0)

        result = _with_retries(lambda: 0, 2, 0, Exception)
        self.assertEqual(result, 0)

    @mock.patch('gobexport.export.logger', mock.MagicMock())
    def test_exception(self):
        # retries is sufficient
        test_retry = SucceedAfterNTimes(2)
        method = lambda: test_retry.f("result", KeyError)
        result = _with_retries(method, 2, 0, KeyError)
        self.assertEqual(result, "result")
        self.assertEqual(test_retry.n_exec, 2)

        # retries is not sufficient
        test_retry = SucceedAfterNTimes(2)
        method = lambda: test_retry.f("result", KeyError)
        with self.assertRaises(KeyError):
            result = _with_retries(method, 1, 0, KeyError)
        self.assertEqual(test_retry.n_exec, 1)

        # Only catch the given exception
        test_retry = SucceedAfterNTimes(2)
        method = lambda: test_retry.f("result", AttributeError)
        with self.assertRaises(AttributeError):
            result = _with_retries(method, 1, 0, KeyError)
        self.assertEqual(test_retry.n_exec, 1)
