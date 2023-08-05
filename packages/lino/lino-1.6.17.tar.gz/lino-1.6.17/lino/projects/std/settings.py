# Copyright 2009-2014 Luc Saffre
# License: BSD (see file COPYING for details)

"""This defines Lino default settings. You include this (directly or
indirectly) into your local :xfile:`settings.py` using::

  from lino.projects.std.settings import *

"""


import os
import sys
import datetime
from tempfile import gettempdir
from os.path import join, abspath, dirname, normpath
import lino

from lino.ad import Site, configure_plugin, _

def TIM2LINO_LOCAL(alias, obj):
    """Hook for local special treatment on instances that have been
    imported from TIM.

    """
    return obj


def TIM2LINO_USERNAME(userid):
    if userid == "WRITE":
        return None
    return userid.lower()


DEBUG = False
TEMPLATE_DEBUG = DEBUG
DEBUG_PROPAGATE_EXCEPTIONS = DEBUG


ADMINS = [
    # ('Your Name', 'your_email@domain.com'),
]

MANAGERS = ADMINS


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be avilable on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
#~ TIME_ZONE = 'Europe/Brussels'
TIME_ZONE = None
# TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
#~ LANGUAGE_CODE = 'de-BE'
#~ LANGUAGE_CODE = 'fr-BE'

# ~ SITE_ID = 1 # see also fill.py

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

EMAIL_HOST = "mail.example.com"
#EMAIL_PORT = ""

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}

# Django wants system admins to define their own `SECRET_KEY
# <https://docs.djangoproject.com/en/dev/ref/settings/#secret-key>`__
# setting.  Hint: as long as you're on a development server you just
# put some non-empty string and that's okay.

SECRET_KEY = "20227"  # see :djangoticket:`20227`

