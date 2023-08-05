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
Data Models
"""

from __future__ import unicode_literals

import re
import datetime
import logging

import sqlalchemy as sa
from sqlalchemy import Column, ForeignKey
from sqlalchemy import String, Integer, Numeric, DateTime, Date, Boolean, Text
from sqlalchemy import and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, object_session
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.orderinglist import ordering_list

from ..core import Object
from .core import uuid_column, getset_factory
from .types import GPCType
from rattail.util import load_object


Base = declarative_base(cls=Object)

log = logging.getLogger(__name__)


class Setting(Base):
    """
    Represents a setting stored within the database.
    """

    __tablename__ = 'settings'

    name = Column(String(length=255), primary_key=True)
    value = Column(Text())

    def __repr__(self):
        return "Setting(name={0})".format(repr(self.name))

    def __unicode__(self):
        return unicode(self.name or '')


class Change(Base):
    """
    Represents a changed (or deleted) record, which is pending synchronization
    to another database.
    """

    __tablename__ = 'changes'

    class_name = Column(String(length=25), primary_key=True)
    uuid = Column(String(length=32), primary_key=True)
    deleted = Column(Boolean())

    def __repr__(self):
        return "Change(class_name={0}, uuid={1})".format(
            repr(self.class_name), repr(self.uuid))


class PhoneNumber(Base):
    """
    Represents a phone (or fax) number associated with a contactable entity.
    """

    __tablename__ = 'phone_numbers'

    uuid = uuid_column()
    parent_type = Column(String(length=20), nullable=False)
    parent_uuid = Column(String(length=32), nullable=False)
    preference = Column(Integer(), nullable=False)
    type = Column(String(length=15))
    number = Column(String(length=20), nullable=False)

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

    __tablename__ = 'email_addresses'

    uuid = uuid_column()
    parent_type = Column(String(length=20), nullable=False)
    parent_uuid = Column(String(length=32), nullable=False)
    preference = Column(Integer(), nullable=False)
    type = Column(String(length=15))
    address = Column(String(length=255), nullable=False)

    __mapper_args__ = {'polymorphic_on': parent_type}

    def __repr__(self):
        return "{0}(uuid={1})".format(
            self.__class__.__name__, repr(self.uuid))

    def __unicode__(self):
        return unicode(self.address)


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

    __tablename__ = 'people'

    uuid = uuid_column()
    first_name = Column(String(length=50))
    last_name = Column(String(length=50))
    display_name = Column(String(length=100), default=get_person_display_name)

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
    primaryjoin=and_(
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
    primaryjoin=and_(
        PersonEmailAddress.parent_uuid == Person.uuid,
        PersonEmailAddress.preference == 1,
        ),
    foreign_keys=[PersonEmailAddress.parent_uuid],
    uselist=False,
    viewonly=True)


class Role(Base):
    """
    Represents a role within the system; used to manage permissions.
    """

    __tablename__ = 'roles'

    uuid = uuid_column()
    name = Column(String(length=25), nullable=False, unique=True)

    def __repr__(self):
        return "Role(uuid={0})".format(repr(self.uuid))

    def __unicode__(self):
        return unicode(self.name or '')


class Permission(Base):
    """
    Represents permission a role has to do a particular thing.
    """

    __tablename__ = 'permissions'

    role_uuid = Column(String(length=32), ForeignKey('roles.uuid'), primary_key=True)
    permission = Column(String(length=50), primary_key=True)

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
    username = Column(String(length=25), nullable=False, unique=True)
    password = Column(String(length=60))
    salt = Column(String(length=29))
    person_uuid = Column(String(length=32), ForeignKey('people.uuid'))

    active = sa.Column(sa.Boolean(), nullable=False, default=True)
    """
    Whether the user is active, e.g. allowed to log in via the UI.
    """

    def __repr__(self):
        return "User(uuid={0})".format(repr(self.uuid))

    def __unicode__(self):
        return unicode(self.username or '')

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
    user_uuid = Column(String(length=32), ForeignKey('users.uuid'))
    role_uuid = Column(String(length=32), ForeignKey('roles.uuid'))

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


class Store(Base):
    """
    Represents a store (physical or otherwise) within the organization.
    """

    __tablename__ = 'stores'

    uuid = uuid_column()
    id = Column(String(length=10))
    name = Column(String(length=100))
    database_key = sa.Column(sa.String(length=30))

    def __repr__(self):
        return "Store(uuid={0})".format(repr(self.uuid))

    def __unicode__(self):
        return unicode(self.name or '')

    def add_email_address(self, address, type='Info'):
        email = StoreEmailAddress(address=address, type=type)
        self.emails.append(email)

    def add_phone_number(self, number, type='Voice'):
        phone = StorePhoneNumber(number=number, type=type)
        self.phones.append(phone)


class StorePhoneNumber(PhoneNumber):
    """
    Represents a phone (or fax) number associated with a store.
    """

    __mapper_args__ = {'polymorphic_identity': 'Store'}


Store.phones = relationship(
    StorePhoneNumber,
    backref='store',
    primaryjoin=StorePhoneNumber.parent_uuid == Store.uuid,
    foreign_keys=[StorePhoneNumber.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=StorePhoneNumber.preference,
    cascade='save-update, merge, delete, delete-orphan')

Store.phone = relationship(
    StorePhoneNumber,
    primaryjoin=and_(
        StorePhoneNumber.parent_uuid == Store.uuid,
        StorePhoneNumber.preference == 1),
    foreign_keys=[StorePhoneNumber.parent_uuid],
    uselist=False,
    viewonly=True)


class StoreEmailAddress(EmailAddress):
    """
    Represents an email address associated with a store.
    """

    __mapper_args__ = {'polymorphic_identity': 'Store'}


Store.emails = relationship(
    StoreEmailAddress,
    backref='store',
    primaryjoin=StoreEmailAddress.parent_uuid == Store.uuid,
    foreign_keys=[StoreEmailAddress.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=StoreEmailAddress.preference,
    cascade='save-update, merge, delete, delete-orphan')

Store.email = relationship(
    StoreEmailAddress,
    primaryjoin=and_(
        StoreEmailAddress.parent_uuid == Store.uuid,
        StoreEmailAddress.preference == 1),
    foreign_keys=[StoreEmailAddress.parent_uuid],
    uselist=False,
    viewonly=True)


class Department(Base):
    """
    Represents an organizational department.
    """

    __tablename__ = 'departments'

    uuid = uuid_column()
    number = Column(Integer())
    name = Column(String(length=30))

    def __repr__(self):
        return "Department(uuid={0})".format(repr(self.uuid))

    def __unicode__(self):
        return unicode(self.name or '')


class Subdepartment(Base):
    """
    Represents an organizational subdepartment.
    """

    __tablename__ = 'subdepartments'

    uuid = uuid_column()
    number = Column(Integer())
    name = Column(String(length=30))
    department_uuid = Column(String(length=32), ForeignKey('departments.uuid'))

    def __repr__(self):
        return "Subdepartment(uuid={0})".format(repr(self.uuid))

    def __unicode__(self):
        return unicode(self.name or '')


Department.subdepartments = relationship(
    Subdepartment,
    backref='department',
    order_by=Subdepartment.name)


class Category(Base):
    """
    Represents an organizational category for products.
    """

    __tablename__ = 'categories'

    uuid = uuid_column()
    number = Column(Integer())
    name = Column(String(length=50))
    department_uuid = Column(String(length=32), ForeignKey('departments.uuid'))

    department = relationship(Department)

    def __repr__(self):
        return "Category(uuid={0})".format(repr(self.uuid))

    def __unicode__(self):
        return unicode(self.name or '')


class Family(Base):
    """
    Represents an organizational family for products.
    """

    __tablename__ = 'families'

    uuid = uuid_column()
    code = Column(Integer())
    name = Column(String(length=50))

    products = relationship(
        u'Product', back_populates=u'family', doc=u"""\
