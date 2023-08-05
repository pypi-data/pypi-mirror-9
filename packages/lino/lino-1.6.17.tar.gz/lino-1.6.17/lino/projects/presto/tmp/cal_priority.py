# -*- coding: UTF-8 -*-
logger.info("Loading 4 objects to table cal_priority...")
# fields: id, name, ref
loader.save(create_cal_priority(1,[u'very urgent', u'sehr dringend', u'tr\xe8s urgent', u'v\xe4ga kiire'],u'1'))
loader.save(create_cal_priority(2,[u'urgent', u'dringend', u'urgent', u'kiire'],u'3'))
loader.save(create_cal_priority(3,[u'normal', u'normal', u'normal', u'keskmine'],u'5'))
loader.save(create_cal_priority(4,[u'not urgent', u'nicht dringend', u'pas urgent', u'mitte kiire'],u'9'))

loader.flush_deferred_objects()
