# -*- coding: UTF-8 -*-
logger.info("Loading 3 objects to table lists_listtype...")
# fields: id, name
loader.save(create_lists_listtype(1,[u'Mailing list', u'Mailing list', u'Mailing list', u'Infokiri']))
loader.save(create_lists_listtype(2,[u'Discussion group', u'Discussion group', u'Discussion group', u'Arutelugrupp']))
loader.save(create_lists_listtype(3,[u'Flags', u'Flags', u'Flags', u'Flags']))

loader.flush_deferred_objects()
