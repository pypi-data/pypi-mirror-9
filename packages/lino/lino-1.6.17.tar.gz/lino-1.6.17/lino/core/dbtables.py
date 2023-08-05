# Copyright 2009-2014 Luc Saffre
# License: BSD (see file COPYING for details)

"""
This defines the :class:`Table` class.
"""

import logging
logger = logging.getLogger(__name__)

import datetime

from django.conf import settings
from django.db.models.fields import NOT_PROVIDED
from django.utils.translation import ugettext_lazy as _

from django.db import models
from django.db.models.query import QuerySet
from django.contrib.contenttypes.models import ContentType


from lino.core import fields
from lino.core import actions
from lino.core.model import Model
from lino.core import actors
from lino.core import frames


from lino.core.dbutils import full_model_name
from lino.core.dbutils import resolve_model, resolve_field, get_field, UnresolvedModel
from lino.core.tables import AbstractTable, TableRequest, VirtualTable

from lino.utils.xmlgen.html import E


def unused_parse_js_date(s, name):
    #~ v = dateparser.parse(s)
    #~ v = dateparser.parse(s,fuzzy=True)
    return datetime.date(*settings.SITE.parse_date(s))
    #~ print "parse_js_date %s : %r -> %s" % (name,s,v)
    #~ return v


def wildcard_data_elems(model):
    """
    Yields names that will be used as wildcard column_names of a Table.
    """
    meta = model._meta
    #~ for f in meta.fields: yield f.name
    #~ for f in meta.many_to_many: yield f.name
    #~ for f in meta.virtual_fields: yield f.name
    for f in meta.fields:
        #~ if f.editable:
        if not isinstance(f, fields.RichTextField):
            if not isinstance(f, fields.VirtualField):
                if not getattr(f, '_lino_babel_field', False):
                    yield f
    for f in meta.many_to_many:
        yield f
    for f in meta.virtual_fields:
        if not isinstance(f, fields.VirtualField):
            yield f
    # todo: for slave in self.report.slaves

    #~ for de in data_elems(self.model): yield de


def base_attrs(cl):
    #~ if cl is Table or len(cl.__bases__) == 0:
        #~ return
    #~ myattrs = set(cl.__dict__.keys())
    for b in cl.__bases__:
        for k in base_attrs(b):
            yield k
        for k in b.__dict__.keys():
            yield k


def add_quick_search_filter(qs, search_text):
    if not isinstance(qs, QuerySet):
        # TODO: filter also simple lists
        return qs
    return qs.filter(quick_search_filter(qs.model, search_text))


def quick_search_filter(model, search_text, prefix=''):
    #~ logger.info("20130425 quick_search_filter(%s,%r)",model,search_text)
    q = models.Q()
    if model.quick_search_fields is not None:
        for fn in model.quick_search_fields:
            kw = {prefix + fn + "__icontains": search_text}
            q = q | models.Q(**kw)
            #~ logger.info("20130425 %s",kw)
    else:
        for field in model._meta.fields:
            if isinstance(field, models.CharField):
                kw = {prefix + field.name + "__icontains": search_text}
                q = q | models.Q(**kw)
                #~ logger.info("20120709 %s__icontains=%r",field.name,search_text)
            #~ else:
                #~ logger.info("20120709 %s : not a CharField",field.name)
    if search_text.isdigit():
        for field in model._meta.fields:
            if isinstance(field, (models.IntegerField, models.AutoField)):
                kw = {prefix + field.name: int(search_text)}
                q = q | models.Q(**kw)
    return q


