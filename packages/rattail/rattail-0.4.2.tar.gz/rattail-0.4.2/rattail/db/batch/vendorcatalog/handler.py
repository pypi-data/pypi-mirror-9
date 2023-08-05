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
Handler for Vendor Catalog batches
"""

from __future__ import unicode_literals

from sqlalchemy.orm import joinedload

from rattail.db import api
from rattail.db import model
from rattail.db.batch.handler import BatchHandler
from rattail.vendors.catalogs import require_catalog_parser


class VendorCatalogHandler(BatchHandler):
    """
    Handler for vendor catalog batches.
    """
    show_progress = True

    def refresh_data(self, session, batch, progress_factory=None):
        """
        Refresh all data for the batch.
        """
        del batch.data_rows[:]
        data_path = batch.filepath(self.config)
        parser = require_catalog_parser(batch.parser_key)
        batch.effective = parser.parse_effective_date(data_path)

        # Pre-cache products by UPC and vendor code.
        self.vendor = api.get_vendor(session, parser.vendor_key)
        self.products = {'upc': {}, 'vendor_code': {}}
        products = session.query(model.Product)\
            .options(joinedload(model.Product.costs))
        for product in products:
            if product.upc:
                self.products['upc'][product.upc] = product
            cost = product.cost_for_vendor(self.vendor)
            product.vendor_cost = cost
            if cost and cost.code:
                self.products['vendor_code'][cost.code] = product

        data = list(parser.parse_rows(data_path))
        self.make_rows(session, batch, data, progress_factory=progress_factory)

    def cognize_row(self, session, row):
        """
        Inspect a single row from a catalog, and set its attributes based on
        whether or not the product exists, if already have a cost record for
        the vendor, if the catalog contains a change etc.
        """
        if row.upc:
            row.product = self.products['upc'].get(row.upc)
        if not row.product and row.vendor_code:
            row.product = self.products['vendor_code'].get(row.vendor_code)
        if row.product:

            row.upc = row.product.upc
            row.brand_name = row.product.brand.name if row.product.brand else None
            row.description = row.product.description
            row.size = row.product.size

            old_cost = row.product.vendor_cost
            if old_cost:
                row.old_vendor_code = old_cost.code
                row.old_case_size = old_cost.case_size

                row.old_case_cost = old_cost.case_cost
                if row.case_cost is not None and row.old_case_cost is not None:
                    row.case_cost_diff = row.case_cost - row.old_case_cost

                row.old_unit_cost = old_cost.unit_cost
                if row.unit_cost is not None and row.old_unit_cost is not None:
                    row.unit_cost_diff = row.unit_cost - row.old_unit_cost

                if self.cost_differs(row, old_cost):
                    row.status_code = row.STATUS_UPDATE_COST
                else:
                    row.status_code = row.STATUS_NO_CHANGE

            else:
                row.status_code = row.STATUS_NEW_COST
        else:
            row.status_code = row.STATUS_PRODUCT_NOT_FOUND

    def cost_differs(self, row, cost):
        """
        Compare a batch row with a cost record to determine whether they match
        or differ.
        """
        if row.vendor_code != cost.code:
            return True
        if row.case_cost != cost.case_cost:
            return True
        if row.unit_cost != cost.unit_cost:
            return True
        return False

    def execute(self, batch):
        return True
