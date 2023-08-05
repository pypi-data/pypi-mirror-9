# -*- coding: UTF-8 -*-
# Copyright 2009-2014 Luc Saffre
# License: BSD (see file COPYING for details)

"""

Summary from <http://en.wikipedia.org/wiki/Restful>: 

    On an element:

    - GET : Retrieve a representation of the addressed member of the collection expressed in an appropriate MIME type.
    - PUT : Update the addressed member of the collection or create it with the specified ID. 
    - POST : Treats the addressed member as a collection and creates a new subordinate of it. 
    - DELETE : Delete the addressed member of the collection. 

    On a list:

    - GET : List the members of the collection. 
    - PUT : Replace the entire collection with another collection. 
    - POST : Create a new entry in the collection where the ID is assigned automatically by the collection. 
      The ID created is included as part of the data returned by this operation. 
    - DELETE : Delete the entire collection.
    



"""

import logging
logger = logging.getLogger(__name__)

from django import http
from django.db import models
from django.conf import settings
from django.views.generic import View
import json
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode

from lino import dd

from lino.utils.xmlgen import html as xghtml
E = xghtml.E

from lino.utils.jsgen import py2js
from lino.utils import ucsv
from lino.utils import isiterable
from lino.utils import dblogger
from lino.core import auth

from lino.core import actions
from lino.core import dbtables

from lino.core.views import requested_actor, action_request
from lino.core.views import json_response, json_response_kw

from lino.core import constants as ext_requests

MAX_ROW_COUNT = 300


class HttpResponseDeleted(http.HttpResponse):
    status_code = 204


def elem2rec_empty(ar, ah, elem, **rec):
    """
    Returns a dict of this record, designed for usage by an EmptyTable.
    """
    #~ rec.update(data=rh.store.row2dict(ar,elem))
    rec.update(data=elem._data)
    #~ rec = elem2rec1(ar,ah,elem)
    #~ rec.update(title=_("Insert into %s...") % ar.get_title())
    rec.update(title=ar.get_action_title())
    rec.update(id=-99998)
    #~ rec.update(id=elem.pk) or -99999)
    if ar.actor.parameters:
        #~ rec.update(param_values=ar.ah.store.pv2dict(ar.ui,ar.param_values))
        rec.update(
            param_values=ar.actor.params_layout.params_store.pv2dict(
                ar.param_values))
    return rec


def delete_element(ar, elem):
    if elem is None:
        raise Warning("Cannot delete None")
    msg = ar.actor.disable_delete(elem, ar)
    if msg is not None:
        ar.error(None, msg, alert=True)
        return settings.SITE.ui.render_action_response(ar)

    #~ dblogger.log_deleted(ar.request,elem)

    #~ changes.log_delete(ar.request,elem)

    dd.pre_ui_delete.send(sender=elem, request=ar.request)

    try:
        elem.delete()
    except Exception, e:
        dblogger.exception(e)
        msg = _("Failed to delete %(record)s : %(error)s."
                ) % dict(record=dd.obj2unicode(elem), error=e)
        #~ msg = "Failed to delete %s." % element_name(elem)
        ar.error(None, msg)
        return settings.SITE.ui.render_action_response(ar)
        #~ raise Http404(msg)

    return HttpResponseDeleted()


class AdminIndex(View):

    """
    Similar to PlainIndex
    """

    def get(self, request, *args, **kw):
        #~ logger.info("20130719 AdminIndex")
        settings.SITE.startup()
        ui = settings.SITE.ui
        if settings.SITE.user_model is not None:
            user = request.subst_user or request.user
            a = settings.SITE.get_main_action(user)
            if a is not None and a.get_view_permission(user.profile):
                kw.update(on_ready=ui.extjs_renderer.action_call(
                    request, a, {}))
        return http.HttpResponse(ui.extjs_renderer.html_page(request, **kw))


class MainHtml(View):

    def get(self, request, *args, **kw):
        #~ logger.info("20130719 MainHtml")
        settings.SITE.startup()
        ui = settings.SITE.ui
        #~ raise Exception("20131023")
        from lino.core import requests
        ar = requests.BaseRequest(request)
        ar.set_response(
            success=True,
            html=settings.SITE.get_main_html(request))
        return ui.render_action_response(ar)


