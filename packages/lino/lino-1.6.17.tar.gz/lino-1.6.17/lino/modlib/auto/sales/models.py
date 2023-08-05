# -*- coding: UTF-8 -*-
# Copyright 2013-2014 Luc Saffre
# License: BSD (see file COPYING for details)

"See :mod:`ml.sales`."

from __future__ import unicode_literals


import logging
logger = logging.getLogger(__name__)

import datetime

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import string_concat

from django.contrib.contenttypes.models import ContentType

from decimal import Decimal

ZERO = Decimal()

from lino import dd, rt
from lino.utils import AttrDict
from lino.utils.xmlgen.html import E

from lino.mixins.printable import BuildMethods

from lino.core import dbtables

contacts = dd.resolve_app('contacts')


from lino.modlib.sales.models import *


class InvoicingMode(mixins.PrintableType, mixins.BabelNamed):

    "See :class:``"
    class Meta:
        verbose_name = _("Invoicing Mode")
        verbose_name_plural = _("Invoicing Modes")
    #~ id = models.CharField(max_length=3, primary_key=True)
    #~ journal = journals.JournalRef()
    price = dd.PriceField(blank=True, null=True, help_text=_("""\
Additional fee charged when using this invoicing mode."""))
    #~ channel = Channel.field(help_text="""
        #~ Method used to send the invoice.""")
    #~ channel = models.CharField(max_length=1,
                #~ choices=CHANNEL_CHOICES,help_text="""
    #~ Method used to send the invoice.
                #~ """)
    advance_days = models.IntegerField(
        default=0,
        help_text="""
How many days in advance invoices should be posted so that the customer
has a chance to pay them in time.""")

    #~ def __unicode__(self):
        #~ return unicode(dd.babelattr(self,'name'))


class InvoicingModes(dd.Table):
    model = InvoicingMode


class Invoiceable(dd.Model):

    "See :class:`ml.sales.Invoiceable`."

    invoiceable_date_field = ''

    class Meta:
        abstract = True

    invoice = dd.ForeignKey('sales.Invoice',
                            blank=True, null=True)

    @classmethod
    def get_partner_filter(cls, partner):
        raise NotImplementedError()

    def get_invoiceable_product(self):
        return None

    def get_invoiceable_qty(self):
        return None

    def get_invoiceable_title(self):
        return unicode(self)

    def get_invoiceable_amount(self):
        return None

    @classmethod
    def get_invoiceables_for(cls, partner, max_date=None):
        if settings.SITE.site_config.site_company:
            if partner.id == settings.SITE.site_config.site_company.id:
                return
        #~ logger.info('20130711 get_invoiceables_for (%s,%s)', partner, max_date)
        for m in rt.models_by_base(cls):
            flt = m.get_partner_filter(partner)
            qs = m.objects.filter(flt)
            for obj in qs.order_by(m.invoiceable_date_field):
                if obj.get_invoiceable_product() is not None:
                    yield obj


def create_invoice_for(obj, ar):
    invoiceables = list(Invoiceable.get_invoiceables_for(obj))
    if len(invoiceables) == 0:
        raise Warning(_("No invoiceables found for %s.") % obj)
    jnl = Invoice.get_journals()[0]
    invoice = Invoice(partner=obj, journal=jnl, date=settings.SITE.today())
    invoice.save()
    for ii in invoiceables:
        i = InvoiceItem(voucher=invoice, invoiceable=ii,
                        product=ii.get_invoiceable_product(),
                        title=ii.get_invoiceable_title(),
                        qty=ii.get_invoiceable_qty())
        #~ i.product_changed(ar)
        am = ii.get_invoiceable_amount()
        if am is not None:
            i.set_amount(ar, am)
        i.full_clean()
        i.save()
    invoice.compute_totals()
    invoice.save()
    return invoice


class CreateInvoice(dd.Action):
    "See :class:`ml.sales.CreateInvoice`."
    icon_name = 'money'
    sort_index = 50
    label = _("Create invoice")

    def get_partners(self, ar):
        return [o.partner for o in ar.selected_rows]

    def run_from_ui(self, ar, **kw):
        partners = list(self.get_partners(ar))
        if len(partners) > 1:
            rv = []

            def ok(ar2):
                for obj in partners:
                    invoice = create_invoice_for(obj, ar)
                    rv.append(invoice)
                ar2.success(_("%d invoices have been created.") % len(rv))
                return rv
            msg = _("This will create %d invoices.") % len(partners)
            ar.confirm(ok, msg, _("Are you sure?"))
            return

        if len(partners) == 1:
            obj = partners[0]
            invoice = create_invoice_for(obj, ar)
            ar.goto_instance(invoice, **kw)

        return


