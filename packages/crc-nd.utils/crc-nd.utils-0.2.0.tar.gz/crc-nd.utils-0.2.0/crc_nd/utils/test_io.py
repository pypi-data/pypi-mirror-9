# This file is part of the crc_nd.utils package.
# For copyright and licensing information about this package, see the
# NOTICE.txt and LICENSE.txt files in its top-level directory; they are
# available at https://github.com/crc-nd/py-utils
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.


import unittest

from path import path

from .file_io import clean_out_dir


class WritesOutputFiles(unittest.TestCase):
    """
    Mixin class for tests that write output data to the file system.
    """

    @classmethod
    def set_output_root(cls, output_root):
        """
        Set the root directory where the test output directories will be created.
        """
        if not isinstance(output_root, path):
            output_root = path(output_root)
        cls.output_root = output_root

    def get_output_dir(self):
        """
        Get the path to the output directory for the current unit test (i.e., test method).
        It'll be the output_root / TEST_CASE_NAME / TEST_METHOD_NAME
        """
        test_case, test_method = self.id().split('.')[-2:]
        output_dir = self.output_root / test_case / test_method
        return output_dir

    def initialize_output_dir(self):
        """
        Initialize the output directory for the current test.  If the directory does not exist, then create it.
        If the directory does exist, then remove all its contents.
        """
        output_dir = self.get_output_dir()
        if output_dir.exists():
            if output_dir.isfile():
                self.fail('"%s" is not a directory' % output_dir)
            else:
                clean_out_dir(output_dir)
        else:
            output_dir.makedirs()
