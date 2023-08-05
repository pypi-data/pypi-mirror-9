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
Batch Utilities
"""

from __future__ import unicode_literals

import re
import datetime
import logging

from sqlalchemy import MetaData
from sqlalchemy import and_

from .. import Session
from .. import model


batch_pattern = re.compile(r'^batch\.[0-9a-f]{32}$')

log = logging.getLogger(__name__)


def purge_batches(effective_date=None, purge_everything=False):
    """
    Purge old batches from the database.

    :param effective_date: Date against which comparisons should be made when
      determining if a batch is "old" (based on its ``purge_date`` attribute).
      The current date is assumed if none is specified.

    :param purge_everything: Boolean indicating whether the purge should be
      complete and indiscriminate, as opposed to honoring batch purge dates.
      (Use with caution!)

    :returns: Number of batches purged.
    :rtype: int
    """
    if effective_date is None:
        effective_date = datetime.date.today()

    session = Session()
    batches = session.query(model.Batch)
    if not purge_everything:
        batches = batches.filter(and_(
                model.Batch.purge != None,
                model.Batch.purge < effective_date))

    purged = 0
    for batch in batches:
        batch.drop_table()
        session.delete(batch)
        purged += 1
    session.commit()
    session.close()
    return purged


def purge_orphaned_batches():
    """
    Drop any orphaned batch tables which happen to still exist.

    This should theoretically not be necessary, if/when the batch processing is
    cleaning up after itself properly.  For now though, it seems that orphaned
    data tables are sometimes being left behind.  This removes them.
    """
    session = Session()
    current_batches = []
    for batch in session.query(model.Batch):
        current_batches.append('batch.{0}'.format(batch.uuid))
    session.close()

    def orphaned_batches(name, metadata):
        return batch_pattern.match(name) and name not in current_batches

    metadata = MetaData(session.bind)
    metadata.reflect(only=orphaned_batches)
    count = len(metadata.tables)
    for table in reversed(metadata.sorted_tables):
        log.debug("dropping orphaned batch table: {0}".format(table.name))
        table.drop()
    return count
