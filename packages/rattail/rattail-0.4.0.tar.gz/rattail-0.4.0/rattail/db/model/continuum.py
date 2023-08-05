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
SQLAlchemy-Continuum integration
"""

from __future__ import unicode_literals

import socket

import six

import sqlalchemy as sa
import sqlalchemy_continuum as continuum
from sqlalchemy_continuum.transaction import TransactionBase, create_triggers
from sqlalchemy_continuum.plugins import Plugin
from sqlalchemy_utils.functions import get_primary_keys

from rattail.util import OrderedDict


class RattailTransactionFactory(continuum.TransactionFactory):
    """
    Custom transaction factory for Continuum.  This is a little heavy-handed
    (it copies a fair chunk of code from upstream) but as of this writing was
    the only way to work around Continuum's assumption that the foreign key for
    ``Transaction.user`` should reference the ``user.id`` column (which we
    don't have).
    """

    def create_class(self, manager):
        """
        Create Transaction class.
        """
        class Transaction(
            manager.declarative_base,
            TransactionBase
        ):
            __tablename__ = 'transaction'
            __versioning_manager__ = manager

            id = sa.Column(
                sa.types.BigInteger,
                primary_key=True,
                autoincrement=True
            )

            if self.remote_addr:
                remote_addr = sa.Column(sa.String(50))

            if manager.user_cls:
                user_cls = manager.user_cls
                registry = manager.declarative_base._decl_class_registry

                if isinstance(user_cls, six.string_types):
                    try:
                        user_cls = registry[user_cls]
                    except KeyError:
                        raise continuum.ImproperlyConfigured(
                            'Could not build relationship between Transaction'
                            ' and %s. %s was not found in declarative class '
                            'registry. Either configure VersioningManager to '
                            'use different user class or disable this '
                            'relationship ' % (user_cls, user_cls)
                        )

                user_uuid = sa.Column(
                    sa.inspect(user_cls).primary_key[0].type,
                    sa.ForeignKey(
                        '%s.uuid' % user_cls.__tablename__
                    ),
                    index=True
                )

                user = sa.orm.relationship(user_cls)

            def __repr__(self):
                fields = ['id', 'issued_at', 'user']
                field_values = OrderedDict(
                    (field, getattr(self, field))
                    for field in fields
                    if hasattr(self, field)
                )
                return '<Transaction %s>' % ', '.join(
                    (
                        '%s=%r' % (field, value)
                        if not isinstance(value, six.integer_types)
                        # We want the following line to ensure that longs get
                        # shown without the ugly L suffix on python 2.x
                        # versions
                        else '%s=%d' % (field, value)
                        for field, value in field_values.items()
                    )
                )

        if manager.options['native_versioning']:
            create_triggers(Transaction)
        return Transaction


class RattailPlugin(Plugin):

    def transaction_args(self, uow, session):
        user = getattr(session, 'continuum_user', None)
        return {
            'user_uuid': user.uuid if user else None,
            'remote_addr': socket.gethostbyname(socket.gethostname()),
            }


versioning_manager = continuum.VersioningManager(
    transaction_cls=RattailTransactionFactory())

continuum.make_versioned(
    manager=versioning_manager,
    plugins=[RattailPlugin()])


def count_versions(obj):
    """
    Return the number of versions given object has.

    .. note::
       This function was copied from the one at
       :func:`continuum:sqlalchemy_continuum.utils.count_versions()`, and
       changed so as not to try to use the ``repr()`` value of the table's
       primary key value, since for us that's usually an UUID as unicode string.

    :param obj: SQLAlchemy declarative model object
    """
    session = sa.orm.object_session(obj)
    if session is None:
        # If object is transient, we assume it has no version history.
        return 0
    manager = continuum.get_versioning_manager(obj)
    table_name = manager.option(obj, 'table_name') % obj.__table__.name

    def value(o, k):
        v = getattr(o, k)
        if isinstance(v, unicode):
            v = v.encode('utf_8')
        return v

    criteria = [
        '%s = %r' % (pk, value(obj, pk))
        for pk in get_primary_keys(obj)
    ]
    query = 'SELECT COUNT(1) FROM %s WHERE %s' % (
        table_name,
        ' AND '.join(criteria)
    )
    return session.execute(query).scalar()


def model_transaction_query(session, uuid, parent_class, child_classes=None):
    """
    Return a query capable of finding all Continuum ``Transaction`` instances
    which are associated with a model instance.
    """
    from rattail.db import model

    Transaction = continuum.transaction_class(parent_class)
    Version = continuum.version_class(parent_class)

    def normalize_child_classes():
        classes = []
        for cls in child_classes:
            if not isinstance(cls, tuple):
                cls = (cls, 'uuid')
            classes.append(cls)
        return classes

    query = session.query(Transaction)\
        .outerjoin(Version, sa.and_(
            Version.uuid == uuid,
            Version.transaction_id == Transaction.id))

    classes = [Version]
    if child_classes:
        for model_class, attr in normalize_child_classes():
            if isinstance(model_class, type) and issubclass(model_class, model.Base):
                cls = continuum.version_class(model_class)
                query = query.outerjoin(cls, sa.and_(
                        cls.transaction_id == Transaction.id,
                        getattr(cls, attr) == uuid))
                classes.append(cls)

    return query.filter(sa.or_(
            *[cls.uuid != None for cls in classes]))
