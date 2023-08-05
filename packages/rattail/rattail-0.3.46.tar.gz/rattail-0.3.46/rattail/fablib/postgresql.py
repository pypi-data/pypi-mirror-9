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
Fabric Library for PostgreSQL
"""

from __future__ import unicode_literals

from fabric.api import sudo, hide


def psql(sql, database=''):
    """
    Execute some SQL as the 'postgres' user.
    """
    return sudo('sudo -u postgres psql --tuples-only --no-align --command="{0}" {1}'.format(sql, database), shell=False)
    

def pg_db_exists(name):
    """
    Determine if a given PostgreSQL database exists.
    """
    db = psql("SELECT datname FROM pg_database WHERE datname = '{0}'".format(name))
    return db == name


def create_pg_db(name, owner=None, checkfirst=True):
    """
    Create a PostgreSQL database.
    """
    if not checkfirst or not pg_db_exists(name):
        args = '--owner={0}'.format(owner) if owner else ''
        sudo('sudo -u postgres createdb {0} {1}'.format(args, name), shell=False)


def drop_pg_db(name, checkfirst=True):
    """
    Drop a PostgreSQL database.
    """
    if not checkfirst or pg_db_exists(name):
        sudo('sudo -u postgres dropdb {0}'.format(name), shell=False)


def pg_user_exists(name):
    """
    Determine if a given PostgreSQL user exists.
    """
    user = psql("SELECT rolname FROM pg_roles WHERE rolname = '{0}'".format(name))
    return bool(user)


def create_pg_user(name, password=None, checkfirst=True):
    """
    Create a PostgreSQL user account.
    """
    if not checkfirst or not pg_user_exists(name):
        sudo('sudo -u postgres createuser --no-createdb --no-createrole --no-superuser {0}'.format(name))
        if password:
            with hide('running'):
                psql("ALTER USER \"{0}\" PASSWORD '{1}';".format(name, password))
