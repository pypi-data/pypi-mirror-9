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
Basic Models for Batches

Actually the classes in this module are not true models but rather are mixins,
which provide the common columns etc. for batch tables.
"""

from __future__ import unicode_literals

import os
import datetime

import sqlalchemy as sa
from sqlalchemy.orm import relationship, object_session
from sqlalchemy.ext.declarative import declared_attr

from rattail.db.core import uuid_column
from rattail.db.types import GPCType
from rattail.db.model import User, Product


class BatchMixin(object):
    """
    Mixin for all (new-style) batch classes.

    .. note::
       This is all still very experimental.
    """

    @declared_attr
    def __table_args__(cls):
        return cls.__default_table_args__()

    @classmethod
    def __default_table_args__(cls):
        return (
            sa.ForeignKeyConstraint(['created_by_uuid'], ['user.uuid'],
                                    name='{0}_fk_created_by'.format(cls.__tablename__)),
            sa.ForeignKeyConstraint(['cognized_by_uuid'], ['user.uuid'],
                                    name='{0}_fk_cognized_by'.format(cls.__tablename__)), 
            sa.ForeignKeyConstraint(['executed_by_uuid'], ['user.uuid'],
                                    name='{0}_fk_executed_by'.format(cls.__tablename__)),
            )

    @declared_attr
    def batch_key(cls):
        return cls.__tablename__

    uuid = uuid_column()

    created = sa.Column(sa.DateTime(), nullable=False, default=datetime.datetime.utcnow, doc="""
Date and time when the batch was first created.
""")

    created_by_uuid = sa.Column(sa.String(length=32), nullable=False)

    @declared_attr
    def created_by(cls):
        return relationship(User,
                            primaryjoin=lambda: User.uuid == cls.created_by_uuid,
                            foreign_keys=lambda: [cls.created_by_uuid], doc="""
Reference to the :class:`User` who first created the batch.
""")

    cognized = sa.Column(sa.DateTime(), nullable=True, doc="""
Date and time when the batch data was last cognized.
""")

    cognized_by_uuid = sa.Column(sa.String(length=32), nullable=True)

    @declared_attr
    def cognized_by(cls):
        return relationship(User,
                            primaryjoin=lambda: User.uuid == cls.cognized_by_uuid,
                            foreign_keys=lambda: [cls.cognized_by_uuid], doc="""
Reference to the :class:`User` who last cognized the batch data.
""")

    rowcount = sa.Column(sa.Integer(), nullable=True, doc="""
Cached row count for the batch.  No guarantees perhaps, but should be accurate.
""")

    executed = sa.Column(sa.DateTime(), nullable=True, doc="""
Date and time when the batch was (last) executed.
""")

    executed_by_uuid = sa.Column(sa.String(length=32), nullable=True)

    @declared_attr
    def executed_by(cls):
        return relationship(User,
                            primaryjoin=lambda: User.uuid == cls.executed_by_uuid,
                            foreign_keys=lambda: [cls.executed_by_uuid], doc="""
Reference to the :class:`User` who (last) executed the batch.
""")

    purge = sa.Column(sa.Date(), nullable=True, doc="""
Date after which the batch may be purged.
""")


class FileBatchMixin(BatchMixin):
    """
    Mixin for all (new-style) batch classes which involve a file upload as
    their first step.

    .. note::
       This is all still very experimental.
    """

    filename = sa.Column(sa.String(length=255), nullable=False, doc="""
