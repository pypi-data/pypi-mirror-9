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
CSV Import Data Providers
"""

from __future__ import unicode_literals

import datetime
from decimal import Decimal

from .core import DataProvider
from rattail.db import model
from rattail.gpc import GPC
from rattail.db.importing import models
from rattail.util import load_object
from rattail.csvutil import UnicodeDictReader
from rattail.db.util import maxlen
from rattail.time import localtime, make_utc


def make_provider(config, session, spec, **kwargs):
    """
    Create a provider instance according to the given spec.  For now..see the
    source code for more details.
    """
    provider = None
    if '.' not in spec and ':' not in spec:
        from rattail.db.importing.providers import csv
        if hasattr(csv, spec):
            provider = getattr(csv, spec)
        elif hasattr(csv, '{0}Provider'.format(spec)):
            provider = getattr(csv, '{0}Provider'.format(spec))
    else:
        provider = load_object(spec)
    if provider:
        return provider(config, session, **kwargs)


class CsvProvider(DataProvider):
    """
    Base class for CSV data providers.
    """
    time_format = '%Y-%m-%d %H:%M:%S'

    def get_source_data(self, progress=None):
        with open(self.data_path, 'rb') as f:
            reader = UnicodeDictReader(f)
            return list(reader)

    def make_utc(self, time):
        if time is None:
            return None
        return make_utc(localtime(self.config, time))

    def make_time(self, value):
        if not value:
            return None
        time = datetime.datetime.strptime(value, self.time_format)
        return self.make_utc(time)


class ProductProvider(CsvProvider):
    """
    CSV product data provider.
    """
    importer_class = models.ProductImporter
    supported_fields = [
        'uuid',
        'upc',
        'description',
        'size',
        'department_uuid',
        'subdepartment_uuid',
        'category_uuid',
        'brand_uuid',
        'regular_price',
        'sale_price',
        'sale_starts',
        'sale_ends',
        ]
    maxlen_description = maxlen(model.Product.description)
    maxlen_size = maxlen(model.Product.size)

    def normalize(self, data):

        if 'upc' in data:
            upc = data['upc']
            data['upc'] = GPC(upc) if upc else None

        # Warn about truncation until Rattail schema is addressed.
        if 'description' in data:
            description = data['description'] or ''
            if self.maxlen_description and len(description) > self.maxlen_description:
                log.warning("product description is more than {} chars and will be truncated: {}".format(
                        self.maxlen_description, repr(description)))
                description = description[:self.maxlen_description]
            data['description'] = description

        # Warn about truncation until Rattail schema is addressed.
        if 'size' in data:
            size = data['size'] or ''
            if self.maxlen_size and len(size) > self.maxlen_size:
                log.warning("product size is more than {} chars and will be truncated: {}".format(
                        self.maxlen_size, repr(size)))
                size = size[:self.maxlen_size]
            data['size'] = size

        if 'department_uuid' in data:
            data['department_uuid'] = data['department_uuid'] or None

        if 'subdepartment_uuid' in data:
            data['subdepartment_uuid'] = data['subdepartment_uuid'] or None

        if 'category_uuid' in data:
            data['category_uuid'] = data['category_uuid'] or None

        if 'brand_uuid' in data:
            data['brand_uuid'] = data['brand_uuid'] or None

        if 'regular_price' in data:
            price = data['regular_price']
            data['regular_price'] = Decimal(price) if price else None

        # Determine if sale price is currently active; if it is not then we
        # will declare None for all sale fields.
        if 'sale_starts' in data:
            data['sale_starts'] = self.make_time(data['sale_starts'])
        if 'sale_ends' in data:
            data['sale_ends'] = self.make_time(data['sale_ends'])
        if 'sale_price' in data:
            price = data['sale_price']
            data['sale_price'] = Decimal(price) if price else None
            if data['sale_price']:
                sale_starts = data.get('sale_starts')
                sale_ends = data.get('sale_ends')
                active = False
                if sale_starts and sale_ends:
                    if sale_starts <= self.now <= sale_ends:
                        active = True
                elif sale_starts:
                    if sale_starts <= self.now:
                        active = True
                elif sale_ends:
                    if self.now <= sale_ends:
                        active = True
                else:
                    active = True
                if not active:
                    data['sale_price'] = None
                    data['sale_starts'] = None
                    data['sale_ends'] = None
            else:
                data['sale_starts'] = None
                data['sale_ends'] = None

        return data
