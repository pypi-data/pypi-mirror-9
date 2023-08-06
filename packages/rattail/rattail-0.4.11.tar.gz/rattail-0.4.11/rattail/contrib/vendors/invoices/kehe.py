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
Vendor invoice parser for KeHE Distributors
"""

from __future__ import unicode_literals

import re
import csv
import datetime

from rattail.vendors.invoices import InvoiceParser
from rattail.db.batch.vendorinvoice import VendorInvoiceRow
from rattail.gpc import GPC


class KeheInvoiceParser(InvoiceParser):
    """
    Vendor invoice parser for KeHE Distributors.
    """
    key = 'rattail.contrib.kehe'
    display = "KeHE Distributors"
    vendor_key = 'kehe'

    pack_size_pattern = re.compile('^(?P<case_quantity>\d+)/(?P<size>\d*\.\d+ \w\w)$')

    def parse_invoice_date(self, path):
        with open(path, 'rb') as f:
            reader = csv.DictReader(f, delimiter=b'\t')
            data = reader.next()
            return datetime.datetime.strptime(data['Invoice Date'], '%Y-%m-%d').date()

    def parse_rows(self, path):
        with open(path, 'rb') as f:
            reader = csv.DictReader(f, delimiter=b'\t')
            for data in reader:

                row = VendorInvoiceRow()
                row.upc = GPC(data['UPC Code'])
                row.vendor_code = data['Ship Item']
                row.brand_name = data['Brand']
                row.description = data['Description']
                row.ordered_units = self.int_(data['Order Qty'])
                row.shipped_units = self.int_(data['Ship Qty'])
                row.unit_cost = self.decimal(data['Net Each'])
                row.total_cost = self.decimal(data['Net Billable'])

                # Case quantity may be embedded in size string.
                row.size = data['Pack Size']
                row.case_quantity = 1
                match = self.pack_size_pattern.match(row.size)
                if match:
                    row.case_quantity = int(match.group('case_quantity'))
                    row.size = match.group('size')

                yield row
