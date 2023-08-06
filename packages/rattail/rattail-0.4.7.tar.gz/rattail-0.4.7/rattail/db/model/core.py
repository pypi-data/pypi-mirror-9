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
Data Models
"""

from __future__ import unicode_literals

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

from rattail.core import Object

# These are imported because most sibling modules import them *from* here (if
# that makes sense).  Probably need to think harder about the "best" place for
# these things to live.
from rattail.db.core import uuid_column, getset_factory
from rattail.db.types import GPCType


Base = declarative_base(cls=Object)


class Setting(Base):
    """
    Represents a setting stored within the database.
    """

    __tablename__ = 'setting'

    name = sa.Column(sa.String(length=255), primary_key=True)
    value = sa.Column(sa.Text())

    def __repr__(self):
        return "Setting(name={0})".format(repr(self.name))

    def __unicode__(self):
        return unicode(self.name or '')


class Change(Base):
    """
    Represents a changed (or deleted) record, which is pending synchronization
    to another database.
    """

    __tablename__ = 'change'

    class_name = sa.Column(sa.String(length=25), primary_key=True)
    uuid = sa.Column(sa.String(length=32), primary_key=True)
    deleted = sa.Column(sa.Boolean())

    def __repr__(self):
        return "Change(class_name={0}, uuid={1})".format(
            repr(self.class_name), repr(self.uuid))
