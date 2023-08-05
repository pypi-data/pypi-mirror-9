# -*- coding: UTF-8 -*-
logger.info("Loading 1 objects to table accounts_chart...")
# fields: id, name
loader.save(create_accounts_chart(1,[u'Minimal Accounts Chart', u'Reduzierter Kontenplan', u'Plan comptable r\xe9duit', u'Minimaalne kontoplaan']))

loader.flush_deferred_objects()
