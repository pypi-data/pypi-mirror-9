# -*- coding: UTF-8 -*-
# Copyright 2012-2014 Luc Saffre
# License: BSD (see file COPYING for details)

"""
A :term:`dummy module` for `postings`, used by 
"""

from lino import dd


class Postable(object):
    pass

PostingsByController = dd.DummyField
