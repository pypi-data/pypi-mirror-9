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

import os
import shutil


class BatchHandler(object):
    """
    Base class for all batch handlers.  This isn't really useful by itself but
    it is expected that other batches will derive from it.
    """
    show_progress = False

    def __init__(self, config):
        self.config = config

    @property
    def batch_model_class(self):
        """
        Reference to the data model class of the batch type for which this
        handler is responsible.
        """
        raise NotImplementedError("Must set the 'batch_model_class' attribute "
                                  "for class '{0}'".format(self.__class__.__name__))

    def make_batch(self, session, **kwargs):
        """
        Create a new batch instance and return it.  All keyword arguments are
        passed to the batch model constructor.  Note that some keyword
        arguments may be required, depending on the type of batch.
        """
        return self.batch_model_class(**kwargs)

    def get_execute_title(self, batch):
        """
        Get a human-friendly string describing the execution step for a batch.
        Most handlers should probably override this to provide something more
        useful than the default, which is just "Execute this batch".
        """
        return "Execute this batch"

    def refresh_data(self, session, batch, progress=None):
        """
        Refresh all data for the batch.
        """
        del batch.data_rows[:]

    def make_rows(self, session, batch, data, progress=None):
        """
        Create batch rows from the given data set.
        """
        prog = None
        if progress:
            prog = progress("Refreshing data for batch", len(data))

        cancel = False
        for i, row in enumerate(data, 1):
            row.sequence = i
            self.cognize_row(session, row)
            batch.data_rows.append(row)
            if i % 250 == 0:    # seems to help progres UI
                session.flush()
            if prog and not prog.update(i):
                cancel = True
                break

        if prog:
            prog.destroy()
        return not cancel

    def cognize_row(self, session, row):
        raise NotImplementedError

    def execute(self, batch):
        raise NotImplementedError


class FileBatchHandler(BatchHandler):
    """
    Base class for all file-based batch handlers.  Adds some conveniences for
    managing data file storage.

    .. note::
       Current implementation only supports one data file per batch.
    """

    @property
    def root_datadir(self):
        """
        The absolute path of the root folder in which data for this particular
        type of batch is stored.  The structure of this path is as follows:

        .. code-block:: none

           /{root_batch_data_dir}/{batch_type_key}

        * ``{root_batch_data_dir}`` - Value of the 'batch.files' option in the
          [rattail] section of config file.
        * ``{batch_type_key}`` - Unique key for the type of batch it is.

        .. note::
           While it is likely that the data folder returned by this method
           already exists, this method does not guarantee it.
        """
        return os.path.join(self.config.require('rattail', 'batch.files'),
                            self.batch_model_class.batch_key)

    def datadir(self, batch):
        """
        Returns the absolute path of the folder in which the batch's source
        data file(s) resides.  Note that the batch must already have been
        persisted to the database.  The structure of the path returned is as
        follows:

        .. code-block:: none

           /{root_datadir}/{uuid[:2]}/{uuid[2:]}

        * ``{root_datadir}`` - Value returned by :meth:`root_datadir()`.
        * ``{uuid[:2]}`` - First two characters of batch UUID.
        * ``{uuid[2:]}`` - All batch UUID characters *after* the first two.

        .. note::
           While it is likely that the data folder returned by this method
           already exists, this method does not guarantee any such thing.  It
           is typically assumed that the path will have been created by a
           previous call to :meth:`make_batch()` however.
        """
        return os.path.join(self.root_datadir, batch.uuid[:2], batch.uuid[2:])

    def data_path(self, batch):
        """
        Returns the full path to the batch's one and only data file.  As with
        :meth:`datadir()`, this method does not guarantee the existence of the
        file.
        """
        return os.path.join(self.datadir(batch), batch.filename)

    def make_batch(self, session, path, **kwargs):
        """
        Create a new batch as per usual, plus save a copy of the data file (at
        ``path``) to the configured batch storage folder.
        """
        batch = self.batch_model_class(**kwargs)
        session.add(batch)
        session.flush()
        self.set_data_file(batch, path)
        return batch

    def set_data_file(self, batch, path):
        """
        Assign the data file found at ``path`` to the batch.  This overwrites
        the batch's :attr:`filename` attribute and places a copy of the data
        file in the batch's data folder.
        """
        batch.filename = os.path.basename(path)
        datadir = self.datadir(batch)
        os.makedirs(datadir)
        shutil.copyfile(path, os.path.join(datadir, batch.filename))
