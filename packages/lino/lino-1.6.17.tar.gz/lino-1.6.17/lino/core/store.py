# Copyright 2009-2014 Luc Saffre
# License: BSD (see file COPYING for details)
"""

Defines the `Store` class and its "fields" (aka atomizers).

"""

from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)

import datetime

from django.conf import settings
from django.db import models
from django.core import exceptions
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_unicode
from django.contrib.contenttypes import generic

from lino.utils.jsgen import py2js
from lino.utils.quantities import parse_decimal

from lino.core import constants

from lino.core import fields
from lino.core import actions
from lino.core import frames
from lino.utils import choosers
from lino.utils import curry
from lino.utils import iif
from lino.utils.format_date import fds
from lino.core.requests import PhantomRow
from lino.utils import IncompleteDate


class StoreField(object):

    """Base class for the fields of a :class:`Store`.
    
    Note: `value_from_object` and `full_value_from_object` are
    similar, but for ForeignKeyStoreField and GenericForeignKeyField
    one returns the primary key while the other returns the full
    instance.

    """

    form2obj_default = None
    "because checkboxes are not submitted when they are off"

    list_values_count = 1
    "Necessary to compute :attr:`Store.pk_index`."

    def __init__(self, field, name, **options):
        self.field = field
        self.name = name
        #~ if isinstance(field,generic.GenericForeignKey):
            #~ self.editable = False
        #~ else:
            # ~ self.editable = field.editable # VirtualField changes this
        #~ options.update(name=name or field.name)
        self.options = options

    #~ def __repr__(self):
        #~ return self.__class__.__name__ + ' ' + self.field.name

    def as_js(self, name):
        """
        possible side effect. but self.options is used only for as_js(),
        and in case of virtual remote fields they use the virtual field's 
        delegate as_js method but with their own name.
        """
        self.options.update(name=name)
        return py2js(self.options)

    def __repr__(self):
        return "%s '%s'" % (self.__class__.__name__, self.name)

    def column_names(self):
        #~ if not self.options.has_key('name'):
            #~ raise Exception("20130719 %s has no option 'name'" % self)
        #~ yield self.options['name']
        yield self.name

    def value_from_object(self, obj, ar):
        return self.full_value_from_object(obj, ar)

    def full_value_from_object(self, obj, ar):
        return self.field.value_from_object(obj)

    def value2list(self, ar, v, l, row):
        return l.append(v)

    def value2dict(self, v, d, row):
        d[self.name] = v

    #~ def value2odt(self,ar,v,tc,**params):
        #~ """
        #~ Add the necessary :term:`odfpy` element(s) to the containing element `tc`.
        #~ """
        #~ params.update(text=force_unicode(v))
        #~ tc.addElement(odf.text.P(**params))

    def parse_form_value(self, v, obj):
        #~ if v == '' and not self.field.empty_strings_allowed:
            #~ return None
        return self.field.to_python(v)

    def extract_form_data(self, post_data):
        #~ logger.info("20130128 StoreField.extract_form_data %s",self.name)
        return post_data.get(self.name, None)

    def form2obj(self, ar, instance, post_data, is_new):
        """
        Test cases:
        - setting a CharField to ''
        - sales.Invoice.number may be blank        
        """
        v = self.extract_form_data(post_data)
        #~ logger.info("20130128 %s.form2obj() %s = %r",self.__class__.__name__,self.name,v)
        if v is None:
            # means that the field wasn't part of the submitted form. don't
            # touch it.
            return
        if v == '':
            #~ print 20130125, self.field.empty_strings_allowed, self.field.name, self.form2obj_default
            if self.field.empty_strings_allowed:
                v = self.parse_form_value(v, instance)

                # If a field has been posted with empty string, we
                # don't want it to get the field's default value!
                # Otherwise checkboxes with default value True can
                # never be unset!

                # Charfields have empty_strings_allowed (e.g. id field
                # may be empty) but don't do this for other cases.
            else:
                v = self.form2obj_default
        else:
            v = self.parse_form_value(v, instance)
        if not is_new and self.field.primary_key and instance.pk is not None:
            if instance.pk == v:
                return
            raise exceptions.ValidationError({
                self.field.name: _(
                    "Existing primary key value %r "
                    "may not be modified.") % instance.pk})

        return self.set_value_in_object(ar, instance, v)

    def set_value_in_object(self, ar, instance, v):
        old_value = self.value_from_object(instance, ar.request)
        #~ old_value = getattr(instance,self.field.attname)
        if old_value != v:
            setattr(instance, self.name, v)
            return True

    def format_value(self, ar, v):
        """
        Return a plain textual representation as a unicode string
        of the given value `v`.   Note that `v` might be `None`.
        """
        return force_unicode(v)


