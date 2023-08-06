#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2009-2015 Joao Carlos Roseta Matos
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Application basic information."""

# Python 3 compatibility
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
# incompatible with setup for bdist_wheel and py2exe
# must also be commented in imported modules
#from __future__ import unicode_literals

import datetime as dt
import glob


APP_NAME = 'daysgrounded'
APP_VERSION = '0.0.27'
AUTHOR = 'Joao Carlos Roseta Matos'
COPYRIGHT = 'Copyright ' + '2009-' + str(dt.date.today().year) + ' '  + AUTHOR
# the previous line must be like that

LICENSE = 'GNU General Public License v2 or later (GPLv2+)'
URL = 'https://github.com/jcrmatos/daysgrounded'
AUTHOR_EMAIL = 'jcrmatos@gmail.com'
KEYWORDS = 'days grounded'
CLASSIFIERS = ['Development Status :: 4 - Beta',
               'Environment :: Console',
               'Environment :: Win32 (MS Windows)',
               'Intended Audience :: End Users/Desktop',
               'Natural Language :: Portuguese',
               'Natural Language :: English',
               'License :: OSI Approved ::' + ' ' + LICENSE,
               'Operating System :: OS Independent',
               'Programming Language :: Python',
               'Programming Language :: Python :: 2.7',
               'Programming Language :: Python :: 3.4',
               'Topic :: Other/Nonlisted Topic',
               #'Private :: Do Not Upload'  # to prevent PyPI publishing
              ]

PATH = APP_NAME + '/'
DATA_FILES = glob.glob(PATH + '*.txt') + glob.glob(PATH + '*.rst')

README_FILE = 'README.txt'

APP_TYPE = 'application'  # it can be application or module
