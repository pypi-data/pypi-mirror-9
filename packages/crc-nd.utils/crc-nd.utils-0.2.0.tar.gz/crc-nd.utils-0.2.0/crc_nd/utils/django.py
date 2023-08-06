# This file is part of the crc_nd.utils package.
# For copyright and licensing information about this package, see the
# NOTICE.txt and LICENSE.txt files in its top-level directory; they are
# available at https://github.com/crc-nd/py-utils
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.


"""
Helper functions
"""


def make_choices_tuple(choices, get_display_name):
    """
    Make a tuple for the choices parameter for a data model field.

    :param choices: sequence of valid values for the model field
    :param get_display_name: callable that returns the human-readable name for a choice

    :return: A tuple of 2-tuples (choice, display_name) suitable for the choices parameter
    """
    assert callable(get_display_name)
    return tuple((x, get_display_name(x)) for x in choices)