class CreateInvoiceForPartner(CreateInvoice):
    help_text = _("Create invoice from invoiceables for this partner")

    def get_partners(self, ar):
        return ar.selected_rows


#~ dd.inject_action('contacts.Partner','create_invoice',CreateInvoiceForPartner())
contacts.Partner.create_invoice = CreateInvoiceForPartner()


class Invoice(Invoice):  # 20130709

    #~ fill_invoice = FillInvoice()

    class Meta(Invoice.Meta):  # 20130709
        #~ app_label = 'sales'
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")

    def before_state_change(self, ar, old, new):
        if new.name == 'registered':
            for i in self.items.filter(invoiceable_id__isnull=False):
                if i.invoiceable.invoice != self:
                    i.invoiceable.invoice = self
                    i.invoiceable.save()
                    #~ logger.info("20130711 %s now invoiced",i.invoiceable)
        elif new.name == 'draft':
            for i in self.items.filter(invoiceable_id__isnull=False):
                if i.invoiceable.invoice != self:
                    logger.warning(
                        "Oops: i.invoiceable.invoice != self in %s", self)
                i.invoiceable.invoice = None
                i.invoiceable.save()
            #~ self.deregister_voucher(ar)
        super(Invoice, self).before_state_change(ar, old, new)

    def get_invoiceables(self, model):
        lst = []
        for i in self.items.all():
            if isinstance(i.invoiceable, model):
                if not i.invoiceable in lst:
                    lst.append(i.invoiceable)
            #~ else:
                #~ print 20130910, i.invoiceable.__class__
        return lst

    def get_build_method(self):
        return BuildMethods.appypdf  # must be appypdf for print_multiple


class InvoiceItem(InvoiceItem):  # 20130709

    invoiceable_label = _("Invoiceable")

    class Meta(InvoiceItem.Meta):  # 20130709
        #~ app_label = 'sales'
        verbose_name = _("Voucher item")
        verbose_name_plural = _("Voucher items")

    invoiceable_type = dd.ForeignKey(
        ContentType,
        editable=False, blank=True, null=True,
        verbose_name=string_concat(invoiceable_label, ' ', _('(type)')))
    invoiceable_id = dd.GenericForeignKeyIdField(
        invoiceable_type,
        editable=False, blank=True, null=True,
        verbose_name=string_concat(invoiceable_label, ' ', _('(object)')))
    invoiceable = dd.GenericForeignKey(
        'invoiceable_type', 'invoiceable_id',
        verbose_name=invoiceable_label)

    #~ def product_changed(self,ar):
        #~ super(InvoiceItem,self).product_changed(ar)
        #~ if self.invoiceable:
            #~ self.title = self.invoiceable.get_invoiceable_title()


class ItemsByInvoice(ItemsByInvoice):  # 20130709
    # ~ app_label = 'sales' # we want to "override" the original table

    column_names = "invoiceable product title description:20x1 discount unit_price qty total_incl total_base total_vat"



class InvoicingsByInvoiceable(InvoiceItemsByProduct):  # 20130709
    label = _("Invoicings")
    #~ app_label = 'sales'
    master_key = 'invoiceable'
    editable = False
    column_names = "voucher qty title description:20x1 discount unit_price total_incl total_base total_vat"


class CreateAllInvoices(mixins.CachedPrintAction):
    #~ icon_name = 'money'

    #~ label = _("Create invoices")
    help_text = _(
        "Create and print the invoice for each selected row, making these rows disappear from this table")

    def run_from_ui(self, ar, **kw):
        #~ obj = ar.selected_rows[0]
        #~ assert obj is None
        def ok(ar2):
            invoices = []
            for row in ar.selected_rows:
                partner = contacts.Partner.objects.get(pk=row.pk)
                invoice = create_invoice_for(partner, ar)
                invoices.append(invoice)
            #~ for obj in ar:
                #~ invoice = create_invoice_for(obj.partner,ar)
                #~ invoices.append(invoice)
            mf = self.print_multiple(ar, invoices)
            ar2.success(open_url=mf.url, refresh_all=True)

        #~ msg = _("This will create and print %d invoices.") % ar.get_total_count()
        msg = _("This will create and print %d invoice(s).") % len(
            ar.selected_rows)
        return ar.confirm(ok, msg, _("Are you sure?"))


