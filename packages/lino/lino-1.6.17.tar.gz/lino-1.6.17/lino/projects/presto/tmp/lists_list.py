# -*- coding: UTF-8 -*-
logger.info("Loading 8 objects to table lists_list...")
# fields: id, ref, name, list_type, remarks
loader.save(create_lists_list(1,None,[u'Announcements', u'Announcements', u'Announcements', u'Kuulutused'],1,u''))
loader.save(create_lists_list(2,None,[u'Weekly newsletter', u'Weekly newsletter', u'Weekly newsletter', u'N\xe4daline infokiri'],1,u''))
loader.save(create_lists_list(3,None,[u'General discussion', u'General discussion', u'General discussion', u'\xdcldine arutelu'],2,u''))
loader.save(create_lists_list(4,None,[u'Beginners forum', u'Beginners forum', u'Beginners forum', u'Algajate foorum'],2,u''))
loader.save(create_lists_list(5,None,[u'Developers forum', u'Developers forum', u'Developers forum', u'Developers forum'],2,u''))
loader.save(create_lists_list(6,None,[u'PyCon 2014', u'PyCon 2014', u'PyCon 2014', u'PyCon 2014'],3,u''))
loader.save(create_lists_list(7,None,[u'Free Software Day 2014', u'Free Software Day 2014', u'Free Software Day 2014', u'Free Software Day 2014'],3,u''))
loader.save(create_lists_list(8,None,[u'Schools', u'Schulen', u'Schools', u'Koolid'],3,u''))

loader.flush_deferred_objects()
