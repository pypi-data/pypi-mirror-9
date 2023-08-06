# This file is part of the crc_nd.utils package.
# For copyright and licensing information about this package, see the
# NOTICE.txt and LICENSE.txt files in its top-level directory; they are
# available at https://github.com/crc-nd/py-utils
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.


"""
Error-related types.
"""
import string


class CallerError(object):
    """
    Represents a programming error when calling a function or method in a package or component's API.
    """

    def __init__(self, description):
        self.description = description

    def __str__(self):
        return str(self.description)

    def __repr__(self):
        return '%s("%s")' % (self.__class__.__name__, self.description)


class DescriptionTemplate(string.Template):
    """
    A CallerError description that's a template with one or more placeholders (e.g., "$identifier" or "${identifier}").
    The values of the placeholders are assigned right before the error is raised.  These values are substituted into
    the description when it's accessed as a string.
    """

    def __init__(self, template):
        super(DescriptionTemplate, self).__init__(template)
        self.placeholders = dict()

    def __str__(self):
        return self.safe_substitute(self.placeholders)

    def __repr__(self):
        return '%s("%s")' % (self.__class__.__name__, self.template)
