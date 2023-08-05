# -*- coding: UTF-8 -*-
# Copyright 2012-2014 Luc Saffre
# License: BSD (see file COPYING for details)

"""
The :term:`dummy module` for `outbox`, 
used by :func:`lino.core.dbutils.resolve_app`.
"""
from lino import dd


class Mailable(object):
    pass

#~ class MailableType(object): pass


class MailableType(dd.Model):
    email_template = dd.DummyField()
    attach_to_email = dd.DummyField()

    class Meta:
        abstract = True

MailsByController = dd.DummyField()