#~ class RemoteStoreField(StoreField):
    #~ def __init__(self,store,rf):
        #~ self.remote_field = rf
        #~ self.delegate = store.create_atomizer(rf.field)
        #~ StoreField.__init__


class RelatedMixin(object):

    def get_rel_to(self, obj):
        #~ if self.field.rel is None:
            #~ return None
        return self.field.rel.to

    def full_value_from_object(self, obj, ar):
        # here we don't want the pk (stored in field's attname)
        # but the full object this field refers to
        relto_model = self.get_rel_to(obj)
        if not relto_model:
            #~ logger.warning("%s get_rel_to returned None",self.field)
            return None
        try:
            return getattr(obj, self.name)
        except relto_model.DoesNotExist:
            return None


class ComboStoreField(StoreField):

    list_values_count = 2

    def as_js(self, name):
        s = StoreField.as_js(self, name)
        #~ s += "," + repr(self.field.name+constants.CHOICES_HIDDEN_SUFFIX)
        s += ", '%s'" % (name + constants.CHOICES_HIDDEN_SUFFIX)
        return s

    def column_names(self):
        #~ yield self.options['name']
        #~ yield self.options['name'] + constants.CHOICES_HIDDEN_SUFFIX
        yield self.name
        yield self.name + constants.CHOICES_HIDDEN_SUFFIX

    def extract_form_data(self, post_data):
        #~ logger.info("20130128 ComboStoreField.extract_form_data %s",self.name)
        return post_data.get(self.name + constants.CHOICES_HIDDEN_SUFFIX, None)

    #~ def obj2list(self,request,obj):
    def value2list(self, ar, v, l, row):
        value, text = self.get_value_text(v, row)
        l += [text, value]

    #~ def obj2dict(self,request,obj,d):
    def value2dict(self, v, d, row):
        value, text = self.get_value_text(v, row)
        d[self.name] = text
        d[self.name + constants.CHOICES_HIDDEN_SUFFIX] = value

    def get_value_text(self, v, obj):
        #~ v = self.full_value_from_object(None,obj)
        if v is None or v == '':
            return (None, None)
        if obj is not None:
            ch = obj.__class__.get_chooser_for_field(self.field.name)
            if ch is not None:
                return (v, ch.get_text_for_value(v, obj))
        for i in self.field.choices:
            if i[0] == v:
                return (v, unicode(i[1]))
        return (v, _("%r (invalid choice)") % v)


class ForeignKeyStoreField(RelatedMixin, ComboStoreField):

    #~ def cell_html(self,req,row):
        #~ obj = self.full_value_from_object(req,row)
        #~ if obj is None:
            #~ return ''
        #~ return req.ui.obj2html(obj)

    def get_value_text(self, v, obj):
        #~ v = self.full_value_from_object(None,obj)
        #~ if isinstance(v,basestring):
            #~ logger.info("20120109 %s -> %s -> %r",obj,self,v)
        if v is None:
            return (None, None)
        else:
            return (v.pk, unicode(v))

    def parse_form_value(self, v, obj):
        relto_model = self.get_rel_to(obj)
        if not relto_model:
            #~ logger.info("20111209 get_value_text: no relto_model")
            return
        try:
            return relto_model.objects.get(pk=v)
        except ValueError:
            pass
        except relto_model.DoesNotExist:
            pass

        if obj is not None:
            ch = obj.__class__.get_chooser_for_field(self.field.name)
            if ch and ch.can_create_choice:
                return ch.create_choice(obj, v)
        return None


#~ class LinkedForeignKeyField(ForeignKeyStoreField):

    #~ def get_rel_to(self,obj):
        #~ ct = self.field.get_content_type(obj)
        #~ if ct is None:
            #~ return None
        #~ return ct.model_class()


class VirtStoreField(StoreField):

    def __init__(self, vf, delegate, name):
        self.vf = vf
        StoreField.__init__(self, vf.return_type, name)
        self.as_js = delegate.as_js
        self.column_names = delegate.column_names
        self.list_values_count = delegate.list_values_count
        self.form2obj_default = delegate.form2obj_default
        #~ 20130130 self.value2num = delegate.value2num
        #~ 20130130 self.value2html = delegate.value2html
        self.value2list = delegate.value2list
        self.value2dict = delegate.value2dict
        self.format_value = delegate.format_value
        #~ 20130130 self.format_sum = delegate.format_sum
        #~ 20130130 self.sum2html = delegate.sum2html
        #~ self.form2obj = delegate.form2obj
        # as long as http://code.djangoproject.com/ticket/15497 is open:
        self.parse_form_value = delegate.parse_form_value
        self.set_value_in_object = vf.set_value_in_object
        #~ 20130130 self.apply_cell_format = delegate.apply_cell_format
        #~ self.value_from_object = vf.value_from_object

        self.delegate = delegate

    def __repr__(self):
        return '(virtual)' + self.delegate.__class__.__name__ + ' ' + self.name

    def full_value_from_object(self, obj, ar):
        return self.vf.value_from_object(obj, ar)


