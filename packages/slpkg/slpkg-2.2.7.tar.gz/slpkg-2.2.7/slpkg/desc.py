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


from utils import Utils
from messages import Msg
from __metadata__ import MetaData as _m


class PkgDesc(object):

    def __init__(self, name, repo, paint):
        self.name = name
        self.repo = repo
        self.paint = paint
        self.COLOR = ""
        self.lib = ""
        color_text = {
            'red': _m.color['RED'],
            'green': _m.color['GREEN'],
            'yellow': _m.color['YELLOW'],
            'cyan': _m.color['CYAN'],
            'grey': _m.color['GREY'],
            '': ''
        }
        self.COLOR = color_text[self.paint]
        if self.repo in _m.repositories and self.repo != "sbo":
            self.lib = _m.lib_path + '{0}_repo/PACKAGES.TXT'.format(self.repo)
        else:
            self.lib = _m.lib_path + '{0}_repo/SLACKBUILDS.TXT'.format(
                self.repo)

    def view(self):
        PACKAGES_TXT = Utils().read_file(self.lib)
        print("")   # new line at start
        count = 0
        if self.repo != "sbo":
            for line in PACKAGES_TXT.splitlines():
                if line.startswith(self.name + ":"):
                    print(self.COLOR + line[len(self.name) + 1:] +
                          _m.color['ENDC'])
                    count += 1
                    if count == 11:
                        break
        else:
            for line in PACKAGES_TXT.splitlines():
                if (line.startswith("SLACKBUILD SHORT DESCRIPTION:  "
                                    + self.name + " (")):
                    count += 1
                    print(self.COLOR + line[31:] + _m.color['ENDC'])
        if count == 0:
            Msg().pkg_not_found("", self.name, "No matching", "\n")
        else:
            print("")   # new line at end
