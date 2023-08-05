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
Import Data Providers
"""

from __future__ import unicode_literals

import datetime

from rattail.core import Object
from rattail.db.cache import cache_model


class DataProvider(Object):
    """
    Base class for import data providers.
    """
    importer_class = None
    normalize_progress_message = "Normalizing source data"
    progress = None

    def __init__(self, config, session, importer=None, importer_kwargs={}, **kwargs):
        self.config = config
        self.session = session
        if importer is None:
            self.importer = self.importer_class(config, session, **importer_kwargs)
        else:
            self.importer = importer
        super(DataProvider, self).__init__(**kwargs)

    @property
    def model_class(self):
        return self.importer.model_class

    @property
    def key(self):
        """
        Key by which records should be matched between the source data and
        Rattail.
        """
        raise NotImplementedError("Please define the `key` for your data provider.")

    @property
    def model_name(self):
        return self.model_class.__name__

    def cache_model(self, model_class, key, **kwargs):
        """
        Convenience method for caching a model.
        """
        kwargs.setdefault('progress', self.progress)
        return cache_model(self.session, model_class, key=key, **kwargs)

    def setup(self, progress):
        """
        Perform any setup necessary, e.g. cache lookups for existing data.
        """

    def get_data(self, progress=None, normalize_progress_message=None):
        """
        Return the full set of normalized data which is to be imported.
        """
        self.now = datetime.datetime.utcnow()
        self.progress = progress
        self.setup(progress)
        source_data = self.get_source_data(progress=progress)
        return self.normalize_source_data(source_data, progress=progress)

    def get_source_data(self, progress=None):
        """
        Return the data which is to be imported.
        """
        return []

    def normalize_source_data(self, source_data, progress=None):
        """
        Return a normalized version of the full set of source data.
        """
        data = []
        count = len(source_data)
        if count == 0:
            return data
        prog = None
        if progress:
            prog = progress(self.normalize_progress_message, count)
        for i, record in enumerate(source_data, 1):
            record = self.normalize(record)
            if record:
                data.append(record)
            if prog:
                prog.update(i)
        if prog:
            prog.destroy()
        return data

    def normalize(self, data):
        """
        Normalize a source data record.  Generally this is where the provider
        may massage the record in any way necessary, so that its values are
        more "native" and can be used for direct comparison with, and
        assignment to, the target model instance.

        Note that if you override this, your method must return the data to be
        imported.  If your method returns ``None`` then that particular record
        would be skipped and not imported.
        """
        return data


class QueryDataProxy(object):
    """
    Simple proxy to wrap a SQLAlchemy query and make it sort of behave like a
    normal sequence, as much as needed to make a ``DataProvider`` happy.
    """

    def __init__(self, query):
        self.query = query

    def __len__(self):
        return self.query.count()

    def __iter__(self):
        return iter(self.query)


class QueryProvider(DataProvider):
    """
    Data provider whose data source is a SQLAlchemy query.  Note that this
    needn't be a Rattail database query; any database will work as long as a
    SQLAlchemy query is behind it.
    """

    def query(self):
        """
        Return the query which will define the data set.
        """
        raise NotImplementedError

    def get_source_data(self, progress=None):
        """
        Return the data which is to be imported.
        """
        return QueryDataProxy(self.query())
