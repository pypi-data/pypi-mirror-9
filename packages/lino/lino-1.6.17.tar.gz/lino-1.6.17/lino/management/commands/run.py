# -*- coding: UTF-8 -*-
# Copyright 2012-2013 by Luc Saffre.
# License: BSD, see LICENSE for more details.
"""

.. management_command:: run

Execute a standalone Python script after having set up the Django 
environment. Also modify `sys.args`, `__file__` and `__name__` so that 
the invoked script sees them as if it had been called directly.

This is yet another answer to the frequently asked Django question
about how to run standalone Django scripts
(`[1] <http://stackoverflow.com/questions/4847469/use-django-from-python-manage-py-shell-to-python-script>`__,
`[2] <http://www.b-list.org/weblog/2007/sep/22/standalone-django-scripts/>`__).
It is almost the same as redirecting stdin of Django's ``shell`` command 
(i.e. doing ``python manage.py shell < myscript.py``), 
but with the possibility of using command line arguments
and without the disturbing messages from the interactive console.

For example if you have a file `myscript.py` with the following content...

::

  from myapp.models import Partner
  print Partner.objects.all()

... then you can run this script using::

  $ python manage.py run myscript.py
  [<Partner: Rumma & Ko OÜ>, ...  <Partner: Charlier Ulrike>, 
  '...(remaining elements truncated)...']
  
"""

from __future__ import unicode_literals

import sys
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = __doc__
    args = "scriptname [args ...]"

    def handle(self, *args, **options):
        if len(args) == 0:
            raise CommandError("I need at least one argument.")
        fn = args[0]
        sys.argv = sys.argv[2:]
        globals()['__name__'] = '__main__'
        globals()['__file__'] = fn
        execfile(fn, globals())
        #~ execfile(fn,{})
