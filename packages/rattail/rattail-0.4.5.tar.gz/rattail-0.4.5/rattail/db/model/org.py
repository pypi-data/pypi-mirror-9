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
Data Models for Organization etc.
"""

from __future__ import unicode_literals

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from .core import Base, uuid_column


class Department(Base):
    """
    Represents an organizational department.
    """
    __tablename__ = 'department'
    __versioned__ = {}

    uuid = uuid_column()
    number = sa.Column(sa.Integer())
    name = sa.Column(sa.String(length=30))

    def __repr__(self):
        return "Department(uuid={0})".format(repr(self.uuid))

    def __unicode__(self):
        return unicode(self.name or '')


class Subdepartment(Base):
    """
    Represents an organizational subdepartment.
    """
    __tablename__ = 'subdepartment'
    __table_args__ = (
        sa.ForeignKeyConstraint(['department_uuid'], ['department.uuid'], name='subdepartment_fk_department'),
        )
    __versioned__ = {}

    uuid = uuid_column()
    number = sa.Column(sa.Integer())
    name = sa.Column(sa.String(length=30))
    department_uuid = sa.Column(sa.String(length=32))

    def __repr__(self):
        return "Subdepartment(uuid={0})".format(repr(self.uuid))

    def __unicode__(self):
        if self.number:
            return "{0} {1}".format(self.number, self.name or '')
        return self.name or ''


Department.subdepartments = relationship(
    Subdepartment,
    backref='department',
    order_by=Subdepartment.name)


class Category(Base):
    """
    Represents an organizational category for products.
    """
    __tablename__ = 'category'
    __table_args__ = (
        sa.ForeignKeyConstraint(['department_uuid'], ['department.uuid'], name='category_fk_department'),
        )
    __versioned__ = {}

    uuid = uuid_column()
    number = sa.Column(sa.Integer())
    name = sa.Column(sa.String(length=50))
    department_uuid = sa.Column(sa.String(length=32))

    department = relationship(Department)

    def __repr__(self):
        return "Category(uuid={0})".format(repr(self.uuid))

    def __unicode__(self):
        if self.number:
            return "{0} {1}".format(self.number, self.name or '')
        return self.name or ''


class Family(Base):
    """
    Represents an organizational family for products.
    """
    __tablename__ = 'family'
    __versioned__ = {}

    uuid = uuid_column()
    code = sa.Column(sa.Integer())
    name = sa.Column(sa.String(length=50))

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
    __tablename__ = 'report_code'
    __table_args__ = (
        sa.UniqueConstraint('code', name='report_code_uq_code'),
        )
    __versioned__ = {}

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