class RequestStoreField(StoreField):

    """
    StoreField for :class:`lino.core.fields.RequestField`.
    """

    def __init__(self, vf, delegate, name):
        self.vf = vf
        StoreField.__init__(self, vf.return_type, name)
        #~ self.editable = False
        self.as_js = delegate.as_js
        self.column_names = delegate.column_names
        self.list_values_count = delegate.list_values_count

    def full_value_from_object(self, obj, ar):
        return self.vf.value_from_object(obj, ar)

    def value2list(self, ar, v, l, row):
        return l.append(self.format_value(ar, v))

    def value2dict(self, v, d, row):
        d[self.name] = self.format_value(settings.SITE.ui, v)
        #~ d[self.options['name']] = self.format_value(ui,v)
        #~ d[self.field.name] = v

    def format_value(self, ar, v):
        if v is None:
            return ''
        return str(v.get_total_count())

    #~ def sum2html(self,ar,sums,i,**cellattrs):
        #~ cellattrs.update(align="right")
        #~ return super(RequestStoreField,self).sum2html(ar,sums,i,**cellattrs)

    #~ def value2odt(self,ar,v,tc,**params):
        #~ params.update(text=self.format_value(ar,v))
        #~ tc.addElement(odf.text.P(**params))


class PasswordStoreField(StoreField):

    def value_from_object(self, obj, request):
        v = super(PasswordStoreField, self).value_from_object(obj, request)
        if v:
            return "*" * len(v)
        return v


class SpecialStoreField(StoreField):
    field = None
    name = None
    editable = False

    def __init__(self, store):
        self.options = dict(name=self.name)
        self.store = store

    #~ def value2dict(self,v,d):
        #~ d[self.name] = v

    #~ def obj2dict(self,request,obj,d):
        # ~ # d.update(disable_editing=self.value_from_object(request,obj))
        #~ d[self.name] = self.value_from_object(request,obj)

    #~ def __repr__(self):
        #~ return "%s '%s'" % (self.__class__.__name__, self.name)

    def parse_form_value(self, v, instance):
        pass

    #~ def obj2list(self,request,obj):
        #~ return [self.value_from_object(request,obj)]

    #~ def value2list(self,ui,v):
        #~ return [v]

    def form2obj(self, ar, instance, post_data, is_new):
        pass
        #~ raise NotImplementedError
        #~ return instance


class DisabledFieldsStoreField(SpecialStoreField):

    """See also blog entries 20100803, 20111003, 20120901
    
    Note some special cases:
    
    - vat.VatDocument.total_incl (readonly virtual PriceField) must be
      disabled and may not get submitted.  ExtJS requires us to set
      this dynamically each time.

    - JobsOverview.body (a virtual HtmlBox) or Model.workflow_buttons
      (a displayfield) must *not* have the 'disabled' css class -

    """
    name = 'disabled_fields'

    def __init__(self, store):
        SpecialStoreField.__init__(self, store)
        self.always_disabled = set()
        for f in self.store.all_fields:
            if f.field is not None:
                if isinstance(f, VirtStoreField):
                    if not f.vf.editable:
                        if not isinstance(
                                f.vf.return_type, fields.DisplayField):
                            self.always_disabled.add(f.name)
                            #~ print "20121010 always disabled:", f
                elif not isinstance(f.field, generic.GenericForeignKey):
                    if not f.field.editable:
                        self.always_disabled.add(f.name)

    def full_value_from_object(self, obj, ar):
        d = dict()
        for name in self.store.actor.disabled_fields(obj, ar):
            if name is not None:
                d[name] = True

        for name in self.always_disabled:
            d[name] = True

        # disable the primary key field if pk is set (i.e. on saved instance):
        if self.store.pk is not None and obj.pk is not None:
            if self.store.pk.attname is None:
                raise Exception('20130322b')
            d[self.store.pk.attname] = True
            #~ l.append(self.store.pk.attname)
            # MTI children have two "primary keys":
            if isinstance(self.store.pk, models.OneToOneField):
                #~ l.append(self.store.pk.rel.field_name)
                if self.store.pk.rel.field_name is None:
                    raise Exception('20130322c')
                d[self.store.pk.rel.field_name] = True
        return d


