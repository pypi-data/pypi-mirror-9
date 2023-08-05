# -*- coding: UTF-8 -*-
logger.info("Loading 4 objects to table users_user...")
# fields: id, modified, created, username, password, profile, initials, first_name, last_name, email, remarks, language, partner, access_class, event_type
loader.save(create_users_user(3,dt(2015,1,7,8,30,35),dt(2015,1,7,8,30,33),u'romain',u'pbkdf2_sha256$12000$a1uKVJ4NTrE1$HgR1xlrPDlkZctQ0dD3s6+roRK76UBMYCG8AgUybp9I=','900',u'RR',u'Romain',u'Raffault',u'luc.saffre@gmx.net',u'',u'fr',None,u'30',None))
loader.save(create_users_user(2,dt(2015,1,7,8,30,35),dt(2015,1,7,8,30,33),u'rolf',u'pbkdf2_sha256$12000$UlSzuxaF4ORj$lV2aSic8VZVFMSEWjBX1DpjqXaiGGeP30SRhbi3EmPE=','900',u'RR',u'Rolf',u'Rompen',u'luc.saffre@gmx.net',u'',u'de',None,u'30',None))
loader.save(create_users_user(1,dt(2015,1,7,8,30,35),dt(2015,1,7,8,30,33),u'robin',u'pbkdf2_sha256$12000$7PNJ0vHubEOc$sikwUm/9yigmCtE2ZCFCZrx634fcvgUjIw8iQda+d3c=','900',u'RR',u'Robin',u'Rood',u'luc.saffre@gmx.net',u'',u'en',None,u'30',None))
loader.save(create_users_user(4,dt(2015,1,7,8,30,35),dt(2015,1,7,8,30,33),u'rando',u'pbkdf2_sha256$12000$dCAUCSvdv99a$svJFh724BwsIZAT5vEKuMaYXSVZiaz+tT2FjNst4uj4=','900',u'RR',u'Rando',u'Roosi',u'luc.saffre@gmx.net',u'',u'et',None,u'30',None))

loader.flush_deferred_objects()
