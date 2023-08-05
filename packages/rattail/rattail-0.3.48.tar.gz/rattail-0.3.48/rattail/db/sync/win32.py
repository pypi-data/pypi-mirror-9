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
Database Synchronization for Windows
"""

from __future__ import unicode_literals

import sys
import logging
import threading

from ...win32.service import Service
from .. import get_default_engine
from . import get_sync_engines, synchronize_changes


log = logging.getLogger(__name__)


class DatabaseSynchronizerService(Service):
    """
    Implements database synchronization as a Windows service.
    """

    _svc_name_ = 'RattailDatabaseSynchronizer'
    _svc_display_name_ = "Rattail : Database Synchronization Service"
    _svc_description_ = ("Monitors the local Rattail database for changes, "
                         "and synchronizes them to the configured remote "
                         "database(s).")

    appname = 'rattail'

    def Initialize(self, config):
        """
        Service initialization.
        """

        if not Service.Initialize(self):
            return False

        local_engine = get_default_engine(config)
        remote_engines = get_sync_engines()
        if not remote_engines:
            return False

        thread = threading.Thread(target=synchronize_changes,
                                  args=(config, local_engine, remote_engines))
        thread.daemon = True
        thread.start()
        return True


if __name__ == '__main__':
    if sys.platform == 'win32':
        import win32serviceutil
        win32serviceutil.HandleCommandLine(DatabaseSynchronizerService)