class Authenticate(View):

    """
    This view is being used when
    :setting:`remote_user_header` is empty
    (and :setting:`user_model` not).

    """

    def get(self, request, *args, **kw):
        action_name = request.GET.get(ext_requests.URL_PARAM_ACTION_NAME)
        if action_name == 'logout':
            username = request.session.pop('username', None)
            request.session.pop('password', None)
            #~ username = request.session['username']
            #~ del request.session['password']

            from lino.core import requests
            ar = requests.BaseRequest(request)
            ar.success("User %r logged out." % username)
            return settings.SITE.ui.render_action_response(ar)
        raise http.Http404()

    def post(self, request, *args, **kw):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username, password)
        from lino.core import requests
        ar = requests.BaseRequest(request)
        if user is None:
            ar.error("Could not authenticate %r" % username)
            return settings.SITE.ui.render_action_response(ar)
        request.session['username'] = username
        request.session['password'] = password
        ar.success(("Now logged in as %r" % username))
        return settings.SITE.ui.render_action_response(ar)


class RunJasmine(View):

    """
    """

    def get(self, request, *args, **kw):
        ui = settings.SITE.ui
        return http.HttpResponse(
            ui.extjs_renderer.html_page(request, run_jasmine=True))


class EidAppletService(View):

    """
    """

    def post(self, request, *args, **kw):
        ui = settings.SITE.ui
        return ui.success(html='Hallo?')


class Callbacks(View):

    def get(self, request, thread_id, button_id):
        return settings.SITE.ui.run_callback(request, thread_id, button_id)


#~ if settings.SITE.user_model:
if settings.SITE.user_model and settings.SITE.use_tinymce:

    from jinja2 import Template as JinjaTemplate

    class Templates(View):

        """
        Called by TinyMCE (`template_external_list_url
        <http://www.tinymce.com/wiki.php/configuration:external_template_list_url>`_)
        to fill the list of available templates.

        """
        #~ def templates_view(self,request,

        def get(self, request,
                app_label=None, actor=None,
                pk=None, fldname=None, tplname=None, **kw):

            if request.method == 'GET':

                rpt = requested_actor(app_label, actor)
                elem = rpt.get_row_by_pk(None, pk)
                if elem is None:
                    raise http.Http404("%s %s does not exist." % (rpt, pk))

                TextFieldTemplate = settings.SITE.\
                    modules.system.TextFieldTemplate
                if tplname:
                    tft = TextFieldTemplate.objects.get(pk=int(tplname))
                    if settings.SITE.trusted_templates:
                        #~ return http.HttpResponse(tft.text)
                        template = JinjaTemplate(tft.text)
                        context = dict(request=request,
                                       instance=elem, **settings.SITE.modules)
                        return http.HttpResponse(template.render(**context))
                    else:
                        return http.HttpResponse(tft.text)

                teams = [o.group for o in
                         request.user.users_membership_set_by_user.all()]
                flt = models.Q(team__isnull=True) | models.Q(team__in=teams)
                qs = TextFieldTemplate.objects.filter(flt).order_by('name')

                templates = []
                for obj in qs:
                    url = settings.SITE.build_admin_url(
                        'templates',
                        app_label, actor, pk, fldname, unicode(obj.pk))
                    templates.append([
                        unicode(obj.name), url, unicode(obj.description)])
                js = "var tinyMCETemplateList = %s;" % py2js(templates)
                return http.HttpResponse(js, content_type='text/json')
            raise http.Http404("Method %r not supported" % request.method)