def add_gridfilters(qs, gridfilters):
    """
    Converts a `filter` request in the format used by :extux:`Ext.ux.grid.GridFilters` into a
    `Django field lookup <http://docs.djangoproject.com/en/1.2/ref/models/querysets/#field-lookups>`_
    on a :class:`django.db.models.query.QuerySet`.

    :param qs: the queryset to be modified.
    :param gridfilters: a list of dictionaries, each having 3 keys `field`, `type` and `value`.

    """
    if not isinstance(qs, QuerySet):
        raise NotImplementedError('TODO: filter also simple lists')
    q = models.Q()
    for flt in gridfilters:
        field = get_field(qs.model, flt['field'])
        flttype = flt['type']
        kw = {}
        if flttype == 'string':
            if isinstance(field, models.CharField):
                kw[field.name + "__icontains"] = flt['value']
                q = q & models.Q(**kw)
            elif isinstance(field, models.ForeignKey):
                q = q & quick_search_filter(
                    field.rel.to, flt['value'], field.name + "__")
                #~ rq = models.Q()
                #~ search_field = field.rel.to.grid_search_field
                #~ for search_field in field.rel.to.quick_search_fields:
                #~ search_field = getattr(field.rel.to,'grid_search_field',None)
                #~ if search_field is not None:
                    #~ rq = rq | models.Q(**{field.name+"__%s__icontains" % search_field : flt['value']})
                #~ q = q & rq
            else:
                raise NotImplementedError(repr(flt))
        elif flttype == 'numeric':
            cmp = str(flt['comparison'])
            if cmp == 'eq':
                cmp = 'exact'
            kw[field.name + "__" + cmp] = flt['value']
            q = q & models.Q(**kw)
        elif flttype == 'boolean':
            kw[field.name + "__equals"] = flt['value']
            q = q & models.Q(**kw)
        elif flttype == 'date':
            v = datetime.date(*settings.SITE.parse_date(flt['value']))
            #~ v = parse_js_date(flt['value'],field.name)
            cmp = str(flt['comparison'])
            if cmp == 'eq':
                cmp = 'exact'
            kw[field.name + "__" + cmp] = v
            q = q & models.Q(**kw)
            #~ print kw
        else:
            raise NotImplementedError(repr(flt))
    return qs.filter(q)


def rc_name(rptclass):
    return rptclass.app_label + '.' + rptclass.__name__

#~ def de_verbose_name(de):
    #~ if isinstance(de,models.Field):
        #~ return de.verbose_name
    #~ return de.name


# TODO : move these global variables to a better place
master_reports = []
slave_reports = []
generic_slaves = {}
frames_list = []
custom_tables = []
#~ rptname_choices = []

#~ config_dirs = []


def register_frame(frm):
    frames_list.append(frm)


def is_candidate(T):
    if T.filter or T.exclude or T.known_values:
        return False
    if not T.use_as_default_table:
        return False
    return True


def register_report(rpt):
    #~ logger.debug("20120103 register_report %s", rpt.actor_id)
    #rptclass.app_label = rptclass.__module__.split('.')[-2]

    #~ if rpt.typo_check:
        #~ myattrs = set(rpt.__dict__.keys())
        #~ for attr in base_attrs(rpt):
            #~ myattrs.discard(attr)
        #~ if len(myattrs):
            #~ logger.warning("%s defines new attribute(s) %s", rpt, ",".join(myattrs))

    if issubclass(rpt, Table) and rpt.model is None:
        #~ logger.debug("20111113 %s is an abstract report", rpt)
        return

    #~ for name,v in rpt.__dict__.items():
    #~ for name in rpt.__class__.__dict__.keys():
    #~ for name in dir(rpt):
        #~ v = getattr(rpt,name)
        #~ if isinstance(v,Group):
            #~ v.name = name
            #~ v.add_to_table(rpt)
            #~ rpt.custom_groups = rpt.custom_groups + [v]
        #~ if isinstance(v,ComputedColumn):
            #~ v.name = name
            #~ v.add_to_table(rpt)
            #~ d = dict()
            #~ d.update(rpt.computed_columns)
            #~ d[name] = v
            #~ rpt.computed_columns = d

    #~ if rpt.model._meta.abstract:

    #~ rptname_choices.append((rpt.actor_id, rpt.get_label()))
    #~ rptname_choices.append(rpt.actor_id)
    
    if issubclass(rpt, Table):
        if rpt.master is None:
            if not rpt.model._meta.abstract:
                #~ logger.debug("20120102 register %s : master report", rpt.actor_id)
                master_reports.append(rpt)
            if not '_lino_default_table' in rpt.model.__dict__:
                if is_candidate(rpt):
                    rpt.model._lino_default_table = rpt
        elif rpt.master is ContentType:
            #~ logger.debug("register %s : generic slave for %r", rpt.actor_id, rpt.master_key)
            generic_slaves[rpt.actor_id] = rpt
        else:
            #~ logger.debug("20120102 register %s : slave for %r", rpt.actor_id, rpt.master_key)
            slave_reports.append(rpt)
    elif issubclass(rpt, VirtualTable):
        custom_tables.append(rpt)


