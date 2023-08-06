# This file is part of the crc_nd.utils package.
# For copyright and licensing information about this package, see the
# NOTICE.txt and LICENSE.txt files in its top-level directory; they are
# available at https://github.com/crc-nd/py-utils
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.


"""
Mixin classes for testing errors.
"""

import unittest


class CallerErrorMixin(unittest.TestCase):
    """
    Mixin for test suites that will check for CallerError objects when AssertionErrors are raised.
    """

    def assertCallerError(self, expected_arg0, callable_obj, *args, **kwargs):
        """
        Assert that a callable raises an AssertionError with a particular argument.

        :param expected_arg0: The expected value for the AssertionError instance's first argument
                              (i.e., instance.args[0]).
        """
        try:
            callable_obj(*args, **kwargs)
            self.fail('Expected AssertionError, but no exception raised')
        except AssertionError, exc:
            self.assertEqual(exc.args[0], expected_arg0)
        except Exception, exc:
            self.fail('Expected AssertionError, but got %s' % repr(exc))