class DisabledActionsStoreField(SpecialStoreField):

    """
    """
    name = 'disabled_actions'

    def full_value_from_object(self, obj, ar):
        return self.store.actor.disabled_actions(ar, obj)


#~ class RecnoStoreField(SpecialStoreField):
    #~ name = 'recno'
    #~ def full_value_from_object(self,request,obj):
        #~ return

class RowClassStoreField(SpecialStoreField):
    name = 'row_class'

    def full_value_from_object(self, obj, ar):
        return ' '.join([ar.renderer.row_classes_map.get(s, '')
                         for s in self.store.actor.get_row_classes(obj, ar)])
        #~ return ar.renderer.row_classes_map.get('x-grid3-row-%s' % s


class DisableEditingStoreField(SpecialStoreField):

    """
    A field whose value is the result of the `get_row_permission`
    method on that row.
    New feature since `/blog/2011/0830`
    """
    name = 'disable_editing'

    def full_value_from_object(self, obj, ar):
        actor = self.store.actor
        if actor.update_action is None:
            #~ print 20120601, self.store.actor, "update_action is None"
            return True  # disable editing if there's no update_action
        v = actor.get_row_permission(
            obj, ar, actor.get_row_state(obj), actor.update_action)
        # if str(actor).startswith('aids.'):
        #     logger.info("20141128 store.py %s %s value=%s",
        #                 actor, actor.update_action, v)
        return not v


#~ class PropertiesStoreField(StoreField):
#~ class PropertyStoreField(StoreField):
    #~ def __init__(self,field,**kw):
        #~ kw['type'] = ...
        #~ StoreField.__init__(self,field,**kw)
    #~ def get_from_form(self,instance,post_data):
        #~ v = post_data.get(self.field.name)
        #~ if v == 'true':
            #~ v = True
        #~ else:
            #~ v = False
        #~ instance[self.field.name] = v
#~ from lino.utils.textfields import extract_summary
#~ class TextStoreField(StoreField):
    #~ def value_from_object(self,request,obj):
        #~ v = self.field.value_from_object(obj)
        #~ if request.expand_memos:
            #~ return v
        #~ return extract_summary(v)
class BooleanStoreField(StoreField):

    """
    This class wouldn't be necessary if Django's 
    `BooleanField.to_python` method would interpret 
    "on" as a valid `True` value. We had some interesting 
    discussion on this in :djangoticket:`#15497 (BooleanField
    should work for all PostgreSQL expressions)<15497>`. 
    """

    form2obj_default = False  # 'off'

    def __init__(self, field, name, **kw):
        kw['type'] = 'boolean'
        StoreField.__init__(self, field, name, **kw)
        if not field.editable:
            def full_value_from_object(self, obj, ar):
                #~ return self.value2html(ar,self.field.value_from_object(obj))
                return self.format_value(ar, self.field.value_from_object(obj))
            self.full_value_from_object = curry(full_value_from_object, self)

    def parse_form_value(self, v, obj):
        """
        Ext.ensible CalendarPanel sends boolean values as 
        """
        #~ print "20110717 parse_form_value", self.field.name, v, obj
        return constants.parse_boolean(v)

    def format_value(self, ar, v):
        return force_unicode(iif(v, _("Yes"), _("No")))


class DisplayStoreField(StoreField):
    pass
    # def full_value_from_object(self, obj, ar):
    #     return self.field.value_from_object(obj, ar)


class GenericForeignKeyField(DisplayStoreField):

    def full_value_from_object(self, obj, ar):
        v = getattr(obj, self.name, None)
        #~ logger.info("20130611 full_value_from_object() %s",v)
        if v is None:
            return ''
        if ar is None:
            return unicode(v)
        if ar.renderer is None:
            return unicode(v)
        return ar.obj2html(v)


class unused_GenericForeignKeyField(StoreField):

    def full_value_from_object(self, obj, ar):
        v = getattr(obj, self.name, None)
        #~ logger.info("full_value_from_object() %s",v)
        return v
        #~ owner = getattr(obj,self.name)
        #~ if owner is None:
            # ~ # owner_id = getattr(obj,self.field.fk_field)
            # ~ # if owner_id is None:
                # ~ # return ''
            #~ return ''
        #~ return ar.obj2html(owner)

    def value2list(self, ar, v, l, row):
        return l.append(unicode(v))

    def value2dict(self, v, d, row):
        d[self.name] = unicode(v)


