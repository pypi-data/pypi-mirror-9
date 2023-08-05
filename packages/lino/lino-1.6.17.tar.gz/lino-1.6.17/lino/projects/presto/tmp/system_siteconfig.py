# -*- coding: UTF-8 -*-
logger.info("Loading 1 objects to table system_siteconfig...")
# fields: id, default_build_method, next_partner_id, site_company, default_event_type, site_calendar, max_auto_events, clients_account, sales_vat_account, sales_account, suppliers_account, purchases_vat_account, purchases_account, wages_account, clearings_account
loader.save(create_system_siteconfig(1,None,231,None,None,1,72,1,3,12,2,4,None,None,None))

loader.flush_deferred_objects()