def choices_for_field(request, holder, field):
    # Return the choices for the given field and the given web request
    # (whose requesting holder is given as `holder`).
    # holder is either a Model, an Actor or an Action.
    # model = holder.get_chooser_model()
    chooser = holder.get_chooser_for_field(field.name)
    # logger.info('20140822 choices_for_field(%s.%s) --> %s',
    #             holder, field.name, chooser)
    if chooser:
        qs = chooser.get_request_choices(request, holder)
        if not isiterable(qs):
            raise Exception("%s.%s_choices() returned non-iterable %r" % (
                holder.model, field.name, qs))
        if chooser.simple_values:
            def row2dict(obj, d):
                d[ext_requests.CHOICES_TEXT_FIELD] = unicode(obj)
                d[ext_requests.CHOICES_VALUE_FIELD] = obj
                return d
        elif chooser.instance_values:
            # same code as for ForeignKey
            def row2dict(obj, d):
                d[ext_requests.CHOICES_TEXT_FIELD] = holder.get_choices_text(
                    obj, request, field)
                d[ext_requests.CHOICES_VALUE_FIELD] = obj.pk
                return d
        else:  # values are (value,text) tuples
            def row2dict(obj, d):
                d[ext_requests.CHOICES_TEXT_FIELD] = unicode(obj[1])
                d[ext_requests.CHOICES_VALUE_FIELD] = obj[0]
                return d

    elif field.choices:
        qs = field.choices

        def row2dict(obj, d):
            if type(obj) is list or type(obj) is tuple:
                d[ext_requests.CHOICES_TEXT_FIELD] = unicode(obj[1])
                d[ext_requests.CHOICES_VALUE_FIELD] = obj[0]
            else:
                d[ext_requests.CHOICES_TEXT_FIELD] = holder.get_choices_text(
                    obj, request, field)
                d[ext_requests.CHOICES_VALUE_FIELD] = unicode(obj)
            return d

    elif isinstance(field, models.ForeignKey):
        m = field.rel.to
        t = m.get_default_table()
        qs = t.request(request=request).data_iterator
        # logger.info('20120710 choices_view(FK) %s --> %s', t, qs.query)

        def row2dict(obj, d):
            d[ext_requests.CHOICES_TEXT_FIELD] = holder.get_choices_text(
                obj, request, field)
            d[ext_requests.CHOICES_VALUE_FIELD] = obj.pk
            return d
    else:
        raise http.Http404("No choices for %s" % field)
    return (qs, row2dict)


def choices_response(request, qs, row2dict, emptyValue):
    quick_search = request.GET.get(ext_requests.URL_PARAM_FILTER, None)
    if quick_search is not None:
        qs = dbtables.add_quick_search_filter(qs, quick_search)

    count = len(qs)

    offset = request.GET.get(ext_requests.URL_PARAM_START, None)
    if offset:
        qs = qs[int(offset):]
        #~ kw.update(offset=int(offset))
    limit = request.GET.get(ext_requests.URL_PARAM_LIMIT, None)
    if limit:
        #~ kw.update(limit=int(limit))
        qs = qs[:int(limit)]

    rows = [row2dict(row, {}) for row in qs]
    if emptyValue is not None:  # 20121203
        empty = dict()
        empty[ext_requests.CHOICES_TEXT_FIELD] = emptyValue
        empty[ext_requests.CHOICES_VALUE_FIELD] = None
        rows.insert(0, empty)
    return json_response_kw(count=count, rows=rows)
    #~ return json_response_kw(count=len(rows),rows=rows)
    #~ return json_response_kw(count=len(rows),rows=rows,title=_('Choices for %s') % fldname)


class ActionParamChoices(View):
    # Examples: `welfare.pcsw.CreateCoachingVisit`
    def get(self, request, app_label=None, actor=None, an=None, field=None, **kw):
        actor = requested_actor(app_label, actor)
        ba = actor.get_url_action(an)
        if ba is None:
            raise Exception("Unknown action %r for %s" % (an, actor))
        field = ba.action.get_param_elem(field)
        qs, row2dict = choices_for_field(request, ba.action, field)
        if field.blank:
            emptyValue = '<br/>'
        else:
            emptyValue = None
        return choices_response(request, qs, row2dict, emptyValue)


