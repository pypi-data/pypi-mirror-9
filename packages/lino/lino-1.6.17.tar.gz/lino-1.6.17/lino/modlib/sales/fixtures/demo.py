# -*- coding: UTF-8 -*-
# Copyright 2009-2014 Luc Saffre
# This file is part of the Lino project.
# Lino is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
# Lino is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# You should have received a copy of the GNU Lesser General Public License
# along with Lino ; if not, see <http://www.gnu.org/licenses/>.
"""Generates 20 fictive sales invoices, distributed over more than
one month.

"""
from __future__ import unicode_literals

from django.conf import settings
from lino.utils import Cycler
from lino import dd

vat = dd.resolve_app('vat')
sales = dd.resolve_app('sales')
ledger = dd.resolve_app('ledger')
products = dd.resolve_app('products')

partner_model = settings.SITE.partners_app_label + '.Partner'
Partner = dd.resolve_model(partner_model)

#~ REQUEST = None
REQUEST = settings.SITE.login()


def objects():

    if False:
        yield sales.InvoicingMode(
            **dd.babel_values(
                'name',
                en='Default', de="Standard", fr="Standard"))

    if ledger:
        Invoice = dd.resolve_model('sales.Invoice')
        InvoiceItem = dd.resolve_model('sales.InvoiceItem')
        vt = ledger.VoucherTypes.get_for_model(Invoice)
        JOURNALS = Cycler(vt.get_journals())
        if len(JOURNALS.items) == 0:
            raise Exception("20140127 no journals for %s" % vt)
        PARTNERS = Cycler(Partner.objects.all())
        USERS = Cycler(settings.SITE.user_model.objects.all())
        PRODUCTS = Cycler(products.Product.objects.all())
        ITEMCOUNT = Cycler(1, 2, 3)
        for i in range(20):
            jnl = JOURNALS.pop()
            invoice = Invoice(
                journal=jnl,
                partner=PARTNERS.pop(),
                user=USERS.pop(),
                date=settings.SITE.demo_date(-30 + 2 * i))
            yield invoice
            for j in range(ITEMCOUNT.pop()):
                item = InvoiceItem(voucher=invoice,
                                   #~ account=jnl.get_allowed_accounts()[0],
                                   product=PRODUCTS.pop(),
                                   )
                item.product_changed(REQUEST)
                item.before_ui_save(REQUEST)
                #~ if item.total_incl:
                    #~ print "20121208 ok", item
                #~ else:
                    #~ if item.product.price:
                        #~ raise Exception("20121208")
                yield item
            invoice.register(REQUEST)
            invoice.save()

    #~ sales.Invoice
