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
Core Fabric Library
"""

from __future__ import unicode_literals

import os
from ConfigParser import SafeConfigParser

from fabric.api import sudo, env, put as fab_put
from fabric.utils import warn
from fabric.contrib.files import upload_template as fab_upload_template


environment_configured = False
"""
Whether or not the environment has been configured via ``fabfile.cfg``.
"""


def configure_environment():
    """
    Looks for a ``fabfile.cfg`` file in the current working directory; if
    present, any passwords and settings it contains will be added to the
    environment.
    """
    global environment_configured
    if not environment_configured:
        if os.path.exists('fabfile.cfg'):
            parser = SafeConfigParser()
            if not parser.read('fabfile.cfg'):
                warn("Config parser failed to read file `fabfile.cfg`")
            else:
                if parser.has_section('passwords'):
                    for key in parser.options('passwords'):
                        setattr(env, 'password_{0}'.format(key), parser.get('passwords', key))
                if parser.has_section('settings'):
                    for key in parser.options('settings'):
                        setattr(env, 'setting_{0}'.format(key), parser.get('settings', key))
        environment_configured = True


def put(local_path, remote_path, owner='root:root', **kwargs):
    """
    Put a file on the server, and set its ownership.
    """
    if 'mode' not in kwargs:
        kwargs.setdefault('mirror_local_mode', True)
    kwargs['use_sudo'] = True
    fab_put(local_path, remote_path, **kwargs)
    sudo('chown {0} {1}'.format(owner, remote_path))


def upload_template(local_path, remote_path, owner='root:root', **kwargs):
    """
    Upload a template to the server, and set its ownership.
    """
    if 'mode' not in kwargs:
        kwargs.setdefault('mirror_local_mode', True)
    kwargs['use_sudo'] = True
    fab_upload_template(local_path, remote_path, **kwargs)
    sudo('chown {0} {1}'.format(owner, remote_path))


def make_deploy(deploy_path, last_segment='deploy'):
    """
    Make a ``deploy()`` function, for uploading files to the server.

    During a deployment, one usually needs to upload certain additional files
    to the server.  It's also often necessary to dynamically define certain
    settings etc. within these files.  The :func:`upload_template()` and
    :func:`put()` functions, respectively, handle uploading files which do and
    do not require dynamic variable substitution.

    The return value from ``make_deploy()`` is a function which will call
    ``put()`` or ``upload_template()`` based on whether or not the file path
    ends with ``'.template'``.

    To make the ``deploy()`` function even simpler for the caller, it will
    assume a certain context for local file paths.  This means one only need
    provide a base file name when calling ``deploy()``, and it will be
    interpreted as relative to the function's context path.

    The ``deploy_path`` argument is used to establish the context path for the
    function.  If it is a folder path, it will be used as-is; otherwise it will
    be constructed by joining the parent folder of ``deploy_path`` with the
    value of ``last_segment``.

    Typical usage then is something like::

       from rattail.fablib import make_deploy

       deploy = make_deploy(__file__)

       deploy('rattail/init-filemon', '/etc/init.d/rattail-filemon',
              mode='0755')

       deploy('rattail/rattail.conf.template', '/etc/rattail.conf')

    This shows what is intended to be typical, i.e. where ``__file__`` is the
    only argument required for ``make_deploy()``.  For the above to work will
    require you to have something like this file structure, where
    ``fabfile.py`` is the script which contains the above code::

       myproject/
       |-- fabfile.py
       |-- deploy/
           `-- rattail/
               |-- init-filemon
               |-- rattail.conf.template
    """
    if not os.path.isdir(deploy_path):
        deploy_path = os.path.abspath(os.path.join(os.path.dirname(deploy_path), last_segment))

    def deploy(local_path, remote_path, **kwargs):
        local_path = '{0}/{1}'.format(deploy_path, local_path)
        if local_path.endswith('.template'):
            upload_template(local_path, remote_path, context=env, **kwargs)
        else:
            put(local_path, remote_path, **kwargs)

    return deploy
