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
Cache Helpers
"""

from __future__ import unicode_literals

from sqlalchemy.orm import joinedload

from ..core import Object
from . import model


class DataCacher(Object):

    def __init__(self, session=None, **kwargs):
        super(DataCacher, self).__init__(session=session, **kwargs)

    @property
    def class_(self):
        raise NotImplementedError
    
    @property
    def name(self):
        return self.class_.__name__

    def query(self):
        return self.session.query(self.class_)

    def get_cache(self, progress):
        self.instances = {}

        query = self.query()
        count = query.count()
        if not count:
            return self.instances
        
        prog = None
        if progress:
            prog = progress("Caching {0} records".format(self.name), count)

        cancel = False
        for i, instance in enumerate(query, 1):
            self.cache_instance(instance)
            if prog and not prog.update(i):
                cancel = True
                break

        if prog:
            prog.destroy()

        if cancel:
            session.close()
            return None
        return self.instances


class DepartmentCacher(DataCacher):

    class_ = model.Department

    def cache_instance(self, dept):
        self.instances[dept.number] = dept


class SubdepartmentCacher(DataCacher):

    class_ = model.Subdepartment

    def cache_instance(self, subdept):
        self.instances[subdept.number] = subdept


class FamilyCacher(DataCacher):

    class_ = model.Family

    def cache_instance(self, family):
        self.instances[family.code] = family


class ReportCodeCacher(DataCacher):

    class_ = model.ReportCode

    def cache_instance(self, report_code):
        self.instances[report_code.code] = report_code


class BrandCacher(DataCacher):

    class_ = model.Brand

    def cache_instance(self, brand):
        self.instances[brand.name] = brand


class VendorCacher(DataCacher):

    class_ = model.Vendor

    def cache_instance(self, vend):
        self.instances[vend.id] = vend


class ProductCacher(DataCacher):

    class_ = model.Product
    with_costs = False

    def query(self):
        q = self.session.query(model.Product)
        if self.with_costs:
            q = q.options(joinedload(model.Product.costs))
            q = q.options(joinedload(model.Product.cost))
        return q

    def cache_instance(self, prod):
        self.instances[prod.upc] = prod


def get_product_cache(session, with_costs=False, progress=None):
    """
    Cache the full product set by UPC.

    Returns a dictionary of all existing products, keyed by
    :attr:`rattail.Product.upc`.
    """

    cacher = ProductCacher(session=session, with_costs=with_costs)
    return cacher.get_cache(progress)


class CustomerGroupCacher(DataCacher):

    class_ = model.CustomerGroup

    def cache_instance(self, group):
        self.instances[group.id] = group


class CustomerCacher(DataCacher):

    class_ = model.Customer

    def cache_instance(self, customer):
        self.instances[customer.id] = customer
