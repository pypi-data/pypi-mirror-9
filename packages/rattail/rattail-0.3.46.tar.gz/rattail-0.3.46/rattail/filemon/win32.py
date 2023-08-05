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
File Monitor for Windows
"""

from __future__ import unicode_literals

import os
import Queue
import logging

from rattail.win32.service import Service
from rattail.threads import Thread
from rattail.filemon.config import load_profiles
from rattail.filemon.actions import perform_actions
from rattail.filemon.util import queue_existing


# TODO: Would be nice to have a note explaining why this hack exists.
name = __name__
if name == u'win32':
   name = u'rattail.filemon.win32'
log = logging.getLogger(name)


class RattailFileMonitor(Service):
    """
    Windows service implementation of the File Monitor.
    """

    _svc_name_ = u"RattailFileMonitor"
    _svc_display_name_ = u"Rattail : File Monitoring Service"
    _svc_description_ = (u"Monitors one or more folders for incoming files, "
                         u"and performs configured actions as new files arrive.")

    def Initialize(self, config):
        """
        Service initialization.
        """
        # Read monitor profile(s) from config.
        self.monitored = load_profiles(config)

        # Make sure we have something to do.
        if not self.monitored:
            return False

        # Create monitor and action threads for each profile.
        for key, profile in self.monitored.iteritems():

            # Create a file queue for the profile.
            profile.queue = Queue.Queue()

            # Perform setup for each of the watched folders.
            for i, path in enumerate(profile.dirs, 1):

                # Maybe put all pre-existing files in the queue.
                if profile.process_existing:
                    queue_existing(profile, path)

                # Create a watcher thread for the folder.
                name = u'watcher_{0}-{1}'.format(key, i)
                log.debug(u"starting {0} thread for folder: {1}".format(repr(name), repr(path)))
                thread = Thread(target=watch_directory, name=name, args=(profile, path))
                thread.daemon = True
                thread.start()

            # Create an action thread for the profile.
            name = u'actions_{0}'.format(key)
            log.debug(u"starting action thread: {0}".format(repr(name)))
            thread = Thread(target=perform_actions, name=name, args=(profile,))
            thread.daemon = True
            thread.start()

        return True
    

def watch_directory(profile, path):
    """
    Callable target for watcher threads.
    """

    import win32file
    import win32con
    import winnt

    hDir = win32file.CreateFile(
        path,
        winnt.FILE_LIST_DIRECTORY,
        win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
        None,
        win32con.OPEN_EXISTING,
        win32con.FILE_FLAG_BACKUP_SEMANTICS,
        None)

    if hDir == win32file.INVALID_HANDLE_VALUE:
        log.error(u"can't open directory with CreateFile(): {0}".format(repr(path)))
        return

    while True:
        results = win32file.ReadDirectoryChangesW(
            hDir,
            1024,
            False,
            win32con.FILE_NOTIFY_CHANGE_FILE_NAME)

        log.debug(u"ReadDirectoryChangesW() returned: {0}".format(repr(results)))
        for action, fname in results:
            fpath = os.path.join(path, fname)
            queue = False
            if profile.watch_locks:
                if action == winnt.FILE_ACTION_REMOVED and fpath.endswith('.lock'):
                    fpath = fpath[:-5]
                    queue = True
            else:
                if action in (winnt.FILE_ACTION_ADDED, winnt.FILE_ACTION_RENAMED_NEW_NAME):
                    queue = True
            if queue:
                log.debug(u"queueing {0} file: {1}".format(repr(profile.key), repr(fpath)))
                profile.queue.put(fpath)


if __name__ == '__main__':
    import win32serviceutil
    win32serviceutil.HandleCommandLine(RattailFileMonitor)