def discover():
    """This is being called at startup.
    
    - Each model can receive a number of "slaves".
      Slaves are tables whose data depends on an instance
      of another model (their master).

    - For each model we want to find out the "default table".
      The "choices table" for a foreignkey field is also currently
      simply the pointed model's default table.
      :modattr:`_lino_default_table`

    """

    logger.debug("Analyzing Tables...")
    #~ logger.debug("20111113 Register Table actors...")
    for rpt in actors.actors_list:
        if issubclass(rpt, Table) and rpt is not Table:
            register_report(rpt)
        elif issubclass(rpt, VirtualTable) and rpt is not VirtualTable:
            register_report(rpt)
        if issubclass(rpt, frames.Frame) and rpt is not frames.Frame:
            register_frame(rpt)

    logger.debug("Instantiate model tables...")
    for model in models.get_models():
        """Not getattr but __dict__.get because of the mixins.Listings trick."""
        rpt = model.__dict__.get('_lino_default_table', None)
        #~ rpt = getattr(model,'_lino_default_table',None)
        #~ logger.debug('20111113 %s._lino_default_table = %s',model,rpt)
        if rpt is None:
            rpt = table_factory(model)
            register_report(rpt)
            rpt.class_init()
            #~ rpt.collect_actions()
            model._lino_default_table = rpt

    logger.debug("Analyze %d slave tables...", len(slave_reports))
    for rpt in slave_reports:
        rpt.master = resolve_model(rpt.master)
        slaves = getattr(rpt.master, "_lino_slaves", None)
        if slaves is None:
            slaves = {}
            rpt.master._lino_slaves = slaves
        slaves[rpt.actor_id] = rpt
        #~ logger.debug("20111113 %s: slave for %s",rpt.actor_id, rpt.master.__name__)
    #~ logger.debug("Assigned %d slave reports to their master.",len(slave_reports))

    #~ logger.debug("reports.setup() done")


def has_fk(rr, name):
    if isinstance(rr, TableRequest):
        return rr.actor.master_key == name
    return False


#~ def model2report(m):
def model2actor(m):
    def f(table, *args):
        return m(*args)
    return classmethod(f)


