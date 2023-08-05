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
Fabric Library for MySQL
"""

from __future__ import unicode_literals

from fabric.api import sudo, hide

from rattail.fablib.system import apt


def mysql(sql, database=''):
    """
    Execute some SQL.
    """
    sql = '"{0}"'.format(sql) if sql.find("'") >= 0 else "'{0}'".format(sql)
    return sudo('mysql --execute={0} --batch --skip-column-names {1}'.format(sql, database))
    

def mysql_db_exists(name):
    """
    Determine if a given MySQL database exists.
    """
    db = mysql("SELECT SCHEMA_NAME FROM SCHEMATA WHERE SCHEMA_NAME = '{0}'".format(name), database='information_schema')
    return db == name


def mysql_table_exists(name, database):
    """
    Determine if a given table exists within the given MySQL database.
    """
    table = mysql("SELECT TABLE_NAME FROM TABLES WHERE TABLE_SCHEMA = '{0}' AND TABLE_NAME = '{1}'".format(database, name), database='information_schema')
    return table == name


def create_mysql_db(name, checkfirst=True, user=None):
    """
    Create a MySQL database.
    """
    if not checkfirst or not mysql_db_exists(name):
        sudo('mysqladmin create {0}'.format(name))
        if user:
            mysql('grant all on `{0}`.* to {1}'.format(name, user))


def drop_mysql_db(name):
    """
    Drop a MySQL database.
    """
    sudo('mysqladmin drop --force {0}'.format(name))


def mysql_user_exists(name, host='localhost'):
    """
    Determine if a given MySQL user exists.
    """
    user = mysql("SELECT User FROM user WHERE User = '{0}' and Host = '{1}'".format(name, host), database='mysql')
    return user == name


def create_mysql_user(name, host='localhost', password=None, checkfirst=True):
    """
    Create a MySQL user account.
    """
    if not checkfirst or not mysql_user_exists(name):
        mysql("CREATE USER '{0}'@'{1}';".format(name, host))
    if password:
        with hide('running'):
            mysql("SET PASSWORD FOR '{0}'@'{1}' = PASSWORD('{2}');".format(
                    name, host, password))


def drop_mysql_user(name, host='localhost'):
    """
    Drop a MySQL user account.
    """
    mysql("drop user '{0}'@'{1}'".format(name, host))
