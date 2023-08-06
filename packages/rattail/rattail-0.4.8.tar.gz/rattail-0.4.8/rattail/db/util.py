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
Database Utilities
"""

from __future__ import unicode_literals

import warnings

from sqlalchemy import engine_from_config as sa_engine_from_config

from rattail.db import Session
from rattail.db.changes import record_changes
from rattail.util import load_object

# This import is provided for caller convenience:
from alembic.util import obfuscate_url_pw


def engine_from_config(configuration, prefix='sqlalchemy.', **kwargs):
    """
    Custom version of the identically-named SQLAlchemy function.

    The purpose of the customization is to allow the ``poolclass`` parameter to
    be specified within the configuration.  If this option is present in the
    configuration dictionary, it will be coerced to the Python class it
    references and passed as a keyword argument to the "upstream" function.

    An example of the configuration leveraging this feature:

    .. code-block:: ini

       [rattail.db]
       sqlalchemy.url = sqlite:///tmp/rattail.sqlite
       sqlalchemy.poolclass = sqlalchemy.pool:NullPool

    .. note::
       The coercion is done via :func:`rattail.util.load_object()`; therefore
       the configuration syntax must follow that function's requirements.
    """
    config = dict(configuration)
    key = prefix + 'poolclass'
    if key in config:
        kwargs.setdefault('poolclass', load_object(config[key]))
        del config[key]
    return sa_engine_from_config(config, prefix, **kwargs)


def get_engines(config, section=None):
    """
    Fetch all database engines defined in the given config object for a given
    section.

    :param config: A ``ConfigParser`` instance containing app configuration.

    :type section: string
    :param section: Optional section name within which the configuration
       options are defined.  If not specified, ``'rattail.db'`` is assumed.

    :returns: A dictionary of SQLAlchemy engine instances, keyed according to
       the config settings.
    """

    def engines_from_section(section):
        keys = config.get(section, u'keys')
        if keys:
            keys = keys.split(u',')
        else:
            keys = [u'default']

        engines = {}
        cfg = config.get_dict(section)
        for key in keys:
            key = key.strip()
            try:
                engines[key] = engine_from_config(cfg, prefix=u'{0}.'.format(key))
            except KeyError:
                if key == u'default':
                    try:
                        engines[key] = engine_from_config(cfg, prefix=u'sqlalchemy.')
                    except KeyError:
                        pass
        return engines

    if section is not None:
        return engines_from_section(section)

    engines = engines_from_section(u'rattail.db')
    if engines:
        return engines

    engines = engines_from_section(u'edbob.db')
    if engines:
        warnings.warn(u"Defining database engines in [edbob.db] is deprecated; please "
                      u"use the [rattail.db] section instead.", DeprecationWarning)
    return engines


def get_default_engine(config, section=None):
    """
    Fetch the default database engine defined in the given config object for a
    given section.

    :param config: A ``ConfigParser`` instance containing app configuration.

    :type section: string
    :param section: Optional section name within which the configuration
       options are defined.  If not specified, ``'rattail.db'`` is assumed.

    :returns: A SQLAlchemy engine instance, or ``None``.

    .. note::
       This function calls :func:`get_engines()` for the heavy lifting; see
       that function for more details on how the engine configuration is read.
    """
    return get_engines(config, section=section).get(u'default')


def configure_session(config, session):
    """
    Configure a session factory or instance.  Currently all this does is
    install the hook to record changes, if so configured.
    """
    if config.getboolean('rattail.db', 'changes.record'):
        ignore_role_changes = config.getboolean(
            'rattail.db', 'changes.ignore_roles', default=True)
        record_changes(session, ignore_role_changes)


def configure_session_factory(config, session_factory=None):
    """
    Configure a session factory using the provided settings.

    :param config: Object containing database configuration.

    :param session_factory: Optional session factory; if none is specified then
        :attr:`Session` will be assumed.
    """
    if session_factory is None:
        session_factory = Session

    engine = get_default_engine(config)
    if engine:
        session_factory.configure(bind=engine)

    configure_session(config, session_factory)


def maxlen(attr):
    """
    Return the maximum length for the given attribute.
    """
    if len(attr.property.columns) == 1:
        type_ = attr.property.columns[0].type
        return getattr(type_, 'length', None)
