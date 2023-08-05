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
Fabric Library for Python
"""

from __future__ import unicode_literals

from contextlib import contextmanager

from fabric.api import sudo, run, prefix, cd
from fabric.contrib.files import append

from rattail.fablib.system import apt, mkdir


def install_pip():
    """
    Install the Pip installer for Python.
    """
    apt('python-setuptools')
    sudo('easy_install pip')
    pip('setuptools', 'pip')


def pip(*packages):
    """
    Install one or more packages via ``pip install``.
    """
    packages = ["'{}'".format(p) for p in packages]
    sudo('pip install --upgrade {0}'.format(' '.join(packages)))


def install_virtualenvwrapper(workon_home='/srv/envs', user='root'):
    """
    Install the `virtualenvwrapper`_ system, with the given ``workon`` home,
    owned by the given user.
    """
    mkdir(workon_home, owner=user)
    pip('virtualenvwrapper')
    for home in (sudo('echo $HOME', user=user), run('echo $HOME')):
        append('{0}/.profile'.format(home), 'export WORKON_HOME={0}'.format(workon_home), use_sudo=True)
        append('{0}/.profile'.format(home), 'source /usr/local/bin/virtualenvwrapper.sh', use_sudo=True)


def mkvirtualenv(name, user='rattail'):
    """
    Make a new Python virtual environment.
    """
    sudo('mkvirtualenv {0}'.format(name))
    with cdvirtualenv(name):
        mkdir('app/log', owner='{0}:{0}'.format(user), mode='0750')


@contextmanager
def workon(name):
    """
    Context manager to prefix your command(s) with the ``workon`` command.
    """
    with prefix('workon {0}'.format(name)):
        yield


@contextmanager
def cdvirtualenv(name, subdirs=[], workon_home='/srv/envs'):
    """
    Context manager to prefix your command(s) with the ``cdvirtualenv`` command.
    """
    if isinstance(subdirs, basestring):
        subdirs = [subdirs]
    path = '{0}/{1}'.format(workon_home, name)
    if subdirs:
        path = '{0}/{1}'.format(path, '/'.join(subdirs))
    with workon(name):
        with cd(path):
            yield
