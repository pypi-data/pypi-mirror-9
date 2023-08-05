# -*- coding: UTF-8 -*-
logger.info("Loading 7 objects to table accounts_group...")
# fields: id, name, chart, ref, account_type
loader.save(create_accounts_group(1,[u'Capital', u'Kapital', u'Capital', u'Kapitaal'],1,u'10',u'C'))
loader.save(create_accounts_group(2,[u'Commercial receivable(?)', u'Forderungen aus Lieferungen und Leistungen', u'Cr\xe9ances commerciales', u'Commercial receivable(?)'],1,u'40',u'A'))
loader.save(create_accounts_group(3,[u'VAT to pay', u'Geschuldete MWSt', u'TVA \xe0 payer', u'K\xe4ibemaksukonto'],1,u'45',u'A'))
loader.save(create_accounts_group(4,[u'Banks', u'Finanzinstitute', u'Institutions financi\xe8res', u'Banks'],1,u'55',u'A'))
loader.save(create_accounts_group(5,[u'Running transactions', u'Laufende Transaktionen', u'Transactions en cours', u'Running transactions'],1,u'58',u'A'))
loader.save(create_accounts_group(6,[u'Expenses', u'Aufwendungen', u'Charges', u'Kulud'],1,u'6',u'E'))
loader.save(create_accounts_group(7,[u'Revenues', u'Ertr\xe4ge', u'Produits', u'Tulud'],1,u'7',u'I'))

loader.flush_deferred_objects()
