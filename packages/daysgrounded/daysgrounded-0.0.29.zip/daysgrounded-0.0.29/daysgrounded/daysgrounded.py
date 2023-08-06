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

"""
Manage child(s) grounded days.

If there are any command line arguments it calls the cli module.
Otherwise the gui module.
See usage.txt for command line usage.
"""

# Python 3 compatibility
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys

import cli
import gui_tk_func as gui
#import gui_tk_oo as gui
#import gui_qt as gui


def main():
    """Start CLI or GUI."""
    args = sys.argv[1:]
    if args:
        cli.start(args)
    else:
        gui.start()


if __name__ == '__main__':
    #import doctest
    #doctest.testmod(verbose=True)
    sys.exit(main())