Collection of :class:`Product` instances which associate with this family.
""")

    def __repr__(self):
        return "Family(uuid={0})".format(repr(self.uuid))

    def __unicode__(self):
        return unicode(self.name or '')


class ReportCode(Base):
    """
    Represents an organizational "report code" for products.
    """
    __tablename__ = u'report_codes'
    __table_args__ = (
        sa.PrimaryKeyConstraint(u'uuid', name=u'report_codes_pk_uuid'),
        sa.UniqueConstraint(u'code', name=u'report_codes_uq_code'),
        )

    uuid = uuid_column()
    code = sa.Column(sa.Integer(), nullable=False)
    name = sa.Column(sa.String(length=50), nullable=True)

    products = relationship(
        u'Product', back_populates=u'report_code', doc=u"""\
Collection of :class:`Product` instances which associate with this report code.
""")

    def __repr__(self):
        return u"ReportCode(uuid={0})".format(repr(self.uuid)).encode(u'utf_8')

    def __unicode__(self):
        return u"{0} - {1}".format(self.code, self.name or u'')


class Brand(Base):
    """
    Represents a brand or similar product line.
    """

    __tablename__ = 'brands'

    uuid = uuid_column()
    name = Column(String(length=100))

    def __repr__(self):
        return "Brand(uuid={0})".format(repr(self.uuid))

    def __unicode__(self):
        return unicode(self.name or '')


class Vendor(Base):
    """
    Represents a vendor from which products are purchased by the store.
    """

    __tablename__ = 'vendors'

    uuid = uuid_column()
    id = Column(String(length=15))
    name = Column(String(length=40))
    special_discount = Column(Numeric(precision=5, scale=3))

    def __repr__(self):
        return "Vendor(uuid={0})".format(repr(self.uuid))

    def __unicode__(self):
        return unicode(self.name or '')

    def add_email_address(self, address, type='Info'):
        email = VendorEmailAddress(address=address, type=type)
        self.emails.append(email)

    def add_phone_number(self, number, type='Voice'):
        phone = VendorPhoneNumber(number=number, type=type)
        self.phones.append(phone)

    
class VendorPhoneNumber(PhoneNumber):
    """
    Represents a phone (or fax) number associated with a vendor.
    """

    __mapper_args__ = {'polymorphic_identity': 'Vendor'}


Vendor.phones = relationship(
    VendorPhoneNumber,
    backref='vendor',
    primaryjoin=VendorPhoneNumber.parent_uuid == Vendor.uuid,
    foreign_keys=[VendorPhoneNumber.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=VendorPhoneNumber.preference,
    cascade='save-update, merge, delete, delete-orphan')

Vendor.phone = relationship(
    VendorPhoneNumber,
    primaryjoin=and_(
        VendorPhoneNumber.parent_uuid == Vendor.uuid,
        VendorPhoneNumber.preference == 1),
    foreign_keys=[VendorPhoneNumber.parent_uuid],
    uselist=False,
    viewonly=True)


class VendorEmailAddress(EmailAddress):
    """
    Represents an email address associated with a vendor.
    """

    __mapper_args__ = {'polymorphic_identity': 'Vendor'}


Vendor.emails = relationship(
    VendorEmailAddress,
    backref='vendor',
    primaryjoin=VendorEmailAddress.parent_uuid == Vendor.uuid,
    foreign_keys=[VendorEmailAddress.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=VendorEmailAddress.preference,
    cascade='save-update, merge, delete, delete-orphan')

Vendor.email = relationship(
    VendorEmailAddress,
    primaryjoin=and_(
        VendorEmailAddress.parent_uuid == Vendor.uuid,
        VendorEmailAddress.preference == 1),
    foreign_keys=[VendorEmailAddress.parent_uuid],
    uselist=False,
    viewonly=True)


class VendorContact(Base):
    """
    Represents a point of contact (e.g. salesperson) for a vendor.
    """

    __tablename__ = 'vendor_contacts'

    uuid = uuid_column()
    vendor_uuid = Column(String(length=32), ForeignKey('vendors.uuid'), nullable=False)
    person_uuid = Column(String(length=32), ForeignKey('people.uuid'), nullable=False)
    preference = Column(Integer(), nullable=False)

    person = relationship(Person)

    def __repr__(self):
        return "VendorContact(uuid={0})".format(repr(self.uuid))

    def __unicode__(self):
        return unicode(self.person)


Vendor._contacts = relationship(
    VendorContact, backref='vendor',
    collection_class=ordering_list('preference', count_from=1),
    order_by=VendorContact.preference,
    cascade='save-update, merge, delete, delete-orphan')

Vendor.contacts = association_proxy(
    '_contacts', 'person',
    getset_factory=getset_factory,
    creator=lambda p: VendorContact(person=p))

Vendor._contact = relationship(
    VendorContact,
    primaryjoin=and_(
        VendorContact.vendor_uuid == Vendor.uuid,
        VendorContact.preference == 1),
    uselist=False,
    viewonly=True)

Vendor.contact = association_proxy(
    '_contact', 'person',
    getset_factory=getset_factory)


class Product(Base):
    """
    Represents a product for sale and/or purchase.
    """
    __tablename__ = u'products'
    __table_args__ = (
        sa.ForeignKeyConstraint([u'report_code_uuid'], [u'report_codes.uuid'], name=u'products_fk_report_code_uuid'),
        )

    uuid = uuid_column()
    upc = Column(GPCType(), index=True)
    department_uuid = Column(String(length=32), ForeignKey('departments.uuid'))
    subdepartment_uuid = Column(String(length=32), ForeignKey('subdepartments.uuid'))
    category_uuid = Column(String(length=32), ForeignKey('categories.uuid'))
    family_uuid = Column(String(length=32), ForeignKey('families.uuid'))

    report_code_uuid = sa.Column(sa.String(length=32), nullable=True, doc=u"""\
