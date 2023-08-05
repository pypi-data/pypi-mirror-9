# -*- coding: UTF-8 -*-
# Copyright 2011-2014 Luc Saffre
# License: BSD (see file COPYING for details)

from lino.utils.instantiator import Instantiator

from lino import rt


def objects():
    HelpText = rt.modules.contenttypes.HelpText
    ContentType = rt.modules.contenttypes.ContentType
    HT = Instantiator(HelpText, "content_type field help_text").build
    yield HT(ContentType.objects.get_for_model(HelpText),
             'field', "The name of the field.")
