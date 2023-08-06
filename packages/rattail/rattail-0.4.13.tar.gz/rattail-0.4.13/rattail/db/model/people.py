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
Data Models for People
"""

from __future__ import unicode_literals

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.ext.orderinglist import ordering_list

from .core import Base, uuid_column
from .contact import PhoneNumber, EmailAddress


def get_person_display_name(context):
    """
    Provides a default value for `Person.display_name`.
    """
    first_name = context.current_parameters.get('first_name')
    last_name = context.current_parameters.get('last_name')
    if first_name and last_name:
        return first_name + ' ' + last_name
    if first_name:
        return first_name
    if last_name:
        return last_name
    return None


class Person(Base):
    """
    Represents a real, living and breathing person.

    (Or, at least was previously living and breathing, in the case of the
    deceased.)
    """
    __tablename__ = 'person'
    __versioned__ = {}

    uuid = uuid_column()
    first_name = sa.Column(sa.String(length=50))
    last_name = sa.Column(sa.String(length=50))
    display_name = sa.Column(sa.String(length=100), default=get_person_display_name)

    def __repr__(self):
        return "Person(uuid={0})".format(repr(self.uuid))

    def __unicode__(self):
        return unicode(self.display_name or '')

    def add_email_address(self, address, type='Home'):
        email = PersonEmailAddress(address=address, type=type)
        self.emails.append(email)

    def add_phone_number(self, number, type='Home'):
        phone = PersonPhoneNumber(number=number, type=type)
        self.phones.append(phone)


class PersonPhoneNumber(PhoneNumber):
    """
    Represents a phone (or fax) number associated with a person.
    """

    __mapper_args__ = {'polymorphic_identity': 'Person'}


Person.phones = relationship(
    PersonPhoneNumber,
    backref='person',
    primaryjoin=PersonPhoneNumber.parent_uuid == Person.uuid,
    foreign_keys=[PersonPhoneNumber.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=PersonPhoneNumber.preference,
    cascade='save-update, merge, delete, delete-orphan')

Person.phone = relationship(
    PersonPhoneNumber,
    primaryjoin=sa.and_(
        PersonPhoneNumber.parent_uuid == Person.uuid,
        PersonPhoneNumber.preference == 1,
        ),
    foreign_keys=[PersonPhoneNumber.parent_uuid],
    uselist=False,
    viewonly=True)


class PersonEmailAddress(EmailAddress):
    """
    Represents an email address associated with a person.
    """

    __mapper_args__ = {'polymorphic_identity': 'Person'}


Person.emails = relationship(
    PersonEmailAddress,
    backref='person',
    primaryjoin=PersonEmailAddress.parent_uuid == Person.uuid,
    foreign_keys=[PersonEmailAddress.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=PersonEmailAddress.preference,
    cascade='save-update, merge, delete, delete-orphan')

Person.email = relationship(
    PersonEmailAddress,
    primaryjoin=sa.and_(
        PersonEmailAddress.parent_uuid == Person.uuid,
        PersonEmailAddress.preference == 1,
        ),
    foreign_keys=[PersonEmailAddress.parent_uuid],
    uselist=False,
    viewonly=True)
