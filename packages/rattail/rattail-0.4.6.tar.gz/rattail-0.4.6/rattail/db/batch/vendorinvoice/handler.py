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
Handler for Vendor Invoice batches
"""

from __future__ import unicode_literals

import os

from sqlalchemy.orm import joinedload

from rattail.db import api
from rattail.db import model
from rattail.db.batch.handler import FileBatchHandler
from rattail.vendors.invoices import require_invoice_parser


class VendorInvoiceHandler(FileBatchHandler):
    """
    Handler for vendor invoice batches.
    """
    batch_model_class = model.VendorInvoice
    show_progress = True
    po_number_title = "PO Number"

    def make_batch(self, session, path, **kwargs):
        parser_key = kwargs.get('parser_key')
        if parser_key and not kwargs.get('vendor') and not kwargs.get('vendor_uuid'):
            parser = require_invoice_parser(parser_key)
            kwargs['vendor'] = api.get_vendor(session, parser.vendor_key)
        return super(VendorInvoiceHandler, self).make_batch(session, path, **kwargs)

    def get_purchase_order(self, number):
        """
        Fetch the purchase order object corresponding to the given PO number.
        Custom handlers should override this if aiming to reconcile invoices to
        purchase orders.
        """

    def validate_po_number(self, number):
        """
        This method does nothing by default.  Derived handlers can validate the
        PO number as they like.  Invalid PO numbers should cause ``ValueError``
        to be raised, with text of the reason for validation failure.
        """

    def refresh_data(self, session, batch, progress=None):
        """
        Refresh all data for the batch.
        """
        self.session = session
        del batch.data_rows[:]
        data_path = self.data_path(batch)
        parser = require_invoice_parser(batch.parser_key)
        parser.session = session
        parser.vendor = api.get_vendor(session, parser.vendor_key)
        batch.invoice_date = parser.parse_invoice_date(data_path)

        # Pre-cache products by UPC and vendor code.
        self.vendor = parser.vendor
        self.products = {'upc': {}, 'vendor_code': {}, 'code': {}}
        products = session.query(model.Product)\
            .options(joinedload(model.Product.brand))\
            .options(joinedload(model.Product.costs))\
            .options(joinedload(model.Product._codes))
        prog = None
        if progress:
            prog = progress("Caching products by UPC and vendor item code", products.count())
        for i, product in enumerate(products, 1):
            if product.upc:
                self.products['upc'][product.upc] = product
            cost = product.cost_for_vendor(self.vendor)
            product.vendor_cost = cost
            if cost and cost.code:
                self.products['vendor_code'][cost.code] = product
            for code in product.codes:
                self.products['code'][code] = product
            if prog:
                prog.update(i)
        if prog:
            prog.destroy()

        # Get data from parser, and convert to rows.
        data = list(parser.parse_rows(data_path))
        self.make_rows(session, batch, data, progress=progress)

        # If we have a PO number, attempt to reconcile against a purchase order.
        if batch.purchase_order_number:
            purchase = self.get_purchase_order(batch.purchase_order_number)
            if purchase:
                self.cognize_purchase_order(session, batch, purchase, progress=progress)

    def find_product(self, row):
        """
        Attempt to locate the product for the row, based on UPC etc.
        """
        if row.upc:
            product = self.products['upc'].get(row.upc)
            if product:
                return product

        if row.vendor_code:
            product = self.products['vendor_code'].get(row.vendor_code)
            if product:
                return product

    def cognize_row(self, session, row):
        """
        Inspect a single row from a invoice, and set its attributes based on
        whether or not the product exists, if we already have a cost record for
        the vendor, if the invoice contains a change etc.  Note that the
        product lookup is done first by UPC and then by vendor item code.
        """
        product = self.find_product(row)
        if not product:
            row.status_code = row.STATUS_NOT_IN_DB
            return

        row.product = product
        row.upc = product.upc
        row.brand_name = product.brand.name if product.brand else None
        row.description = product.description
        row.size = product.size
        if product.cost_for_vendor(self.vendor):
            row.status_code = row.STATUS_OK
        else:
            row.status_code = row.STATUS_COST_NOT_IN_DB

        # Calculate case cost if the parser couldn't provide one.
        if not row.case_cost and row.unit_cost and row.case_quantity:
            row.case_cost = row.unit_cost * row.case_quantity

    def cognize_purchase_order(self, session, invoice, purchase, progress=None):
        """
        Cognize the given invoice against the given purchase order object.
        Custom handlers should override this if aiming to reconcile invoices to
        purchase orders.
        """

    def execute(self, batch, progress=None):
        """
        Execute the vendor invoice batch.  Note that the default handler does
        not perform any actions; a custom handler must be used for anything
        interesting to happen.
        """
        return True
