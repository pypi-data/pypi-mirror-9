# -*- coding: utf-8 -*-
# Copyright 2014 Luc Saffre
# This file is part of the Lino project.
# Lino is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
# Lino is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with Lino; if not, see <http://www.gnu.org/licenses/>.

"""
This module contains "quick" tests that are run on a demo database
without any fixture. You can run only these tests by issuing::

  $ go min2
  $ python manage.py test

"""

from __future__ import unicode_literals
from __future__ import print_function

import logging
logger = logging.getLogger(__name__)

from lino.runtime import *

from lino.utils.djangotest import RemoteAuthTestCase


class QuickTest(RemoteAuthTestCase):

    def test00(self):
        self.assertEqual(1 + 1, 2)
