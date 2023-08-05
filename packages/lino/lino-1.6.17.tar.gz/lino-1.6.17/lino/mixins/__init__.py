# -*- coding: UTF-8 -*-
# Copyright 2010-2014 Luc Saffre
# License: BSD (see file COPYING for details)

"""This package contains Model mixins, some of which are heavily used
by :mod:`lino.modlib`. None of them is mandatory for a Lino
application.

.. autosummary::
   :toctree:

    duplicable
    sequenced
    human
    periods
    polymorphic
    printable
    uploadable

Parameter panels:

- :class:`ObservedPeriod <lino.mixins.periods.ObservedPeriod>`
- :class:`Yearly <lino.mixins.periods.Yearly>`
- :class:`Today <lino.mixins.periods.Today>`

  

"""

from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)


import datetime

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.humanize.templatetags.humanize import naturaltime


from lino.core import fields
from lino.core import model
# from lino.modlib.users.mixins import UserLevels
# from lino.core.dbutils import navinfo
# from lino.utils import AttrDict


class Registrable(model.Model):

    """
    Base class to anything that may be "registered" and "deregistered"
    (e.g. Invoices, Vouchers, Declarations, Reservations,...).
    "Registered" in general means "this object has been taken account of".
    Registered objects are not editable.
    The ChoiceList of the `state` field must have at least two items
    named "draft" and "registered".
    There may be additional states.
    Every state must have an extra attribute "editable".
    """
    class Meta:
        abstract = True

    workflow_state_field = 'state'

    _registrable_fields = None

    @classmethod
    def get_registrable_fields(cls, site):
        """
        Return a list of the fields which are *disabled* when this is
        *registered* (i.e. `state` is not `editable`).
        """
        return []
        #~ yield 'date'

    @classmethod
    def on_analyze(cls, site):
        super(Registrable, cls).on_analyze(site)
        cls._registrable_fields = set(cls.get_registrable_fields(site))
        #~ logger.info("20130128 %s %s",cls,cls._registrable_fields)

    def disabled_fields(self, ar):
        if not self.state.editable:
            return self._registrable_fields
        return super(Registrable, self).disabled_fields(ar)

    def get_row_permission(self, ar, state, ba):
        """
        Only rows in an editable state may be edited.
        """
        #~ if isinstance(ba.action,actions.DeleteSelected):
            #~ logger.info("20130128 Registrable.get_row_permission %s %s %s %s",
                #~ self,state,ba.action,ar.bound_action.action.readonly)
        if state and not state.editable:
            if not ar.bound_action.action.readonly:
                return False
        return super(Registrable, self).get_row_permission(ar, state, ba)

    def register(self, ar):
        """
        Register this item.
        The base implementation just sets the state to "registered".
        Subclasses may override this to add custom behaviour.
        """

        state_field = self._meta.get_field(self.workflow_state_field)
        target_state = state_field.choicelist.registered
        self.set_workflow_state(ar, state_field, target_state)


    #~ def deregister(self,ar):
        #~ """
        #~ Deregister this item.
        #~ The base implementation just sets the state to "draft".
        #~ Subclasses may override this to add custom behaviour.
        #~ """
        #~ state_field = self._meta.get_field('state')
        #~ self.state = state_field.choicelist.draft

    #~ def before_printable_build(self,bm):
        #~ state_field = self._meta.get_field('state')
        #~ if self.state != state_field.choicelist.registered:
            #~ self.register(None)
            #~ self.save()

class Modified(model.Model):

    class Meta:
        abstract = True

    modified = models.DateTimeField(_("Modified"), editable=False)

    def save(self, *args, **kwargs):
        if not settings.SITE.loading_from_dump:
            self.modified = datetime.datetime.now()
        super(Modified, self).save(*args, **kwargs)


