from unittest import TestCase
from unittest.mock import MagicMock, patch

import os

from gobexport.buffered_iterable import Buffer, BufferedIterable

class TestBuffer(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_buffer(self):
        for mode in [Buffer.READ, Buffer.WRITE, Buffer.PASS_THROUGH]:
            buffer = Buffer("any name", mode)
            self.assertIsNotNone(buffer)
        with self.assertRaises(AssertionError):
            buffer = Buffer("any name", "any other mode")

    def test_dir_name(self):
        dirname = Buffer._get_dirname()
        self.assertEqual(dirname[-len("buffer"):], "buffer")

    @patch('gobexport.buffered_iterable.os.makedirs')
    def test_get_filename(self, mock_makedirs):
        name = "name"
        dirname = Buffer._get_dirname()
        filename = Buffer._get_filename(name)
        self.assertEqual(filename[:len(dirname)], dirname)
        mock_makedirs.assert_called()
        self.assertNotEqual(filename[-len(name):], name)

    @patch('gobexport.buffered_iterable.os.path.exists')
    @patch('gobexport.buffered_iterable.os.path.isfile')
    def test_exists(self, mock_isfile, mock_exists):
        name = "any name"
        filename = Buffer._get_filename(name)
        exists = Buffer.exists(name)
        mock_exists.assert_called_with(filename)
        mock_isfile.assert_called_with(filename)
        self.assertFalse(exists)

    def test_clear_all(self):
        dirname = Buffer._get_dirname()
        os.makedirs(dirname, exist_ok=True)
        self.assertTrue(os.path.exists(dirname))
        for i in range(10):
            Buffer.clear_all()
            self.assertFalse(os.path.exists(dirname))

    def test_read_write(self):
        Buffer.clear_all()

        items = [
            {'a': 'b'}, "any string", ['a'], 5
        ]
        name = "any name"
        buffer = Buffer(name, Buffer.WRITE)
        buffer.open()
        for item in items:
            buffer.write(item)
        buffer.close()

        buffer = Buffer(name, Buffer.READ)
        buffer.open()
        read_items = [item for item in buffer.read()]
        buffer.close()

        self.assertEqual(items, read_items)

    def test_context_manager(self):
        Buffer.clear_all()

        items = [
            {'a': 'b'}, "any string", ['a'], 5
        ]
        name = "any name"

        self.assertFalse(Buffer.exists(name))

        with Buffer(name, Buffer.WRITE) as buffer:
            for item in items:
                buffer.write(item)

        self.assertTrue(Buffer.exists(name))

        for i in range(10):
            read_items = []
            with Buffer(name, Buffer.READ) as buffer:
                read_items = [item for item in buffer.read()]

            self.assertEqual(items, read_items)

    def test_context_manager_exception(self):
        Buffer.clear_all()

        items = [
            {'a': 'b'}, "any string", ['a'], 5
        ]
        name = "any name"

        self.assertFalse(Buffer.exists(name))

        try:
            with Buffer(name, Buffer.WRITE) as buffer:
                for item in items:
                    buffer.write(item)
                raise Exception("Test exception")
        except Exception:
            pass

        self.assertFalse(Buffer.exists(name))

    def test_pass_through(self):
        Buffer.clear_all()

        name = "any name"
        self.assertFalse(Buffer.exists(name))

        buffer = Buffer("any name", Buffer.PASS_THROUGH)

        buffer.open()
        buffer.write("anything")
        buffer.close()

        self.assertFalse(Buffer.exists(name))


class MockIterable:

    def __init__(self, items):
        self.items = items
        self.yields = 0

    def __iter__(self):
        for item in self.items:
            self.yields += 1
            yield item


class TestBufferedIterable(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_iterable(self):
        BufferedIterable.clear_all()
        items = range(10)
        bi = BufferedIterable(items, "any name")
        self.assertIsNotNone(bi)

    def test_iter(self):
        BufferedIterable.clear_all()
        yields = 10
        iterable = MockIterable(range(yields))
        for i in range(10):
            bi = BufferedIterable(iterable, "any name")
            read_items = [item for item in bi]
            self.assertEqual(read_items, [i for i in range(yields)])
        self.assertEqual(iterable.yields, yields)

    def test_iter_pass(self):
        BufferedIterable.clear_all()
        yields = 10
        iterable = MockIterable(range(yields))
        n = 10
        for i in range(n):
            bi = BufferedIterable(iterable, "any name", buffer_items=False)
            read_items = [item for item in bi]
            self.assertEqual(read_items, [i for i in range(yields)])
        self.assertEqual(iterable.yields, n * yields)
