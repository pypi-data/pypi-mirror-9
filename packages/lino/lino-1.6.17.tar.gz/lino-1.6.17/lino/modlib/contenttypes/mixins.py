# -*- coding: UTF-8 -*-
# Copyright 2010-2014 Luc Saffre
# License: BSD (see file COPYING for details)


from django.contrib.contenttypes.models import *

from django.conf import settings

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import string_concat

from lino import dd


class Controllable(dd.Model):

    """Mixin for models that are "controllable" by another database object.

    Defines three fields `owned_type`, `owned_id` and `owned`.
    And a class attribute :attr:`owner_label`.

    For example in :mod:`lino.modlibs.cal`, the owner of a Task or Event
    is some other database object that caused the task's or event's
    creation.

    Or in :mod:`lino.modlib.sales` and :mod:`lino.modlib.purchases`,
    an invoice may cause one or several Tasks
    to be automatically generated when a certain payment mode
    is specified.

    Controllable objects are "governed" or "controlled" by their
    controller: If the controller gets modified, it may decide to
    delete or modify some or all of her controlled objects.

    Non-automatic tasks always have an empty `controller` field.
    Some fields are read-only on an automatic Task because
    it makes no sense to modify them.

    """
    # Translators: will also be concatenated with '(type)' '(object)'
    owner_label = _('Controlled by')
    """
    The labels (`verbose_name`) of the fields
    `owned_type`, `owned_id` and `owned`
    are derived from this attribute which
    may be overridden by subclasses.
    """

    controller_is_optional = True
    """Whether the controller is optional (i.e. whether the field `owner`
    may be NULL)

    """

    class Meta:
        abstract = True

    owner_type = dd.ForeignKey(
        ContentType,
        editable=True,
        blank=controller_is_optional, null=controller_is_optional,
        verbose_name=string_concat(owner_label, ' ', _('(type)')))

    owner_id = dd.GenericForeignKeyIdField(
        owner_type,
        editable=True,
        blank=controller_is_optional, null=controller_is_optional,
        verbose_name=string_concat(owner_label, ' ', _('(object)')))

    owner = dd.GenericForeignKey(
        'owner_type', 'owner_id',
        verbose_name=owner_label)

    def update_owned_instance(self, controllable):
        """
        If this (acting as a controller) is itself controlled,
        forward the call to the controller.
        """
        if self.owner:
            self.owner.update_owned_instance(controllable)
        super(Controllable, self).update_owned_instance(controllable)

    def save(self, *args, **kw):
        if settings.SITE.loading_from_dump:
            super(Controllable, self).save(*args, **kw)
        else:
            if self.owner:
                self.owner.update_owned_instance(self)
            super(Controllable, self).save(*args, **kw)
            if self.owner:
                self.owner.after_update_owned_instance(self)


