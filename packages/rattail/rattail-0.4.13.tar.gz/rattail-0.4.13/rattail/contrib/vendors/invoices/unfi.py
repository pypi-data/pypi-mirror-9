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
Vendor invoice parser for United Natural Foods (UNFI)
"""

from __future__ import unicode_literals

import datetime

from rattail.vendors.invoices import InvoiceParser
from rattail.db.batch.vendorinvoice import VendorInvoiceRow
from rattail.csvutil import UnicodeDictReader, UnicodeReader
from rattail.gpc import GPC


class UnfiInvoiceParser(InvoiceParser):
    """
    Parser for UNFI CSV invoice files.
    """
    key = 'rattail.contrib.unfi'
    display = "United Natural Foods (UNFI)"
    vendor_key = 'unfi'

    def parse_invoice_date(self, data_path):
        with open(data_path, 'rb') as f:
            reader = UnicodeDictReader(f, encoding='latin_1')
            data = reader.next()
            return datetime.datetime.strptime(data['InvoiceDate'], '%m/%d/%Y').date()

    def parse_rows(self, data_path):
        with open(data_path, 'rb') as csv_file:

            # TODO: The following logic is largely copied from the Scan Genius
            # order parser (in `rattail_livnat.scangenius`).  I wonder if we
            # can abstract it into a generic yet custom CSV parser...?

            # We want to ignore the header section here.  However the use of
            # UnicodeDictReader below requires iteration, and yet also expects
            # the "beginning" of the file to contain the fieldnames.  To force
            # this all to play nicely, we calculate our offset and then seek to
            # it explicitly.  It's probably likely that there is a better way,
            # but this works.
            offset = self.find_details_offset(csv_file)
            csv_file.seek(offset)

            reader = UnicodeDictReader(csv_file, encoding='latin_1')
            for data in reader:

                # Only consider 'Detail' rows; this check is mostly for the
                # sake of ignoring 'Footer' rows.
                if data['RecType'] != 'Detail':
                    continue

                row = VendorInvoiceRow()
                row.upc = GPC(data['UPC'].replace('-', ''))
                row.vendor_code = data['ProductID']
                row.brand_name = data['Brand']
                row.description = data['Description']
                row.size = data['Size']
                row.case_quantity = self.int_(data['Servings'])
                row.ordered_cases = int(self.decimal(data['QuantityOrdered']))
                row.shipped_cases = self.int_(data['QuantityShipped'])
                row.unit_cost = self.decimal(data['NetPricePerUnit'])
                row.total_cost = self.decimal(data['ExtendedPrice'])
                row.case_cost = row.unit_cost * row.case_quantity

                yield row

    def find_details_offset(self, csv_file):
        """
        Find the character offset of the details data within a CSV file.
        """
        # TODO: The following logic is largely copied from the Scan Genius
        # order parser (in ``rattail_livnat.scangenius``).  I wonder if we can
        # abstract it into a generic yet custom CSV parser...?

        # Calculate the offset of the details section, based on the sum
        # character length of the header section (which is 2 lines long).
        reader = UnicodeReader(csv_file, encoding='latin_1')
        offset = 0
        for line, row in enumerate(csv_file, 1):
            offset += len(row)
            if line == 2:
                break
        return offset
