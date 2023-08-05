# -*- coding: UTF-8 -*-
logger.info("Loading 1 objects to table cal_eventtype...")
# fields: id, seqno, name, attach_to_email, email_template, description, is_appointment, all_rooms, locks_user, start_date, event_label, max_conflicting
loader.save(create_cal_eventtype(1,1,[u'Holidays', u'Holidays', u'Holidays', u'Holidays'],False,u'',u'',True,True,False,None,[u'Appointment', u'', u'', u''],1))

loader.flush_deferred_objects()
