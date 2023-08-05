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
Database Stuff
"""

from __future__ import unicode_literals

from sqlalchemy import orm
from sqlalchemy.orm.exc import NoResultFound

from . import model


class SessionBase(orm.Session):
    """
    Custom SQLAlchemy session class, which adds some convenience methods
    related to the SQLAlchemy-Continuum integration.
    """

    def __init__(self, continuum_user=None, **kwargs):
        """
        Custom constructor, to allow specifying the Continuum user at session
        creation.  If ``continuum_user`` is specified, its value will be passed
        to :meth:`set_continuum_user()`.
        """
        super(SessionBase, self).__init__(**kwargs)
        if continuum_user is None:
            self.continuum_user = None
        else:
            self.set_continuum_user(continuum_user)

    def set_continuum_user(self, user_info):
        """
        Set the effective Continuum user for the session.

        :param user_info: May be a :class:`model.User` instance, or the
          ``uuid`` or ``username`` for one.
        """
        if isinstance(user_info, model.User):
            user = user_info
        else:
            user = self.query(model.User).get(user_info)
            if not user:
                try:
                    user = self.query(model.User).filter_by(username=user_info).one()
                except NoResultFound:
                    user = None
        self.continuum_user = user


Session = orm.sessionmaker(class_=SessionBase)
