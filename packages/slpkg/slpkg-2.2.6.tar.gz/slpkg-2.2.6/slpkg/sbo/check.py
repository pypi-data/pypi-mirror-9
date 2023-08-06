#!/usr/bin/python
# -*- coding: utf-8 -*-

# check.py file is part of slpkg.

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


import os
import sys

from slpkg.messages import Msg
from slpkg.toolbar import status
from slpkg.splitting import split_package
from slpkg.__metadata__ import MetaData as _m

from greps import SBoGrep
from search import sbo_search_pkg


def sbo_upgrade():
    '''
    Return packages for upgrade
    '''
    try:
        Msg().checking()
        upgrade_names, pkg_ver = [], []
        index, toolbar_width = 0, 3
        for pkg in sbo_list():
            index += 1
            toolbar_width = status(index, toolbar_width, 4)
            name = split_package(pkg)[0]
            ver = split_package(pkg)[1]
            if sbo_search_pkg(name):
                sbo_package = ("{0}-{1}".format(name, SBoGrep(name).version()))
                package = ("{0}-{1}".format(name, ver))
                if sbo_package > package:
                    upgrade_names.append(name)
                    pkg_ver.append(ver)
        Msg().done()
        return upgrade_names, pkg_ver
    except KeyboardInterrupt:
        print("")   # new line at exit
        sys.exit(0)


def sbo_list():
    '''
    Return all SBo packages
    '''
    sbo_packages = []
    for pkg in os.listdir(_m.pkg_path):
        if pkg.endswith("_SBo"):
            sbo_packages.append(pkg)
    return sbo_packages
