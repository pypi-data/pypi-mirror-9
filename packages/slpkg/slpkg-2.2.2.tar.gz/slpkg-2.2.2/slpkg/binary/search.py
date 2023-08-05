#!/usr/bin/python
# -*- coding: utf-8 -*-

# search.py file is part of slpkg.

# Copyright 2014 Dimitris Zlatanidis <d.zlatanidis@gmail.com>
# All rights reserved.

# Slpkg is a user-friendly package manager for Slackware installations

# https://github.com/dslackw/slpkg

# Slpkg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import sys

from slpkg.utils import Utils
from slpkg.toolbar import status
from slpkg.blacklist import BlackList
from slpkg.splitting import split_package
from slpkg.__metadata__ import MetaData as _m


def search_pkg(name, repo):
    '''
    Search if package exists in PACKAGES.TXT file
    and return the name.
    '''
    try:
        blacklist = BlackList().packages()
        PACKAGES_TXT = Utils().read_file(_m.lib_path + '{0}_repo/'
                                         'PACKAGES.TXT'.format(repo))
        num_lines = sum(1 for line in PACKAGES_TXT)
        toolbar_width, index, step = 2, 0, num_lines
        for line in PACKAGES_TXT.splitlines():
            index += 1
            toolbar_width = status(index, toolbar_width, step)
            if line.startswith("PACKAGE NAME:  ") and len(line) > 16:
                if repo == 'slackr':
                    pkg_name = line[15:].strip()
                else:
                    pkg_name = split_package(line[15:])[0].strip()
                if name == pkg_name and name not in blacklist:
                    return pkg_name
    except KeyboardInterrupt:
        print("")   # new line at exit
        sys.exit(0)
