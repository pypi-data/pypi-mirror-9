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
Utilities
"""

from __future__ import unicode_literals

import sys

from pkg_resources import iter_entry_points

try:
    from collections import OrderedDict
except ImportError: # pragma no cover
    from ordereddict import OrderedDict


def import_module_path(module_path):
    """
    Import an arbitrary Python module.

    :param module_path: String referencing a module by its "dotted path".

    :returns: The referenced module.
    """
    if module_path in sys.modules:
        return sys.modules[module_path]
    module = __import__(module_path)

    def last_module(module, module_path):
        parts = module_path.split('.')
        parts.pop(0)
        child = getattr(module, parts[0])
        if len(parts) == 1:
            return child
        return last_module(child, '.'.join(parts))

    return last_module(module, module_path)


def load_object(specifier):
    """
    Load an arbitrary object from a module, according to a specifier.

    The specifier string should contain a dotted path to an importable module,
    followed by a colon (``':'``), followed by the name of the object to be
    loaded.  For example:

    .. code-block:: none

       rattail.files:overwriting_move

    You'll notice from this example that "object" in this context refers to any
    valid Python object, i.e. not necessarily a class instance.  The name may
    refer to a class, function, variable etc.  Once the module is imported, the
    ``getattr()`` function is used to obtain a reference to the named object;
    therefore anything supported by that method should work.

    :param specifier: Specifier string.

    :returns: The specified object.
    """
    module_path, name = specifier.split(':')
    module = import_module_path(module_path)
    return getattr(module, name)


def load_entry_points(group):
    """
    Load a set of ``setuptools``-style entry points.

    This is a convenience wrapper around ``pkg_resources.iter_entry_points()``.

    :param group: The group of entry points to be loaded.

    :returns: A dictionary whose keys are the entry point names, and values are
       the loaded entry points.
    """
    entry_points = {}
    for entry_point in iter_entry_points(group):
        entry_points[entry_point.name] = entry_point.load()
    return entry_points
