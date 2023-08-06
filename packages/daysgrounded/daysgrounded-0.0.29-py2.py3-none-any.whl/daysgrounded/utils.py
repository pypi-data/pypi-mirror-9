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

"""Utils library."""

# Python 3 compatibility
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import imp
import locale
import os
#import pkg_resources
import sys


PY = int(sys.version[0])

# set correct path to all data files
DATA_PATH = ''
# if current module is frozen, use exe path
if (hasattr(sys, 'frozen') or  # new py2exe
     hasattr(sys, 'importers') or  # old py2exe
     imp.is_frozen('__main__')):  # tools/freeze
    if PY < 3:
        DATA_PATH = unicode(os.path.dirname(sys.executable), 'latin_1')
    else:
        DATA_PATH = os.path.dirname(sys.executable)
else:
    # use X:\PyhtonXX\Lib\site-packages\daysgrounded
    #DATA_PATH = pkg_resources.resource_filename(__name__, <some file>)
    #DATA_PATH = DATA_PATH.replace(<some file>, '')
    if PY < 3:
        DATA_PATH = unicode(os.path.dirname(sys.argv[0]), 'latin_1')
    else:
        DATA_PATH = os.path.dirname(sys.argv[0])


def sys_lang():
    """Get system language."""
    lang = locale.getdefaultlocale()
    #lang = 'EN'  # only for testing
    if 'pt_' in lang[0]:  # Portuguese
        return 'PT'
    else:  # English
        return 'EN'

LANG = sys_lang()


if __name__ == '__main__':
    # import doctest
    # doctest.testmod(verbose=True)
    pass