class Choices(View):

    #~ def choices_view(self,request,app_label=None,rptname=None,fldname=None,**kw):
    def get(self, request, app_label=None, rptname=None, fldname=None, **kw):
        """
        Return a JSON object with two attributes `count` and `rows`,
        where `rows` is a list of `(display_text,value)` tuples.
        Used by ComboBoxes or similar widgets.
        If `fldname` is not specified, returns the choices for
        the `record_selector` widget.
        """
        rpt = requested_actor(app_label, rptname)
        emptyValue = None
        if fldname is None:
            ar = rpt.request(request=request)  # ,rpt.default_action)
            #~ rh = rpt.get_handle(self)
            #~ ar = ViewReportRequest(request,rh,rpt.default_action)
            #~ ar = dbtables.TableRequest(self,rpt,request,rpt.default_action)
            #~ rh = ar.ah
            #~ qs = ar.get_data_iterator()
            qs = ar.data_iterator
            #~ qs = rpt.request(self).get_queryset()

            def row2dict(obj, d):
                d[ext_requests.CHOICES_TEXT_FIELD] = unicode(obj)
                # getattr(obj,'pk')
                d[ext_requests.CHOICES_VALUE_FIELD] = obj.pk
                return d
        else:
            """
            NOTE: if you define a *parameter* with the same name
            as some existing *data element* name, then the parameter
            will override the data element. At least here in choices view.
            """
            #~ field = find_field(rpt.model,fldname)
            field = rpt.get_param_elem(fldname)
            if field is None:
                field = rpt.get_data_elem(fldname)
            if field.blank:
                #~ logger.info("views.Choices: %r is blank",field)
                emptyValue = '<br/>'
            qs, row2dict = choices_for_field(request, rpt, field)

        return choices_response(request, qs, row2dict, emptyValue)


class Restful(View):

    """
    Used to collaborate with a restful Ext.data.Store.
    """

    def post(self, request, app_label=None, actor=None, pk=None):
        rpt = requested_actor(app_label, actor)
        ar = rpt.request(request=request)

        instance = ar.create_instance()
        # store uploaded files.
        # html forms cannot send files with PUT or GET, only with POST
        if ar.actor.handle_uploaded_files is not None:
            ar.actor.handle_uploaded_files(instance, request)

        data = request.POST.get('rows')
        data = json.loads(data)
        ar.form2obj_and_save(data, instance, True)

        # Ext.ensible needs list_fields, not detail_fields
        ar.set_response(
            rows=[ar.ah.store.row2dict(
                ar, instance, ar.ah.store.list_fields)])
        return json_response(ar.response)

    def delete(self, request, app_label=None, actor=None, pk=None):
        rpt = requested_actor(app_label, actor)
        ar = rpt.request(request=request)
        ar.set_selected_pks(pk)
        return delete_element(ar, ar.selected_rows[0])

    def get(self, request, app_label=None, actor=None, pk=None):
        rpt = requested_actor(app_label, actor)
        assert pk is None, 20120814
        ar = rpt.request(request=request)
        rh = ar.ah
        rows = [
            rh.store.row2dict(ar, row, rh.store.list_fields)
            for row in ar.sliced_data_iterator]
        kw = dict(count=ar.get_total_count(), rows=rows)
        kw.update(title=unicode(ar.get_title()))
        return json_response(kw)

    def put(self, request, app_label=None, actor=None, pk=None):
        rpt = requested_actor(app_label, actor)
        ar = rpt.request(request=request)
        ar.set_selected_pks(pk)
        elem = ar.selected_rows[0]
        rh = ar.ah

        data = http.QueryDict(request.body).get('rows')
        data = json.loads(data)
        a = rpt.get_url_action(rpt.default_list_action_name)
        ar = rpt.request(request=request, action=a)
        ar.renderer = settings.SITE.ui.extjs_renderer
        ar.form2obj_and_save(data, elem, False)
        # Ext.ensible needs list_fields, not detail_fields
        ar.set_response(
            rows=[rh.store.row2dict(ar, elem, rh.store.list_fields)])
        return json_response(ar.response)


