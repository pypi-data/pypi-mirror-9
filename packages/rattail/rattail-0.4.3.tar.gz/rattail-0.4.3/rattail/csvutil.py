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
CSV File Utilities

Contains various utilities relating to CSV file processing.

.. note::
   This module is named ``csvutil`` instead of ``csv`` primarily as a
   workaround to the problem of ``PythonService.exe`` insisting on doing
   relative imports.
"""

from __future__ import unicode_literals

import csv
import codecs
from cStringIO import StringIO


class DictWriter(csv.DictWriter):
    """
    Convenience implementation of ``csv.DictWriter``.

    This exists only to provide the :meth:`writeheader()` method on Python 2.6.
    """

    def writeheader(self):
        if hasattr(csv.DictWriter, 'writeheader'):
            return csv.DictWriter.writeheader(self)
        self.writer.writerow(self.fieldnames)


class UTF8Recoder(object):
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8.

    .. note::
       This class was stolen from the Python 2.7 documentation.
    """

    def __init__(self, fileobj, encoding):
        self.reader = codecs.getreader(encoding)(fileobj)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode('utf_8')


class UnicodeReader(object):
    """
    A CSV reader which will iterate over lines in a CSV file, which is encoded
    in the given encoding.

    .. note::
       This class was stolen from the Python 2.7 documentation.
    """

    def __init__(self, fileobj, dialect=csv.excel, encoding='utf_8', **kwargs):
        fileobj = UTF8Recoder(fileobj, encoding)
        self.reader = csv.reader(fileobj, dialect=dialect, **kwargs)

    def __iter__(self):
        return self

    def next(self):
        row = self.reader.next()
        return [unicode(x, 'utf_8') for x in row]


class UnicodeDictReader(object):
    """
    A CSV Dict reader which will iterate over lines in a CSV file, which is
    encoded in the given encoding.
    """

    def __init__(self, fileobj, dialect=csv.excel, encoding='utf_8', **kwargs):
        fileobj = UTF8Recoder(fileobj, encoding)
        self.reader = csv.reader(fileobj, dialect=dialect, **kwargs)
        self.header = self.reader.next()

    def next(self):
        row = self.reader.next()
        vals = [unicode(s, 'utf_8') for s in row]
        return dict((self.header[i], vals[i]) for i in range(len(self.header)))

    def __iter__(self):
        return self


class UnicodeWriter(object):
    """
    A CSV writer which will write rows to CSV file "f", which is encoded in the
    given encoding.

    .. note::
       This class was stolen from the Python 2.7 documentation.
    """

    def __init__(self, f, dialect=csv.excel, encoding='utf_8', **kwargs):
        # Redirect output to a queue
        self.queue = StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwargs)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode('utf_8') for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode('utf_8')
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
