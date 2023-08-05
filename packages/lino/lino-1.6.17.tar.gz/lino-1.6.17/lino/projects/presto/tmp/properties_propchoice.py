# -*- coding: UTF-8 -*-
logger.info("Loading 2 objects to table properties_propchoice...")
# fields: id, type, value, text
loader.save(create_properties_propchoice(1,3,u'1',[u'Furniture', u'M\xf6bel', u'Meubles', u'']))
loader.save(create_properties_propchoice(2,3,u'2',[u'Web hosting', u'Hosting', u'Hosting', u'']))

loader.flush_deferred_objects()
