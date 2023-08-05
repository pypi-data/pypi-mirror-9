"""
Test Basic
"""
import os
import tempfile
import unittest

import rsync4python.rsync


class BasicTest(unittest.TestCase):

    def setUp(self):
        super(BasicTest, self).setUp()

    def tearDown(self):
        super(BasicTest, self).tearDown()

    def add_data_to_file(self, fileobj, datasize):
            current_position = fileobj.tell()
            fileobj.write(os.urandom(datasize))
            fileobj.seek(current_position)

    def test_basic(self):

        with tempfile.TemporaryFile() as base_data:
            self.add_data_to_file(base_data, 1024 * 1024 * 1024)
            with tempfile.TemporaryFile() as signature_data:
                rsync4python.signature(base_data, signature_data)