Base name of the file which was used as the data source.
""")

    def filedir(self, config):
        """
        Returns the absolute path to the folder in which the data file resides.
        The config object determines the root path for such files, e.g.:

        .. code-block:: ini

           [rattail]
           batch.files = /path/to/batch/files

        Within this root path, a more complete path is generated using the
        :attr:`BatchMixin.key` and the :attr:`BatchMixin.uuid` values.
        """
        batchdir = config.require('rattail', 'batch.files')
        if not self.uuid:
            object_session(self).flush()
        return os.path.abspath(os.path.join(batchdir, self.batch_key, self.uuid[:2], self.uuid[2:]))

    def filepath(self, config):
        """
        Return the absolute path where the data file resides.  This is the path
        returned by :meth:`filedir()` with the batch filename joined to it.
        """
        return os.path.join(self.filedir(config), self.filename)

    def write_file(self, config, contents):
        """
        Save a data file for the batch to the location specified by
        :meth:`filepath()`.
        """
        filedir = self.filedir(config)
        if not os.path.exists(filedir):
            os.makedirs(filedir)
        with open(os.path.join(filedir, self.filename), 'wb') as f:
            f.write(contents)

    def delete_data(self, config):
        """
        Delete the data file and folder for the batch.
        """
        path = self.filepath(config)
        if os.path.exists(path):
            os.remove(path)
        path = self.filedir(config)
        if os.path.exists(path):
            os.rmdir(path)


class BatchRowMixin(object):
    """
    Mixin for all (new-style) batch row classes.

    .. note::
    This is all still very experimental.
    """

    uuid = uuid_column()

    @declared_attr
    def __table_args__(cls):
        return cls.__default_table_args__()

    @classmethod
    def __default_table_args__(cls):
        batch_table = cls.__batch_class__.__tablename__
        row_table = cls.__tablename__
        return (
            sa.ForeignKeyConstraint(['batch_uuid'], ['{0}.uuid'.format(batch_table)],
                                    name='{0}_fk_batch_uuid'.format(row_table)),
            )

    STATUS = {}

    batch_uuid = sa.Column(sa.String(length=32), nullable=False)

    @declared_attr
    def batch(cls):
        batch_class = cls.__batch_class__
        row_class = cls

        # Must establish `Batch.data_rows` here instead of from within `Batch`
        # itself, because the row class doesn't yet exist when that happens.
        batch_class.data_rows = relationship(row_class, back_populates='batch',
                                             order_by=lambda: row_class.sequence,
                                             cascade='all, delete-orphan', doc="""
Collection of data rows for the batch.

.. note::
   I would prefer for this attribute to simply be named "rows" instead of
   "data_rows", but unfortunately (as of this writing) "rows" is essentially a
   reserved word in FormAlchemy.
""")

        # Now, here's the `BatchRow.batch` reference.
        return relationship(batch_class, back_populates='data_rows', doc="""
Reference to the parent batch to which the row belongs.
""")

    sequence = sa.Column(sa.Integer(), nullable=False, doc="""
Sequence number of the row within the batch.  This number should be from 1 to
the actual number of rows in the batch.
""")

    status_code = sa.Column(sa.Integer(), nullable=True, doc="""
Status code for the data row.  This indicates whether the row's product could
be found in the system, etc.  Ultimately the meaning of this is defined by each
particular batch type.
""")

    removed = sa.Column(sa.Boolean(), nullable=False, default=False, doc="""
Flag to indicate a row has been removed from the batch.
""")


class ProductBatchRowMixin(BatchRowMixin):
    """
    Mixin for all row classes of (new-style) batches which pertain to products.

    .. note::
    This is all still very experimental.
    """

    @classmethod
    def __default_table_args__(cls):
        batch_table = cls.__batch_class__.__tablename__
        row_table = cls.__tablename__
        return (
            sa.ForeignKeyConstraint(['batch_uuid'], ['{0}.uuid'.format(batch_table)],
                                    name='{0}_fk_batch'.format(row_table)),
            sa.ForeignKeyConstraint(['product_uuid'], ['product.uuid'],
                                    name='{0}_fk_product'.format(row_table)),
            )

    upc = sa.Column(GPCType(), nullable=True, doc="""
UPC of the product whose authz cost should be changed.
""")

    product_uuid = sa.Column(sa.String(length=32), nullable=True)

    @declared_attr
    def product(self):
        return relationship(Product, doc="""
Reference to the :class:`Product` with which the row is associated, if any.
""")

    brand_name = sa.Column(sa.String(length=100), nullable=True, doc="""
Brand name of the product.
""")

    description = sa.Column(sa.String(length=255), nullable=True, doc="""
Description of the product.
""")

    size = sa.Column(sa.String(length=255), nullable=True, doc="""
Size of the product, as string.
""")
