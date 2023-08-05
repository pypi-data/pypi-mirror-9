# -*- coding: UTF-8 -*-
# Copyright 2012-2014 Luc Saffre
# License: BSD (see file COPYING for details)

from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext

from lino import dd, rt, mixins
from lino.utils import join_words, join_elems
from lino.utils import mti
from lino.utils.xmlgen.html import E

contacts = dd.resolve_app('contacts')

config = dd.apps.households
mnugrp = dd.apps.contacts


class Type(mixins.BabelNamed):

    """
    Type of a household.
    http://www.belgium.be/fr/famille/couple/cohabitation/
    """
    class Meta:
        verbose_name = _("Household Type")
        verbose_name_plural = _("Household Types")


class Types(dd.Table):
    required = dd.required(user_level='admin')
    model = Type
    detail_layout = """
    name
    HouseholdsByType
    """


class MemberRoles(dd.ChoiceList):
    """The list of allowed choices for the role of a household member.
    """
    verbose_name = _("Role")
    verbose_name_plural = _("Roles")

add = MemberRoles.add_item
add('01', _("Head of household"), 'head')
add('02', _("Spouse"), 'spouse')
add('03', _("Partner"), 'partner')
add('04', _("Cohabitant"), 'cohabitant')
add('05', _("Child"), 'child')
add('07', _("Adopted child"), 'adopted')
add('06', _("Relative"), 'relative')
# add('10', _("Child of head"), 'child_of_head')
# add('11', _("Child of partner"), 'child_of_partner')

parent_roles = (MemberRoles.head, MemberRoles.spouse,
                MemberRoles.partner, MemberRoles.cohabitant)

child_roles = (MemberRoles.child, MemberRoles.adopted)
               # MemberRoles.child_of_head, MemberRoles.child_of_partner)


class Household(contacts.Partner):
    """
    A Household is a Partner who represents several Persons living together.
    A Household has a list of :class:`members <Member>`.
    """
    class Meta:
        abstract = dd.is_abstract_model(__name__, 'Household')
        verbose_name = _("Household")
        verbose_name_plural = _("Households")

    prefix = models.CharField(max_length=200, blank=True)
    type = models.ForeignKey(Type, blank=True, null=True)
    # head = dd.ForeignKey('contacts.Person', verbose_name=_("Chef")),

    #~ dummy = models.CharField(max_length=1,blank=True)
    # workaround for https://code.djangoproject.com/ticket/13864

    def add_member(self, person, role=None):
        mbr = rt.modules.households.Member(
            household=self, person=person, role=role)
        mbr.full_clean()
        mbr.save()
        return mbr

    def members_by_role(self, rolename):
        role = MemberRoles.get_by_name(rolename)
        # return rt.modules.households.Member.objects.filter(
        #     household=self, role=role)
        return self.member_set.filter(role=role)

    def get_full_name(self, salutation=True, **salutation_options):
        """Overrides :meth:`ml.contacts.Partner.get_full_name`."""
        return join_words(self.prefix, self.name)
    full_name = property(get_full_name)

    def __unicode__(self):
        # if self.type:
        #     return u"%s %s" % (self.type, self.get_full_name())
        return unicode(self.get_full_name())

    def get_name_elems(self, ar):
        elems = []
        if self.prefix:
            elems += [self.prefix, ' ']
        elems += [E.b(self.name)]
        return elems

    @classmethod
    def create_household(cls, ar, head, partner, type):
        name = head.last_name
        prefix = head.first_name
        if partner:
            name += '-' + partner.last_name
            prefix += ' & ' + partner.first_name
        hh = cls(type=type, name=name, prefix=prefix)
        hh.full_clean()
        hh.save()
        # TODO: see 20140426
        # hh.add_member(head, Role.objects.get(pk=1))
        if head is not None:
            hh.add_member(head, MemberRoles.head)
        if partner is not None:
            hh.add_member(partner, MemberRoles.partner)
        hh.after_ui_create(ar)
        hh.after_ui_save(ar)
        return hh


class HouseholdDetail(dd.FormLayout):

    main = """
    type name language:10 id
    address_box
    bottom_box
    """

    # intro_box = """
    # """

    box3 = """
    country region
    city zip_code:10
    street_prefix street:25 street_no street_box
    addr2:40
    """

    box4 = """
    phone
    gsm
    email:40
    url
    """

    address_box = "box3 box4"

    bottom_box = "remarks households.MembersByHousehold"


class Households(contacts.Partners):
    model = 'households.Household'
    required = dd.Required(user_groups='office')
    order_by = ["name"]
    detail_layout = HouseholdDetail()


class HouseholdsByType(Households):
    #~ label = _("Households")
    master_key = 'type'
    #~ column_names = 'person role *'


