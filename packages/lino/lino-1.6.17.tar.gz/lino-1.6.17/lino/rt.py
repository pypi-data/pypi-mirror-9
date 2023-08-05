# Copyright 2014 Luc Saffre
# License: BSD (see file COPYING for details)

"""

This module is a shortcut to miscellaneous functions and classes which
are available "at runtime", i.e. when the Django machine has been
initialized.

You may *import* it at the global namespace of a :xfile:`models.py`
file, but you should *use* it (access its members) only when the
:func:`startup` function has been called.

"""

from django.conf import settings

from lino.core.dbutils import models_by_base

modules = settings.SITE.modules
login = settings.SITE.login
startup = settings.SITE.startup
get_printable_context = settings.SITE.get_printable_context
lookup_filter = settings.SITE.lookup_filter
find_config_file = settings.SITE.confdirs.find_config_file
find_config_files = settings.SITE.confdirs.find_config_files
find_template_config_files = settings.SITE.confdirs.find_template_config_files
makedirs_if_missing = settings.SITE.makedirs_if_missing
relpath = settings.SITE.relpath


def get_template(*args, **kw):
    """Shortcut to :meth:`get_template` on the global `jinja2.Environment`
    (:attr:`jinja_env <lino.core.site_def.Site.jinja_env>`, see
    :mod:`lino.core.web`).

    """
    return settings.SITE.jinja_env.get_template(*args, **kw)


def show(*args, **kw):
    """Calls :meth:`show <lino.core.requests.BaseRequest.show>` on a
    temporary anonymous session (created using :meth:`Site.login`).

    """
    return login().show(*args, **kw)


def emit_system_note(*args, **kw):
    "Shortcut to :meth:`lino.core.site_def.Site.emit_system_note`."
    return settings.SITE.emit_system_note(*args, **kw)


def send_email(*args, **kw):
    "Shortcut to :meth:`lino.core.site_def.Site.send_email`."
    return settings.SITE.send_email(*args, **kw)
