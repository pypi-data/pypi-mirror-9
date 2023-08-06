#!/usr/bin/python
# -*- coding: utf-8 -*-

# dependency.py file is part of slpkg.

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

from greps import Requires


class Dependencies(object):

    def __init__(self, PACKAGES_TXT, repo):
        self.repo = repo
        self.dep_results = []
        self.packages = Utils().package_name(PACKAGES_TXT, repo)

    def binary(self, name):
        '''
        Build all dependencies of a package
        '''
        try:
            sys.setrecursionlimit(10000)
            dependencies = []
            blacklist = BlackList().packages()
            requires = Requires(name, self.repo).get_deps()
            toolbar_width, index = 2, 0
            if requires:
                for req in requires:
                    index += 1
                    toolbar_width = status(index, toolbar_width, 7)
                    if (req and req in self.packages and req not in blacklist):
                        dependencies.append(req)
                if dependencies:
                    self.dep_results.append(dependencies)
                    for dep in dependencies:
                        self.binary(dep)
            return self.dep_results
        except KeyboardInterrupt:
            print("")   # new line at exit
            sys.exit(0)
