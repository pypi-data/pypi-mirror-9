# -*- coding: UTF-8 -*-
logger.info("Loading 6 objects to table households_type...")
# fields: id, name
loader.save(create_households_type(1,[u'Married', u'Ehepartner', u'Mari\xe9', u'Married']))
loader.save(create_households_type(2,[u'Divorced', u'Geschieden', u'Divorc\xe9', u'Divorced']))
loader.save(create_households_type(3,[u'Factual household', u'Faktischer Haushalt', u'Cohabitation de fait', u'Factual household']))
loader.save(create_households_type(4,[u'Legal cohabitation', u'Legale Wohngemeinschaft', u'Cohabitation l\xe9gale', u'Legal cohabitation']))
loader.save(create_households_type(5,[u'Isolated', u'Getrennt', u'Isol\xe9', u'Isolated']))
loader.save(create_households_type(6,[u'Other', u'Sonstige', u'Autre', u'Other']))

loader.flush_deferred_objects()