class DecimalStoreField(StoreField):
    #~ def __init__(self,field,name,**kw):
        #~ kw['type'] = 'float'
        #~ StoreField.__init__(self,field,name,**kw)

    def parse_form_value(self, v, obj):
        return parse_decimal(v)

    #~ def value2num(self,v):
        # ~ # print "20120426 %s value2num(%s)" % (self,v)
        #~ return v

    def format_value(self, ar, v):
        if not v:
            return ''
        return settings.SITE.decfmt(v, places=self.field.decimal_places)

    #~ def value2html(self,ar,v,**cellattrs):
        #~ cellattrs.update(align="right")
        #~ return E.td(self.format_value(ar,v),**cellattrs)


class IntegerStoreField(StoreField):

    def __init__(self, field, name, **kw):
        kw['type'] = 'int'
        StoreField.__init__(self, field, name, **kw)


class AutoStoreField(StoreField):

    """
    A :class:`StoreField` for 
    `AutoField <https://docs.djangoproject.com/en/dev/ref/models/fields/#autofield>`__
    """

    def __init__(self, field, name, **kw):
        kw['type'] = 'int'
        StoreField.__init__(self, field, name, **kw)

    def form2obj(self, ar, obj, post_data, is_new):
        #~ logger.info("20121022 AutoStoreField.form2obj(%r)",ar.bound_action.full_name())
        if isinstance(ar.bound_action.action, actions.InsertRow):
            return super(AutoStoreField, self).form2obj(
                ar, obj, post_data, is_new)


class DateStoreField(StoreField):

    def __init__(self, field, name, **kw):
        kw['type'] = 'date'
        # date_format # 'Y-m-d'
        kw['dateFormat'] = settings.SITE.date_format_extjs
        StoreField.__init__(self, field, name, **kw)

    def parse_form_value(self, v, obj):
        if v:
            v = datetime.date(*settings.SITE.parse_date(v))
        else:
            v = None
        return v

    def format_value(self, ar, v):
        """Return a plain textual representation of this value as a unicode
        string.

        """
        return fds(v)


class IncompleteDateStoreField(StoreField):

    def parse_form_value(self, v, obj):
        if v:
            v = IncompleteDate(*settings.SITE.parse_date(v))
            #~ v = datetime.date(*settings.SITE.parse_date(v))
        return v


class DateTimeStoreField(StoreField):

    def parse_form_value(self, v, obj):
        if v:
            return settings.SITE.parse_datetime(v)
        return None


class TimeStoreField(StoreField):

    def parse_form_value(self, v, obj):
        if v:
            return settings.SITE.parse_time(v)
        return None


class FileFieldStoreField(StoreField):

    def full_value_from_object(self, obj, request):
        ff = self.field.value_from_object(obj)
        return ff.name


class MethodStoreField(StoreField):

    "Deprecated. See `/blog/2012/0327`."

    def full_value_from_object(self, obj, request):
        unbound_meth = self.field._return_type_for_method
        assert unbound_meth.func_code.co_argcount >= 2, (self.name,
                                                         unbound_meth.func_code.co_varnames)
        #~ print self.field.name
        return unbound_meth(obj, request)

    def value_from_object(self, obj, request):
        unbound_meth = self.field._return_type_for_method
        assert unbound_meth.func_code.co_argcount >= 2, (self.name,
                                                         unbound_meth.func_code.co_varnames)
        #~ print self.field.name
        return unbound_meth(obj, request)

    #~ def obj2list(self,request,obj):
        #~ return [self.value_from_object(request,obj)]

    #~ def obj2dict(self,request,obj,d):
        #  logger.debug('MethodStoreField.obj2dict() %s',self.field.name)
        #~ d[self.field.name] = self.value_from_object(request,obj)

    #~ def get_from_form(self,instance,post_data):
        #~ pass

    def form2obj(self, request, instance, post_data, is_new):
        pass
        #~ return instance
        #raise Exception("Cannot update a virtual field")

#~ class ComputedColumnField(StoreField):

    #~ def value_from_object(self,ar,obj):
        #~ m = self.field.func
        # ~ # assert m.func_code.co_argcount >= 2, (self.field.name, m.func_code.co_varnames)
        # ~ # print self.field.name
        #~ return m(obj,ar)[0]

    #~ def form2obj(self,request,instance,post_data,is_new):
        #~ pass


#~ class SlaveSummaryField(MethodStoreField):
    #~ def obj2dict(self,request,obj,d):
        #~ meth = getattr(obj,self.field.name)
        # ~ #logger.debug('MethodStoreField.obj2dict() %s',self.field.name)
        #~ d[self.field.name] = self.slave_report.()
