# -*- coding: UTF-8 -*-
logger.info("Loading 9 objects to table cal_recurrentevent...")
# fields: id, name, user, start_date, start_time, end_date, end_time, every_unit, every, monday, tuesday, wednesday, thursday, friday, saturday, sunday, max_events, event_type, description
loader.save(create_cal_recurrentevent(1,[u"New Year's Day", u'Neujahr', u"Jour de l'an", u'Uusaasta'],None,date(2013,1,1),None,None,None,u'Y',1,True,True,True,True,True,True,True,None,1,u''))
loader.save(create_cal_recurrentevent(2,[u"International Workers' Day", u'Tag der Arbeit', u'Premier Mai', u'kevadp\xfcha'],None,date(2013,5,1),None,None,None,u'Y',1,True,True,True,True,True,True,True,None,1,u''))
loader.save(create_cal_recurrentevent(3,[u'National Day', u'Nationalfeiertag', u'F\xeate nationale', u'Belgia riigip\xfcha'],None,date(2013,7,21),None,None,None,u'Y',1,True,True,True,True,True,True,True,None,1,u''))
loader.save(create_cal_recurrentevent(4,[u'Assumption of Mary', u'Mari\xe4 Himmelfahrt', u'Assomption de Marie', u'Assumption of Mary'],None,date(2013,8,15),None,None,None,u'Y',1,True,True,True,True,True,True,True,None,1,u''))
loader.save(create_cal_recurrentevent(5,[u"All Souls' Day", u'Allerseelen', u'Comm\xe9moration des fid\xe8les d\xe9funts', u"All Souls' Day"],None,date(2013,10,31),None,None,None,u'Y',1,True,True,True,True,True,True,True,None,1,u''))
loader.save(create_cal_recurrentevent(6,[u"All Saints' Day", u'Allerheiligen', u'Toussaint', u"All Saints' Day"],None,date(2013,11,1),None,None,None,u'Y',1,True,True,True,True,True,True,True,None,1,u''))
loader.save(create_cal_recurrentevent(7,[u'Armistice with Germany', u'Waffenstillstand', u'Armistice', u'Armistice with Germany'],None,date(2013,11,11),None,None,None,u'Y',1,True,True,True,True,True,True,True,None,1,u''))
loader.save(create_cal_recurrentevent(8,[u'Christmas', u'Weihnachten', u'No\xebl', u'Esimene J\xf5ulup\xfcha'],None,date(2013,12,25),None,None,None,u'Y',1,True,True,True,True,True,True,True,None,1,u''))
loader.save(create_cal_recurrentevent(9,[u'Summer holidays', u'Sommerferien', u"Vacances d'\xe9t\xe9", u'Suvevaheaeg'],None,date(2013,7,1),None,date(2013,8,31),None,u'Y',1,True,True,True,True,True,True,True,None,1,u''))

loader.flush_deferred_objects()
