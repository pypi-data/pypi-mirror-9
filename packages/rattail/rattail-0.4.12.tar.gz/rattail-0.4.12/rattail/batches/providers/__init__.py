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
Batch Providers
"""

from __future__ import unicode_literals

import datetime

from rattail.core import Object
from rattail import sil
from ...db import model


__all__ = ['BatchProvider']


class BatchProvider(Object):

    name = None
    description = None
    source = 'RATAIL'
    destination = None
    action_type = None
    purge_date_offset = 60

    session = None

    def __init__(self, config, **kwargs):
        self.config = config
        super(BatchProvider, self).__init__(**kwargs)

    def add_columns(self, batch):
        pass

    def add_rows_begin(self, batch, data):
        pass

    def add_rows(self, batch, data, progress=None):

        result = self.add_rows_begin(batch, data)
        if result is not None and not result:
            return False

        prog = None
        if progress:
            prog = progress("Adding rows to batch \"%s\"" % batch.description,
                            data.count())
        cancel = False
        for i, datum in enumerate(data, 1):
            self.add_row(batch, datum)
            if prog and not prog.update(i):
                cancel = True
                break
        if prog:
            prog.destroy()

        if not cancel:
            result = self.add_rows_end(batch, progress)
            if result is not None:
                cancel = not result

        return not cancel

    def add_rows_end(self, batch, progress=None):
        pass

    def execute(self, batch, progress=None):
        raise NotImplementedError

    def make_batch(self, session, data, progress=None):
        from ...db import model

        self.session = session

        batch = model.Batch()
        batch.provider = self.name
        batch.source = self.source
        batch.id = sil.consume_batch_id(batch.source)
        batch.destination = self.destination
        batch.description = self.description
        batch.action_type = self.action_type
        self.set_purge_date(batch)
        session.add(batch)
        session.flush()

        self.add_columns(batch)
        batch.create_table()
        if not self.add_rows(batch, data, progress=progress):
            batch.drop_table()
            return None
        return batch

    def set_purge_date(self, batch):
        today = datetime.datetime.utcnow().date()
        purge_offset = datetime.timedelta(days=self.purge_date_offset)
        batch.purge = today + purge_offset

    def set_params(self, session, **params):
        pass
