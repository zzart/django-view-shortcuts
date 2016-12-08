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

" Django View Shortcuts setup "

from distutils.core import setup

long_description = '''Some decorators and filters that the author finds
extremely useful when writing non-generic Django views. The package contains
snippets of code that the author had been repeatedly writing with minor
differences for various websites. They were quickly extracted to the single
package.
'''

setup(
    name         = 'django-view-shortcuts',
    version      = '1.3.5',
    packages     = ['view_shortcuts'],

    requires = ['python (>= 2.4)', 'django (>= 1.0)'],

    description  = 'A set of shortcuts for Django views.',
    long_description = long_description,
    author       = 'Andy Mikhailenko',
    author_email = 'andy@neithere.net',
    url          = 'http://bitbucket.org/neithere/django-view-shortcuts/',
    download_url = 'http://bitbucket.org/neithere/django-view-shortcuts/src/',
    license      = 'GNU Lesser General Public License (LGPL), Version 3',
    keywords     = 'django views shortcut',
    classifiers  = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: User Interfaces',
    ],
)
