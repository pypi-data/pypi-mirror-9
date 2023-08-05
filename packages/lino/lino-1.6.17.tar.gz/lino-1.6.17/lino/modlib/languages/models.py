# -*- coding: UTF-8 -*-
# Copyright 2008-2014 Luc Saffre
# License: BSD (see file COPYING for details)

"""Defines the :class:`Language` model.

"""


from django.db import models

from lino import dd, mixins
from django.utils.translation import ugettext_lazy as _


class Language(mixins.BabelNamed):

    class Meta:
        verbose_name = _("Language")
        verbose_name_plural = _("Languages")
        ordering = ['name']

    id = models.CharField(max_length=3, primary_key=True)
    iso2 = models.CharField(max_length=2, blank=True)  # ,null=True)


class Languages(dd.Table):
    model = 'languages.Language'
    required = dd.required(user_groups='office')


def setup_config_menu(site, ui, profile, m):
    p = dd.plugins.languages.get_menu_group()
    m = m.add_menu(p.app_label, p.verbose_name)
    m.add_action('languages.Languages')
