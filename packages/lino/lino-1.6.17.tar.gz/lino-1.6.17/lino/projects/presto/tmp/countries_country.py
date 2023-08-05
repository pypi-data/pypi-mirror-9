# -*- coding: UTF-8 -*-
logger.info("Loading 8 objects to table countries_country...")
# fields: name, isocode, short_code, iso3
loader.save(create_countries_country([u'Estonia', u'Estland', u'Estonie', u'Eesti'],u'EE',u'',u''))
loader.save(create_countries_country([u'Belgium', u'Belgien', u'Belgique', u'Belgia'],u'BE',u'',u''))
loader.save(create_countries_country([u'Germany', u'Deutschland', u'Allemagne', u'Saksamaa'],u'DE',u'',u''))
loader.save(create_countries_country([u'France', u'Frankreich', u'France', u'France'],u'FR',u'',u''))
loader.save(create_countries_country([u'Netherlands', u'Niederlande', u'Pays-Bas', u'Netherlands'],u'NL',u'',u''))
loader.save(create_countries_country([u'Maroc', u'Marokko', u'Maroc', u'Maroc'],u'MA',u'',u''))
loader.save(create_countries_country([u'Russia', u'Russland', u'Russie', u'Russia'],u'RU',u'',u''))
loader.save(create_countries_country([u'Congo (Democratic Republic)', u'Kongo (Demokratische Republik)', u'Congo (R\xe9publique democratique)', u'Congo (Democratic Republic)'],u'CD',u'',u''))

loader.flush_deferred_objects()