class Table(AbstractTable):
    """An :class:`AbstractTable <lino.core.tables.AbstractTable>` that works
    on a Django Model using a QuerySet.

    A Table inherits from :class:`AbstractTable
    <lino.core.tables.AbstractTable>` and adds attributes like
    :attr:`model` and :attr:`master` and :attr:`master_key` who are
    important because Lino handles relations automagically.

    Another class of attributes are `filter`, `exclude` and `sort_order`
    which are thin wrappers to Django's query lookup parameters of same
    name.

    See :class:`dd.Table`.

    """
    
    model = None
    """The model on which this table iterates.

    """

    debug_sql = False

    show_detail_navigator = True

    screenshot_profiles = ['admin']
    """
    The user profile(s) for which we want a screenshot of this table.
    """

    use_as_default_table = True
    """ Set this to `False` if this Table should *not* become the
    Model's default table.

    """

    expand_memos = False
    """(No longer used; see :srcref:`docs/tickets/44`).  Whether multi-line text
    fields in Grid views should be expanded in by default or not.

    """

    details_of_master_template = _("%(details)s of %(master)s")
    """
    Used to build the title of a request on this table when it is a
    slave of a given master. The default value is defined as follows::

        details_of_master_template = _("%(details)s of %(master)s")

    """

    handle_uploaded_files = None
    """
    Handler for uploaded files.
    Same remarks as for :attr:`lino.core.actors.Actor.disabled_fields`.
    """

    @classmethod
    def get_chooser_for_field(self, fieldname):
        ch = super(Table, self).get_chooser_for_field(fieldname)
        if ch is not None:
            return ch
        if self.model is not None:
            return self.model.get_chooser_for_field(fieldname)

    @classmethod
    def request(self, master_instance=None, **kw):  # 20130327
        kw.update(actor=self)
        if master_instance is not None:
            kw.update(master_instance=master_instance)
        kw.setdefault('action', self.default_action)
        return TableRequest(**kw)

    @classmethod
    def column_choices(self):
        return [de.name for de in self.wildcard_data_elems()]

    @classmethod
    def get_screenshot_requests(self, language):
        if self.model is None:
            return
        if self.model._meta.abstract:
            return
        if self is not self.model._lino_default_table:
            return

        profiles2user = dict()
        for u in settings.SITE.user_model.objects.filter(language=language):
            if u.profile and u.profile.name in self.screenshot_profiles and not u.profile in profiles2user:
                profiles2user[u.profile] = u
        for user in profiles2user.values():
            #~ if user.profile.name != 'admin': return
            #~ yield self.default_action.request(user=user)
            # and self.default_action is not self.detail_action:
            if self.detail_action:
                yield self.detail_action.request(user=user)

    #~ @classmethod
    #~ def elem_filename_root(cls,elem):
        #~ return elem._meta.app_label + '.' + elem.__class__.__name__ + '-' + str(elem.pk)
    @classmethod
    def get_detail_sets(self):
        """
        Yield a list of (app_label,name) tuples for which the kernel
        should try to create a Detail Set.
        """
        if self.model is not None:
            def yield_model_detail_sets(m):
                for b in m.__bases__:
                    if issubclass(b, models.Model) and b is not models.Model:
                        for ds in yield_model_detail_sets(b):
                            yield ds
                yield m._meta.app_label + '/' + m.__name__

            for ds in yield_model_detail_sets(self.model):
                yield ds

        for s in super(Table, self).get_detail_sets():
            yield s

    #~ @classmethod
    #~ def find_field(cls,model,name):
        #~ for vf in cls.model._meta.virtual_fields:
            #~ if vf.name == name:
                #~ return vf
        #~ return cls.model._meta.get_field(name)

    @classmethod
    def get_pk_field(self):
        return self.model._meta.pk

    @classmethod
    def get_row_by_pk(self, ar, pk):
        try:
            return self.model.objects.get(pk=pk)
        except ValueError:
            return None
        except self.model.DoesNotExist:
            return None

    @classmethod
    def disabled_actions(self, ar, obj):
        d = dict()
        if obj is not None:
            state = self.get_row_state(obj)
            #~ u = ar.get_user()
            for ba in self.get_actions(ar.bound_action.action):
                if ba.action.action_name:
                    if ba.action.show_in_bbar and not self.get_row_permission(obj, ar, state, ba):
                    #~ if ba.action.show_in_bbar and not obj.get_row_permission(u,state,ba.action):
                    #~ if a.show_in_bbar and not a.get_action_permission(ar.get_user(),obj,state):
                        d[ba.action.action_name] = True
                #~ if ba.action.action_name == 'do_clear_cache':
                    #~ logger.info("20121127 %s %s", obj, d)
            #~ if obj.__class__.__name__ == 'Note':
                #~ logger.info("20120920 %s %s %r", obj, d,obj.__class__.get_row_permission)
        return d

    @classmethod
    def wildcard_data_elems(self):
        return wildcard_data_elems(self.model)

    @classmethod
    def is_valid_row(self, row):
        return isinstance(row, self.model)

    @classmethod
    def get_actor_label(self):
        if self.model is None:
            #~ return self._label or self.__name__
            return super(Table, self).get_actor_label()
        return self._label or self.model._meta.verbose_name_plural

    @classmethod
    def class_init(self):

        if self.model is not None:
            self.model = resolve_model(self.model, self.app_label)

        if isinstance(self.model, UnresolvedModel):
            self.model = None

        if self.model is not None:
            if isinstance(self.hidden_columns, basestring):
                self.hidden_columns = frozenset(
                    fields.fields_list(self.model, self.hidden_columns))
            self.hidden_columns |= self.model.hidden_columns

            if isinstance(self.active_fields, basestring):
                self.active_fields = frozenset(
                    fields.fields_list(self.model, self.active_fields))
            self.active_fields |= self.model.active_fields
            self.hidden_elements |= self.model.hidden_elements

            for b in self.model.mro():
                for k, v in b.__dict__.items():
                    # ~ v = self.model.__dict__.get(k,v) # 20131025 allow disabling inherited actions
                    if isinstance(v, actions.Action):
                        #~ print "20130326 %s.%s = action %s from %s" % (self,k,v,b)
                        existing_value = self.__dict__.get(k, NOT_PROVIDED)
                        if existing_value is NOT_PROVIDED:
                            setattr(self, k, v)
                        else:
                            if existing_value is None:  # 20130820
                                pass
                                #~ logger.info("%s disables model action '%s'",self,k)
                                #~ self.unbind_action(k)
                            else:
                                if not isinstance(existing_value, actions.Action):
                                    raise Exception(
                                        "%s cannot install model action %s because name is already used for %r" %
                                        self, k, existing_value)

            for name in ('workflow_state_field', 'workflow_owner_field'):
                if getattr(self, name) is None:
                    setattr(self, name, getattr(self.model, name))
                    #~ v = getattr(self.model,name,None)
                    #~ if v is not None:
                        #~ setattr(self,name,v)

            for name in (  # 'disabled_fields',
                'handle_uploaded_files',
                #~ 'get_row_permission',
                #~ 'disable_editing',
            ):
                if getattr(self, name) is None:
                    m = getattr(self.model, name, None)
                    if m is not None:
                        #~ logger.debug('20120731 Install model method %s from %r to %r',name,self.model,self)
                        setattr(self, name, model2actor(m))
                        #~ 'dictproxy' object does not support item assignment:
                        #~ self.__dict__[name] = model2actor(m)

            if self.master_key:

                master_model = None
                try:
                    x = self.model._meta.get_field_by_name(self.master_key)
                    fk, remote, direct, m2m = x
                    assert direct
                    assert not m2m
                    if fk.rel is not None:
                        master_model = fk.rel.to
                except models.FieldDoesNotExist as e:
                    for vf in self.model._meta.virtual_fields:
                        if vf.name == self.master_key:
                            fk = vf
                            master_model = ContentType
                            break
                if master_model is None:
                    df = getattr(self.model, self.master_key, None)
                    if isinstance(df, fields.DummyField):
                        self.abstract = True
                    else:
                        raise Exception(
                            "%s : no master for master_key %r in %s" % (
                                self, self.master_key, self.model))
                else:
                    self.master = master_model
                    self.master_field = fk
                    self.hidden_columns |= set([fk.name])
        #~ else:
            #~ assert self.master is None

        super(Table, self).class_init()

        if self.order_by is not None:
            if not isinstance(self.order_by, (list, tuple)):
                raise Exception("%s.order_by is %r (must be a list or tuple)" %
                                (self, self.order_by))
            if False:
                # good idea, but doesn't yet work for foreign fields,
                # e.g. order_by = ['content_type__app_label']
                for fieldname in self.order_by:
                    if fieldname.startswith('-'):
                        fieldname = fieldname[1:]
                    try:
                        fk, remote, direct, m2m = self.model._meta.get_field_by_name(
                            fieldname)
                        assert direct
                        assert not m2m
                    except models.FieldDoesNotExist:
                        raise Exception("Unknown fieldname %r in %s.order_by" %
                                        (fieldname, self))

    @classmethod
    def do_setup(self):

        super(Table, self).do_setup()
        #~ AbstractTable.do_setup(self)
        if self.model is None:
            return

        if hasattr(self.model, '_lino_slaves'):
            self._slaves = self.model._lino_slaves.values()
        else:
            self._slaves = []

        m = getattr(self.model, 'setup_table', None)
        if m is not None:
            m(self)

    @classmethod
    def is_abstract(self):
        if self.model is None \
            or self.model is Model \
                or self.model._meta.abstract:
            #~ logger.info('20120621 %s : no real table',h)
            return True
        return self.abstract

    #~ @classmethod
    #~ def setup_permissions(self):
        #~ if self.model is not None:
        #~ super(Table,self).setup_permissions()

    @classmethod
    def disabled_fields(cls, obj, ar):
        return obj.disabled_fields(ar)

    @classmethod
    def get_row_permission(cls, obj, ar, state, ba):
        """Returns True if the given action is allowed for the given instance
        `obj` and the given user.

        """
        if obj is None:
            return True
        return obj.get_row_permission(ar, state, ba)

    @classmethod
    def disable_delete(self, obj, ar):
        """
        Return either `None` if the given `obj` *is allowed*
        to be deleted by action request `ar`,
        or a string with a message explaining why, if not.
        """
        #~ logger.info("20130225 dbtables.disable_delete")
        if self.delete_action is None:
            return "No delete_action"
        if not self.get_row_permission(obj, ar, self.get_row_state(obj), self.delete_action):
            #~ print "20130222 ar is %r" % ar
            #~ logger.info("20130225 dbtables.disable_delete no permission")
            return _("You have no permission to delete this row.")
        return obj.disable_delete(ar)

    @classmethod
    def get_data_elem(self, name):
        """
        Adds the possibility to specify
        :class:`remote fields <lino.core.fields.RemoteField>`
        in a layout template.
        """
        #~ cc = AbstractTable.get_data_elem(self,name)

        if self.model is not None:
            if not isinstance(self.model, type) or not issubclass(
                    self.model, models.Model):
                raise Exception(
                    "%s.model is %r (and not a Model subclass)" %
                    (self, self.model))

            # logger.info("20120202 Table.get_data_elem found nothing")
            de = self.model.get_data_elem(name)
            if de is not None:
                return de
        return super(Table, self).get_data_elem(name)

    #~ @classmethod
    #~ def get_detail(self):
        #~ return self.model._lino_detail
    #~ @classmethod
    #~ def get_title(self,ar):
        #~ """
        #~ See also :meth:`lino.core.actors.Table.get_title`
        #~ """
        # ~ # NOTE: similar code in tables
        #~ title = self.get_title_base(ar)
        #~ tags = list(self.get_title_tags(ar))
        #~ if len(tags):
            #~ title += " (%s)" % (', '.join(tags))
        #~ return title
    @classmethod
    def get_title_base(self, ar):
        """
        """
        title = self.title or self.label
        if self.master is not None:
            title = self.details_of_master_template % dict(
                details=title,
                master=ar.master_instance)
        return title

    @classmethod
    def get_queryset(self, ar):
        """
        Return an iterable over the items processed by this table.
        Override this to use e.g. select_related() or to return a list.

        Return a customized default queryset
    
        Example::

          def get_queryset(self):
              return self.model.objects.select_related('country', 'city')


        """
        return self.model.objects.all()

    @classmethod
    def get_request_queryset(self, rr):
        """
        Build a Queryset for the specified request on this table.
        Upon first call, this will also lazily install Table.queryset
        which will be reused on every subsequent call.
        """
        qs = self.get_queryset(rr)
        if qs is None:
            return []
        kw = self.get_filter_kw(rr)
        if kw is None:
            return []
        if len(kw):
            qs = qs.filter(**kw)

        if rr.exclude:
            qs = qs.exclude(**rr.exclude)
            #~ qs = qs.exclude(rr.exclude)

        if self.filter:
            qs = qs.filter(self.filter)

        if rr.filter:
            qs = qs.filter(rr.filter)

        if rr.known_values:
            #~ logger.info("20120111 known values %r",rr.known_values)
            d = {}
            for k, v in rr.known_values.items():
                if v is None:
                    d[k + "__isnull"] = True
                else:
                    #~ d[k+"__exact"] = v
                    d[k] = v
                qs = qs.filter(**d)

        if self.exclude:
            qs = qs.exclude(**self.exclude)
            # TODO: use Q object instead of dict

        if rr.quick_search is not None:
            #~ qs = add_quick_search_filter(qs,self.model,rr.quick_search)
            qs = add_quick_search_filter(qs, rr.quick_search)
        if rr.gridfilters is not None:
            qs = add_gridfilters(qs, rr.gridfilters)
        extra = rr.extra or self.extra
        if extra is not None:
            qs = qs.extra(**extra)
        order_by = rr.order_by or self.order_by
        if order_by:
            #~ logger.info("20120122 order_by %s",order_by)
            qs = qs.order_by(*order_by)
        if self.debug_sql:
            logger.info("%s %s", self.debug_sql, qs.query)
        return qs

    @classmethod
    def create_instance(self, ar, **kw):
        """
        Create a model instance using the specified keyword args,
        calling also :meth:`lino.core.model.Model.on_create`.
        """
        #~ print 20120630, "Actor.create_instance", kw
        instance = self.model(**kw)
        instance.on_create(ar)
        return instance


    #~ @classmethod
    #~ def ajax_update(self,request):
        #~ print request.POST
        #~ return HttpResponse("1", mimetype='text/x-json')


