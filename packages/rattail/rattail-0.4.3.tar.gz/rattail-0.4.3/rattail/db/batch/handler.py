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
Basic Batch Handler
"""

from __future__ import unicode_literals


class BatchHandler(object):
    """
    Base class for all batch handlers.  This isn't really useful by itself but
    it is expected that other batches will derive from it.
    """
    show_progress = False

    def __init__(self, config):
        self.config = config

    def refresh_data(self, session, batch, progress_factory=None):
        """
        Refresh all data for the batch.
        """
        del batch.data_rows[:]

    def make_rows(self, session, batch, data, progress_factory=None):
        """
        Create batch rows from the given data set.
        """
        progress = None
        if progress_factory:
            progress = progress_factory("Refreshing data for batch", len(data))

        cancel = False
        for i, row in enumerate(data, 1):
            row.sequence = i
            self.cognize_row(session, row)
            batch.data_rows.append(row)
            if progress and not progress.update(i):
                cancel = True
                break

        if progress:
            progress.destroy()
        return not cancel

    def cognize_row(self, session, batch, row):
        raise NotImplementedError

    def execute(self, batch):
        raise NotImplementedError
