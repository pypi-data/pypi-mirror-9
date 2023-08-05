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
Data Models for Products
"""

from __future__ import unicode_literals

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.ext.associationproxy import association_proxy

from .core import Base, uuid_column, GPCType, getset_factory
from .org import Department, Subdepartment, Category
from .vendors import Vendor


class Brand(Base):
    """
    Represents a brand or similar product line.
    """
    __tablename__ = 'brand'
    __versioned__ = {}

    uuid = uuid_column()
    name = sa.Column(sa.String(length=100))

    def __repr__(self):
        return "Brand(uuid={0})".format(repr(self.uuid))

    def __unicode__(self):
        return unicode(self.name or '')


class Product(Base):
    """
    Represents a product for sale and/or purchase.
    """
    __tablename__ = 'product'
    __table_args__ = (
        sa.ForeignKeyConstraint(['department_uuid'], ['department.uuid'], name='product_fk_department'),
        sa.ForeignKeyConstraint(['subdepartment_uuid'], ['subdepartment.uuid'], name='product_fk_subdepartment'),
        sa.ForeignKeyConstraint(['category_uuid'], ['category.uuid'], name='product_fk_category'),
        sa.ForeignKeyConstraint(['family_uuid'], ['family.uuid'], name='product_fk_family'),
        sa.ForeignKeyConstraint(['brand_uuid'], ['brand.uuid'], name='product_fk_brand'),
        sa.ForeignKeyConstraint(['report_code_uuid'], ['report_code.uuid'], name='product_fk_report_code'),
        sa.ForeignKeyConstraint(['regular_price_uuid'], ['product_price.uuid'], name='product_fk_regular_price', use_alter=True),
        sa.ForeignKeyConstraint(['current_price_uuid'], ['product_price.uuid'], name='product_fk_current_price', use_alter=True),
        sa.Index('product_ix_upc', 'upc'),
        )
    __versioned__ = {}

    uuid = uuid_column()
    upc = sa.Column(GPCType())
    department_uuid = sa.Column(sa.String(length=32))
    subdepartment_uuid = sa.Column(sa.String(length=32))
    category_uuid = sa.Column(sa.String(length=32))
    family_uuid = sa.Column(sa.String(length=32))

    report_code_uuid = sa.Column(sa.String(length=32), nullable=True, doc=u"""\
UUID of the product's report code, if any.
""")

    brand_uuid = sa.Column(sa.String(length=32))
    description = sa.Column(sa.String(length=60))
    description2 = sa.Column(sa.String(length=60))
    size = sa.Column(sa.String(length=30))
    unit_of_measure = sa.Column(sa.String(length=4))

    case_pack = sa.Column(sa.Integer(), nullable=True, doc="""
Pack size for the product, i.e. how many units are in a case.
""")

    not_for_sale = sa.Column(sa.Boolean(), nullable=False, default=False, doc="""
Flag to indicate items which are not available for sale.
""")

    deleted = sa.Column(sa.Boolean(), nullable=False, default=False, doc="""
Flag to indicate items which have been deleted.  Obviously this is implies
"false" deletion, where the record is actually kept on file.  Whether or not
you use this is up to you.
""")

    regular_price_uuid = sa.Column(sa.String(length=32))
    current_price_uuid = sa.Column(sa.String(length=32))

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
        return "{0} {1}".format(self.pretty_upc, self.full_description)

    @property
    def full_description(self):
        """
        Convenience attribute which returns a more complete description.

        Most notably, this includes the brand name and product size.
        """
        fields = [
            (self.brand.name or '') if self.brand else '',
            self.description or '',
            self.size or '']
        fields = [f.strip() for f in fields if f.strip()]
        return ' '.join(fields)

    @property
    def pretty_upc(self):
        """
        Product's UPC as a somewhat human-readable string.
        """
        if self.upc is None:
            return None
        return "{0}-{1}".format(unicode(self.upc)[:-1], unicode(self.upc)[-1])

    def cost_for_vendor(self, vendor):
        """
        Of the product's cost records, return the first one associated with the
        given vendor.
        """
        for cost in self.costs:
            if cost.vendor is vendor:
                return cost


class ProductCode(Base):
    """
    Represents an arbitrary "code" for a product.
    """
    __tablename__ = 'product_code'
    __table_args__ = (
        sa.ForeignKeyConstraint(['product_uuid'], ['product.uuid'], name='product_code_fk_product'),
        )
    __versioned__ = {}

    uuid = uuid_column()
    product_uuid = sa.Column(sa.String(length=32), nullable=False)
    ordinal = sa.Column(sa.Integer(), nullable=False)
    code = sa.Column(sa.String(length=20))

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
    primaryjoin=sa.and_(
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
    __tablename__ = 'product_cost'
    __table_args__ = (
        sa.ForeignKeyConstraint(['product_uuid'], ['product.uuid'], name='product_cost_fk_product'),
        sa.ForeignKeyConstraint(['vendor_uuid'], ['vendor.uuid'], name='product_cost_fk_vendor'),
        )
    __versioned__ = {}

    uuid = uuid_column()
    product_uuid = sa.Column(sa.String(length=32), nullable=False)
    vendor_uuid = sa.Column(sa.String(length=32), nullable=False)
    preference = sa.Column(sa.Integer(), nullable=False)
    code = sa.Column(sa.String(length=20))

    case_size = sa.Column(sa.Integer())
    case_cost = sa.Column(sa.Numeric(precision=9, scale=5))
    pack_size = sa.Column(sa.Integer())
    pack_cost = sa.Column(sa.Numeric(precision=9, scale=5))
    unit_cost = sa.Column(sa.Numeric(precision=9, scale=5))
    effective = sa.Column(sa.DateTime())

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
    primaryjoin=sa.and_(
        ProductCost.product_uuid == Product.uuid,
        ProductCost.preference == 1,
        ),
    uselist=False,
    viewonly=True)

Product.vendor = relationship(
    Vendor,
    secondary=ProductCost.__table__,
    primaryjoin=sa.and_(
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
    __tablename__ = 'product_price'
    __table_args__ = (
        sa.ForeignKeyConstraint(['product_uuid'], ['product.uuid'], name='product_price_fk_product'),
        )
    __versioned__ = {}

    uuid = uuid_column()
    product_uuid = sa.Column(sa.String(length=32), nullable=False)
    type = sa.Column(sa.Integer())
    level = sa.Column(sa.Integer())
    starts = sa.Column(sa.DateTime())
    ends = sa.Column(sa.DateTime())
    price = sa.Column(sa.Numeric(precision=8, scale=3))
    multiple = sa.Column(sa.Integer())
    pack_price = sa.Column(sa.Numeric(precision=8, scale=3))
    pack_multiple = sa.Column(sa.Integer())

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
