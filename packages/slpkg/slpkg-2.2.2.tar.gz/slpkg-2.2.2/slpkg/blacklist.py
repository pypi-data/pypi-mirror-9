#!/usr/bin/python
# -*- coding: utf-8 -*-

# blacklist.py file is part of slpkg.

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
from __metadata__ import MetaData as _m


class BlackList(object):
    '''
    Blacklist class to add, remove or listed packages
    in blacklist file.
    '''
    def __init__(self):
        self.quit = False
        self.blackfile = "/etc/slpkg/blacklist"
        self.black_conf = Utils().read_file(self.blackfile)

    def packages(self):
        '''
        Return blacklist packages from /etc/slpkg/blacklist
        configuration file.
        '''
        blacklist = []
        for read in self.black_conf.splitlines():
            read = read.lstrip()
            if not read.startswith("#"):
                blacklist.append(read.replace("\n", ""))
        return blacklist

    def listed(self):
        '''
        Print blacklist packages
        '''
        print("\nPackages in blacklist:\n")
        for black in self.packages():
            if black:
                print("{0}{1}{2}".format(_m.color['GREEN'], black,
                                         _m.color['ENDC']))
                self.quit = True
        if self.quit:
            print("")   # new line at exit

    def add(self, pkgs):
        '''
        Add blacklist packages if not exist
        '''
        blacklist = self.packages()
        pkgs = set(pkgs)
        print("\nAdd packages in blacklist:\n")
        with open(self.blackfile, "a") as black_conf:
            for pkg in pkgs:
                if pkg not in blacklist:
                    print("{0}{1}{2}".format(_m.color['GREEN'], pkg,
                                             _m.color['ENDC']))
                    black_conf.write(pkg + "\n")
                    self.quit = True
            black_conf.close()
        if self.quit:
            print("")   # new line at exit

    def remove(self, pkgs):
        '''
        Remove packages from blacklist
        '''
        print("\nRemove packages from blacklist:\n")
        with open(self.blackfile, "w") as remove:
            for line in self.black_conf.splitlines():
                if line not in pkgs:
                    remove.write(line + "\n")
                else:
                    print("{0}{1}{2}".format(_m.color['RED'], line,
                                             _m.color['ENDC']))
                    self.quit = True
            remove.close()
        if self.quit:
            print("")   # new line at exit
