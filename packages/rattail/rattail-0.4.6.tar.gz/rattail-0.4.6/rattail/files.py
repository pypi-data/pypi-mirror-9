# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2014 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
File Utilities

This module contains various utility functions for use with the filesystem.
"""

from __future__ import unicode_literals

import io
import os
import os.path
import shutil
import lockfile
import tempfile
from datetime import datetime

import pkg_resources


def count_lines(path, encoding=None):
    """
    Counts the number of lines in a text file.  Some attempt is made to ensure
    cross-platform compatibility.

    :param path: Path to the file.
    :type path: string

    :param encoding: Optional encoding to be used when opening the file for
      reading.  This is passed directly to :func:`python:io.open()`.

    :returns: Number of lines in the file.
    :rtype: integer
    """
    with io.open(path, 'rt', encoding=encoding) as f:
        lines = f.read().count('\n')
    return lines


def creation_time(path):
    """
    Returns the "naive" (i.e. not timezone-aware) creation timestamp for a
    file.

    :param path: Path to the file.
    :type path: string

    :returns: The creation timestamp for the file.
    :rtype: ``datetime.datetime`` instance
    """

    time = os.path.getctime(path)
    return datetime.fromtimestamp(time)


def locking_copy(src, dst, timeout=None):
    """
    Implements a "locking" version of the standard library's
    :func:`python:shutil.copy()` function.

    This exists to provide a more atomic method for copying a file into a
    folder which is being watched by a file monitor.  The assumption is that
    the monitor is configured to watch for file "locks" and therefore only
    process files once they have had their locks removed.  See also
    :ref:`filemon-profile-watchlocks`.

    :param src: Path to the source file.
    :type src: string

    :param dst: Path to the destination file (or directory).
    :type dst: string

    :type timeout: float
    :param timeout: Number of seconds to wait for the file lock to clear, if it
       already exists.  This value may be specified as an integer or float, or
       string (which will be coerced to a float).

       .. note::
          There is no default value for the timeout, which means that by
          default, the function will wait indefinitely for the lock to clear.
    """
    # Coerce timeout to float in case it isn't already, e.g. in the case of
    # being called as a filemon action.
    if timeout is not None:
        timeout = float(timeout)

    if os.path.isdir(dst):
        fn = os.path.basename(src)
        dst = os.path.join(dst, fn)

    with lockfile.LockFile(dst, timeout=timeout):
        shutil.copy(src, dst)


def overwriting_move(src, dst):
    """
    Convenience function which is equivalent to ``shutil.move()``, except it
    will cause the destination file to be overwritten if it exists.
    """

    if os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    if os.path.exists(dst):
        os.remove(dst)
    shutil.move(src, dst)


def resource_path(path):
    """
    Obtain a resource file path, extracting the resource and/or coercing the
    path as necessary.

    :param path: May be either a package resource specifier, or a regular file
       path.
    :type path: string

    :returns: Absolute file path to the resource.
    :rtype: string

    If ``path`` is a package resource specifier, and the package containing it
    is a zipped egg, then the resource will be extracted and the resultant
    filename will be returned.
    """

    if not os.path.isabs(path) and ':' in path:
        return pkg_resources.resource_filename(*path.split(':'))
    return path


def temp_path(suffix='.tmp', prefix='rattail.', **kwargs):
    """
    Returns a path for a temporary file.

    This is a convenience function which wraps ``tempfile.mkstemp()``.  The
    meaning of the arguments is the same.
    """

    fd, path = tempfile.mkstemp(suffix, prefix, **kwargs)
    os.close(fd)
    return path
