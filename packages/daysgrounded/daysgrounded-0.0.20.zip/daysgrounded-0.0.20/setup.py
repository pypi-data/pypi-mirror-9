#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setup for source, egg, wheel and py2exe (CXF still not working).

Copyright 2009-2015 Joao Carlos Roseta Matos

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# Python 3 compatibility
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
# incompatible with setup for bdist_wheel and py2exe
# must also be commented in imported modules
#from __future__ import unicode_literals

#import codecs
import glob
import os
import sys

import setuptools
import py2exe  # must be after setuptools

# add modules_dir to PYTHONPATH so all modules inside it are included
# in py2exe library and import appinfo works
# this assumes that the current dir has the same name as the subdir where
# the modules reside
modules_dir = os.getcwd().split(os.sep)[-1]
sys.path.insert(1, modules_dir)

import appinfo


DESC = LONG_DESC = ''
if os.path.isfile(appinfo.PATH + appinfo.README_FILE):
    #with codecs.open(appinfo.PATH + appinfo.README_FILE,
    #                 encoding='cp1252') as file_:
    with open(appinfo.PATH + appinfo.README_FILE) as file_:
        LONG_DESC = file_.read()
        DESC = LONG_DESC.split('\n')[3]

#PACKAGES = [appinfo.APP_NAME]  # use only if find_packages() doesn't work

REQUIREMENTS_FILE = 'requirements.txt'
REQUIREMENTS = ''
if os.path.isfile(REQUIREMENTS_FILE):
    with open(REQUIREMENTS_FILE) as file_:
        REQUIREMENTS = file_.read().splitlines()

# not needed?!
#PKG_DATA = {appinfo.APP_NAME: appinfo.DATA_FILES}
#PKG_DATA = {'': ['*.txt', '*.rst'], appinfo.APP_NAME: ['*.txt'],
#            appinfo.APP_NAME + '.data': ['*.pkl']}

# bdist_wininst section
#ENTRY_POINTS = {'console_scripts': [appinfo.APP_NAME + '=' + \
#                                    appinfo.APP_NAME + '.' + \
#                                    appinfo.APP_NAME + ':main'],
#                #gui_scripts=['app_gui=' + appinfo.APP_NAME + '.' + \
#                #             appinfo.APP_NAME + ':start']
#               }

SCRIPT = appinfo.PATH + appinfo.APP_NAME + '.py'

# py2exe section
if sys.argv[1] and str.lower(sys.argv[1]) == 'py2exe':
    DATA_FILES_PY2EXE = [('', appinfo.DATA_FILES)]
else:
    # if not cleared they are added to bdist_egg root
    DATA_FILES_PY2EXE = ''

OPTIONS = {'py2exe': {'compressed': True,
                      'ascii': False,
                      #'packages': ['colorama'],
                      #'bundle_files': 1,  # exe does not work
                      #'includes': ['colorama'],
                      #'excludes': ['doctest', 'pdb', 'unittest', 'difflib',
                      #             'inspect', 'pyreadline', 'optparse',
                      #             'calendar', 'email', '_ssl',
                      #             # 'locale', 'pickle'
                      #            ]
                     }
          }

# global section
setuptools.setup(name=appinfo.APP_NAME,
                 version=appinfo.APP_VERSION,
                 description=DESC,
                 long_description=LONG_DESC,
                 license=appinfo.LICENSE,
                 url=appinfo.URL,
                 author=appinfo.AUTHOR,
                 author_email=appinfo.AUTHOR_EMAIL,

                 classifiers=appinfo.CLASSIFIERS,
                 keywords=appinfo.KEYWORDS,

                 packages=setuptools.find_packages(),
                 #packages=setuptools.find_packages(exclude=['tests*']),

                 # use only if find_packages() doesn't work
                 #packages=PACKAGES,
                 #package_dir={'': appinfo.APP_NAME},

                 # to create the Scripts exe using bdist_wininst build option
                 # TODO returns error No module named cli
                 #entry_points=ENTRY_POINTS,

                 install_requires=REQUIREMENTS,

                 # used only if the package is not in PyPI, but exists as an
                 # egg, sdist format or as a single .py file
                 # see http://peak.telecommunity.com/DevCenter/setuptools#dependencies-that-aren-t-in-pypi
                 #dependency_links = ['http://host.domain.local/dir/'],

                 # required by bdist_egg and bdist_wheel
                 include_package_data=True,
                 #package_data=PKG_DATA,  # not needed?!

                 #zip_safe=False,  # incompatible with docs?

                 # py2exe section
                 console=[SCRIPT],
                 options=OPTIONS,
                 data_files=DATA_FILES_PY2EXE,
                 #windows=[{'script': appinfo.APP_NAME + '.py',
                 #          'icon_resources': [(0, appinfo.APP_NAME + '.ico')]
                 #         }],
                )
