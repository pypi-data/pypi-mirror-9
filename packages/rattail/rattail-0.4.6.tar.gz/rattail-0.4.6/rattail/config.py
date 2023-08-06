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
Configuration Utilities
"""

from __future__ import unicode_literals

import sys
import shlex

from edbob.configuration import AppConfigParser


def parse_list(value):
    """
    Parse a configuration value, splitting by whitespace and/or commas and
    taking quoting into account, etc., yielding a list of strings.
    """
    if value is None:
        return []
    # Per the shlex docs (https://docs.python.org/2/library/shlex.html):
    # "Prior to Python 2.7.3, this module did not support Unicode input."
    if sys.version_info < (2, 7, 3) and isinstance(value, unicode): # pragma: no cover
        value = value.encode(u'utf-8')
    parser = shlex.shlex(value)
    parser.whitespace += u','
    parser.whitespace_split = True
    values = list(parser)
    for i, value in enumerate(values):
        if value.startswith(u'"') and value.endswith(u'"'):
            values[i] = value[1:-1]
    return values


class RattailConfig(object):
    """
    Rattail configuration object.  Represents the sum total of configuration in
    effect for a running app.  This is essentially a thin wrapper over the
    standard library's ``ConfigParser`` class(es); in fact any attribute not
    found in this class will fall back to the parser.

    .. warning::
       This API should hardly be considered stable.
    """

    def __init__(self, parser=None):
        """
        Create a config object.  You may optionally specify the config parser
        instance; if none is provided then an instance of
        ``edbob.configuration.AppConfigParser`` will be created.
        """
        if parser is None:
            parser = AppConfigParser('rattail')
        self.parser = parser

    def __getattr__(self, name):
        return getattr(self.parser, name)

    def setdefault(self, section, option, value):
        """
        Sets a default value for given section and option, if no value exists
        there yet.  The final value (whether pre-existing or newly-set) is
        returned.
        """
        exists = True           # start by assuming value exists
        if not self.parser.has_section(section):
            self.parser.add_section(section)
            exists = False
        elif not self.parser.has_option(section, option):
            exists = False
        if not exists:
            self.parser.set(section, option, value)
        return self.parser.get(section, option)