class Created(model.Model):

    class Meta:
        abstract = True

    created = models.DateTimeField(_("Created"), editable=False)

    @fields.displayfield(_('Created'))
    def created_natural(self, ar):
        return naturaltime(self.created)

    def save(self, *args, **kwargs):
        if self.created is None and not settings.SITE.loading_from_dump:
            self.created = datetime.datetime.now()
        super(Created, self).save(*args, **kwargs)


class CreatedModified(Created, Modified):

    """Adds two timestamp fields `created` and `modified`.

    We don't use Django's `auto_now` and `auto_now_add` features
    because their deserialization (restore from a python dump) would
    be problematic.

    """

    class Meta:
        abstract = True


class ProjectRelated(model.Model):

    """Mixin for Models that are automatically related to a "project".  A
    project means here "the central most important thing that is used
    to classify most other things".  

    Whether an application has such a concept of "project",
    and which model has this privileged status,
    is set in :attr:`lino.core.site_def.Site.project_model`.

    For example in :ref:`welfare` the "project" is a Client.

    """

    class Meta:
        abstract = True

    if settings.SITE.project_model:
        project = models.ForeignKey(
            settings.SITE.project_model,
            blank=True, null=True,
            related_name="%(app_label)s_%(class)s_set_by_project",
        )
    else:
        project = fields.DummyField()

    def get_related_project(self):
        if settings.SITE.project_model:
            return self.project

    #~ def summary_row(self,ui,rr,**kw):
    def summary_row(self, ar, **kw):
        s = [ar.obj2html(self)]
        if settings.SITE.project_model:
            #~ if self.project and not dd.has_fk(rr,'project'):
            if self.project:
                #~ s += " (" + ui.obj2html(self.project) + ")"
                s += [" (", ar.obj2html(self.project), ")"]
        return s

    def update_owned_instance(self, controllable):
        """
        When a :class:`project-related <ProjectRelated>`
        object controls another project-related object,
        then the controlled automatically inherits
        the `project` of its controller.
        """
        if isinstance(controllable, ProjectRelated):
            controllable.project = self.project
        super(ProjectRelated, self).update_owned_instance(controllable)

    def get_mailable_recipients(self):
        if isinstance(self.project, settings.SITE.modules.contacts.Partner):
            if self.project.email:
                yield ('to', self.project)
        for r in super(ProjectRelated, self).get_mailable_recipients():
            yield r

    def get_postable_recipients(self):
        if isinstance(self.project, settings.SITE.modules.contacts.Partner):
            yield self.project
        for p in super(ProjectRelated, self).get_postable_recipients():
            yield p


class Referrable(model.Model):

    """
    Mixin for things that have a unique `ref` field and a `get_by_ref` method.
    """
    class Meta:
        abstract = True

    ref = fields.NullCharField(_("Reference"),
                               max_length=40,
                               blank=True, null=True,
                               unique=True)

    @classmethod
    def get_by_ref(cls, ref, default=models.NOT_PROVIDED):
        try:
            return cls.objects.get(ref=ref)
        except cls.DoesNotExist:
            if default is models.NOT_PROVIDED:
                raise cls.DoesNotExist(
                    "No %s with reference %r" % (unicode(cls._meta.verbose_name), ref))
            return default

    #~ def __unicode__(self):
        #~ return self.ref or unicode(_('(Root)'))

    def __unicode__(self):
        return super(Referrable, self).__unicode__() + " (" + self.ref + ")"



from lino.mixins.printable import (Printable, PrintableType,
                                   CachedPrintable, TypedPrintable,
                                   DirectPrintAction, CachedPrintAction)

from lino.mixins.duplicable import Duplicable, Duplicate
from lino.mixins.sequenced import Sequenced, Hierarizable
from lino.mixins.periods import DatePeriod
from lino.mixins.periods import ObservedPeriod, Yearly, Today
from lino.mixins.polymorphic import Polymorphic
from lino.mixins.uploadable import Uploadable

from lino.utils.mldbc.fields import BabelCharField, BabelTextField
from lino.utils.mldbc.mixins import BabelNamed

from lino.mixins.human import Human, Born

# from lino.core.report import Report