class OneToOneStoreField(RelatedMixin, StoreField):

    def value_from_object(self, obj, request):
        v = self.full_value_from_object(obj, request)
        #~ try:
            #~ v = getattr(obj,self.field.name)
        #~ except self.field.rel.to.DoesNotExist,e:
            #~ v = None
        if v is None:
            return None
        return v.pk

    #~ def obj2list(self,request,obj):
        #~ return [self.value_from_object(request,obj)]

    #~ def obj2dict(self,request,obj,d):
        #~ d[self.field.name] = self.value_from_object(request,obj)


def get_atomizer(model, fld, name):
    sf = getattr(fld, '_lino_atomizer', None)
    if sf is None:
        sf = create_atomizer(model, fld, name)
        setattr(fld, '_lino_atomizer', sf)
    return sf


def create_atomizer(model, fld, name):
    if isinstance(fld, fields.RemoteField):
        """
        Hack: we create a StoreField based on the remote field,
        then modify its behaviour.
        """
        sf = create_atomizer(model, fld.field, fld.name)

        def value_from_object(sf, obj, ar):
            #~ if fld.name == 'event__when_text':
                #~ logger.info("20130802 create_atomizer RemoteField value_from_object")
            m = fld.func
            return m(obj, ar)

        def full_value_from_object(sf, obj, ar):
            #~ logger.info("20120406 %s.full_value_from_object(%s)",sf.name,sf)
            m = fld.func
            v = m(obj, ar)
            #~ if fld.name == 'event__when_text':
                #~ logger.info("20130802 full_value_from_object %s",obj)
            return v

        sf.value_from_object = curry(value_from_object, sf)
        sf.full_value_from_object = curry(full_value_from_object, sf)
        #~ sf.field = fld.field
        #~ sf.value2list = curry(value2list,sf)
        return sf
    #~ if isinstance(fld,tables.ComputedColumn):
        #~ logger.info("20111230 Store.create_atomizer(%s)", fld)
        #~ return ComputedColumnField(fld)
    meth = getattr(fld, '_return_type_for_method', None)
    if meth is not None:
        # uh, this is tricky...
        return MethodStoreField(fld, name)
    #~ if isinstance(fld,fields.HtmlBox):
        #~ ...
    #~ if isinstance(fld,dd.LinkedForeignKey):
        #~ return LinkedForeignKeyField(fld,name)

    sf_class = getattr(fld, 'lino_atomizer_class', None)
    if sf_class is not None:
        return sf_class(fld, name)

    if isinstance(fld, fields.DummyField):
        return None
    if isinstance(fld, fields.RequestField):
        delegate = create_atomizer(model, fld.return_type, fld.name)
        return RequestStoreField(fld, delegate, name)
    if isinstance(fld, fields.VirtualField):
        delegate = create_atomizer(model, fld.return_type, fld.name)
        return VirtStoreField(fld, delegate, name)
    if isinstance(fld, models.FileField):
        return FileFieldStoreField(fld, name)
    if isinstance(fld, models.ManyToManyField):
        return StoreField(fld, name)
    if isinstance(fld, fields.PasswordField):
        return PasswordStoreField(fld, name)
    if isinstance(fld, models.OneToOneField):
        return OneToOneStoreField(fld, name)
    if isinstance(fld, generic.GenericForeignKey):
        return GenericForeignKeyField(fld, name)
    if isinstance(fld, fields.GenericForeignKeyIdField):
        return ComboStoreField(fld, name)
    if isinstance(fld, models.ForeignKey):
        return ForeignKeyStoreField(fld, name)
    if isinstance(fld, models.TimeField):
        return TimeStoreField(fld, name)
    if isinstance(fld, models.DateTimeField):
        return DateTimeStoreField(fld, name)
    if isinstance(fld, fields.IncompleteDateField):
        return IncompleteDateStoreField(fld, name)
    if isinstance(fld, models.DateField):
        return DateStoreField(fld, name)
    if isinstance(fld, models.BooleanField):
        return BooleanStoreField(fld, name)
    if isinstance(fld, models.DecimalField):
        return DecimalStoreField(fld, name)
    if isinstance(fld, models.AutoField):
        return AutoStoreField(fld, name)
        #~ kw.update(type='int')
    if isinstance(fld, models.SmallIntegerField):
        return IntegerStoreField(fld, name)
    if isinstance(fld, fields.DisplayField):
        return DisplayStoreField(fld, name)
    if isinstance(fld, models.IntegerField):
        return IntegerStoreField(fld, name)
    kw = {}
    if choosers.uses_simple_values(model, fld):
        return StoreField(fld, name, **kw)
    else:
        return ComboStoreField(fld, name, **kw)


class BaseStore(object):
    pass


