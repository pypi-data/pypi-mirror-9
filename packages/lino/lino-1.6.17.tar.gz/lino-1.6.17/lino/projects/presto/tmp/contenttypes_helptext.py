# -*- coding: UTF-8 -*-
logger.info("Loading 2 objects to table contenttypes_helptext...")
# fields: id, content_type, field, help_text
loader.save(create_contenttypes_helptext(1,contenttypes_HelpText,u'field',u'The name of the field.'))
loader.save(create_contenttypes_helptext(2,contacts_Partner,u'language',u'Die Sprache, in der Dokumente ausgestellt werden sollen.'))

loader.flush_deferred_objects()
