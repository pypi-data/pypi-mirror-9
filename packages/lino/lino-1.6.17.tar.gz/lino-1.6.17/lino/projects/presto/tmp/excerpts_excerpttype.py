# -*- coding: UTF-8 -*-
logger.info("Loading 1 objects to table excerpts_excerpttype...")
# fields: id, build_method, template, name, attach_to_email, email_template, certifying, remark, body_template, content_type, primary, backward_compat, print_recipient, print_directly, shortcut
loader.save(create_excerpts_excerpttype(1,None,u'Default.odt',[u'Invoice', u'Rechnung', u'Invoice', u'Arve'],False,u'',True,u'',u'',sales_Invoice,True,False,True,True,None))

loader.flush_deferred_objects()
