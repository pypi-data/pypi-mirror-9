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
**Enumerations**

The following enumerations are provided:

.. attribute:: BATCH_ACTION

   Action types for use with batches.  These are taken from the SIL
   specification.

.. attribute:: EMAIL_PREFERENCE

   Various options indicating a person's preferences on whether to receive
   email, and if so, in what format.

.. attribute:: EMPLOYEE_STATUS

   Status types for employees (e.g. current, former).

.. attribute:: PHONE_TYPE

   Various "types" of phone contact information (e.g. home, work).

.. attribute:: PRICE_TYPE

   Various types of prices which may exist for a product.  These are taken from
   the SIL specification.

.. attribute:: UNIT_OF_MEASURE

   Units of measure for use with products (e.g. each, pound).  These are taken
   from the SIL specification.
"""

from __future__ import unicode_literals


BATCH_ACTION_ADD                = 'ADD'
BATCH_ACTION_ADD_REPLACE        = 'ADDRPL'
BATCH_ACTION_CHANGE             = 'CHANGE'
BATCH_ACTION_LOAD               = 'LOAD'
BATCH_ACTION_REMOVE             = 'REMOVE'

BATCH_ACTION = {
    BATCH_ACTION_ADD            : "Add",
    BATCH_ACTION_ADD_REPLACE    : "Add/Replace",
    BATCH_ACTION_CHANGE         : "Change",
    BATCH_ACTION_LOAD           : "Load",
    BATCH_ACTION_REMOVE         : "Remove",
    }


EMAIL_PREFERENCE_NONE           = 0
EMAIL_PREFERENCE_TEXT           = 1
EMAIL_PREFERENCE_HTML           = 2
EMAIL_PREFERENCE_MOBILE         = 3

EMAIL_PREFERENCE = {
    EMAIL_PREFERENCE_NONE       : "No Emails",
    EMAIL_PREFERENCE_TEXT       : "Text",
    EMAIL_PREFERENCE_HTML       : "HTML",
    EMAIL_PREFERENCE_MOBILE     : "Mobile",
    }


PHONE_TYPE_HOME                 = 'home'
PHONE_TYPE_MOBILE               = 'mobile'
PHONE_TYPE_OTHER                = 'other'

PHONE_TYPE = {
    PHONE_TYPE_HOME             : "Home",
    PHONE_TYPE_MOBILE           : "Mobile",
    PHONE_TYPE_OTHER            : "Other",
    }


PRICE_TYPE_REGULAR              = 0
PRICE_TYPE_TPR                  = 1
PRICE_TYPE_SALE                 = 2
PRICE_TYPE_MANAGER_SPECIAL      = 3
PRICE_TYPE_ALTERNATE            = 4
PRICE_TYPE_FREQUENT_SHOPPER     = 5
PRICE_TYPE_MFR_SUGGESTED        = 901

PRICE_TYPE = {
    PRICE_TYPE_REGULAR          : "Regular Price",
    PRICE_TYPE_TPR              : "TPR",
    PRICE_TYPE_SALE             : "Sale",
    PRICE_TYPE_MANAGER_SPECIAL  : "Manager Special",
    PRICE_TYPE_ALTERNATE        : "Alternate Price",
    PRICE_TYPE_FREQUENT_SHOPPER : "Frequent Shopper",
    PRICE_TYPE_MFR_SUGGESTED    : "Manufacturer's Suggested",
    }


UNIT_OF_MEASURE_EACH            = '01'
UNIT_OF_MEASURE_POUND           = '49'
UNIT_OF_MEASURE_CASE            = '102'

UNIT_OF_MEASURE = {
    UNIT_OF_MEASURE_EACH        : "Each",
    UNIT_OF_MEASURE_POUND       : "Pound",
    UNIT_OF_MEASURE_CASE        : "Case",
    }


EMPLOYEE_STATUS_CURRENT         = 1
EMPLOYEE_STATUS_FORMER          = 2

EMPLOYEE_STATUS = {
    EMPLOYEE_STATUS_CURRENT     : "current",
    EMPLOYEE_STATUS_FORMER      : "former",
    }


# VENDOR_CATALOG_NOT_PARSED       = 1
# VENDOR_CATALOG_PARSED           = 2
# VENDOR_CATALOG_COGNIZED         = 3
# VENDOR_CATALOG_PROCESSED        = 4

# VENDOR_CATALOG_STATUS = {
#     VENDOR_CATALOG_NOT_PARSED   : "not parsed",
#     VENDOR_CATALOG_PARSED       : "parsed",
#     VENDOR_CATALOG_COGNIZED     : "cognized",
#     VENDOR_CATALOG_PROCESSED    : "processed",
#     }
