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
Data Models for Employees
"""

from __future__ import unicode_literals

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.orderinglist import ordering_list

from .core import Base, uuid_column, getset_factory
from .people import Person
from .contact import PhoneNumber, EmailAddress


class Employee(Base):
    """
    Represents an employee within the organization.
    """
    __tablename__ = 'employee'
    __table_args__ = (
        sa.ForeignKeyConstraint(['person_uuid'], ['person.uuid'], name='employee_fk_person'),
        sa.UniqueConstraint('person_uuid', name='employee_uq_person'),
        )
    __versioned__ = {}

    uuid = uuid_column()
    id = sa.Column(sa.Integer())
    person_uuid = sa.Column(sa.String(length=32), nullable=False)
    status = sa.Column(sa.Integer())
    display_name = sa.Column(sa.String(length=100))

    person = relationship(Person)

    first_name = association_proxy('person', 'first_name',
                                   getset_factory=getset_factory,
                                   creator=lambda n: Person(first_name=n))
    last_name = association_proxy('person', 'last_name',
                                  getset_factory=getset_factory,
                                  creator=lambda n: Person(last_name=n))
    user = association_proxy('person', 'user')

    def __repr__(self):
        return "Employee(uuid={0})".format(repr(self.uuid))

    def __unicode__(self):
        return unicode(self.display_name or self.person)

    def add_email_address(self, address, type='Home'):
        email = EmployeeEmailAddress(address=address, type=type)
        self.emails.append(email)

    def add_phone_number(self, number, type='Home'):
        phone = EmployeePhoneNumber(number=number, type=type)
        self.phones.append(phone)


class EmployeePhoneNumber(PhoneNumber):
    """
    Represents a phone (or fax) number associated with a :class:`Employee`.
    """

    __mapper_args__ = {'polymorphic_identity': 'Employee'}


Employee.phones = relationship(
    EmployeePhoneNumber,
    backref='employee',
    primaryjoin=EmployeePhoneNumber.parent_uuid == Employee.uuid,
    foreign_keys=[EmployeePhoneNumber.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=EmployeePhoneNumber.preference,
    cascade='save-update, merge, delete, delete-orphan')

Employee.phone = relationship(
    EmployeePhoneNumber,
    primaryjoin=sa.and_(
        EmployeePhoneNumber.parent_uuid == Employee.uuid,
        EmployeePhoneNumber.preference == 1),
    foreign_keys=[EmployeePhoneNumber.parent_uuid],
    uselist=False,
    viewonly=True)


class EmployeeEmailAddress(EmailAddress):
    """
    Represents an email address associated with a :class:`Employee`.
    """

    __mapper_args__ = {'polymorphic_identity': 'Employee'}


Employee.emails = relationship(
    EmployeeEmailAddress,
    backref='employee',
    primaryjoin=EmployeeEmailAddress.parent_uuid == Employee.uuid,
    foreign_keys=[EmployeeEmailAddress.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=EmployeeEmailAddress.preference,
    cascade='save-update, merge, delete, delete-orphan')

Employee.email = relationship(
    EmployeeEmailAddress,
    primaryjoin=sa.and_(
        EmployeeEmailAddress.parent_uuid == Employee.uuid,
        EmployeeEmailAddress.preference == 1),
    foreign_keys=[EmployeeEmailAddress.parent_uuid],
    uselist=False,
    viewonly=True)
