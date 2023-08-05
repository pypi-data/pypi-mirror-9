# Copyright 2009-2014 Luc Saffre
# License: BSD (see file COPYING for details)

"""
A collection of tools around :doc:`/topics/mti`.
See the source code of :mod:`lino.test_apps.mti`.
Certainly not perfect, but works for me.
I wrote it mainly to solve ticket :srcref:`docs/tickets/22`.



"""
import logging
logger = logging.getLogger(__name__)
import six

from django.db import models
from django.db import router
from django.db.models.deletion import Collector, DO_NOTHING
from django.core.exceptions import ValidationError


from lino.core.dbutils import resolve_model
from lino.core.fields import VirtualField
from lino.core.signals import pre_remove_child, pre_add_child


class ChildCollector(Collector):

    """
    A Collector that does not delete the MTI parents.
    """

    def collect(self, objs, source=None, nullable=False, collect_related=True,
        source_attr=None, reverse_dependency=False):
        # modified copy of django.db.models.deletion.Collector.collect()
        # changes:
        # DOES NOT Recursively collect concrete model's parent models.
        # calls get_all_related_objects() with local_only=True

        if self.can_fast_delete(objs):
            self.fast_deletes.append(objs)
            return
        new_objs = self.add(objs, source, nullable,
                            reverse_dependency=reverse_dependency)
        if not new_objs:
            return

        model = new_objs[0].__class__

        if collect_related:
            for related in model._meta.get_all_related_objects(
                    include_hidden=True, include_proxy_eq=True,
                    local_only=True):
                field = related.field
                if field.rel.on_delete == DO_NOTHING:
                    continue
                sub_objs = self.related_objects(related, new_objs)
                if self.can_fast_delete(sub_objs, from_field=field):
                    self.fast_deletes.append(sub_objs)
                elif sub_objs:
                    field.rel.on_delete(self, field, sub_objs, self.using)
            for field in model._meta.virtual_fields:
                if hasattr(field, 'bulk_related_objects'):
                    # Its something like generic foreign key.
                    sub_objs = field.bulk_related_objects(new_objs, self.using)
                    self.collect(sub_objs,
                                 source=model,
                                 source_attr=field.rel.related_name,
                                 nullable=True)


class OldChildCollector(Collector):
    # version which worked for Django 1.5
    def collect(self, objs, source=None, nullable=False, collect_related=True,
                source_attr=None, collect_parents=True):
        # modified copy from original Django code
        new_objs = self.add(objs, source, nullable)
        if not new_objs:
            return
        model = new_objs[0].__class__

        if collect_related:
            #~ for m,related in model._meta.get_all_related_objects_with_model(include_hidden=True):
            for related in model._meta.get_all_related_objects(include_hidden=True, local_only=True):
                field = related.field
                if related.model._meta.auto_created:
                    # Django 1.5.x:
                    self.add_batch(related.model, field, new_objs)
                else:
                    sub_objs = self.related_objects(related, new_objs)
                    #~ print 20130828, related.model._meta.concrete_model
                    if not sub_objs:
                        continue
                    field.rel.on_delete(self, field, sub_objs, self.using)

            # TODO This entire block is only needed as a special case
            # to support cascade-deletes for GenericRelation. It
            # should be removed/fixed when the ORM gains a proper
            # abstraction for virtual or composite fields, and GFKs
            # are reworked to fit into that.
            for relation in model._meta.many_to_many:
                if not relation.rel.through:
                    sub_objs = relation.bulk_related_objects(
                        new_objs, self.using)
                    self.collect(sub_objs,
                                 source=model,
                                 source_attr=relation.rel.related_name,
                                 nullable=True)


def get_child(obj, child_model):
    if obj.pk is not None:
        try:
            return child_model.objects.get(pk=obj.pk)
        except child_model.DoesNotExist:
            # logger.warning(
            #     "No mti child %s in %s",
            #     obj.pk, child_model.objects.all().query)
            return None


def delete_child(obj, child_model, ar=None, using=None):
    """
    Delete the `child_model` instance related to `obj` without 
    deleting the parent `obj` itself.
    """
    #~ logger.info(u"delete_child %s from %s",child_model.__name__,obj)
    using = using or router.db_for_write(obj.__class__, instance=obj)
    child = get_child(obj, child_model)
    if child is None:
        raise Exception("%s has no child in %s" % (obj, child_model.__name__))
    #~ msg = child_model._lino_ddh.disable_delete(child)
    msg = child.disable_delete(ar)
    if msg:
        raise ValidationError(msg)
    #~ logger.debug(u"Delete child %s from %s",child_model.__name__,obj)
    if True:
        collector = ChildCollector(using=using)
        collector.collect([child])
        # raise Exception(repr(collector.data))
        # model = obj.__class__

        # remove the collected MTI parents so they are not deleted
        # (this idea didnt work: yes the parents were saved, but not
        # their related objects).

        # concrete_model = child_model._meta.concrete_model
        # for ptr in six.itervalues(concrete_model._meta.parents):
        #     if ptr:
        #         # raise Exception(repr(ptr.rel.to))
        #         del collector.data[ptr.rel.to]

    else:
        collector = ChildCollector(using=using)
        collector.collect([child], source=obj.__class__,
                          nullable=True, collect_parents=False)
    collector.delete()

    #~ setattr(obj,child_model.__name__.lower(),None)
    #~ delattr(obj,child_model.__name__.lower())

    # TODO: unchecking e.g. Company.is_courseprovider deletes the
    # child when saving the form, but the response to the PUT returns
    # still a True value because it works on the same memory instance
    # (`obj`).  User sees the effect only after clicking the refresh
    # button.  Fortunately there's no problem if the user unchecks the
    # field and saves the form a second time.


