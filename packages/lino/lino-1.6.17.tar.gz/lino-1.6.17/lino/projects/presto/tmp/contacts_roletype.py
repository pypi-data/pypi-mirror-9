# -*- coding: UTF-8 -*-
logger.info("Loading 5 objects to table contacts_roletype...")
# fields: id, name
loader.save(create_contacts_roletype(1,[u'Manager', u'Gesch\xe4ftsf\xfchrer', u'G\xe9rant', u'Tegevjuht']))
loader.save(create_contacts_roletype(2,[u'Director', u'Direktor', u'Directeur', u'Direktor']))
loader.save(create_contacts_roletype(3,[u'Secretary', u'Sekret\xe4r', u'Secr\xe9taire', u'Sekret\xe4r']))
loader.save(create_contacts_roletype(4,[u'IT Manager', u'EDV-Manager', u'G\xe9rant informatique', u'IT manager']))
loader.save(create_contacts_roletype(5,[u'President', u'Pr\xe4sident', u'Pr\xe9sident', u'President']))

loader.flush_deferred_objects()
