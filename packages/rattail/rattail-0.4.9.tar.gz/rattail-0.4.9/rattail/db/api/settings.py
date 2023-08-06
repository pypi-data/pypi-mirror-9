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
Settings API
"""

from __future__ import unicode_literals

from .. import model


__all__ = ['get_setting', 'save_setting']


def get_setting(session, name):
    """
    Returns a setting value from the database.
    """
    setting = session.query(model.Setting).get(name)
    if setting:
        return setting.value


def save_setting(session, name, value):
    """
    Saves a setting to the database.
    """
    setting = session.query(model.Setting).get(name)
    if not setting:
        setting = model.Setting(name=name)
        session.add(setting)
    setting.value = value
