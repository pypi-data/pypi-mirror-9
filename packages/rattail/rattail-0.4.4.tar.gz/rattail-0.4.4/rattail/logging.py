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
Logging Utilities
"""

from __future__ import absolute_import

import os
import sys
import logging
import socket
import getpass


class RattailAdapter(logging.LoggerAdapter):
    """
    Adds various items to a logger's context.

    Specifically, this adds the following keys to the ``extra`` dictionary
    available to the logger's formatter(s):

    * ``'hostname'`` - The fully-qualified domain name of the host machine.
    * ``'hostip'`` - The IPv4 address of the host machine.
    * ``'argv'`` - The value of ``sys.argv`` (a list).
    * ``'uid'`` - The effective UID of the running process.
    * ``'username'`` - The login name of the effective user.
    """

    def __init__(self, logger):
        hostname = socket.getfqdn()
        extra = {
            'hostname': hostname,
            'hostip':   socket.gethostbyname(hostname),
            'argv':     sys.argv,
            'uid':      "??",
            'username': getpass.getuser(),
            }
        if hasattr(os, 'getuid'):
            extra['uid'] = os.getuid()
        # LoggerAdapter is a new-style class only as of Python 2.7; must not
        # use super() in case we're running on Python 2.6.
        logging.LoggerAdapter.__init__(self, logger, extra)

    def process(self, msg, kwargs):
        extra = dict(self.extra)
        extra.update(kwargs.get('extra', {}))
        kwargs['extra'] = extra
        return msg, kwargs


def get_logger(name):
    """
    Fetches a logger by name, and wraps it in an adapter.

    This is intended to effectively replace the ``logging.getLogger()``
    function.  It does the same thing, except for wrapping the logger within a
    :class:`RattailAdapter`.
    """
    log = logging.getLogger(name)
    return RattailAdapter(log)
