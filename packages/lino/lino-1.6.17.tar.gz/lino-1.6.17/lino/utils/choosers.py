# Copyright 2009-2014 Luc Saffre
# License: BSD (see file COPYING for details)

"""Extends the possibilities for defining choices for fields of a
Django model.

- Context-sensitive choices
- Non-limiting choices :
  specify a pick list of suggestions but leave the possibility
  to store manually entered values
- :ref:`learning_combos`

TODO: compare with `django-ajax-selects
<https://github.com/crucialfelix/django-ajax-selects>`_


.. _learning_combos:

Learning Comboboxes
-------------------

Choosers inspect the model, and if it defines a method
`create_FOO_choice`, then the chooser will become "learning": the
ComboBox will be told to accept also new values, and the server will
handle these cases accordingly.

"""

import logging
logger = logging.getLogger(__name__)

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey

from lino.utils.instantiator import make_converter
from lino.core import constants


def is_foreignkey(fld):
    return isinstance(fld, (models.ForeignKey, GenericForeignKey))


class BaseChooser:
    pass


class FieldChooser(BaseChooser):

    def __init__(self, field):
        self.field = field


class ChoicesChooser(FieldChooser):

    def __init__(self, field):
        FieldChooser.__init__(self, field)
        self.simple_values = type(field.choices[0])


