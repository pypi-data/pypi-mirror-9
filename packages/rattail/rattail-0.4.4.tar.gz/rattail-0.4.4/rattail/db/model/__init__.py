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

from .core import Base, uuid_column, getset_factory, Setting, Change
from .contact import PhoneNumber, EmailAddress

from .people import Person, PersonPhoneNumber, PersonEmailAddress
from .users import Role, Permission, User, UserRole
from .stores import Store, StorePhoneNumber, StoreEmailAddress
from .employees import Employee, EmployeePhoneNumber, EmployeeEmailAddress
from .customers import (Customer, CustomerPhoneNumber, CustomerEmailAddress,
                        CustomerGroup, CustomerGroupAssignment, CustomerPerson)

from .vendors import Vendor, VendorPhoneNumber, VendorEmailAddress, VendorContact
from .org import Department, Subdepartment, Category, Family, ReportCode
from .products import Brand, Product, ProductCode, ProductCost, ProductPrice

from .batches import Batch, BatchColumn, BatchRow
from .labels import LabelProfile

from rattail.db.batch.model import (BatchMixin, FileBatchMixin,
                                    BatchRowMixin, ProductBatchRowMixin)
from rattail.db.batch.vendorcatalog.model import VendorCatalog, VendorCatalogRow