class ParameterStore(BaseStore):
    # instantiated in `lino.core.layouts`
    def __init__(self, params_layout_handle, url_param):
        self.param_fields = []

        holder = params_layout_handle.layout.get_chooser_holder()
        for pf in params_layout_handle._store_fields:
            sf = create_atomizer(holder, pf, pf.name)
            if sf is not None:
                self.param_fields.append(sf)

        self.param_fields = tuple(self.param_fields)
        self.url_param = url_param
        self.params_layout_handle = params_layout_handle

    def __str__(self):
        return "%s of %s" % (
            self.__class__.__name__, self.params_layout_handle)

    def pv2dict(self, pv, **d):
        for fld in self.param_fields:
            v = pv.get(fld.name, None)
            fld.value2dict(v, d, None)
        return d

    def pv2list(self, ar, pv, **d):  # new since 20140930
        l = []
        for fld in self.param_fields:
            v = pv.get(fld.name, None)
            l.append(v)
        return l

    def parse_params(self, request, **kw):
        pv = request.REQUEST.getlist(self.url_param)
        #~ logger.info("20120221 ParameterStore.parse_params(%s) --> %s",self.url_param,pv)

        def parse(sf, form_value):
            if form_value == '' and not sf.field.empty_strings_allowed:
                return sf.form2obj_default
                # When a field has been posted with empty string, we
                # don't want it to get the field's default value
                # because otherwise checkboxes with default value True
                # can never be unset.  charfields have
                # empty_strings_allowed e.g. id field may be empty.
                # But don't do this for other cases.
            else:
                return sf.parse_form_value(form_value, None)

        if len(pv) > 0:
            if len(self.param_fields) != len(pv):
                raise Exception(
                    "%s expects a list of %d values but got %d: %s" % (
                        self, len(self.param_fields), len(pv), pv))
            for i, f in enumerate(self.param_fields):
                kw[f.field.name] = parse(f, pv[i])
        return kw


