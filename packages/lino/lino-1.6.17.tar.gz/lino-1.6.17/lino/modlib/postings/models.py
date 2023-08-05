# -*- coding: UTF-8 -*-
# Copyright 2012-2014 Luc Saffre
# License: BSD (see file COPYING for details)

"""
Defines models for :mod:`lino.modlib.postings`.
"""

import logging
logger = logging.getLogger(__name__)

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from lino import mixins
from lino import dd

from lino.modlib.contenttypes.mixins import Controllable
from lino.modlib.users.mixins import ByUser, UserAuthored


class PostingStates(dd.Workflow):

    """
    List of possible values for the `state` field of a 
    :class:`Posting`.
    """
    #~ label = _("State")

add = PostingStates.add_item
add('10', _("Open"), 'open')  # owner still working on it
# ~ add('20',_("Ready to print"),'ready') # secretary can send it out
add('20', _("Ready"), 'ready')  # secretary can print and send it out
add('30', _("Printed"), 'printed')
add('40', _("Sent"), 'sent')
add('50', _("Returned"), 'returned')


class PrintPosting(dd.Action):
    label = _('Print')
    help_text = _('Print this posting')
    icon_name = 'printer'
    show_in_workflow = True

    def run_from_ui(self, ar, **kw):
        elem = ar.selected_rows[0]
        elem.owner.do_print.run_from_code(ar, **kw)
        #~ r = elem.owner.print_from_posting(elem,ar,**kw)
        if elem.state in (PostingStates.open, PostingStates.ready):
            elem.state = PostingStates.printed
        elem.save()
        ar.success(refresh=True)
        #~ return kw


class Posting(UserAuthored, mixins.ProjectRelated, Controllable):

    """
    A Posting is the fact that a letter or other item 
    has been sent using snail mail.
    """
    workflow_state_field = 'state'

    class Meta:
        verbose_name = _("Posting")
        verbose_name_plural = _("Postings")

    print_posting = PrintPosting()

    partner = models.ForeignKey('contacts.Partner',
                                verbose_name=_("Recipient"),
                                blank=True, null=True)
    state = PostingStates.field()
    #~ sender = models.ForeignKey(settings.SITE.user_model)
    date = models.DateField()

    def unused_save(self, *args, **kw):
        # see blog/2012/0929
        if not isinstance(self.owner, Postable):
            # raise Exception("Controller of a Posting must be a Postable.")
            raise ValidationError("Controller %s (%r,%r) is not a Postable" % (
                dd.obj2str(self.owner), self.owner_type, self.owner_id))
            #~ raise ValidationError("Controller %s is not a Postable" % dd.obj2str(self.owner))
        super(Posting, self).save(*args, **kw)

    #~ @dd.action(_("Print"),icon_name='x-tbar-print')
    #~ def print_action(self,ar,**kw):
        #~ kw.update(refresh=True)
        #~ r = self.owner.print_from_posting(self,ar,**kw)
        #~ if self.state in (PostingStates.open,PostingStates.ready):
            #~ self.state = PostingStates.printed
        #~ self.save()
        #~ return r


class Postings(dd.Table):
    required = dd.Required(user_level='manager', user_groups='office')
    model = Posting
    column_names = 'date user owner partner *'
    order_by = ['date']

    #~ @dd.action(_("Print"),icon_name='x-tbar-print')
    #~ def print_action(cls,ar,self,**kw):
        #~ kw.update(refresh=True)
        #~ r = self.owner.print_from_posting(self,ar,**kw)
        #~ if self.state in (PostingStates.open,PostingStates.ready):
            #~ self.state = PostingStates.printed
        #~ self.save()
        #~ return r


class MyPostings(Postings, ByUser):
    required = dd.Required(user_groups='office')
    #~ required = dict()
    #~ master_key = 'owner'
    column_names = 'date partner state workflow_buttons *'


class PostingsByState(Postings):
    #~ required = dd.Required(user_groups='office',user_level='secretary')
    required = dd.Required(user_groups='office')
    column_names = 'date user partner workflow_buttons *'


class PostingsReady(PostingsByState):
    label = _("Postings ready to print")
    known_values = dict(state=PostingStates.ready)

    @classmethod
    def get_welcome_messages(cls, ar, **kw):
        sar = ar.spawn(cls)
        count = sar.get_total_count()
        if count > 0:
            txt = _("%d postings are ready to print.") % count
            yield ar.href_to_request(sar, txt)


class PostingsPrinted(PostingsByState):
    label = _("Postings printed")
    known_values = dict(state=PostingStates.printed)


class PostingsSent(PostingsByState):
    label = _("Postings sent")
    known_values = dict(state=PostingStates.sent)


class PostingsByController(Postings):
    required = dd.Required(user_groups='office')
    master_key = 'owner'
    column_names = 'date partner workflow_buttons'
    auto_fit_column_widths = True


class PostingsByPartner(Postings):
    required = dd.Required(user_groups='office')
    master_key = 'partner'
    column_names = 'date owner state workflow_buttons *'


class PostingsByProject(Postings):
    required = dd.Required(user_groups='office')
    master_key = 'project'
    column_names = 'date partner state workflow_buttons *'


#~ MODULE_LABEL = _("Outbox")
MODULE_LABEL = _("Postings")

system = dd.resolve_app('system')


def setup_main_menu(site, ui, profile, m):
    m = m.add_menu("office", system.OFFICE_MODULE_LABEL)
    m = m.add_menu("postings", MODULE_LABEL)
    m.add_action(MyPostings)
    m.add_action(PostingsReady)
    m.add_action(PostingsPrinted)
    m.add_action(PostingsSent)


#~ def setup_main_menu(site,ui,profile,m): pass
#~ def setup_my_menu(site,ui,profile,m):
    #~ m  = m.add_menu("postings",MODULE_LABEL)
    #~ m.add_action(MyInbox)
    #~ m.add_action(MySent)
def setup_config_menu(site, ui, profile, m):
    pass
    #~ if user.level >= UserLevels.manager:
    #~ m  = m.add_menu("outbox",MODULE_LABEL)
    #~ m.add_action(MailTypes)


def setup_explorer_menu(site, ui, profile, m):
    #~ if user.level >= UserLevels.manager:
    m = m.add_menu("office", system.OFFICE_MODULE_LABEL)
    #~ m  = m.add_menu("postings",MODULE_LABEL)
    m.add_action(Postings)
