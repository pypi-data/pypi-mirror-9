# -*- coding: UTF-8 -*-
logger.info("Loading 6 objects to table ledger_journal...")
# fields: id, build_method, template, seqno, name, ref, trade_type, voucher_type, force_sequence, chart, account, printed_name, dc
loader.save(create_ledger_journal(1,None,u'',1,[u'Sales invoices', u'Verkaufsrechnungen', u'Factures vente', u'M\xfc\xfcgiarved'],u'S',u'S',u'sales.Invoice',False,1,None,[u'', u'', u'', u''],False))
loader.save(create_ledger_journal(2,None,u'',2,[u'Purchase invoices', u'Einkaufsrechnungen', u'Factures achat', u'Ostuarved'],u'P',u'P',u'ledger.AccountInvoice',False,1,None,[u'', u'', u'', u''],True))
loader.save(create_ledger_journal(3,None,u'',3,[u'Bestbank', u'', u'', u''],u'B',None,u'finan.BankStatement',False,1,5,[u'', u'', u'', u''],True))
loader.save(create_ledger_journal(4,None,u'',4,[u'Payment Orders', u'Zahlungsauftr\xe4ge', u'Ordres de paiement', u'Maksekorraldused'],u'PO',u'P',u'finan.PaymentOrder',False,1,7,[u'', u'', u'', u''],True))
loader.save(create_ledger_journal(5,None,u'',5,[u'Cash', u'Kasse', u'Caisse', u'Kassa'],u'C',None,u'finan.BankStatement',False,1,6,[u'', u'', u'', u''],True))
loader.save(create_ledger_journal(6,None,u'',6,[u'Miscellaneous Journal Entries', u'Diverse Buchungen', u'Op\xe9rations diverses', u'Muud operatsioonid'],u'M',None,u'finan.JournalEntry',False,1,None,[u'', u'', u'', u''],True))

loader.flush_deferred_objects()
