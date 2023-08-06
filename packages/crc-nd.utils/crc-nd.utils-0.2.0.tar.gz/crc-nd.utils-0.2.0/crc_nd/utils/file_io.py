# This file is part of the crc_nd.utils package.
# For copyright and licensing information about this package, see the
# NOTICE.txt and LICENSE.txt files in its top-level directory; they are
# available at https://github.com/crc-nd/py-utils
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License (MPL), version 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.


from path import path


def clean_out_dir(directory):
    """
    Delete all the files and subdirectories in a directory.
    """
    if not isinstance(directory, path):
        directory = path(directory)
    for file_path in directory.files():
        file_path.remove()
    for dir_path in directory.dirs():
        dir_path.rmtree()