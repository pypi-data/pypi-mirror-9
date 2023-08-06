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
Vendor invoice parser for Albert's Organics
"""

from __future__ import unicode_literals

import csv
import datetime

from rattail.vendors.invoices import InvoiceParser
from rattail.db.batch.vendorinvoice import VendorInvoiceRow
from rattail.gpc import GPC


class AlbertsInvoiceParser(InvoiceParser):
    """
    Invoice parser for Albert's Organics CSV files.
    """
    key = 'rattail.contrib.alberts'
    display = "Albert's Organics"
    vendor_key = 'alberts'

    def parse_invoice_date(self, path):
        with open(path, 'rb') as f:
            reader = csv.DictReader(f)
            data = reader.next()
            return datetime.datetime.strptime(data['Invoice Date'], '%m/%d/%Y').date()

    def parse_rows(self, path):
        with open(path, 'rb') as f:
            reader = csv.DictReader(f)
            for data in reader:

                row = VendorInvoiceRow()
                row.upc = GPC(data['UPCPLU'].replace('-', '').replace(' ', ''))
                row.vendor_code = data['ItemNumber']
                row.brand_name = data['BrandName']
                row.description = data['MV']
                row.size = "{0} {1}".format(data['PkgSize'], data['UOMAbbr'])
                row.case_quantity = self.int_(data['PkgCount']) or int(self.decimal(data['PkgSize']))
                row.shipped_cases = self.decimal(data['ShipQty'])
                row.case_cost = self.decimal(data['CasePrice'])
                row.unit_cost = self.decimal(data['EachPrice'])
                row.total_cost = row.case_cost * row.shipped_cases

                yield row
