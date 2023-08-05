# -*- coding: UTF-8 -*-
logger.info("Loading 3 objects to table properties_proptype...")
# fields: id, name, choicelist, default_value, limit_to_choices, multiple_choices
loader.save(create_properties_proptype(1,[u'Present or not', u'Vorhanden oder nicht', u'Pr\xe9sent ou pas', u'Olemas v\xf5i mitte'],u'',u'',False,False))
loader.save(create_properties_proptype(2,[u'Rating', u'Bewertung', u'Appr\xe9ciation(?)', u'Hinnang'],u'properties.HowWell',u'2',False,False))
loader.save(create_properties_proptype(3,[u'Division', u'Abteilung', u'Division', u''],u'',u'',False,False))

loader.flush_deferred_objects()
