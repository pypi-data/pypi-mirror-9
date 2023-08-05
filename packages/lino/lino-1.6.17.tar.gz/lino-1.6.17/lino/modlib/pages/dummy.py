# -*- coding: UTF-8 -*-
# Copyright 2012 Luc Saffre
# License: BSD (see file COPYING for details)
"""
The dummy module for `pages`.
"""

#~ print 20121219, __file__


import logging
logger = logging.getLogger(__name__)

from django.conf import settings
from django.db import models

from lino.utils import AttrDict
from lino.core import web

from lino.utils.restify import restify
from lino.utils.restify import doc2rst

DUMMY_PAGES = {}


class DummyPage(AttrDict):
    raw_html = False
    #~ special = False

    def __unicode__(self):
        return u'%s %s' % (self._meta.verbose_name, self.ref)

    def get_sidebar_html(self, request):
        return ''

    def full_clean(self):
        pass

    def save(self):
        pass


def create_page(**kw):
    #~ logger.info("20121219 dummy create_page %s",kw)
    obj = DummyPage(**kw)
    DUMMY_PAGES[obj.ref] = obj
    return obj


def lookup(ref, default=models.NOT_PROVIDED):
    if default is models.NOT_PROVIDED:
        return DUMMY_PAGES[ref]
    return DUMMY_PAGES.get(ref, default)


def render_node(request, node, template_name='pages/node.html', **context):
    context.update(node=node)
    heading = dd.babelattr(node, 'title', '')
    if heading:
        context.update(heading=heading)
        context.update(title=heading + ' &middot; ' + settings.SITE.title)
    else:
        context.update(heading=settings.SITE.title)
        context.update(title=settings.SITE.title)
    body = dd.babelattr(node, 'body', '')
    if not node.raw_html:
        body = restify(doc2rst(body))
    #~ logger.info("20121227 render_node %s -> body is %s",node,body)
    context.update(body=body)
    return web.render_from_request(request, template_name, **context)


def get_all_pages():
    return DUMMY_PAGES.values()

if not settings.SITE.is_installed('pages'):
    # fill DUMMY_PAGES at import by running the std fixture
    from lino.modlib.pages.fixtures import std
    for o in std.objects():
        pass
