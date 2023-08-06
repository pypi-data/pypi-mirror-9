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

"""Localization."""

# Python 3 compatibility
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import utils


if utils.LANG == 'PT':  # Portuguese
    ABOUT = 'Sobre'
    CHILD = 'Criança:'
    CONFIRM_EXIT = 'Tem a certeza que pretende sair?'
    DAYS_GROUNDED = 'Dias de castigo'
    DAYS_RANGE = 'O número de dias tem que estar entre 0 e '
    EXIT = 'Sair'
    FILE = 'Ficheiro'
    HELP = 'Ajuda'
    LAST_UPDATE = 'Última atualização:'
    SET = 'Atribuir'
    UPDATE = 'Atualizar'
    VERSION = 'Versão'
    VERSION_WITH_SPACES = ' versão '
    WARNING = 'AVISO'
    WRONG_ARG = 'Erro: argumento incorreto '
else:  # English
    ABOUT = 'About'
    CHILD = 'Child:'
    CONFIRM_EXIT = 'Are you sure you want to exit?'
    DAYS_GROUNDED = 'Days grounded'
    DAYS_RANGE = 'Number of days must be between 0 and '
    EXIT = 'Exit'
    FILE = 'File'
    HELP = 'Help'
    LAST_UPDATE = 'Last update:'
    SET = 'Set'
    UPDATE = 'Update'
    VERSION = 'Version'
    VERSION_WITH_SPACES = ' version '
    WARNING = 'WARNING'
    WRONG_ARG = 'Err: incorrect argument '
