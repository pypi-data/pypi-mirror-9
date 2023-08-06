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
Core Importer Stuff
"""

from __future__ import unicode_literals

import logging

from sqlalchemy.orm.exc import NoResultFound

from rattail.db import model
from rattail.core import Object
from rattail.util import load_object
from rattail.db.cache import cache_model


log = logging.getLogger(__name__)


def make_importer(config, session, spec):
    """
    Create an importer instance according to the given spec.  For now..see the
    source code for more details.
    """
    importer = None
    if '.' not in spec and ':' not in spec:
        from rattail.db.importing import models
        if hasattr(models, spec):
            importer = getattr(models, spec)
        elif hasattr(models, '{0}Importer'.format(spec)):
            importer = getattr(models, '{0}Importer'.format(spec))
    else:
        importer = load_object(spec)
    if importer:
        return importer(config, session)


class Importer(Object):
    """
    Base class for model importers.
    """
    supported_fields = []
    cached_data = None

    complex_fields = []
    """
    Sequence of field names which are considered complex and therefore require
    custom logic provided by the derived class, etc.
    """

    def __init__(self, config, session, **kwargs):
        self.config = config
        self.session = session
        super(Importer, self).__init__(**kwargs)

    @property
    def model_class(self):
        return getattr(model, self.__class__.__name__[:-8])

    @property
    def model_name(self):
        return self.model_class.__name__

    @property
    def simple_fields(self):
        return self.supported_fields

    def import_data(self, records, fields, key, count=None, progress=None):
        """
        Import some data.
        """
        if count is None:
            count = len(records)
        if count == 0:
            return 0

        self.fields = fields
        self.key = key
        if isinstance(key, basestring):
            self.key = (key,)
        self.progress = progress
        self.setup(progress)
        self.cache_data(progress)

        prog = None
        if progress:
            prog = progress("Importing {0} data".format(self.model_name), count)

        affected = 0
        for i, src_data in enumerate(records, 1):
            self.normalize_record(src_data)

            dirty = False
            inst_data = self.get_instance_data(src_data)
            if inst_data:
                if self.data_differs(inst_data, src_data):
                    instance = self.get_instance(src_data)
                    self.update_instance(instance, src_data)
                    dirty = True
            else:
                instance = self.new_instance(src_data)
                assert instance, "Failed to create new model instance for data: {0}".format(repr(src_data))
                self.update_instance(instance, src_data)
                self.session.add(instance)
                log.debug("created new {0}: {1}".format(self.model_name, instance))
                dirty = True

            if dirty:
                self.session.flush()
                affected += 1

            if prog:
                prog.update(i)
        if prog:
            prog.destroy()

        return affected

    def setup(self, progress):
        """
        Perform any setup necessary, e.g. cache lookups for existing data.
        """

    def cache_query_options(self):
        """
        Return a list of options to apply to the cache query, if needed.
        """

    def cache_model(self, model_class, key, **kwargs):
        """
        Convenience method for caching a model.
        """
        kwargs.setdefault('progress', self.progress)
        return cache_model(self.session, model_class, key=key, **kwargs)

    def get_cache_key(self, instance, normalized):
        """
        Get the primary model cache key for a given instance/data object.
        """
        return tuple(normalized['data'].get(k) for k in self.key)

    def cache_data(self, progress):
        """
        Cache all existing model instances as normalized data.
        """
        self.cached_data = self.cache_model(self.model_class, self.get_cache_key,
                                       query_options=self.cache_query_options(),
                                       normalizer=self.normalize_cache)

    def normalize_cache(self, instance):
        """
        Normalizer for cache data.  This adds the instance to the cache in
        addition to its normalized data.  This is so that if lots of updates
        are required, we don't we have to constantly fetch them.
        """
        return {'instance': instance, 'data': self.normalize_instance(instance)}

    def data_differs(self, inst_data, src_data):
        """
        Compare source record data to instance data to determine if there is a
        net change.
        """
        for field in src_data:
            if src_data[field] != inst_data[field]:
                log.debug("field {0} differed for instance data: {1}, source data: {2}".format(
                        field, repr(inst_data), repr(src_data)))
                return True
        return False

    def string_or_null(self, data, *fields):
        """
        For each field specified, ensure the data value is a non-empty string,
        or ``None``.
        """
        for field in fields:
            if field in data:
                value = data[field]
                value = value.strip() if value else None
                data[field] = value or None

    def int_or_null(self, data, *fields):
        """
        For each field specified, ensure the data value is a non-zero integer,
        or ``None``.
        """
        for field in fields:
            if field in data:
                value = data[field]
                value = int(value) if value else None
                data[field] = value or None

    def prioritize_2(self, data, field):
        """
        Prioritize the data values for the pair of fields implied by the given
        fieldname.  I.e., if only one non-empty value is present, make sure
        it's in the first slot.
        """
        field2 = '{0}_2'.format(field)
        if field in data and field2 in data:
            if data[field2] and not data[field]:
                data[field], data[field2] = data[field2], None

    def normalize_record(self, data):
        """
        Normalize the source data record, if necessary.
        """

    def get_key(self, data):
        """
        Return the key value for the given source data record.
        """
        return tuple(data.get(k) for k in self.key)

    def get_instance(self, data):
        """
        Fetch an instance from our database which corresponds to the source
        data, if possible; otherwise return ``None``.
        """
        key = self.get_key(data)
        if not key:
            log.warning("source {0} has no {1}: {2}".format(
                    self.model_name, self.key, repr(data)))
            return None

        if self.cached_data is not None:
            data = self.cached_data.get(key)
            return data['instance'] if data else None

        q = self.session.query(self.model_class)
        for i, k in enumerate(self.key):
            q = q.filter(getattr(self.model_class, k) == key[i])
        try:
            instance = q.one()
        except NoResultFound:
            return None
        else:
            return instance

    def get_instance_data(self, data):
        """
        Return a normalized data record for the model instance corresponding to
        the source data record, or ``None``.
        """
        key = self.get_key(data)
        if not key:
            log.warning("source {0} has no {1}: {2}".format(
                    self.model_name, self.key, repr(data)))
            return None
        if self.cached_data is not None:
            data = self.cached_data.get(key)
            return data['data'] if data else None
        instance = self.get_instance(data)
        if instance:
            return self.normalize_instance(instance)

    def normalize_instance(self, instance):
        """
        Normalize a model instance.
        """
        data = {}
        for field in self.simple_fields:
            data[field] = getattr(instance, field)
        return data

    def new_instance(self, data):
        """
        Return a new model instance to correspond to the source data record.
        """
        kwargs = {}
        key = self.get_key(data)
        for i, k in enumerate(self.key):
            if k in self.simple_fields:
                kwargs[k] = key[i]
        return self.model_class(**kwargs)

    def update_instance(self, instance, data):
        """
        Update the given model instance with the given data.
        """
        for field in self.simple_fields:
            if field in data:
                setattr(instance, field, data[field])