class ApiElement(View):

    def get(self, request, app_label=None, actor=None, pk=None):
        ui = settings.SITE.ui
        rpt = requested_actor(app_label, actor)

        action_name = request.GET.get(ext_requests.URL_PARAM_ACTION_NAME,
                                      rpt.default_elem_action_name)
        ba = rpt.get_url_action(action_name)
        if ba is None:
            raise http.Http404("%s has no action %r" % (rpt, action_name))

        if pk and pk != '-99999' and pk != '-99998':
            #~ ar = ba.request(request=request,selected_pks=[pk])
            #~ print 20131004, ba.actor
            ar = ba.request(request=request)

            ar.set_selected_pks(pk)
            elem = ar.selected_rows[0]
            if elem is None:
                raise http.Http404(
                    "%s has no row with primary key %r" % (rpt, pk))
        else:
            ar = ba.request(request=request)
            elem = None

        ar.renderer = ui.extjs_renderer
        ah = ar.ah

        fmt = request.GET.get(
            ext_requests.URL_PARAM_FORMAT, ba.action.default_format)

        if ba.action.opens_a_window:

            if fmt == ext_requests.URL_FORMAT_JSON:
                if pk == '-99999':
                    elem = ar.create_instance()
                    datarec = ar.elem2rec_insert(ah, elem)
                elif pk == '-99998':
                    elem = ar.create_instance()
                    datarec = elem2rec_empty(ar, ah, elem)
                else:
                    datarec = ar.elem2rec_detailed(elem)

                return json_response(datarec)

            after_show = ar.get_status(record_id=pk)

            tab = request.GET.get(ext_requests.URL_PARAM_TAB, None)
            if tab is not None:
                tab = int(tab)
                after_show.update(active_tab=tab)

            return http.HttpResponse(
                ui.extjs_renderer.html_page(
                    request, ba.action.label,
                    on_ready=ui.extjs_renderer.action_call(
                        request, ba, after_show)))

        if isinstance(ba.action, actions.RedirectAction):
            target = ba.action.get_target_url(elem)
            if target is None:
                raise http.Http404("%s failed for %r" % (ba, elem))
            return http.HttpResponseRedirect(target)

        if pk == '-99998':
            assert elem is None
            elem = ar.create_instance()
            ar.selected_rows = [elem]

        return settings.SITE.ui.run_action(ar)

    def post(self, request, app_label=None, actor=None, pk=None):
        ar = action_request(
            app_label, actor, request, request.POST, True,
            renderer=settings.SITE.ui.extjs_renderer)
        if pk == '-99998':
            elem = ar.create_instance()
            ar.selected_rows = [elem]
        else:
            ar.set_selected_pks(pk)
        return settings.SITE.ui.run_action(ar)

    def put(self, request, app_label=None, actor=None, pk=None):
        data = http.QueryDict(request.body)  # raw_post_data before Django 1.4
        # logger.info("20141206 %s", data)
        ar = action_request(
            app_label, actor, request, data, False,
            renderer=settings.SITE.ui.extjs_renderer)
        ar.set_selected_pks(pk)
        return settings.SITE.ui.run_action(ar)

    def delete(self, request, app_label=None, actor=None, pk=None):
        data = http.QueryDict(request.body)
        ar = action_request(
            app_label, actor, request, data, False,
            renderer=settings.SITE.ui.extjs_renderer)
        ar.set_selected_pks(pk)
        return settings.SITE.ui.run_action(ar)
        
    def old_delete(self, request, app_label=None, actor=None, pk=None):
        rpt = requested_actor(app_label, actor)
        ar = rpt.request(request=request)
        ar.set_selected_pks(pk)
        elem = ar.selected_rows[0]
        return delete_element(ar, elem)


