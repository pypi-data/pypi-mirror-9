# -*- coding: UTF-8 -*-
logger.info("Loading 13 objects to table sepa_account...")
# fields: id, iban, bic, partner, remark, primary
loader.save(create_sepa_account(1,u'EE872200221012067904',u'HABAEE2X',223,u'',False))
loader.save(create_sepa_account(2,u'EE732200221045112758',u'HABAEE2X',224,u'',False))
loader.save(create_sepa_account(3,u'EE232200001180005555',u'HABAEE2X',225,u'Eraklilendile',False))
loader.save(create_sepa_account(4,u'EE322200221112223334',u'HABAEE2X',225,u'\xc4rikliendile',False))
loader.save(create_sepa_account(5,u'EE081010002059413005',u'EEUHEE2X',225,u'',False))
loader.save(create_sepa_account(6,u'EE703300332099000006',u'FOREEE2X',225,u'',False))
loader.save(create_sepa_account(7,u'EE431700017000115797',u'NDEAEE2X',225,u'',False))
loader.save(create_sepa_account(8,u'EE382200221013987931',u'HABAEE2X',226,u'',False))
loader.save(create_sepa_account(9,u'EE522200221013264447',u'HABAEE2X',227,u'',False))
loader.save(create_sepa_account(10,u'EE202200221001178338',u'HABAEE2X',228,u'',False))
loader.save(create_sepa_account(11,u'BE46000325448336',u'BPOTBEB1',229,u'',False))
loader.save(create_sepa_account(12,u'BE81000325873924',u'BPOTBEB1',229,u'',False))
loader.save(create_sepa_account(13,u'BE79827081803833',u'ETHIBEBB',230,u'',False))

loader.flush_deferred_objects()
