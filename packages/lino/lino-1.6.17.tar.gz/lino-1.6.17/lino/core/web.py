# Copyright 2012-2014 Luc Saffre
# License: BSD (see file COPYING for details)

"""

"""

from __future__ import unicode_literals
from __future__ import print_function

import logging
logger = logging.getLogger(__name__)

from os.path import join, dirname, isdir
import datetime
import jinja2


from django.conf import settings
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _
#~ from django.template.loaders import app_directories
from django.template.loader import BaseLoader
from django.template.base import TemplateDoesNotExist

from lino.utils import iif
from lino.utils import format_date

from lino.utils.xmlgen import html as xghtml
E = xghtml.E
from jinja2.exceptions import TemplateNotFound

#~ SUBDIR_NAME = 'templates_jinja'
SUBDIR_NAME = 'config'


def list_templates(self, ext, *groups):
    """
    Return a list of possible choices for a field that contains a
    template name.
    """
    # logger.info("20140617 list_templates(%r, %r)", ext, groups)
    if len(groups):
        retval = []
        for group in groups:
            #~ prefix = os.path.join(*(group.split('/')))
            def ff(fn):
                return fn.startswith(group) and fn.endswith(ext)
            lst = self.jinja_env.list_templates(filter_func=ff)
            L = len(group) + 1
            retval += [i[L:] for i in lst]
        return retval
    return self.jinja_env.list_templates(extensions=[ext])


def site_setup(self):
    """
    Adds a `jinja_env` attribute to `settings.SITE`.
    This is being called from
    :meth:`lino.core.kernel.Kernel.kernel_startup`.
    
    Lino has an automatic and currently not configurable method
    for building Jinja's template loader. It looks for
    a "config" subfolder in the following places:
    
    - the directory where your settings.py is defined.
    - the directories of each installed app
    
    """
    #~ logger.debug("Setting up Jinja environment")
    #~ from django.utils.importlib import import_module

    self.__class__.list_templates = list_templates

    loaders = []
    prefix_loaders = {}

    paths = list(self.get_settings_subdirs(SUBDIR_NAME))
    if self.is_local_project_dir:
        p = join(self.project_dir, SUBDIR_NAME)
        if isdir(p):
            paths.append(p)
    #~ logger.info("20130717 web.py paths %s",paths)
    if len(paths) > 0:
        loaders.append(jinja2.FileSystemLoader(paths))

    def func(name, m):
        #~ logger.info("20130717 jinja loader %s %s",name,SUBDIR_NAME)
        if isdir(join(dirname(m.__file__), SUBDIR_NAME)):
            loader = jinja2.PackageLoader(name, SUBDIR_NAME)
            loaders.append(loader)
            prefix_loaders[name] = loader
    self.for_each_app(func)

    loaders.insert(0, jinja2.PrefixLoader(prefix_loaders, delimiter=":"))

    #~ loaders = reversed(loaders)
    #~ print 20130109, loaders
    self.jinja_env = jinja2.Environment(
        #~ extensions=['jinja2.ext.i18n'],
        loader=jinja2.ChoiceLoader(loaders))
    #~ jinja_env = jinja2.Environment(trim_blocks=False)

    #~ from django.utils import translation

    #~ jinja_env.install_gettext_translations(translation)

    def as_table(action_spec):
        from lino.core import auth
        a = self.modules.resolve(action_spec)
        ar = a.request(user=auth.AnonymousUser.instance())
        ar.renderer = settings.SITE.plugins.bootstrap3.renderer

        t = xghtml.Table()
        #~ t = doc.add_table()
        #~ ar.ui.ar2html(ar,t,ar.sliced_data_iterator)
        ar.dump2html(t, ar.sliced_data_iterator)

        #~ print ar.get_total_count()
        return E.tostring(t.as_element())
        #~ return E.tostring(E.ul(*[E.li(ar.summary_row(obj)) for obj in ar]),method="html")

    def as_ul(action_spec):
        from lino.core import auth
        a = self.modules.resolve(action_spec)
        ar = a.request(user=auth.AnonymousUser.instance())
        ar.renderer = settings.SITE.plugins.bootstrap3.renderer
        return E.tostring(E.ul(*[obj.as_list_item(ar) for obj in ar]))

    self.jinja_env.globals.update(
        settings=settings,
        site=self,
        dtos=format_date.fds,
        dtosl=format_date.fdl,
        as_ul=as_ul,
        as_table=as_table,
        iif=iif,
        unicode=unicode,
        len=len,
        E=E,
        _=_,
    )

    #~ print __file__, 20121231, self.jinja_env.list_templates('.html')


def extend_context(context):
    def parse(s):
        #~ print 20121221, s
        #~ return Template(s).render(**context)
        return settings.SITE.jinja_env.from_string(s).render(**context)
    context.update(
        now=datetime.datetime.now(),
        parse=parse,
        requested_language=get_language(),
    )

from lino.core import requests


def render_from_request(request, template_name, **context):
    """
    Adds some more context names
    """
    extend_context(context)
    context.update(request=request)
    ar = requests.BaseRequest(
        renderer=settings.SITE.ui.default_renderer,
        request=request)
    context.update(ar=ar)
    template = settings.SITE.jinja_env.get_template(template_name)
    return template.render(**context)


class DjangoJinjaTemplate:

    """
    used e.g. to render :srcref:`/lino/lino/config/500.html`
    """

    def __init__(self, jt):
        self.jt = jt

    def render(self, context):
        # flatten the Django Context into a single dictionary.
        #~ logger.info("20130118 %s",context)
        context_dict = {}
        for d in context.dicts:
            context_dict.update(d)
        extend_context(context_dict)
        context_dict.setdefault('request', None)
        context_dict.setdefault(
            'ar', requests.BaseRequest(
                renderer=settings.SITE.ui.default_renderer))
        #~ logger.info("20130118 %s",context_dict.keys())
        return self.jt.render(context_dict)


class Loader(BaseLoader):

    is_usable = True

    def load_template(self, template_name, template_dirs=None):
        #~ source, origin = self.load_template_source(template_name, template_dirs)
        try:
            jt = settings.SITE.jinja_env.get_template(template_name)
        except TemplateNotFound:
            raise TemplateDoesNotExist(template_name)
        template = DjangoJinjaTemplate(jt)
        return template, None

