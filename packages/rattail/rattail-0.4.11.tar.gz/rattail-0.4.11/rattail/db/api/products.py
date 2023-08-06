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
Products API
"""

from __future__ import unicode_literals

from sqlalchemy.orm.exc import NoResultFound

from rattail.db import model
from rattail import enum


__all__ = ['get_product_by_upc', 'get_product_by_code']


def get_product_by_upc(session, upc):
    """
    Returns the :class:`rattail.Product` associated with ``upc`` (if found), or
    ``None``.
    """

    q = session.query(model.Product)
    q = q.filter(model.Product.upc == upc)
    try:
        return q.one()
    except NoResultFound:
        return None


def get_product_by_code(session, code):
    """
    Locate a ``Product`` instance using a code value.

    :param session: An open SQLAlchemy session.

    :param code: Product code for which to search.
    :type code: string

    :returns: A :class:`rattail.db.model.Product` instance, or ``None``.

    .. note::
       This function will return the *first* product found, and does not warn
       if multiple products would have matched the search.
    """

    q = session.query(model.Product)\
        .outerjoin(model.ProductCode)\
        .filter(model.ProductCode.code == code)
    return q.first()


def set_regular_price(product, newprice, **kwargs):
    """
    Simple way to set the regular price for the product, using sane defaults.
    """
    regular = product.regular_price
    if newprice is None:
        if regular:
            product.regular_price = None
        return

    if regular and regular.price == newprice:
        return                  # nothing to do

    price = regular or model.ProductPrice()
    price.type = kwargs.get('type', enum.PRICE_TYPE_REGULAR)
    price.level = kwargs.get('level', 1)
    price.price = newprice
    price.multiple = kwargs.get('multiple', 1)
    price.starts = kwargs.get('starts', None)
    price.ends = kwargs.get('ends', None)
    if price is not regular:
        product.prices.append(price)
    product.regular_price = price
    return price


def set_current_sale_price(product, newprice, starts=None, ends=None, **kwargs):
    """
    Simple way to set the current sale price for the product, using sane
    defaults.  Note that this does not check to confirm that your date range
    encompasses "today".
    """
    current = product.current_price
    if newprice is None:
        if current:
            product.current_price = None
        return
        
    if (current and current.price == newprice
        and current.starts == starts and current.ends == ends):
        return                  # nothing to do

    price = current or model.ProductPrice()
    price.type = kwargs.get('type', enum.PRICE_TYPE_SALE)
    price.level = kwargs.get('level', 1)
    price.price = newprice
    price.multiple = kwargs.get('multiple', 1)
    price.starts = starts
    price.ends = ends
    if price is not current:
        product.prices.append(price)
    product.current_price = price
    return price
