#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (c) 2008--2009 Andy Mikhailenko and contributors
#
#  This file is part of Django View Shortcuts.
#
#  Django View Shortcuts is free software under terms of the GNU Lesser
#  General Public License version 3 (LGPLv3) as published by the Free
#  Software Foundation. See the file README for copying conditions.
#

from django.conf import settings
from django.core.management import call_command

settings.configure(
    INSTALLED_APPS=('view_shortcuts',),
    DATABASE_ENGINE='sqlite3'
)

if __name__ == "__main__":
    call_command('test', 'view_shortcuts')
