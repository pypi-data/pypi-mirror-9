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
Vendor catalog parser for Dutch Valley
"""

from __future__ import unicode_literals

import re
import datetime
import logging
from decimal import Decimal

import xlrd

from rattail.vendors.catalogs import CatalogParser
from rattail.db.batch.vendorcatalog import VendorCatalogRow


log = logging.getLogger(__name__)


class DutchValleyCatalogParser(CatalogParser):
    """
    Vendor catalog parser for Dutch Valley.
    """
    key = 'rattail.contrib.dutchvalley'
    display = "Dutch Valley"
    vendor_key = 'dutch-valley'

    def parse_effective_date(self, path):
        book = xlrd.open_workbook(path)
        sheet = book.sheet_by_index(0)
        date = sheet.cell_value(0, 0)
        date = xlrd.xldate_as_tuple(date, book.datemode)
        return datetime.datetime(*date).date()

    def parse_rows(self, path):
        book = xlrd.open_workbook(path)
        sheet = book.sheet_by_index(0)
        code_pattern = re.compile(r'^\d{3} \d{3}$')
        description_pattern = re.compile(r'^(\d+(?:\.\d+)?)((?:/(\d+(?:\.\d+)?))?\w+) (.*)$')
        for r in range(sheet.nrows):

            # Product code is in first column...but so is a lot of other
            # garbage.  Use strict regex to find good rows.
            code = sheet.cell_value(r, 0)
            if not isinstance(code, basestring):
                continue
            if not code_pattern.match(code):
                continue
            code = code.replace(' ', '')
            
            row = VendorCatalogRow()
            row.vendor_code = code

            # Try to parse unit and/or case size from description.
            description = sheet.cell_value(r, 1)
            match = description_pattern.match(description)
            if match:
                row.description = match.group(3) or ''
                row.size = match.group(2)
                row.case_size = int(float(match.group(1)))
            else:
                log.warning("description doesn't match pattern at row {0}: {1}".format(
                        r + 1, repr(description)))
                row.description = description or ''

            case_cost = sheet.cell_value(r, 2)
            try:
                row.case_cost = Decimal(unicode(case_cost))
            except ValueError:
                log.warning("bad case cost at row {0}: {1}".format(r + 1, repr(case_cost)))

            unit_cost = sheet.cell_value(r, 4)
            try:
                row.unit_cost = Decimal(unicode(unit_cost))
            except ValueError:
                log.warning("bad unit cost at row {0}: {1}".format(r + 1, repr(unit_cost)))

            yield row