class Store(BaseStore):

    """
    A Store is the collection of StoreFields for a given Table.
    """

    pk = None

    def __init__(self, rh, **options):
        #~ assert isinstance(rh,tables.TableHandle)
        #~ Component.__init__(self,id2js(rh.report.actor_id),**options)
        self.rh = rh
        self.actor = rh.actor
        """
        MTI children have two primary keys. Example::
        >>> from lino.projects.pcsw.models import Person
        >>> [f for f in Person._meta.fields if f.primary_key]
        [<django.db.models.fields.AutoField: id>, <django.db.models.fields.related.OneToOneField: contact_ptr>]
        >>> Person._meta.pk
        <django.db.models.fields.related.OneToOneField: contact_ptr>
        >>> p = Person.objects.get(pk=118)
        >>> p
        <Person: ARENS Annette (118)>
        >>> p.contact_ptr_id = 117
        >>> print p.pk
        117
        >>> p.save()
        >>>        
        """
        #~ if issubclass(rh.report,dbtables.Table):
            #~ self.pk = self.report.model._meta.pk
            #~ assert self.pk is not None, "Cannot make Store for %s because %s has no pk" % (
              #~ self.report.actor_id,self.report.model)

        #~ fields = []

        # temporary dict used by collect_fields and add_field_for
        self.df2sf = {}
        self.all_fields = []
        self.list_fields = []
        self.detail_fields = []

        def addfield(sf):
            self.all_fields.append(sf)
            self.list_fields.append(sf)
            self.detail_fields.append(sf)

        if not issubclass(rh.actor, frames.Frame):
            self.collect_fields(self.list_fields, rh.get_list_layout())

        form = rh.actor.detail_layout
        if form:
            dh = form.get_layout_handle(rh.ui)
            self.collect_fields(self.detail_fields, dh)

        form = rh.actor.insert_layout
        if form:
            dh = form.get_layout_handle(rh.ui)
            self.collect_fields(self.detail_fields, dh)

        if self.pk is not None:
            self.pk_index = 0
            found = False
            for fld in self.list_fields:
                """
                Django's Field.__cmp__() does::
                
                  return cmp(self.creation_counter, other.creation_counter)
                  
                which causes an exception when trying to compare a field
                with an object of other type.
                """
                if (fld.field.__class__ is self.pk.__class__) \
                   and fld.field == self.pk:
                    #~ self.pk = fld.field
                    found = True
                    break
                self.pk_index += fld.list_values_count
            if not found:
                raise Exception("Primary key %s not found in list_fields %s" %
                                (self.pk, self.list_fields))

        del self.df2sf

        #~ if not issubclass(rh.report,dbtables.Table):
            #~ addfield(RecnoStoreField(self))

        if rh.actor.editable:  # condition added 20131017

            addfield(DisabledFieldsStoreField(self))

        addfield(DisabledActionsStoreField(self))

        if rh.actor.editable:
            addfield(DisableEditingStoreField(self))

        if rh.actor.get_row_classes is not None:
            addfield(RowClassStoreField(self))

        # virtual fields must come last so that Store.form2obj()
        # processes "real" fields first.
        self.all_fields = [
            f for f in self.all_fields if not isinstance(f, VirtStoreField)
        ] + [
            f for f in self.all_fields if isinstance(f, VirtStoreField)
        ]
        self.all_fields = tuple(self.all_fields)
        self.list_fields = tuple(self.list_fields)
        self.detail_fields = tuple(self.detail_fields)

    def collect_fields(self, fields, *layouts):
        """
        `fields` is a pointer to either `self.detail_fields` or `self.list_fields`.
        Each of these must contain a primary key field.
        
        """
        pk_found = False
        for layout in layouts:
            for df in layout._store_fields:
                assert df is not None
                self.add_field_for(fields, df)
                if df.primary_key:
                    pk_found = True
                    if self.pk is None:
                        self.pk = df

        if self.pk is None:
            self.pk = self.actor.get_pk_field()
        if self.pk is not None:
            if not pk_found:
                self.add_field_for(fields, self.pk)

    def add_field_for(self, fields, df):
        sf = get_atomizer(self.actor, df, df.name)
        if sf is None:  # dummy fields
            return
        if not sf in self.all_fields:
            self.all_fields.append(sf)

        #~ sf = self.df2sf.get(df,None)
        #~ if sf is None:
            #~ sf = self.create_atomizer(df,df.name)
            #~ self.all_fields.append(sf)
            #~ self.df2sf[df] = sf
        fields.append(sf)

    def form2obj(self, ar, form_values, instance, is_new):
        disabled_fields = set(self.actor.disabled_fields(instance, ar))
        changed_triggers = []
        for f in self.all_fields:
            if not f.name in disabled_fields:
                try:
                    if f.form2obj(ar, instance, form_values, is_new):
                        m = getattr(instance, f.name + "_changed", None)
                        if m is not None:
                            changed_triggers.append(m)
                except exceptions.ValidationError as e:
                    raise exceptions.ValidationError({f.name: e})
                except ValueError as e:
                    raise exceptions.ValidationError(
                        {f.name: _("Invalid value for this field (%s).") % e})
                except Exception as e:
                    logger.warning(
                        "Exception during Store.form2obj (field %s) : %s",
                        f.name, e)
                    logger.exception(e)
                    raise
                # logger.info("20120228 Store.form2obj %s -> %s",
                # f, dd.obj2str(instance))
        for m in changed_triggers:
            m(ar)

    def column_names(self):
        l = []
        for fld in self.list_fields:
            l += fld.column_names()
        return l

    def column_index(self, name):
        """
        Used to set `disabled_actions_index`.
        Was used to write definition of Ext.ensible.cal.CalendarMappings
        and Ext.ensible.cal.EventMappings 
        """
        #~ logger.info("20111214 column_names: %s",list(self.column_names()))
        return list(self.column_names()).index(name)

    def row2list(self, request, row):
        #~ assert isinstance(request,dbtables.AbstractTableRequest)
        #~ if not isinstance(request,dbtables.ListActionRequest):
            #~ raise Exception()
        #~ logger.info("20120107 Store %s row2list(%s)", self.report.model, dd.obj2str(row))
        l = []
        if isinstance(row, PhantomRow):
            for fld in self.list_fields:
                fld.value2list(request, None, l, row)
        #~ elif isinstance(row,actions.VirtualRow):
            #~ for fld in self.list_fields:
                #~ fld.value2list(request,None,l,row)
        else:
            for fld in self.list_fields:
                v = fld.full_value_from_object(row, request)
                fld.value2list(request, v, l, row)
        #~ logger.info("20130611 Store row2list() --> %r", l)
        return l

    def row2dict(self, ar, row, fields=None, **d):
        #~ assert isinstance(ar,dbtables.AbstractTableRequest)
        #~ logger.info("20111209 Store.row2dict(%s)", dd.obj2str(row))
        if fields is None:
            fields = self.detail_fields
        for fld in fields:
            # logger.info("20140429 Store.row2dict %s", fld)
            v = fld.full_value_from_object(row, ar)
            fld.value2dict(v, d, row)
            # logger.info("20140429 Store.row2dict %s -> %s", fld, v)
        return d

    #~ def row2odt(self,request,fields,row,sums):
        #~ for i,fld in enumerate(fields):
            #~ if fld.field is not None:
                #~ v = fld.full_value_from_object(request,row)
                #~ if v is None:
                    #~ yield ''
                #~ else:
                    #~ sums[i] += fld.value2num(v)
                    #~ yield fld.value2odt(request,v)
