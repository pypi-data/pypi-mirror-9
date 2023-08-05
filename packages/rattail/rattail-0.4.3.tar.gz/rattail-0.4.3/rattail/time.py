# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2015 Lance Edgar
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
Time Utilities
"""

from __future__ import unicode_literals

import datetime
import warnings

import pytz


def localtime(config, time=None, key='default'):
    """
    Return a datetime which has been localized to a particular timezone.  The
    :func:`timezone()` function will be used to obtain the timezone to which
    the time value will be localized.

    :param config: Reference to a config object.

    :param time: Optional :class:`python:datetime.datetime` instance to be
       localized.  If not provided, the current time ("now") is assumed.

    :param key: Config key to be used in determining to which timezone the time
       should be localized.
    """
    zone = timezone(config, key)
    if time is None:
        time = datetime.datetime.utcnow()
        time = pytz.utc.localize(time)
        time = zone.normalize(time.astimezone(zone))
    else:
        time = zone.localize(time)
    return time


def timezone(config, key='default'):
    """
    Return a timezone object based on the definition found in config.

    :param config: Reference to a config object.

    :param key: Config key used to determine which timezone should be returned.

    :returns: A :class:`pytz:pytz.tzinfo` instance, created using the Olson
       time zone name found in the config file.

    An example of the configuration syntax which is assumed by this function:

    .. code-block:: ini

       [rattail]

       # retrieve with: timezone(config)
       timezone.default = America/Los_Angeles

       # retrieve with: timezone(config, 'headoffice')
       timezone.headoffice = America/Chicago

       # retrieve with: timezone(config, 'satellite')
       timezone.satellite = America/New_York

    See `Wikipedia`_ for the full list of Olson time zone names.

    .. _`Wikipedia`: http://en.wikipedia.org/wiki/List_of_tz_database_time_zones
    """
    # Don't *require* the correct config option yet, so we can fall back to
    # deprecated edbob equivalent (for now).
    zone = config.get('rattail', 'timezone.{0}'.format(key))
    if zone is None and key == 'default':
        zone = config.get('rattail', 'timezone.local')
    if zone is None:
        zone = config.get('edbob.time', 'zone.{0}'.format(key))
        if zone is None and key == 'default':
            zone = config.get('edbob.time', 'zone.local')
        if zone is not None:
            warnings.warn("Configuring timezone within [edbob.time] is deprecated; "
                          "please update your config file to use the new syntax",
                          DeprecationWarning)
    if zone is None:
        # If no legacy option was set either, let's require the correct one.
        zone = config.require('rattail', 'timezone.{0}'.format(key))
    return pytz.timezone(zone)


def make_utc(time):
    """
    Convert a timezone-aware time back to a naive UTC equivalent.
    """
    utctime = pytz.utc.normalize(time.astimezone(pytz.utc))
    return utctime.replace(tzinfo=None)
