#!/usr/bin/python
# -*- coding: utf-8 -*-

# desc.py file is part of slpkg.

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


from messages import pkg_not_found
from __metadata__ import (
    lib_path,
    repositories,
    color,
)


class PkgDesc(object):

    def __init__(self, name, repo, paint):
        self.name = name
        self.repo = repo
        self.paint = paint
        self.COLOR = ""
        self.lib = ""
        color_text = {
            'red': color['RED'],
            'green': color['GREEN'],
            'yellow': color['YELLOW'],
            'cyan': color['CYAN'],
            'grey': color['GREY'],
            '': ''
        }
        self.COLOR = color_text[self.paint]
        if self.repo in repositories:
            self.lib = lib_path + '{0}_repo/PACKAGES.TXT'.format(self.repo)

    def view(self):
        f = open(self.lib, "r")
        PACKAGES_TXT = f.read()
        f.close()
        print("")   # new line at start
        count = 0
        if self.repo != "sbo":
            for line in PACKAGES_TXT.splitlines():
                if line.startswith(self.name + ":"):
                    print(self.COLOR + line[len(self.name) + 1:] +
                          color['ENDC'])
                    count += 1
                    if count == 11:
                        break
        else:
            for line in PACKAGES_TXT.splitlines():
                if (line.startswith("SLACKBUILD SHORT DESCRIPTION:  "
                                    + self.name + " (")):
                    count += 1
                    print(self.COLOR + line[31:] + color['ENDC'])
        if count == 0:
            pkg_not_found("", self.name, "No matching", "\n")
        else:
            print("")   # new line at end
