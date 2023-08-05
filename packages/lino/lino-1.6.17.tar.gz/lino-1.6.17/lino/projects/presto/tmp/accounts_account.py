# -*- coding: UTF-8 -*-
logger.info("Loading 12 objects to table accounts_account...")
# fields: id, seqno, name, chart, group, ref, type, sales_allowed, purchases_allowed, wages_allowed, clearings_allowed, clearable
loader.save(create_accounts_account(5,5,[u'Bestbank', u'Bestbank', u'Bestbank', u'Parimpank'],1,4,u'bestbank',u'A',False,False,False,False,False))
loader.save(create_accounts_account(7,7,[u'Payment Orders Bestbank', u'Zahlungsauftr\xe4ge Bestbank', u'Ordres de paiement Bestbank', u'Maksekorraldused Parimpank'],1,5,u'bestbankpo',u'A',False,False,False,False,True))
loader.save(create_accounts_account(6,6,[u'Cash', u'Kasse', u'Caisse', u'Sularaha'],1,4,u'cash',u'A',False,False,False,False,False))
loader.save(create_accounts_account(1,1,[u'Customers', u'Kunden', u'Clients', u'Kliendid'],1,2,u'customers',u'A',False,False,False,False,True))
loader.save(create_accounts_account(9,9,[u'Purchase of goods', u'Wareneink\xe4ufe', u'Achat de marchandise', u'Varade soetamine'],1,6,u'goods',u'E',False,True,False,False,False))
loader.save(create_accounts_account(11,11,[u'Purchase of investments', u'Anlagen', u'Investissements', u'Investeeringud'],1,6,u'investments',u'E',False,True,False,False,False))
loader.save(create_accounts_account(12,12,[u'Sales', u'Verk\xe4ufe', u'Ventes', u'M\xfc\xfck'],1,7,u'sales',u'I',True,False,False,False,False))
loader.save(create_accounts_account(10,10,[u'Purchase of services', u'Dienstleistungen', u'Services et biens divers', u'Teenuste soetamine'],1,6,u'services',u'E',False,True,False,False,False))
loader.save(create_accounts_account(2,2,[u'Suppliers', u'Lieferanten', u'Fournisseurs', u'Hankijad'],1,2,u'suppliers',u'A',False,False,False,False,True))
loader.save(create_accounts_account(4,4,[u'VAT deductible', u'Abziehbare MWSt', u'TVA d\xe9ductible', u'Enammakstud k\xe4ibemaks'],1,3,u'vat_deductible',u'A',False,False,False,False,True))
loader.save(create_accounts_account(3,3,[u'VAT due', u'Geschuldete MWSt', u'TVA due', u'K\xe4ibemaks maksta'],1,3,u'vat_due',u'A',False,False,False,False,True))
loader.save(create_accounts_account(8,8,[u'VAT to declare', u'MWSt zu deklarieren', u'TVA \xe0 declarer', u'K\xe4ibemaks deklareerimata'],1,5,u'vatdcl',u'A',False,False,False,False,False))

loader.flush_deferred_objects()
