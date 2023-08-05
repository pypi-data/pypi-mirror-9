# -*- coding: UTF-8 -*-
# Copyright 2008-2014 Luc Saffre
# License: BSD (see file COPYING for details)

"""See :mod:`ml.vat`.

>>> from decimal import Decimal
>>> from lino.modlib.vat.utils import add_vat, remove_vat
>>> rate = Decimal(21)
>>> add_vat(100, rate)
Decimal('121')
>>> remove_vat(Decimal('121.00'), rate)
Decimal('100')

"""

from __future__ import unicode_literals

from decimal import Decimal
HUNDRED = Decimal('100')
ZERO = Decimal(0)


def add_vat(base, rate):
    "Add to the given base amount `base` the VAT of rate `rate`."
    return base * (HUNDRED + rate) / HUNDRED


def remove_vat(incl, rate):
    "Remove from the given amount `incl` the VAT of rate `rate`."
    return incl / ((HUNDRED + rate) / HUNDRED)
