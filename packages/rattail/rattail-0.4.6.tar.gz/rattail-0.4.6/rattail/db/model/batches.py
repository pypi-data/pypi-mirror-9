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
Data Models for *OLD* Batch System

Please don't use any of this for future development!  New batches should
instead be based on :class:`rattail.db.batch.BatchMixin` and friends.
"""

from __future__ import unicode_literals

import re
import datetime
import logging

import sqlalchemy as sa
from sqlalchemy.orm import relationship, object_session
from sqlalchemy.ext.orderinglist import ordering_list

from .core import Base, uuid_column, GPCType
from rattail.sil import get_column
 

log = logging.getLogger(__name__)


class Batch(Base):
    """
    Represents a SIL-compliant batch of data.
    """

    __tablename__ = 'batch'

    uuid = uuid_column()
    provider = sa.Column(sa.String(length=50))
    id = sa.Column(sa.String(length=8))
    source = sa.Column(sa.String(length=6))
    destination = sa.Column(sa.String(length=6))
    action_type = sa.Column(sa.String(length=6))
    description = sa.Column(sa.String(length=50))
    rowcount = sa.Column(sa.Integer(), default=0)
    executed = sa.Column(sa.DateTime())
    # TODO: Convert this to a DateTime, to handle time zone issues.
    purge = sa.Column(sa.Date())

    _rowclasses = {}

    sil_type_pattern = re.compile(r'^(CHAR|NUMBER)\((\d+(?:\,\d+)?)\)$')

    def __repr__(self):
        return "Batch(uuid={0})".format(repr(self.uuid))

    def __unicode__(self):
        return unicode(self.description or '')

    @property
    def rowclass(self):
        """
        Returns the mapped class for the underlying row (data) table.
        """

        if not self.uuid:
            object_session(self).flush()
            assert self.uuid

        if self.uuid not in self._rowclasses:

            kwargs = {
                '__tablename__': 'batch.%s' % self.uuid,
                'uuid': uuid_column(),
                'ordinal': sa.Column(sa.Integer(), nullable=False),
                }

            for column in self.columns:
                data_type = self.get_sqlalchemy_type(column.data_type)
                kwargs[column.name] = sa.Column(data_type)
            rowclass = type('BatchRow_{0}'.format(self.uuid).encode('ascii'), (Base, BatchRow), kwargs)

            batch_uuid = self.uuid
            def batch(self):
                return object_session(self).query(Batch).get(batch_uuid)
            rowclass.batch = property(batch)

            self._rowclasses[self.uuid] = rowclass

        return self._rowclasses[self.uuid]

    @classmethod
    def get_sqlalchemy_type(cls, sil_type):
        """
        Returns a SQLAlchemy data type according to a SIL data type.
        """

        if sil_type == 'GPC(14)':
            return GPCType()

        if sil_type == 'FLAG(1)':
            return sa.Boolean()

        m = cls.sil_type_pattern.match(sil_type)
        if m:
            data_type, precision = m.groups()
            if precision.isdigit():
                precision = int(precision)
                scale = 0
            else:
                precision, scale = precision.split(',')
                precision = int(precision)
                scale = int(scale)
            if data_type == 'CHAR':
                assert not scale, "FIXME"
                return sa.String(length=precision)
            if data_type == 'NUMBER':
                return sa.Numeric(precision=precision, scale=scale)

        assert False, "FIXME"

    def add_column(self, sil_name=None, **kwargs):
        column = BatchColumn(sil_name, **kwargs)
        self.columns.append(column)

    def add_row(self, row, **kwargs):
        """
        Adds a row to the batch data table.
        """
        session = object_session(self)
        # FIXME: This probably needs to use a func.max() query.
        row.ordinal = self.rowcount + 1
        session.add(row)
        self.rowcount += 1
        session.flush()

    def create_table(self):
        """
        Creates the batch's data table within the database.
        """
        session = object_session(self)
        self.rowclass.__table__.create(session.bind)

    def drop_table(self):
        """
        Drops the batch's data table from the database.
        """
        log.debug("dropping normal batch table: {0}".format(self.rowclass.__table__.name))
        session = object_session(self)
        self.rowclass.__table__.drop(bind=session.bind, checkfirst=True)

    def execute(self, progress=None):
        from rattail.batches.exceptions import BatchProviderNotFound

        try:
            provider = self.get_provider()
            if not provider.execute(self, progress):
                return False

        except BatchProviderNotFound:
            executor = self.get_executor()
            if not executor.execute(self, progress):
                return False

        self.executed = datetime.datetime.utcnow()
        object_session(self).flush()
        return True

    def get_provider(self):
        from rattail.batches import get_provider
        assert self.provider
        return get_provider(self.provider)

    def get_executor(self):
        from rattail.db.batches import get_batch_executor
        assert self.provider
        return get_batch_executor(self.provider)

    @property
    def rows(self):
        session = object_session(self)
        q = session.query(self.rowclass)
        q = q.order_by(self.rowclass.ordinal)
        return q


class BatchColumn(Base):
    """
    Represents a SIL column associated with a batch.
    """
    __tablename__ = 'batch_column'
    __table_args__ = (
        sa.ForeignKeyConstraint(['batch_uuid'], ['batch.uuid'], name='batch_column_fk_batch'),
        )

    uuid = uuid_column()
    batch_uuid = sa.Column(sa.String(length=32))
    ordinal = sa.Column(sa.Integer(), nullable=False)
    name = sa.Column(sa.String(length=20))
    display_name = sa.Column(sa.String(length=50))
    sil_name = sa.Column(sa.String(length=10))
    data_type = sa.Column(sa.String(length=15))
    description = sa.Column(sa.String(length=50))
    visible = sa.Column(sa.Boolean(), default=True)

    def __init__(self, sil_name=None, **kwargs):
        if sil_name:
            kwargs['sil_name'] = sil_name
            sil_column = get_column(sil_name)
            kwargs.setdefault('name', sil_name)
            kwargs.setdefault('data_type', sil_column.data_type)
            kwargs.setdefault('description', sil_column.description)
            kwargs.setdefault('display_name', sil_column.display_name)
        super(BatchColumn, self).__init__(**kwargs)

    def __repr__(self):
        return "BatchColumn(uuid={0})".format(repr(self.uuid))

    def __unicode__(self):
        return unicode(self.display_name or '')


Batch.columns = relationship(
    BatchColumn, backref='batch',
    collection_class=ordering_list('ordinal'),
    order_by=BatchColumn.ordinal,
    cascade='save-update, merge, delete, delete-orphan')


class BatchRow(object):
    """
    Superclass of batch row objects.
    """

    def __unicode__(self):
        return u"Row {0}".format(self.ordinal)