class ApiList(View):

    def post(self, request, app_label=None, actor=None):
        ar = action_request(app_label, actor, request, request.POST, True)
        ar.renderer = settings.SITE.ui.extjs_renderer
        return settings.SITE.ui.run_action(ar)

    def get(self, request, app_label=None, actor=None):
        ar = action_request(app_label, actor, request, request.GET, True)
        ar.renderer = settings.SITE.ui.extjs_renderer
        rh = ar.ah

        fmt = request.GET.get(
            ext_requests.URL_PARAM_FORMAT,
            ar.bound_action.action.default_format)

        if fmt == ext_requests.URL_FORMAT_JSON:
            rows = [rh.store.row2list(ar, row)
                    for row in ar.sliced_data_iterator]
            total_count = ar.get_total_count()
            for row in ar.create_phantom_rows():
                d = rh.store.row2list(ar, row)
                rows.append(d)
                total_count += 1
            kw = dict(count=total_count,
                      rows=rows,
                      success=True,
                      no_data_text=ar.no_data_text,
                      title=unicode(ar.get_title()))
            if ar.actor.parameters:
                kw.update(
                    param_values=ar.actor.params_layout.params_store.pv2dict(
                        ar.param_values))
            return json_response(kw)

        if fmt == ext_requests.URL_FORMAT_HTML:
            after_show = ar.get_status()

            sp = request.GET.get(
                ext_requests.URL_PARAM_SHOW_PARAMS_PANEL, None)
            if sp is not None:
                #~ after_show.update(show_params_panel=sp)
                after_show.update(
                    show_params_panel=ext_requests.parse_boolean(sp))

            if isinstance(ar.bound_action.action, actions.InsertRow):
                elem = ar.create_instance()
                #~ print 20120630
                #~ print elem.national_id
                rec = ar.elem2rec_insert(rh, elem)
                after_show.update(data_record=rec)

            kw = dict(on_ready=
                      ar.renderer.action_call(
                          ar.request,
                          ar.bound_action, after_show))
            #~ print '20110714 on_ready', params
            kw.update(title=ar.get_title())
            return http.HttpResponse(ar.renderer.html_page(request, **kw))

        if fmt == 'csv':
            #~ response = HttpResponse(mimetype='text/csv')
            charset = settings.SITE.csv_params.get('encoding', 'utf-8')
            response = http.HttpResponse(
                content_type='text/csv;charset="%s"' % charset)
            if False:
                response['Content-Disposition'] = \
                    'attachment; filename="%s.csv"' % ar.actor
            else:
                #~ response = HttpResponse(content_type='application/csv')
                response['Content-Disposition'] = \
                    'inline; filename="%s.csv"' % ar.actor

            #~ response['Content-Disposition'] = 'attachment; filename=%s.csv' % ar.get_base_filename()
            w = ucsv.UnicodeWriter(response, **settings.SITE.csv_params)
            w.writerow(ar.ah.store.column_names())
            if True:  # 20130418 : also column headers, not only internal names
                column_names = None
                fields, headers, cellwidths = ar.get_field_info(column_names)
                w.writerow(headers)

            for row in ar.data_iterator:
                w.writerow([unicode(v) for v in rh.store.row2list(ar, row)])
            return response

        if fmt == ext_requests.URL_FORMAT_PRINTER:
            if ar.get_total_count() > MAX_ROW_COUNT:
                raise Exception(_("List contains more than %d rows") %
                                MAX_ROW_COUNT)
            response = http.HttpResponse(
                content_type='text/html;charset="utf-8"')
            doc = xghtml.Document(force_unicode(ar.get_title()))
            doc.body.append(E.h1(doc.title))
            t = doc.add_table()
            #~ settings.SITE.ui.ar2html(ar,t,ar.data_iterator)
            ar.dump2html(t, ar.data_iterator)
            doc.write(response, encoding='utf-8')
            return response

        return settings.SITE.ui.run_action(ar)
        #~ raise http.Http404("Format %r not supported for GET on %s" % (fmt,ar.actor))


class GridConfig(View):

    def put(self, request, app_label=None, actor=None):
        ui = settings.SITE.ui
        rpt = requested_actor(app_label, actor)
        PUT = http.QueryDict(request.body)  # raw_post_data before Django 1.4
        gc = dict(
            widths=[int(x)
                    for x in PUT.getlist(ext_requests.URL_PARAM_WIDTHS)],
            columns=[str(x)
                     for x in PUT.getlist(ext_requests.URL_PARAM_COLUMNS)],
            hiddens=[(x == 'true')
                     for x in PUT.getlist(ext_requests.URL_PARAM_HIDDENS)],
            #~ hidden_cols=[str(x) for x in PUT.getlist('hidden_cols')],
        )

        filter = PUT.get('filter', None)
        if filter is not None:
            filter = json.loads(filter)
            gc['filters'] = [ext_requests.dict2kw(flt) for flt in filter]

        name = PUT.get('name', None)
        if name is None:
            name = ext_requests.DEFAULT_GC_NAME
        else:
            name = int(name)

        gc.update(label=PUT.get('label', "Standard"))
        try:
            msg = rpt.save_grid_config(name, gc)
        except IOError, e:
            msg = _("Error while saving GC for %(table)s: %(error)s") % dict(
                table=rpt, error=e)
            return settings.SITE.ui.error(None, msg, alert=True)
        #~ logger.info(msg)
        settings.SITE.ui.extjs_renderer.build_site_cache(True)
        return settings.SITE.ui.success(msg)