min_amount = Decimal()


class InvoicesToCreate(dd.VirtualTable):
    label = _("Invoices to create")
    cell_edit = False
    help_text = _("Table of all partners who should receive an invoice.")
    issue_invoice = CreateInvoice()
    column_names = "first_date last_date partner amount action_buttons"
    create_all_invoices = CreateAllInvoices()

    @classmethod
    def get_data_rows(self, ar):
        qs = contacts.Partner.objects.all()
        if ar.quick_search is not None:
            qs = dbtables.add_quick_search_filter(qs, ar.quick_search)
        if ar.gridfilters is not None:
            qs = dbtables.add_gridfilters(qs, ar.gridfilters)

        rows = []
        for p in qs:
            row = self.get_row_for(p)
            if row.amount >= min_amount and row.first_date is not None:
                rows.append(row)

        def f(a, b):
            return cmp(a.first_date, b.first_date)
        rows.sort(f)
        return rows

    @classmethod
    def get_row_for(self, partner):
        invoiceables = list(Invoiceable.get_invoiceables_for(partner))
        amount = Decimal()
        first_date = last_date = None
        for i in invoiceables:
            am = i.get_invoiceable_amount()
            if am is not None:
                amount += am
            d = getattr(i, i.invoiceable_date_field)
            if d is not None:
                if first_date is None or d < first_date:
                    first_date = d
                if last_date is None or d > last_date:
                    last_date = d
        return AttrDict(
            id=partner.id,
            pk=partner.pk,
            first_date=first_date,
            last_date=last_date,
            partner=partner,
            amount=amount,
            invoiceables=invoiceables)

    @classmethod
    def get_pk_field(self):
        #~ print 20130831,repr(contacts.Partner._meta.pk)
        return contacts.Partner._meta.pk

    @classmethod
    def get_row_by_pk(self, ar, pk):
        partner = contacts.Partner.objects.get(pk=pk)
        return self.get_row_for(partner)

    @dd.virtualfield(models.DateField(_("First date")))
    def first_date(self, row, ar):
        return row.first_date

    @dd.virtualfield(models.DateField(_("Last date")))
    def last_date(self, row, ar):
        return row.last_date

    @dd.virtualfield(dd.PriceField(_("Amount")))
    def amount(self, row, ar):
        return row.amount

    @dd.virtualfield(models.ForeignKey('contacts.Partner'))
    def partner(self, row, ar):
        return row.partner

    @dd.displayfield(_("Invoiceables"))
    def unused_invoiceables(self, row, ar):
        items = []
        for i in row.invoiceables:
            items += [ar.obj2html(i), ' ']
        return E.p(*items)

    @dd.displayfield(_("Actions"))
    def action_buttons(self, obj, ar):
        # must override because the action is on obj.partner, not on obj
        return obj.partner.show_invoiceables.as_button(ar)
        #~ return obj.partner.create_invoice.as_button(ar)


class InvoiceablesByPartner(dd.VirtualTable):
    icon_name = 'basket'
    sort_index = 50
    label = _("Invoices to create")
    #~ label = _("Invoiceables")
    help_text = _("List of invoiceable items for this partner")

    #~ app_label = 'sales'
    master = 'contacts.Partner'
    column_names = 'date info'

    @classmethod
    def get_data_rows(self, ar):
        rows = []
        mi = ar.master_instance
        if mi is None:
            return rows
        for obj in Invoiceable.get_invoiceables_for(mi):
            rows.append((getattr(obj, obj.invoiceable_date_field), obj))

        def f(a, b):
            return cmp(a[0], b[0])
        rows.sort(f)
        return rows

    @dd.virtualfield(models.DateField(_("Date")))
    def date(self, row, ar):
        return row[0]

    @dd.displayfield(_("Invoiceable"))
    def info(self, row, ar):
        return ar.obj2html(row[1])

contacts.Partner.show_invoiceables = dd.ShowSlaveTable(InvoiceablesByPartner)


#~ f = setup_main_menu
def setup_main_menu(site, ui, profile, m):
    #~ f(site,ui,profile,m)
    m = m.add_menu("sales", MODULE_LABEL)
    #~ m.add_action('sales.InvoiceablePartners')
    m.add_action('sales.InvoicesToCreate')
