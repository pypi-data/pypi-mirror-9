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
Data Changes Interface
"""

from __future__ import unicode_literals

import logging

from sqlalchemy.orm import object_mapper, RelationshipProperty
from sqlalchemy.orm.interfaces import SessionExtension
from sqlalchemy.orm.session import Session

from rattail.core import get_uuid
from rattail.db.continuum import versioning_manager


__all__ = ['record_changes']

log = logging.getLogger(__name__)


def record_changes(session, ignore_role_changes=True):
    """
    Record all changes which occur within a session.

    :param session: A :class:`sqlalchemy:sqlalchemy.orm.session.Session` class,
       or an instance thereof.

    :param ignore_role_changes: Whether changes involving roles and role
       membership should be ignored.  This defaults to ``True``, which means
       each database will be responsible for maintaining its own role (and by
       extension, permissions) data.
    """
    recorder = ChangeRecorder(ignore_role_changes)
    try:
        from sqlalchemy.event import listen
    except ImportError: # pragma: no cover
        extension = ChangeRecorderExtension(recorder)
        if isinstance(session, Session):
            session.extensions.append(extension)
        else:
            session.configure(extension=extension)
    else:
        listen(session, u'before_flush', recorder)


class ChangeRecorder(object):
    """
    Listener for session ``before_flush`` events.

    This class is responsible for adding stub records to the ``changes`` table,
    which will in turn be used by the database synchronizer to manage change
    data propagation.
    """

    def __init__(self, ignore_role_changes=True):
        self.ignore_role_changes = ignore_role_changes

    def __call__(self, session, flush_context, instances):
        """
        Method invoked when session ``before_flush`` event occurs.
        """
        # TODO: Not sure if our event replaces the one registered by Continuum,
        # or what.  But this appears to be necessary to keep that system
        # working when we enable ours...
        versioning_manager.before_flush(session, flush_context, instances)

        for instance in session.deleted:
            log.debug("ChangeRecorder: found deleted instance: {0}".format(repr(instance)))
            self.record_change(session, instance, deleted=True)
        for instance in session.new:
            log.debug("ChangeRecorder: found new instance: {0}".format(repr(instance)))
            self.record_change(session, instance)
        for instance in session.dirty:
            if session.is_modified(instance, passive=True):
                # Orphaned objects which really are pending deletion show up in
                # session.dirty instead of session.deleted, hence this check.
                # See also https://groups.google.com/d/msg/sqlalchemy/H4nQTHphc0M/Xr8-Cgra0Z4J
                if self.is_deletable_orphan(instance):
                    log.debug("ChangeRecorder: found orphan pending deletion: {0}".format(repr(instance)))
                    self.record_change(session, instance, deleted=True)
                else:
                    log.debug("ChangeRecorder: found dirty instance: {0}".format(repr(instance)))
                    self.record_change(session, instance)

    def is_deletable_orphan(self, instance):
        """
        Determine if an object is an orphan and pending deletion.
        """
        mapper = object_mapper(instance)
        for property_ in mapper.iterate_properties:
            if isinstance(property_, RelationshipProperty):
                relationship = property_

                # Does this relationship refer back to the instance class?
                backref = relationship.backref or relationship.back_populates
                if backref:

                    # Does the other class mapper's relationship wish to delete orphans?
                    # other_relationship = relationship.mapper.relationships[backref]

                    # Sometimes backrefs are tuples; first element is name.
                    if isinstance(backref, tuple):
                        backref = backref[0]

                    other_relationship = relationship.mapper.get_property(backref)
                    if other_relationship.cascade.delete_orphan:

                        # Is this instance an orphan?
                        if getattr(instance, relationship.key) is None:
                            return True

        return False

    def record_change(self, session, instance, deleted=False):
        """
        Record a change record in the database.

        If ``instance`` represents a change in which we are interested, then
        this method will create (or update) a :class:`rattail.db.model.Change`
        record.

        :returns: ``True`` if a change was recorded, or ``False`` if it was
           ignored.
        """
        from rattail.db import model

        # No need to record changes for changes.
        if isinstance(instance, model.Change):
            return False

        # No need to record changes for batch data.
        if isinstance(instance, (model.Batch, model.BatchColumn, model.BatchRow,
                                 model.BatchMixin, model.BatchRowMixin)):
            return False

        # Ignore instances which don't use UUID.
        if not hasattr(instance, 'uuid'):
            return False

        # Ignore Role instances, if so configured.
        if self.ignore_role_changes and isinstance(instance, (model.Role, model.UserRole)):
            return False

        # Provide an UUID value, if necessary.
        self.ensure_uuid(instance)

        # Record the change.
        change = session.query(model.Change).get(
            (instance.__class__.__name__, instance.uuid))
        if not change:
            change = model.Change(
                class_name=instance.__class__.__name__,
                uuid=instance.uuid)
            session.add(change)
        change.deleted = deleted
        log.debug("ChangeRecorder.record_change: recorded change: %s" % repr(change))
        return True

    def ensure_uuid(self, instance):
        """
        Ensure the given instance has a UUID value.

        This uses the following logic:

        * If the instance already has a UUID, nothing will be done.

        * If the instance contains a foreign key to another table, then that
          relationship will be traversed and the foreign object's UUID will be used
          to populate that of the instance.

        * Otherwise, a new UUID will be generated for the instance.
        """

        if instance.uuid:
            return

        mapper = object_mapper(instance)
        if not mapper.columns['uuid'].foreign_keys:
            instance.uuid = get_uuid()
            return

        for prop in mapper.iterate_properties:
            if (isinstance(prop, RelationshipProperty)
                and len(prop.remote_side) == 1
                and list(prop.remote_side)[0].key == 'uuid'):

                foreign_instance = getattr(instance, prop.key)
                if foreign_instance:
                    self.ensure_uuid(foreign_instance)
                    instance.uuid = foreign_instance.uuid
                    return

        instance.uuid = get_uuid()
        log.error("ChangeRecorder.ensure_uuid: unexpected scenario; generated new UUID for instance: {0}".format(repr(instance)))


class ChangeRecorderExtension(SessionExtension): # pragma: no cover
    """
    Session extension for recording changes.

    .. note::
       This is only used when the installed SQLAlchemy version is old enough
       not to support the new event interfaces.
    """

    def __init__(self, recorder):
        self.recorder = recorder

    def before_flush(self, session, flush_context, instances):
        self.recorder(session, flush_context, instances)
