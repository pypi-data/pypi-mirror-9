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
Data Models for Customers
"""

from __future__ import unicode_literals

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.orderinglist import ordering_list

from .core import Base, uuid_column, getset_factory
from .contact import PhoneNumber, EmailAddress
from .people import Person


class Customer(Base):
    """
    Represents a customer account.

    Customer accounts may consist of more than one person, in some cases.
    """
    __tablename__ = 'customer'
    __versioned__ = {}

    uuid = uuid_column()
    id = sa.Column(sa.String(length=20))
    name = sa.Column(sa.String(length=255))
    email_preference = sa.Column(sa.Integer())

    def __repr__(self):
        return "Customer(uuid={0})".format(repr(self.uuid))

    def __unicode__(self):
        return unicode(self.name or self.person)

    def add_email_address(self, address, type='Home'):
        email = CustomerEmailAddress(address=address, type=type)
        self.emails.append(email)

    def add_phone_number(self, number, type='Home'):
        phone = CustomerPhoneNumber(number=number, type=type)
        self.phones.append(phone)


class CustomerPhoneNumber(PhoneNumber):
    """
    Represents a phone (or fax) number associated with a :class:`Customer`.
    """

    __mapper_args__ = {'polymorphic_identity': 'Customer'}


Customer.phones = relationship(
    CustomerPhoneNumber,
    backref='customer',
    primaryjoin=CustomerPhoneNumber.parent_uuid == Customer.uuid,
    foreign_keys=[CustomerPhoneNumber.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=CustomerPhoneNumber.preference,
    cascade='save-update, merge, delete, delete-orphan')

Customer.phone = relationship(
    CustomerPhoneNumber,
    primaryjoin=sa.and_(
        CustomerPhoneNumber.parent_uuid == Customer.uuid,
        CustomerPhoneNumber.preference == 1),
    foreign_keys=[CustomerPhoneNumber.parent_uuid],
    uselist=False,
    viewonly=True)


class CustomerEmailAddress(EmailAddress):
    """
    Represents an email address associated with a :class:`Customer`.
    """

    __mapper_args__ = {'polymorphic_identity': 'Customer'}


Customer.emails = relationship(
    CustomerEmailAddress,
    backref='customer',
    primaryjoin=CustomerEmailAddress.parent_uuid == Customer.uuid,
    foreign_keys=[CustomerEmailAddress.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=CustomerEmailAddress.preference,
    cascade='save-update, merge, delete, delete-orphan')

Customer.email = relationship(
    CustomerEmailAddress,
    primaryjoin=sa.and_(
        CustomerEmailAddress.parent_uuid == Customer.uuid,
        CustomerEmailAddress.preference == 1),
    foreign_keys=[CustomerEmailAddress.parent_uuid],
    uselist=False,
    viewonly=True)


class CustomerGroup(Base):
    """
    Represents an arbitrary group to which customers may belong.
    """
    __tablename__ = 'customer_group'
    __versioned__ = {}

    uuid = uuid_column()
    id = sa.Column(sa.String(length=20))
    name = sa.Column(sa.String(length=255))

    def __repr__(self):
        return "CustomerGroup(uuid={0})".format(repr(self.uuid))

    def __unicode__(self):
        return unicode(self.name or '')


class CustomerGroupAssignment(Base):
    """
    Represents the assignment of a customer to a group.
    """
    __tablename__ = 'customer_x_group'
    __table_args__ = (
        sa.ForeignKeyConstraint(['group_uuid'], ['customer_group.uuid'], name='customer_x_group_fk_group'),
        sa.ForeignKeyConstraint(['customer_uuid'], ['customer.uuid'], name='customer_x_group_fk_customer'),
        )

    uuid = uuid_column()
    customer_uuid = sa.Column(sa.String(length=32), nullable=False)
    group_uuid = sa.Column(sa.String(length=32), nullable=False)
    ordinal = sa.Column(sa.Integer(), nullable=False)

    group = relationship(CustomerGroup)

    def __repr__(self):
        return "CustomerGroupAssignment(uuid={0})".format(repr(self.uuid))


Customer._groups = relationship(
    CustomerGroupAssignment, backref='customer',
    collection_class=ordering_list('ordinal', count_from=1),
    order_by=CustomerGroupAssignment.ordinal,
    cascade='save-update, merge, delete, delete-orphan')

Customer.groups = association_proxy(
    '_groups', 'group',
    getset_factory=getset_factory,
    creator=lambda g: CustomerGroupAssignment(group=g))


class CustomerPerson(Base):
    """
    Represents the association between a person and a customer account.
    """
    __tablename__ = 'customer_x_person'
    __table_args__ = (
        sa.ForeignKeyConstraint(['customer_uuid'], ['customer.uuid'], name='customer_x_person_fk_customer'),
        sa.ForeignKeyConstraint(['person_uuid'], ['person.uuid'], name='customer_x_person_fk_person'),
        )

    uuid = uuid_column()
    customer_uuid = sa.Column(sa.String(length=32), nullable=False)
    person_uuid = sa.Column(sa.String(length=32), nullable=False)
    ordinal = sa.Column(sa.Integer(), nullable=False)

    person = relationship(Person, back_populates='_customers')

    def __repr__(self):
        return "CustomerPerson(uuid={0})".format(repr(self.uuid))


Customer._people = relationship(
    CustomerPerson, backref='customer',
    primaryjoin=CustomerPerson.customer_uuid == Customer.uuid,
    collection_class=ordering_list('ordinal', count_from=1),
    order_by=CustomerPerson.ordinal,
    cascade='save-update, merge, delete, delete-orphan')

Customer.people = association_proxy(
    '_people', 'person',
    getset_factory=getset_factory,
    creator=lambda p: CustomerPerson(person=p))

Customer._person = relationship(
    CustomerPerson,
    primaryjoin=sa.and_(
        CustomerPerson.customer_uuid == Customer.uuid,
        CustomerPerson.ordinal == 1),
    uselist=False,
    viewonly=True)

Customer.person = association_proxy(
    '_person', 'person',
    getset_factory=getset_factory)

Person._customers = relationship(CustomerPerson, back_populates='person',
                                 primaryjoin=CustomerPerson.person_uuid == Person.uuid,
                                 viewonly=True)

Person.customers = association_proxy('_customers', 'customer',
                                     getset_factory=getset_factory,
                                     creator=lambda c: CustomerPerson(customer=c))
