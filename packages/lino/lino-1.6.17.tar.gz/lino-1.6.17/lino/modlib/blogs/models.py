# -*- coding: UTF-8 -*-
# Copyright 2009-2012 Luc Saffre
# License: BSD (see file COPYING for details)

from django.db import models
from django.utils.translation import ugettext_lazy as _


from lino import dd
from lino import mixins
from lino.modlib.contenttypes.mixins import Controllable
from lino.modlib.users.mixins import ByUser, UserAuthored


class EntryType(mixins.BabelNamed, mixins.PrintableType):

    templates_group = 'blogs/Entry'

    class Meta:
        verbose_name = _("Blog Entry Type")
        verbose_name_plural = _("Blog Entry Types")

    #~ name = models.CharField(max_length=200)
    important = models.BooleanField(
        verbose_name=_("important"),
        default=False)
    remark = models.TextField(verbose_name=_("Remark"), blank=True)

    def __unicode__(self):
        return self.name


# def html_text(s):
#     return '<div class="htmlText">' + s + '</div>'


class EntryTypes(dd.Table):
    model = EntryType
    column_names = 'name build_method template *'
    order_by = ["name"]

    detail_layout = """
    id name
    build_method template
    remark:60x5
    blogs.EntriesByType
    """


class Entry(mixins.TypedPrintable,
            mixins.CreatedModified,
            UserAuthored,
            Controllable):

    """
    Deserves more documentation.
    """
    class Meta:
        verbose_name = _("Blog Entry")
        verbose_name_plural = _("Blog Entries")

    language = dd.LanguageField()
    type = models.ForeignKey(EntryType, blank=True, null=True)
    # ,null=True)
    title = models.CharField(_("Heading"), max_length=200, blank=True)
    #~ summary = dd.RichTextField(_("Summary"),blank=True,format='html')
    body = dd.RichTextField(_("Body"), blank=True, format='html')

    def __unicode__(self):
        return u'%s #%s' % (self._meta.verbose_name, self.pk)


class EntryDetail(dd.FormLayout):
    main = """
    title type:12 user:10 id
    # summary
    language:10 created modified owner build_time
    body
    """


class Entries(dd.Table):
    model = Entry
    detail_layout = EntryDetail()
    column_names = "id modified user type title * body"
    #~ hide_columns = "body"
    #~ hidden_columns = frozenset(['body'])
    order_by = ["id"]
    #~ label = _("Notes")


class MyEntries(ByUser, Entries):
    #~ master_key = 'user'
    column_names = "modified type title body *"
    #~ column_names = "date event_type type subject body *"
    #~ column_names = "date type event_type subject body_html *"
    #~ can_view = perms.is_authenticated
    order_by = ["-modified"]

    #~ def setup_request(self,req):
        #~ if req.master_instance is None:
            #~ req.master_instance = req.get_user()

#~ class NotesByProject(Notes):
    #~ master_key = 'project'
    #~ column_names = "date subject user *"
    #~ order_by = "date"

#~ class NotesByController(Notes):
    #~ master_key = 'owner'
    #~ column_names = "date subject user *"
    #~ order_by = "date"


class EntriesByType(Entries):
    master_key = 'type'
    column_names = "modified title user *"
    order_by = ["modified-"]
    #~ label = _("Notes by person")


class EntriesByController(Entries):
    master_key = 'owner'
    column_names = "modified title user *"
    order_by = ["modified-"]
    #~ label = _("Notes by person")


MODULE_NAME = _("~Blog")

#~ def setup_main_menu(site,ui,user,m): pass


def setup_main_menu(site, ui, profile, m):
    m = m.add_menu("blogs", MODULE_NAME)
    m.add_action(MyEntries)


def setup_config_menu(site, ui, profile, m):
    m = m.add_menu("blogs", MODULE_NAME)
    m.add_action(EntryTypes)


def setup_explorer_menu(site, ui, profile, m):
    m = m.add_menu("blogs", MODULE_NAME)
    m.add_action(Entries)
