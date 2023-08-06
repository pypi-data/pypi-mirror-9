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
Batch Exceptions
"""

from __future__ import unicode_literals


class BatchError(Exception):

    pass


class BatchProviderNotFound(BatchError):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "Batch provider not found: %s" % self.name


class BatchDestinationNotSupported(BatchError):

    def __init__(self, batch):
        self.batch = batch

    def __str__(self):
        return "Destination '%s' not supported for batch: %s" % (
            self.batch.destination, self.batch.description)
