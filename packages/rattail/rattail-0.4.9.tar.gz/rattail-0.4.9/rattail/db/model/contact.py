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
Data Models for Contact Info
"""

from __future__ import unicode_literals

import sqlalchemy as sa

from .core import Base, uuid_column


class PhoneNumber(Base):
    """
    Represents a phone (or fax) number associated with a contactable entity.
    """
    __tablename__ = 'phone'
    __versioned__ = {}

    uuid = uuid_column()
    parent_type = sa.Column(sa.String(length=20), nullable=False)
    parent_uuid = sa.Column(sa.String(length=32), nullable=False)
    preference = sa.Column(sa.Integer(), nullable=False)
    type = sa.Column(sa.String(length=15))
    number = sa.Column(sa.String(length=20), nullable=False)

    __mapper_args__ = {'polymorphic_on': parent_type}

    def __repr__(self):
        return "{0}(uuid={1})".format(
            self.__class__.__name__, repr(self.uuid))

    def __unicode__(self):
        return unicode(self.number)


class EmailAddress(Base):
    """
    Represents an email address associated with a contactable entity.
    """
    __tablename__ = 'email'
    __versioned__ = {}

    uuid = uuid_column()
    parent_type = sa.Column(sa.String(length=20), nullable=False)
    parent_uuid = sa.Column(sa.String(length=32), nullable=False)
    preference = sa.Column(sa.Integer(), nullable=False)
    type = sa.Column(sa.String(length=15))
    address = sa.Column(sa.String(length=255), nullable=False)

    __mapper_args__ = {'polymorphic_on': parent_type}

    def __repr__(self):
        return "{0}(uuid={1})".format(
            self.__class__.__name__, repr(self.uuid))

    def __unicode__(self):
        return unicode(self.address)
