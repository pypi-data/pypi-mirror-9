# -*- coding: UTF-8 -*-
logger.info("Loading 14 objects to table households_household...")
# fields: partner_ptr, prefix, type
loader.save(create_households_household(181,u'J\xe9r\xf4me & Lisa',1))
loader.save(create_households_household(182,u'Denis & Marie-Louise',2))
loader.save(create_households_household(183,u'Robin & Erna',3))
loader.save(create_households_household(184,u'Karl & \xd5ie',4))
loader.save(create_households_household(185,u'Bernd & Inge',5))
loader.save(create_households_household(186,u'Robin & Hedi',6))
loader.save(create_households_household(203,u'Hubert & Gaby',1))
loader.save(create_households_household(204,u'Paul & Paula',2))
loader.save(create_households_household(205,u'Paul & Petra',1))
loader.save(create_households_household(206,u'Ludwig & Laura',1))
loader.save(create_households_household(219,u'Albert & Eveline',1))
loader.save(create_households_household(220,u'Albert & Fran\xe7oise',2))
loader.save(create_households_household(221,u'Bruno & Eveline',2))
loader.save(create_households_household(222,u'Bruno & Fran\xe7oise',1))

loader.flush_deferred_objects()