UUID of the product's report code, if any.
""")

    brand_uuid = Column(String(length=32), ForeignKey('brands.uuid'))
    description = Column(String(length=60))
    description2 = Column(String(length=60))
    size = Column(String(length=30))
    unit_of_measure = Column(String(length=4))

    not_for_sale = sa.Column(sa.Boolean(), nullable=False, default=False, doc="""
Flag to indicate items which are not available for sale.
""")

    regular_price_uuid = Column(
        String(length=32),
        ForeignKey('product_prices.uuid',
                   use_alter=True,
                   name='products_regular_price_uuid_fkey'))

    current_price_uuid = Column(
        String(length=32),
        ForeignKey('product_prices.uuid',
                   use_alter=True,
                   name='products_current_price_uuid_fkey'))

    department = relationship(Department, order_by=Department.name)
    subdepartment = relationship(Subdepartment, order_by=Subdepartment.name)
    category = relationship(Category)
    brand = relationship(Brand)

    family = relationship(
        u'Family', back_populates=u'products', doc=u"""\
Reference to the :class:`Family` instance with which the product associates, if
any.
""")

    report_code = relationship(
        u'ReportCode', back_populates=u'products', doc=u"""\
Reference to the :class:`ReportCode` instance with which the product
associates, if any.
""")

    def __repr__(self):
        return "Product(uuid={0})".format(repr(self.uuid))

    def __unicode__(self):
        return unicode(self.description or '')

    @property
    def full_description(self):
        """
        Convenience attribute which returns a more complete description.

        Most notably, this includes the brand name and product size.
        """
        fields = [
            self.brand.name if self.brand else '',
            self.description or '',
            self.size or '']
        fields = [f.strip() for f in fields if f.strip()]
        return ' '.join(fields)


class ProductCode(Base):
    """
    Represents an arbitrary "code" for a product.
    """

    __tablename__ = 'product_codes'

    uuid = uuid_column()
    product_uuid = Column(String(length=32), ForeignKey('products.uuid'), nullable=False)
    ordinal = Column(Integer(), nullable=False)
    code = Column(String(length=20))

    def __repr__(self):
        return "ProductCode(uuid={0})".format(repr(self.uuid))


Product._codes = relationship(
    ProductCode, backref='product',
    collection_class=ordering_list('ordinal', count_from=1),
    order_by=ProductCode.ordinal,
    cascade='save-update, merge, delete, delete-orphan')

Product.codes = association_proxy(
    '_codes', 'code',
    getset_factory=getset_factory,
    creator=lambda c: ProductCode(code=c))

Product._code = relationship(
    ProductCode,
    primaryjoin=and_(
        ProductCode.product_uuid == Product.uuid,
        ProductCode.ordinal == 1,
        ),
    uselist=False,
    viewonly=True)

Product.code = association_proxy(
    '_code', 'code',
    getset_factory=getset_factory)


class ProductCost(Base):
    """
    Represents a source from which a product may be obtained via purchase.
    """

    __tablename__ = 'product_costs'

    uuid = uuid_column()
    product_uuid = Column(String(length=32), ForeignKey('products.uuid'), nullable=False)
    vendor_uuid = Column(String(length=32), ForeignKey('vendors.uuid'), nullable=False)
    preference = Column(Integer(), nullable=False)
    code = Column(String(length=15))

    case_size = Column(Integer())
    case_cost = Column(Numeric(precision=9, scale=5))
    pack_size = Column(Integer())
    pack_cost = Column(Numeric(precision=9, scale=5))
    unit_cost = Column(Numeric(precision=9, scale=5))
    effective = Column(DateTime())

    vendor = relationship(Vendor)

    def __repr__(self):
        return "ProductCost(uuid={0})".format(repr(self.uuid))


Product.costs = relationship(
    ProductCost, backref='product',
    collection_class=ordering_list('preference', count_from=1),
    order_by=ProductCost.preference,
    cascade='save-update, merge, delete, delete-orphan')

Product.cost = relationship(
    ProductCost,
    primaryjoin=and_(
        ProductCost.product_uuid == Product.uuid,
        ProductCost.preference == 1,
        ),
    uselist=False,
    viewonly=True)

Product.vendor = relationship(
    Vendor,
    secondary=ProductCost.__table__,
    primaryjoin=and_(
        ProductCost.product_uuid == Product.uuid,
        ProductCost.preference == 1,
        ),
    secondaryjoin=Vendor.uuid == ProductCost.vendor_uuid,
    uselist=False,
    viewonly=True)


class ProductPrice(Base):
    """
    Represents a price for a product.
    """

    __tablename__ = 'product_prices'

    uuid = uuid_column()
    product_uuid = Column(String(length=32), ForeignKey('products.uuid'), nullable=False)
    type = Column(Integer())
    level = Column(Integer())
    starts = Column(DateTime())
    ends = Column(DateTime())
    price = Column(Numeric(precision=8, scale=3))
    multiple = Column(Integer())
    pack_price = Column(Numeric(precision=8, scale=3))
    pack_multiple = Column(Integer())

    def __repr__(self):
        return "ProductPrice(uuid={0})".format(repr(self.uuid))


Product.prices = relationship(
    ProductPrice, backref='product',
    primaryjoin=ProductPrice.product_uuid == Product.uuid,
    cascade='save-update, merge, delete, delete-orphan')

Product.regular_price = relationship(
    ProductPrice,
    primaryjoin=Product.regular_price_uuid == ProductPrice.uuid,
    lazy='joined',
    post_update=True)

Product.current_price = relationship(
    ProductPrice,
    primaryjoin=Product.current_price_uuid == ProductPrice.uuid,
    lazy='joined',
    post_update=True)


class Customer(Base):
    """
    Represents a customer account.

    Customer accounts may consist of more than one person, in some cases.
    """

    __tablename__ = 'customers'

    uuid = uuid_column()
    id = Column(String(length=20))
    name = Column(String(length=255))
    email_preference = Column(Integer())

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
    primaryjoin=and_(
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
    primaryjoin=and_(
        CustomerEmailAddress.parent_uuid == Customer.uuid,
        CustomerEmailAddress.preference == 1),
    foreign_keys=[CustomerEmailAddress.parent_uuid],
    uselist=False,
    viewonly=True)


class CustomerGroup(Base):
    """
    Represents an arbitrary group to which customers may belong.
    """

    __tablename__ = 'customer_groups'

    uuid = uuid_column()
    id = Column(String(length=20))
    name = Column(String(length=255))

    def __repr__(self):
        return "CustomerGroup(uuid={0})".format(repr(self.uuid))

    def __unicode__(self):
        return unicode(self.name or '')


class CustomerGroupAssignment(Base):
    """
    Represents the assignment of a customer to a group.
    """

    __tablename__ = 'customers_groups'

    uuid = uuid_column()
    customer_uuid = Column(String(length=32), ForeignKey('customers.uuid'), nullable=False)
    group_uuid = Column(String(length=32), ForeignKey('customer_groups.uuid'), nullable=False)
    ordinal = Column(Integer(), nullable=False)

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

    __tablename__ = 'customers_people'

    uuid = uuid_column()
    customer_uuid = Column(String(length=32), ForeignKey('customers.uuid'), nullable=False)
    person_uuid = Column(String(length=32), ForeignKey('people.uuid'), nullable=False)
    ordinal = Column(Integer(), nullable=False)

    person = relationship(Person)

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
    primaryjoin=and_(
        CustomerPerson.customer_uuid == Customer.uuid,
        CustomerPerson.ordinal == 1),
    uselist=False,
    viewonly=True)

Customer.person = association_proxy(
    '_person', 'person',
    getset_factory=getset_factory)


class Employee(Base):
    """
    Represents an employee within the organization.
    """

    __tablename__ = 'employees'

    uuid = uuid_column()
    id = Column(Integer())
    person_uuid = Column(String(length=32), ForeignKey('people.uuid'), nullable=False)
    status = Column(Integer())
    display_name = Column(String(length=100))

    person = relationship(Person)

    first_name = association_proxy('person', 'first_name')
    last_name = association_proxy('person', 'last_name')
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
    primaryjoin=and_(
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
    primaryjoin=and_(
        EmployeeEmailAddress.parent_uuid == Employee.uuid,
        EmployeeEmailAddress.preference == 1),
    foreign_keys=[EmployeeEmailAddress.parent_uuid],
    uselist=False,
    viewonly=True)


class Batch(Base):
    """
    Represents a SIL-compliant batch of data.
    """

    __tablename__ = 'batches'

    uuid = uuid_column()
    provider = Column(String(length=50))
    id = Column(String(length=8))
    source = Column(String(length=6))
    destination = Column(String(length=6))
    action_type = Column(String(length=6))
    description = Column(String(length=50))
    rowcount = Column(Integer(), default=0)
    executed = Column(DateTime())
    # TODO: Convert this to a DateTime, to handle time zone issues.
    purge = Column(Date())

    _rowclasses = {}

    sil_type_pattern = re.compile(r'^(CHAR|NUMBER)\((\d+(?:\,\d+)?)\)$')

    def __repr__(self):
        return "Batch(uuid={0})".format(repr(self.uuid))

    def __unicode__(self):
        return unicode(self.description or '')

    @property
    def rowclass(self):
        """
        Returns the mapped class for the underlying row (data) table.
        """

        if not self.uuid:
            object_session(self).flush()
            assert self.uuid

        if self.uuid not in self._rowclasses:

            kwargs = {
                '__tablename__': 'batch.%s' % self.uuid,
                'uuid': uuid_column(),
                'ordinal': Column(Integer(), nullable=False),
                }

            for column in self.columns:
                data_type = self.get_sqlalchemy_type(column.data_type)
                kwargs[column.name] = Column(data_type)
            rowclass = type('BatchRow_{0}'.format(self.uuid).encode('ascii'), (Base, BatchRow), kwargs)

            batch_uuid = self.uuid
            def batch(self):
                return object_session(self).query(Batch).get(batch_uuid)
            rowclass.batch = property(batch)

            self._rowclasses[self.uuid] = rowclass

        return self._rowclasses[self.uuid]

    @classmethod
    def get_sqlalchemy_type(cls, sil_type):
        """
        Returns a SQLAlchemy data type according to a SIL data type.
        """

        if sil_type == 'GPC(14)':
            return GPCType()

        if sil_type == 'FLAG(1)':
            return Boolean()

        m = cls.sil_type_pattern.match(sil_type)
        if m:
            data_type, precision = m.groups()
            if precision.isdigit():
                precision = int(precision)
                scale = 0
            else:
                precision, scale = precision.split(',')
                precision = int(precision)
                scale = int(scale)
            if data_type == 'CHAR':
                assert not scale, "FIXME"
                return String(length=precision)
            if data_type == 'NUMBER':
                return Numeric(precision=precision, scale=scale)

        assert False, "FIXME"

    def add_column(self, sil_name=None, **kwargs):
        column = BatchColumn(sil_name, **kwargs)
        self.columns.append(column)

    def add_row(self, row, **kwargs):
        """
        Adds a row to the batch data table.
        """
        session = object_session(self)
        # FIXME: This probably needs to use a func.max() query.
        row.ordinal = self.rowcount + 1
        session.add(row)
        self.rowcount += 1
        session.flush()

    def create_table(self):
        """
        Creates the batch's data table within the database.
        """
        session = object_session(self)
        self.rowclass.__table__.create(session.bind)

    def drop_table(self):
        """
        Drops the batch's data table from the database.
        """
        log.debug("dropping normal batch table: {0}".format(self.rowclass.__table__.name))
        session = object_session(self)
        self.rowclass.__table__.drop(bind=session.bind, checkfirst=True)

    def execute(self, progress=None):
        from ..batches.exceptions import BatchProviderNotFound

        try:
            provider = self.get_provider()
            if not provider.execute(self, progress):
                return False

        except BatchProviderNotFound:
            executor = self.get_executor()
            if not executor.execute(self, progress):
                return False

        self.executed = datetime.datetime.utcnow()
        object_session(self).flush()
        return True

    def get_provider(self):
        from ..batches import get_provider
        assert self.provider
        return get_provider(self.provider)

    def get_executor(self):
        from .batches import get_batch_executor
        assert self.provider
        return get_batch_executor(self.provider)

    @property
    def rows(self):
        session = object_session(self)
        q = session.query(self.rowclass)
        q = q.order_by(self.rowclass.ordinal)
        return q


class BatchColumn(Base):
    """
    Represents a SIL column associated with a batch.
    """

    __tablename__ = 'batch_columns'

    uuid = uuid_column()
    batch_uuid = Column(String(length=32), ForeignKey('batches.uuid'))
    ordinal = Column(Integer(), nullable=False)
    name = Column(String(length=20))
    display_name = Column(String(length=50))
    sil_name = Column(String(length=10))
    data_type = Column(String(length=15))
    description = Column(String(length=50))
    visible = Column(Boolean(), default=True)

    def __init__(self, sil_name=None, **kwargs):
        from ..sil import get_column
        if sil_name:
            kwargs['sil_name'] = sil_name
            sil_column = get_column(sil_name)
            kwargs.setdefault('name', sil_name)
            kwargs.setdefault('data_type', sil_column.data_type)
            kwargs.setdefault('description', sil_column.description)
            kwargs.setdefault('display_name', sil_column.display_name)
        super(BatchColumn, self).__init__(**kwargs)

    def __repr__(self):
        return "BatchColumn(uuid={0})".format(repr(self.uuid))

    def __unicode__(self):
        return unicode(self.display_name or '')


Batch.columns = relationship(
    BatchColumn, backref='batch',
    collection_class=ordering_list('ordinal'),
    order_by=BatchColumn.ordinal,
    cascade='save-update, merge, delete, delete-orphan')


class BatchRow(object):
    """
    Superclass of batch row objects.
    """

    def __unicode__(self):
        return u"Row {0}".format(self.ordinal)


class LabelProfile(Base):
    """
    Represents a collection of settings for product label printing.
    """

    __tablename__ = 'label_profiles'

    uuid = uuid_column()
    ordinal = Column(Integer())
    code = Column(String(length=3))
    description = Column(String(length=50))
    printer_spec = Column(String(length=255))
    formatter_spec = Column(String(length=255))
    format = Column(Text())
    visible = Column(Boolean())

    _printer = None
    _formatter = None

    def __repr__(self):
        return "LabelProfile(uuid={0})".format(repr(self.uuid))

    def __unicode__(self):
        return unicode(self.description or '')

    def get_formatter(self):
        if not self._formatter and self.formatter_spec:
            try:
                formatter = load_object(self.formatter_spec)
            except AttributeError:
                pass
            else:
                self._formatter = formatter()
                self._formatter.format = self.format
        return self._formatter        

    def get_printer(self, config):
        if not self._printer and self.printer_spec:
            try:
                printer = load_object(self.printer_spec)
            except AttributeError:
                pass
            else:
                self._printer = printer(config)
                for name in printer.required_settings:
                    setattr(printer, name, self.get_printer_setting(name))
                self._printer.formatter = self.get_formatter()
        return self._printer

    def get_printer_setting(self, name):
        from .api import get_setting
        if self.uuid is None:
            return None
        session = object_session(self)
        name = 'labels.{0}.printer.{1}'.format(self.uuid, name)
        return get_setting(session, name)

    def save_printer_setting(self, name, value):
        from .api import save_setting
        session = object_session(self)
        if self.uuid is None:
            session.flush()
        name = 'labels.{0}.printer.{1}'.format(self.uuid, name)
        save_setting(session, name, value)


__all__ = []
for key, obj in locals().items():
    if isinstance(obj, type) and issubclass(obj, Base):
        __all__.append(key)