def table_factory(model):
    """
    Automatically define a Table class for the specified model.
    This is used during kernel setup to create default tables for
    models who have no Table.
    """
    #~ logger.info('table_factory(%s)',model.__name__)
    bases = (Table,)
    for b in model.__bases__:
        rpt = getattr(b, '_lino_default_table', None)
        if rpt is not None:
            if issubclass(model, rpt.model):
            #~ if issubclass(rpt.model,model):
                bases = (rpt,)
                #~ bases = (rpt.__class__,)
    #~ logger.info('table_factory(%s) : bases is %s',model.__name__,bases)
    app_label = model._meta.app_label
    name = model.__name__ + "Table"
    cls = type(name, bases, dict(model=model, app_label=app_label))
    #~ cls.class_init()
    #~ cls.setup()

    #~ """
    #~ 20120104 We even add the factored class to the module because
    #~ actor lookup needs it. Otherwise we'd get a
    #~ `'module' object has no attribute 'DataControlListingTable'` error.

    #~ We cannot simply do ``settings.SITE.modules.define(app_label,name,cls)``
    #~ because this code is executed when `settings.SITE.modules` doesn't yet exist.
    #~ """

    #~ m = import_module(model.__module__)
    #~ if getattr(m,name,None) is not None:
        #~ raise Exception(
          #~ "Name of factored class %s clashes with existing name in %s"
          #~ %(cls,m))
    #~ setattr(m,name,cls)
    return actors.register_actor(cls)


def column_choices(rptname):
    rpt = actors.get_actor(rptname)
    return rpt.column_choices()

