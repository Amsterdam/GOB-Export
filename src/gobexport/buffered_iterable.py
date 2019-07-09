"""
Classes to allow buffering of iterables in local files

The output of an iterable is written into a local file
When the same iterable is requested the previous result is returned

These classes eliminate duplicate API calls
"""
import os
import shutil
import tempfile
import hashlib
import json
import functools
import ijson


class Buffer:

    READ = "READ"                  # Previously recorded data is 'replayed'
    WRITE = "WRITE"                # Data from the iterable is written into a local file
    PASS_THROUGH = "PASS_THROUGH"  # Basically a noop

    def __init__(self, name, mode):
        assert mode in [self.READ, self.WRITE, self.PASS_THROUGH], f"Unknown mode {mode}"
        self.name = name
        self.mode = mode
        self.file = None

    @classmethod
    def _get_dirname(cls):
        # Store buffers in system temp dir
        dir = tempfile.gettempdir()
        # Store in a subfolder of temp dir
        return os.path.join(dir, "buffer")

    @classmethod
    def _get_filename(cls, name):
        # Buffers are stored in a file
        # Use a hash of the name as the name of the file
        filename = hashlib.md5(name.encode('utf-8')).hexdigest()
        dirname = cls._get_dirname()
        name = os.path.join(dirname, filename)
        # Create the path if it does not already exist
        os.makedirs(os.path.dirname(name), exist_ok=True)
        # Return the name of the file
        return name

    @classmethod
    def exists(cls, name):
        filename = cls._get_filename(name)
        return (os.path.exists(filename) and os.path.isfile(filename)) is True

    @classmethod
    def clear_all(cls):
        dirname = cls._get_dirname()
        if os.path.exists(dirname):
            shutil.rmtree(dirname)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if self.file is not None:
            if self.mode == self.WRITE:
                # Close recorded data in array [..., ..., ]
                self.file.write("\n]")
            self.file.close()

    def read(self):
        assert self.mode == self.READ
        for item in ijson.items(self.file, prefix="item"):
            yield item

    def write(self, data):
        if self.mode == self.PASS_THROUGH:
            return
        assert self.mode == self.WRITE
        if not self.empty:
            # Append data to array
            self.file.write(",\n")
        self.empty = False
        json_data = json.dumps(data)
        self.file.write(json_data)

    def open(self):
        if self.mode == self.PASS_THROUGH:
            return
        filename = self._get_filename(self.name)
        if self.mode == self.READ:
            self.file = open(filename, 'r')
        elif self.mode == self.WRITE:
            # Record data in an array [..., ..., ]
            self.file = open(filename, 'w')
            self.empty = True
            self.file.write("[\n")


class BufferedIterable:

    def __init__(self, items, name, buffer_items=True):
        self.items = items                # generator
        self.name = name                  # identifying name, eg an url or query
        self.buffer_items = buffer_items  # whether or not to buffer items

        self._set_buffer_mode()

    def _set_buffer_mode(self):
        if self.buffer_items:
            # Check if a buffer already exists
            if Buffer.exists(self.name):
                self.buffer_mode = Buffer.READ   # Read previously yielded items from buffer
            else:
                self.buffer_mode = Buffer.WRITE  # Write to buffer while yielding
        else:
            self.buffer_mode = Buffer.PASS_THROUGH

    def __iter__(self):
        with Buffer(self.name, self.buffer_mode) as buffer:
            if self.buffer_mode == Buffer.READ:
                yield from buffer.read()
            else:
                for item in self.items:
                    buffer.write(item)
                    yield item

    @classmethod
    def clear_all(cls):
        Buffer.clear_all()


def with_buffered_iterable(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Clean-up any previously buffered items
        BufferedIterable.clear_all()
        # Process a sequence of API calls
        result = func(*args, **kwargs)
        # Clean-up any saved data
        BufferedIterable.clear_all()
        return result
    return wrapper
