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
System Fabric Library
"""

from __future__ import unicode_literals

from fabric.api import sudo, settings
from fabric.contrib.files import append


def make_system_user(name='rattail', home='/srv/rattail', shell=None, alias=False):
    """
    Make a new system user account, with the given home folder.  Optionally add
    a mail alias to root as well.
    """
    with settings(warn_only=True):
        result = sudo('getent passwd {0}'.format(name))
    if result.failed:
        args = '--shell {0}'.format(shell) if shell else ''
        sudo('adduser --system --home {0} --group {1} {2}'.format(home, name, args))
    if alias:
        append('/etc/aliases', '{}: root'.format(name), use_sudo=True)
        sudo('newaliases')


def mkdir(paths, owner='root:root', mode=None):
    """
    Recursively make one or more directories.
    """
    if isinstance(paths, basestring):
        paths = [paths]
    sudo('mkdir --parents {0}'.format(' '.join(paths)))
    sudo('chown {0} {1}'.format(owner, ' '.join(paths)))
    if mode is not None:
        sudo('chmod {0} {1}'.format(mode, ' '.join(paths)))


def apt(*packages):
    """
    Install one or more packages via ``apt-get install``.
    """
    sudo('DEBIAN_FRONTEND=noninteractive apt-get --assume-yes install {0}'.format(
            ' '.join(packages)))
