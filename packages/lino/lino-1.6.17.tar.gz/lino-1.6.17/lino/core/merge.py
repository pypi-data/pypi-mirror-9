# -*- coding: UTF-8 -*-
# Copyright 2013-2014 Luc Saffre
# License: BSD (see file COPYING for details)
"""
This defines the :class:`MergeAction` class.

Usage example::

  @dd.receiver(dd.pre_analyze)
  def set_merge_actions(sender,**kw):
      modules = sender.modules
      for m in (modules.contacts.Person,modules.contacts.Company):
          m.define_action(merge_row=dd.MergeAction(m))

If should not be used on models that have MTI children.

"""

import logging
logger = logging.getLogger(__name__)

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext as _

from lino.core import actions
from lino.core import layouts
from lino.core.signals import pre_merge
from lino.core.dbutils import full_model_name
from lino.utils.xmlgen.html import E


class MergePlan(object):
    """A volatile object which represents what is going to happen after
    the user confirms to merge two objects.

    """

    def __init__(self, obj, merge_to, keep_volatiles={}):
        if merge_to == obj:
            raise Warning(_("Cannot merge an instance to itself."))
        self.obj = obj
        self.merge_to = merge_to
        self.keep_volatiles = keep_volatiles

    def analyze(self):
        self.volatiles = []
        self.related = []
        for m, fk in self.obj._lino_ddh.fklist:
            qs = m.objects.filter(**{fk.name: self.obj})
            if fk.name in m.allow_cascaded_delete and \
               not self.keep_volatiles.get(full_model_name(m, '_')):
                self.volatiles.append((fk, qs))
            else:
                self.related.append((fk, qs))
        self.generic_related = []
        for gfk, qs in settings.SITE.kernel.get_generic_related(self.obj):
            if not getattr(gfk, 'dont_merge', False):
                self.generic_related.append((gfk, qs))

    def logmsg(self):
        #~ self.analyze()
        lst = []
        lst.append(_("Merge %(origin)s into %(target)s") %
                   dict(origin=self.obj, target=self.merge_to))

        def add(name):
            for f, qs in getattr(self, name):
                if qs.count() > 0:
                    lst.append('- %d %s %s rows using %s : %s' % (
                        qs.count(),
                        name,
                        full_model_name(f.model),
                        f.name,
                        ' '.join([str(o.pk) for o in qs])))
        add('volatiles')
        add('related')
        add('generic_related')
        return '\n'.join(lst)

    def build_confirmation_message(self):
        self.analyze()
        items = []

        def collect_summary(prefix, fk_qs):
            parts = []
            for fld, qs in fk_qs:
                if qs.count() > 0:
                    parts.append("%d %s" %
                                 (qs.count(), unicode(fld.model._meta.verbose_name_plural)))
            if len(parts) != 0:
                items.append(E.li(', '.join(parts), ' ', E.b(prefix)))

        collect_summary(_("will be deleted."), self.volatiles)
        collect_summary(_("will get reassigned."),
                        self.related + self.generic_related)
        items.append(E.li(_("%s will be deleted") % self.obj))
        msg = _("Are you sure you want to merge %(this)s into %(merge_to)s?") % dict(
            this=self.obj, merge_to=self.merge_to)
        if len(items) != 0:
            return E.div(E.p(msg), E.ul(*items), class_="htmlText")
        return msg

    def execute(self, **kw):
        self.analyze()  # refresh since there may be changes since summary()
        # give others a chance to object
        #~ pre_merge.send(self.obj,merge_to=self.merge_to)
        kw.update(sender=self)
        pre_merge.send(**kw)
        update_count = 0
        # change FK fields of related objects
        for fk, qs in self.related:
            #~ print 20131026, qs.query, fk.name, self.merge_to
            update_count += qs.update(**{fk.name: self.merge_to})
            #~ for relobj in qs:
                #~ setattr(relobj,fk.name,merge_to)
                #~ relobj.full_clean()
                #~ relobj.save()

        # merge GenericForeignKey relations
        for gfk, qs in self.generic_related:
            update_count += qs.update(**{gfk.fk_field: self.merge_to.pk})
            #~ for i in qs:
                #~ setattr(qs,gfk.fk_field,merge_to.pk)
                # ~ # setattr(qs,gfk.name,merge_to)
                #~ i.full_clean()
                #~ i.save()

        # Build the return message
        msg = _("Merged %(this)s into %(merge_to)s. Updated %(updated)d related rows.") % dict(
            this=self.obj, merge_to=self.merge_to, updated=update_count)

        # delete any reference to the deleted object
        self.obj.delete()
        del self.obj
        return msg


class MergeAction(actions.Action):
    """Action which merges the selected object into another object of same
    class. It has an automatically generated parameters window.

    """
    help_text = _("Merge this object into another object of same class.")
    label = _("Merge")
    icon_name = 'arrow_join'
    sort_index = 31
    show_in_workflow = False
    readonly = False
    required = dict(user_level='admin')

    def __init__(self, model, **kw):

        fields = dict(
            #~ merge_from=models.ForeignKey(model,verbose_name=_("Merge...")),
            merge_to=models.ForeignKey(model, verbose_name=_("into...")),
            reason=models.CharField(_("Reason"), max_length=100)
            #~ notify=models.BooleanField(_("Send notifications"))
        )

        keep_volatiles = []

        #~ logger.info("20131025 MergeAction for %s",model)
        #~ logger.info("20130421 MergeAction for %s : _lino_ddh.fklist is %s",model,model._lino_ddh.fklist)
        for m, fk in model._lino_ddh.fklist:
            if fk.name in m.allow_cascaded_delete:
                fieldname = full_model_name(m, '_')
                if not fieldname in keep_volatiles:
                    keep_volatiles.append(fieldname)
                    fields[fieldname] = models.BooleanField(
                        m._meta.verbose_name_plural, default=False)
            #~ logger.info("20130421 %r in %r",fk.name,m.allow_cascaded_delete)

        layout = dict()
        if len(keep_volatiles) == 0:
            width = 50
            main = """
            merge_to
            reason
            """
        else:
            COLCOUNT = 2
            width = 70
            if len(keep_volatiles) > COLCOUNT:
                tpl = ''
                for i, name in enumerate(keep_volatiles):
                    if i % COLCOUNT == 0:
                        tpl += '\n'
                    else:
                        tpl += ' '
                    tpl += name
            else:
                tpl = ' '.join(keep_volatiles)
            main = """
            merge_to
            keep_volatiles
            reason
            """
            layout.update(keep_volatiles=layouts.Panel(
                tpl, label=_("Also reassign volatile related objects")))

        layout.update(window_size=(width, 'auto'))
        #~ from lino.mixins.mergeable import MergeAction
        kw.update(
            parameters=fields,
            params_layout=layouts.Panel(main, **layout))

        super(MergeAction, self).__init__(**kw)

    #~ def action_param_defaults(self,ar,obj,**kw):
        #~ kw = super(MergeAction,self).action_param_defaults(ar,obj,**kw)
        #~ kw.update(merge_from=obj)
        #~ return kw

    def run_from_ui(self, ar):
        """
        Implements :meth:`dd.Action.run_from_ui`.
        """
        obj = ar.selected_rows[0]
        mp = MergePlan(obj, ar.action_param_values.merge_to,
                       ar.action_param_values)
        msg = mp.build_confirmation_message()

        def ok(ar2):
            msg = mp.execute(request=ar.request)
            ar2.goto_instance(mp.merge_to)
            ar2.success(msg, alert=True, close_window=True)

        if msg is None:
            return ok(ar)
        ar.confirm(ok, msg)