# class Role(mixins.BabelNamed):
#     """
#     The role of a :class:`Member` in a :class:`Household`.
#     """
#     class Meta:
#         verbose_name = _("Household Role")
#         verbose_name_plural = _("Household Roles")

#     name_giving = models.BooleanField(
#         _("name-giving"),
#         default=False,
#         help_text=(
#             "Whether this role is name-giving for its household. "
#             "The name of a Household is computed by joining the "
#             "`Last Name` of all name-giving members with a dash (`-`)."
#         ))


# class Roles(dd.Table):
#     model = Role
#     required = dd.required(user_level='admin')
#     detail_layout = """
#     name name_giving
#     #male
#     #female
#     MembersByRole
#     """


class Member(mixins.DatePeriod):
    """
    The role of a given :class:`Person` in a given :class:`Household`.
    """

    class Meta:
        abstract = dd.is_abstract_model(__name__, 'Member')
        verbose_name = _("Household Member")
        verbose_name_plural = _("Household Members")

    allow_cascaded_delete = 'household'

    role = MemberRoles.field(
        default=MemberRoles.child, blank=True, null=True)
    person = models.ForeignKey(
        config.person_model,
        related_name='household_members')
    household = models.ForeignKey('households.Household')
    primary = models.BooleanField(
        _("Primary"),
        default=False,
        help_text=_(
            "Whether this is the primary household of this person. "
            "Checking this field will automatically disable any "
            "other primary memberships."))

    def after_ui_save(self, ar):
        super(Member, self).after_ui_save(ar)
        mi = self.person
        if mi is None:
            return
        if self.primary:
            for o in mi.household_members.exclude(id=self.id):
                if o.primary:
                    o.primary = False
                    o.save()
                    ar.set_response(refresh_all=True)

    def __unicode__(self):
        if self.person_id is None:
            return super(Member, self).__unicode__()
        if self.role is None:
            return unicode(self.person)
        return u"%s (%s)" % (self.person, self.role)

    def get_address_lines(self):
        for ln in self.person.address_person_lines():
            yield ln
        if self.household:
            for ln in self.household.address_person_lines():
                yield ln
            for ln in self.household.address_location_lines():
                yield ln
        else:
            for ln in self.address_location_lines():
                yield ln

    @dd.action(help_text=_("Make this the primary household."))
    def set_primary(self, ar):
        self.primary = True
        self.full_clean()
        self.save()
        self.after_ui_save(ar)
        ar.success(refresh=True)


class Members(dd.Table):
    model = 'households.Member'
    required = dd.required(user_level='admin')
    order_by = ['start_date', 'end_date']


class MembersByHousehold(Members):
    required = dd.required()
    label = _("Household Members")
    master_key = 'household'
    column_names = 'person role start_date end_date *'


class SiblingsByPerson(Members):
    """
    If the master is member of a single household, display the members
    of that Household. Otherwise display an explanation message.

    """
    label = _("Household composition")
    required = dd.required()
    master = config.person_model
    column_names = 'person role start_date end_date *'
    auto_fit_column_widths = True
    # slave_grid_format = 'summary'
    window_size = (100, 20)

    @classmethod
    def setup_request(self, ar):
        ar.master_household = None
        mi = ar.master_instance  # a Person
        if mi is None:
            return
        M = rt.modules.households.Member
        mbr = M.objects.filter(person=mi)
        if mbr.count() == 1:
            ar.master_household = mbr[0].household
        elif mbr.count() == 0:
            ar.no_data_text = _("%s is not member of any household") % mi
        else:  # more than 1 row
            mbr = mbr.filter(primary=True)
            if mbr.count() == 1:
                ar.master_household = mbr[0].household
            else:
                mbr = M.objects.filter(person=mi)
                mbr = dd.PeriodEvents.active.add_filter(mbr, dd.today())
                if mbr.count() == 1:
                    ar.master_household = mbr[0].household
                else:
                    ar.no_data_text = _(
                        "%s is member of multiple households") % mi

    @classmethod
    def get_filter_kw(self, ar, **kw):
        # hh = self.get_master_household(ar.master_instance)
        hh = ar.master_household
        if hh is None:
            return None
        kw.update(household=hh)
        return super(SiblingsByPerson, self).get_filter_kw(ar, **kw)

    @classmethod
    def get_slave_summary(self, obj, ar):
        # For every child, we want to display its relationship to
        # every parent of this household.
        sar = self.request(master_instance=obj)
        if sar.master_household is None:
            return E.div(ar.no_data_text)
        # obj is the Person for which we display the household

        def format_item(m):
            elems = [unicode(m.role), ': ']
            if m.person:
                elems += [obj.format_family_member(ar, m.person)]
                hl = self.find_links(ar, m.person, obj)
                if len(hl):
                    elems += [' ('] + hl + [')']
            else:
                elems += [obj.format_family_member(ar, m)]
            return elems
            
        items = []
        for m in sar.data_iterator:
            items.append(E.li(*format_item(m)))
        elems = []
        if len(items) > 0:
            elems = []
            elems.append(E.ul(*items))
        return E.div(*elems)

    @classmethod
    def find_links(self, ar, child, parent):
        if not dd.is_installed('humanlinks'):
            return []
        types = {}  # mapping LinkType -> list of parents
        for lnk in rt.modules.humanlinks.Link.objects.filter(child=child):
                # child=child, parent=p):
            tt = lnk.type.as_child(lnk.child)
            l = types.setdefault(tt, [])
            l.append(lnk.parent)
        elems = []
        for tt, parents in types.items():
            if len(elems):
                elems.append(', ')
            text = join_elems(
                [parent.format_family_member(ar, p) for p in parents],
                sep=_(" and "))
            elems += [tt, _(" of ")] + text
        return elems