class Chooser(FieldChooser):

    """
    A Chooser holds information about the possible choices of a field.
    """
    #~ stored_name = None
    simple_values = False
    instance_values = True
    force_selection = True
    choice_display_method = None  # not yet used.
    can_create_choice = False

    def __init__(self, model, field, meth):
        FieldChooser.__init__(self, field)
        self.model = model
        #~ self.field = model._meta.get_field(fldname)
        self.meth = meth
        if not is_foreignkey(field):
            self.simple_values = getattr(meth, 'simple_values', False)
            self.instance_values = getattr(meth, 'instance_values', False)
            self.force_selection = getattr(
                meth, 'force_selection', self.force_selection)
        #~ self.context_params = meth.func_code.co_varnames[1:meth.func_code.co_argcount]
        self.context_params = meth.context_params
        #~ self.multiple = meth.multiple
        #~ self.context_params = meth.func_code.co_varnames[:meth.func_code.co_argcount]
        #~ print '20100724', meth, self.context_params
        #~ logger.warning("20100527 %s %s",self.context_params,meth)
        self.context_values = []
        self.context_fields = []
        for name in self.context_params:
            f = self.get_data_elem(name)
            if f is None:
                raise Exception(
                    "No data element '%s' in %s "
                    "(method %s_choices)" % (
                        name, self.model, field.name))
            #~ if name == 'p_book':
                #~ print 20131012, f
            self.context_fields.append(f)
            self.context_values.append(name + "Hidden")
            #~ if isinstance(f,models.ForeignKey):
                #~ self.context_values.append(name+"Hidden")
            #~ else:
                #~ self.context_values.append(name)
        self.converters = []
        #~ try:
        for f in self.context_fields:
            cv = make_converter(f)
            if cv is not None:
                self.converters.append(cv)
        #~ except models.FieldDoesNotExist,e:
            #~ print e

        if hasattr(model, "create_%s_choice" % field.name):
            self.can_create_choice = True

        #~ if hasattr(model,"get_%s_display" % field.name):
        m = getattr(model, "%s_choice_display" % field.name, None)
        if m is not None:
            self.choice_display_method = m

    def __str__(self):
        return "Chooser(%s.%s,%s)" % (
            self.model.__name__, self.field.name,
            self.context_params)

    def create_choice(self, obj, text):
        m = getattr(obj, "create_%s_choice" % self.field.name)
        return m(text)

    def get_data_elem(self, name):
        """Calls :meth:`dd.Actor.get_data_elem` or
        :meth:`dd.Model.get_data_elem` or
        :meth:`dd.Action.get_data_elem`.

        """
        de = self.model.get_data_elem(name)
        if de is None:
            return self.model.get_param_elem(name)
        return de

    #~ def get_data_elem(self,name):
        #~ for vf in self.model._meta.virtual_fields:
            #~ if vf.name == name:
                #~ return vf
        #~ return self.model._meta.get_field(name)

    def __call__(self, *args, **kw):
        for i, v in enumerate(args):
            kw[self.context_fields[i]] = v
        return self.get_choices(**kw)

    def get_choices(self, **context):  # 20120918b
        """Return a list of choices for this chooser, using keyword parameters
        as context.

        """
        args = []
        for varname in self.context_params:
            args.append(context.get(varname, None))
        return self.meth(*args)

    #~ def get_instance_choices(self,obj):
        #~ "Return a list of choices for this chooser, using `obj` as context."
        #~ args = []
        #~ for varname in self.context_params:
            #~ args.append(getattr(obj,varname,None))
        #~ return self.meth(*args)

    #~ def get_request_choices(self,ar,tbl):
    def get_request_choices(self, request, tbl):
        """
        Return a list of choices for this chooser, 
        using a HttpRequest to build the context.
        """
        kw = {}

        # 20120202
        if tbl.master_field is not None:
            mt = request.REQUEST.get(constants.URL_PARAM_MASTER_TYPE)
            try:
                master = ContentType.objects.get(pk=mt).model_class()
            except ContentType.DoesNotExist, e:
                pass

            pk = request.REQUEST.get(constants.URL_PARAM_MASTER_PK, None)
            if pk:
                try:
                    kw[tbl.master_field.name] = master.objects.get(pk=pk)
                except ValueError, e:
                    raise Exception(
                        "Invalid primary key %r for %s", pk, master.__name__)
                except master.DoesNotExist, e:
                    # todo: ReportRequest should become a subclass of Dialog
                    # and this exception should call dlg.error()
                    raise Exception("There's no %s with primary key %r" %
                                    (master.__name__, pk))

        for k, v in request.GET.items():
            kw[str(k)] = v

        # logger.info(
        #     "20130513 get_request_choices(%r) -> %r",
        #     tbl, kw)

        for cv in self.converters:
            kw = cv.convert(**kw)

        if tbl.known_values:
            kw.update(tbl.known_values)

        if False:  # removed 20120815 #1114
            #~ ar = tbl.request(ui,request,tbl.default_action)
            if ar.create_kw:
                kw.update(ar.create_kw)
            if ar.known_values:
                kw.update(ar.known_values)
            if tbl.master_key:
                kw[tbl.master_key] = ar.master_instance
            #~ if tbl.known_values:
                #~ kw.update(tbl.known_values)
        return self.get_choices(**kw)  # 20120918b

    def get_text_for_value(self, value, obj):
        m = getattr(self.field, 'get_text_for_value', None)
        if m is not None:  # e.g. lino.utils.choicelist.ChoiceListField
            return m(value)
        #~ raise NotImplementedError
        #~ assert not self.simple_values
        m = getattr(obj, "get_" + self.field.name + "_display")
        #~ if m is None:
            #~ raise Exception("")
        return m(value)
        #~ raise NotImplementedError("%s : Cannot get text for value %r" % (self.meth,value))


def uses_simple_values(holder, fld):
    "used by :class:`lino.ui.extjs.ext_store.Store`"
    if is_foreignkey(fld):
        return False
    if holder is not None:
        ch = holder.get_chooser_for_field(fld.name)
        if ch is not None:
            return ch.simple_values
    choices = list(fld.choices)
    if len(choices) == 0:
        return True
    if type(choices[0]) in (list, tuple):
        return False
    return True


def _chooser(make, **options):
    #~ options.setdefault('quick_insert_field',None)
    def chooser_decorator(fn):
        def wrapped(*args):
            #~ print 20101220, args
            return fn(*args)
        wrapped.context_params = fn.func_code.co_varnames[
            1:fn.func_code.co_argcount]
        #~ 20120918b wrapped.context_params = fn.func_code.co_varnames[2:fn.func_code.co_argcount]
        for k, v in options.items():
            setattr(wrapped, k, v)
        return make(wrapped)
        # return classmethod(wrapped)
        # A chooser on an action must not turn it into a classmethod
    return chooser_decorator


def chooser(**options):
    "Decorator which turns the method into a chooser."
    return _chooser(classmethod, **options)


def noop(x):
    return x


def action_chooser(**options):
    return _chooser(noop, **options)