def insert_child(obj, child_model, **attrs):
    """
    Create and save an instance of `child_model` from existing `obj`.
    """
    #~ assert child_model != obj.__class__
    #~ if child_model == obj.__class__:
        #~ raise ValidationError(
            #~ "A %s cannot be parent for itself" %
            #~ obj.__class__.__name__)
    parent_link_field = child_model._meta.parents.get(obj.__class__, None)
    if parent_link_field is None:
        raise ValidationError("A %s cannot be parent for a %s" % (
            obj.__class__.__name__, child_model.__name__))
    attrs[parent_link_field.name] = obj
    # ~ for pm,pf in child_model._meta.parents.items(): # pm : parent model, pf : parent link field
        #~ attrs[pf.name] = obj
    #~ attrs["%s_ptr" % obj.__class__.__name__.lower()] = obj
    for field in obj._meta.fields:
        attrs[field.name] = getattr(obj, field.name)
    #~ logger.info(u"Promote %s to %s : attrs=%s",
        #~ obj.__class__.__name__,child_model.__name__,attrs)
    #~ logger.debug(u"Promote %s to %s",
        #~ obj.__class__.__name__,child_model.__name__)
    new_obj = child_model(**attrs)
    #~ logger.info("20120830 insert_child %s",obj2str(new_obj))
    new_obj.save()
    return new_obj

#~ def insert_child_and_save(obj,child_model,**attrs):
    #~ """
    #~ Insert (create) and save a `child_model` instance of existing `obj`.
    #~ """
    #~ obj = insert_child(obj,child_model,**attrs)
    #~ obj.save()
    #~ return obj


class EnableChild(VirtualField):

    """
    Rendered as a checkbox that indicates whether an mti 
    child of the given model exists.
    """

    editable = True
    #~ default = models.NOT_PROVIDED

    def __init__(self, child_model, **kw):
        kw.update(default=False)
        self.child_model = child_model
        VirtualField.__init__(self, models.BooleanField(**kw), self.has_child)

    def is_enabled(self, lh):
        """
        When a FormLayout is inherited by an MTI 
        child, EnableChild fields must be disabled.
        """
        return lh.layout._datasource.model != self.child_model \
            and issubclass(self.child_model, lh.layout._datasource.model)

    def attach_to_model(self, model, name):
        self.child_model = resolve_model(
            self.child_model, model._meta.app_label)
        VirtualField.attach_to_model(self, model, name)

    def has_child(self, obj, request=None):
        """
        Returns True if `obj` has an MTI child in `self.child_model`.
        The optional 2nd argument `request` (passed from
        `VirtualField.value_from_object`) is ignored.
        """
        try:
            getattr(obj, self.child_model.__name__.lower())
            #~ child = getattr(obj,self.child_model.__name__.lower())
            #~ if child is None: return False
            #~ print 20120531, repr(child)
            #~ self.child_model.objects.get(pk=obj.pk)
        except self.child_model.DoesNotExist:
            return False
        return True

    def set_value_in_object(self, ar, obj, v):
        if self.has_child(obj):
            #~ logger.debug('set_value_in_object : %s has child %s',
                #~ obj.__class__.__name__,self.child_model.__name__)
            # child exists, delete it if it may not
            if not v:
                if ar is not None:
                    pre_remove_child.send(
                        sender=obj, request=ar.request, child=self.child_model)
                    #~ changes.log_remove_child(ar.request,obj,self.child_model)
                delete_child(obj, self.child_model, ar)
        else:
            #~ logger.debug('set_value_in_object : %s has no child %s',
                #~ obj.__class__.__name__,self.child_model.__name__)
            if v:
                # child doesn't exist. insert if it should
                if ar is not None:
                    pre_add_child.send(
                        sender=obj, request=ar.request, child=self.child_model)
                    #~ changes.log_add_child(ar.request,obj,self.child_model)
                insert_child(obj, self.child_model)


from lino.utils.dpy import create_mti_child as create_child