class CreateHousehold(dd.Action):
    show_in_bbar = False
    custom_handler = True
    label = _("Create Household")
    parameters = dict(
        head=dd.ForeignKey(
            config.person_model, verbose_name=_("Head of household")),
        partner=dd.ForeignKey(
            config.person_model, verbose_name=_("Partner"),
            blank=True, null=True),
        type=dd.ForeignKey('households.Type'))
    params_layout = """
    partner
    type
    head
    """

    def action_param_defaults(self, ar, obj, **kw):
        # logger.info("20140426")
        kw = super(CreateHousehold, self).action_param_defaults(ar, obj, **kw)
        kw.update(head=obj)
        return kw

    def run_from_ui(self, ar, **kw):
        pv = ar.action_param_values
        hh = rt.modules.households.Household.create_household(
            ar, pv.head, pv.partner, pv.type)
        ar.success(
            _("Household has been created"),
            close_window=True, refresh_all=True)
        ar.goto_instance(hh)

dd.inject_action(
    config.person_model,
    create_household=CreateHousehold())


class MembersByPerson(Members):
    required = dd.required()
    label = _("Household memberships")
    master_key = 'person'
    column_names = 'household role primary start_date end_date *'
    # auto_fit_column_widths = True
    # hide_columns = 'id'
    slave_grid_format = 'summary'

    @classmethod
    def get_slave_summary(self, obj, ar):
        sar = self.request(master_instance=obj)
        elems = []
        # n = sar.get_total_count()
        # if n == 0:
        #     elems += [_("Not member of any household."), E.br()]
        # else:

        items = []
        for m in sar.data_iterator:
            
            args = (unicode(m.role), _(" in "),
                    ar.obj2html(m.household))
            if m.primary:
                items.append(E.li(E.b("\u2611 ", *args)))
            else:
                btn = m.set_primary.as_button_elem(
                    ar, "\u2610 ", style="text-decoration:none;")
                items.append(E.li(btn, *args))
        if len(items) > 0:
            elems += [_("%s is") % obj]
            elems.append(E.ul(*items))
        if False:
            elems += [
                E.br(), ar.instance_action_button(obj.create_household)]
        else:
            elems += [E.br(), _("Create a household"), ' : ']
            Type = rt.modules.households.Type
            Person = dd.resolve_model(config.person_model)
            T = Person.get_default_table()
            ba = T.get_action_by_name('create_household')
            buttons = []
            for t in Type.objects.all():
                apv = dict(type=t, head=obj)
                sar = ar.spawn(ba,  # master_instance=obj,
                               action_param_values=apv)
                buttons.append(ar.href_to_request(sar, unicode(t)))
            elems += join_elems(buttons, sep=' / ')
        return E.div(*elems)


# class MembersByRole(Members):
#     required = dd.required()
#     master_key = 'role'
#     column_names = 'person household start_date end_date *'


dd.inject_field(
    'contacts.Partner',
    'is_household',
    mti.EnableChild(
        'households.Household',
        verbose_name=_("is Household"),
        help_text=("Whether this Partner is a Household.")))


def setup_main_menu(site, ui, profile, m):
    m = m.add_menu(mnugrp.app_label, mnugrp.verbose_name)
    m.add_action('households.Households')


def setup_config_menu(site, ui, profile, m):
    m = m.add_menu(mnugrp.app_label, mnugrp.verbose_name)
    # m.add_action(Roles)
    m.add_action('households.Types')


def setup_explorer_menu(site, ui, profile, m):
    m = m.add_menu(mnugrp.app_label, mnugrp.verbose_name)
    m.add_action('households.MemberRoles')
    m.add_action('households.Members')
