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
Print Labels Batch
"""

from __future__ import unicode_literals

from sqlalchemy.orm import object_session

from . import BatchProvider
from ...db import model


class PrintLabels(BatchProvider):

    name = 'print_labels'
    description = "Print Labels"

    default_profile = None
    default_quantity = 1

    def add_columns(self, batch):
        batch.add_column('F01')
        batch.add_column('F155')
        batch.add_column('F02')
        batch.add_column('F22', display_name="Size")
        batch.add_column('F95', display_name="Label")
        batch.add_column('F94', display_name="Quantity")

    def add_rows_begin(self, batch, data):
        session = object_session(batch)
        if not self.default_profile:
            q = session.query(model.LabelProfile)
            q = q.order_by(model.LabelProfile.ordinal)
            self.default_profile = q.first()
            assert self.default_profile
        else:
            self.default_profile = session.merge(self.default_profile)

    def add_row(self, batch, product):
        row = batch.rowclass()
        row.F01 = product.upc
        if product.brand:
            row.F155 = product.brand.name
        row.F02 = product.description[:20]
        row.F22 = product.size
        row.F95 = self.default_profile.code
        row.F94 = self.default_quantity
        batch.add_row(row)

    def execute(self, batch, progress=None):
        prog = None
        if progress:
            prog = progress("Loading product data", batch.rowcount)

        session = object_session(batch)
        profiles = {}

        cancel = False
        for i, row in enumerate(batch.rows, 1):

            profile = profiles.get(row.F95)
            if not profile:
                q = session.query(model.LabelProfile)
                q = q.filter(model.LabelProfile.code == row.F95)
                profile = q.one()
                profile.labels = []
                profiles[row.F95] = profile

            q = session.query(model.Product)
            q = q.filter(model.Product.upc == row.F01)
            product = q.one()

            profile.labels.append((product, row.F94))

            if prog and not prog.update(i):
                cancel = True
                break

        if not cancel:
            for profile in profiles.itervalues():
                printer = profile.get_printer(self.config)
                if not printer.print_labels(profile.labels):
                    cancel = True
                    break

        if prog:
            prog.destroy()
        return not cancel

    def set_params(self, session, **params):
        profile = params.get('profile')
        if profile:
            q = session.query(model.LabelProfile)
            q = q.filter(model.LabelProfile.code == profile)
            self.default_profile = q.one()

        quantity = params.get('quantity')
        if quantity and quantity.isdigit():
            self.default_quantity = int(quantity)
