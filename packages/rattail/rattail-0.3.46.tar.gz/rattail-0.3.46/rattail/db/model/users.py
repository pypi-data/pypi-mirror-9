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
Data Models for Users & Permissions
"""

from __future__ import unicode_literals

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from .core import Base, uuid_column, getset_factory
from .people import Person
 

class Role(Base):
    """
    Represents a role within the system; used to manage permissions.
    """

    __tablename__ = 'roles'

    uuid = uuid_column()
    name = sa.Column(sa.String(length=25), nullable=False, unique=True)

    def __repr__(self):
        return "Role(uuid={0})".format(repr(self.uuid))

    def __unicode__(self):
        return unicode(self.name or '')


class Permission(Base):
    """
    Represents permission a role has to do a particular thing.
    """

    __tablename__ = 'permissions'

    role_uuid = sa.Column(sa.String(length=32), sa.ForeignKey('roles.uuid'), primary_key=True)
    permission = sa.Column(sa.String(length=50), primary_key=True)

    def __repr__(self):
        return "Permission(role_uuid={0}, permission={1})".format(
            repr(self.role_uuid), repr(self.permission))

    def __unicode__(self):
        return unicode(self.permission or '')


Role._permissions = relationship(
    Permission, backref='role',
    cascade='save-update, merge, delete, delete-orphan')

Role.permissions = association_proxy(
    '_permissions', 'permission',
    creator=lambda p: Permission(permission=p),
    getset_factory=getset_factory)


class User(Base):
    """
    Represents a user of the system.

    This may or may not correspond to a real person, i.e. some users may exist
    solely for automated tasks.
    """

    __tablename__ = 'users'

    uuid = uuid_column()
    username = sa.Column(sa.String(length=25), nullable=False, unique=True)
    password = sa.Column(sa.String(length=60))
    salt = sa.Column(sa.String(length=29))
    person_uuid = sa.Column(sa.String(length=32), sa.ForeignKey('people.uuid'))

    active = sa.Column(sa.Boolean(), nullable=False, default=True)
    """
    Whether the user is active, e.g. allowed to log in via the UI.
    """

    def __repr__(self):
        return "User(uuid={0})".format(repr(self.uuid))

    def __unicode__(self):
        s = unicode(self.username)
        if self.person and self.person.display_name:
            s = "{0} ({1})".format(s, self.person.display_name)
        return s

    @property
    def display_name(self):
        """
        Display name for the user.
        
        Returns :attr:`Person.display_name` if available; otherwise returns
        :attr:`username`.
        """
        if self.person and self.person.display_name:
            return self.person.display_name
        return self.username


User.person = relationship(
    Person,
    back_populates='user',
    uselist=False)

Person.user = relationship(
    User,
    back_populates='person',
    uselist=False)


class UserRole(Base):
    """
    Represents the association between a :class:`User` and a :class:`Role`.
    """

    __tablename__ = 'users_roles'

    uuid = uuid_column()
    user_uuid = sa.Column(sa.String(length=32), sa.ForeignKey('users.uuid'))
    role_uuid = sa.Column(sa.String(length=32), sa.ForeignKey('roles.uuid'))

    def __repr__(self):
        return "UserRole(uuid={0})".format(repr(self.uuid))


Role._users = relationship(
    UserRole, backref='role',
    cascade='save-update, merge, delete, delete-orphan')

Role.users = association_proxy(
    '_users', 'user',
    creator=lambda u: UserRole(user=u),
    getset_factory=getset_factory)

User._roles = relationship(
    UserRole, backref='user')

User.roles = association_proxy(
    '_roles', 'role',
    creator=lambda r: UserRole(role=r),
    getset_factory=getset_factory)
