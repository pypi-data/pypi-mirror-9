#!/usr/bin/python
# -*- coding: utf-8 -*-

# utils.py file is part of slpkg.

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

from splitting import split_package


class Utils(object):

    def dimensional_list(self, lists):
        """ Create one dimensional list """
        one_list = []
        for lst in lists:
            one_list += lst
        return one_list

    def remove_dbs(self, double):
        """ Remove douuble item from list """
        one = []
        for dup in double:
            if dup not in one:
                one.append(dup)
        return one

    def read_file(self, registry):
        """ Return reading file """
        with open(registry, "r") as file_txt:
            read_file = file_txt.read()
            file_txt.close()
            return read_file

    def package_name(self, PACKAGES_TXT, repo):
        """ Return PACKAGE NAME """
        packages = []
        for line in PACKAGES_TXT.splitlines():
            # index += 1
            # toolbar_width = status(index, toolbar_width, step)
            if line.startswith("PACKAGE NAME:"):
                if repo == "slackr":
                    packages.append(line[14:].strip())
                else:
                    packages.append(split_package(line[14:].strip())[0])
        return packages

    def check_downloaded(self, path, maybe_downloaded):
        """ Return downloaded packages """
        downloaded = []
        for pkg in maybe_downloaded:
            if os.path.isfile(path + pkg):
                downloaded.append(pkg)
        return downloaded

    def read_file_pkg(self, file_pkg):
        '''
        Return packages from file
        '''
        packages = []
        if os.path.isfile(file_pkg):
            packages = []
            r_file = self.read_file(file_pkg)
            for pkg in r_file.splitlines():
                packages.append(pkg)
        else:
            print("\nThe '{0}' file not found\n".format(
                file_pkg.split('/')[-1]))
        return filter(lambda x: x != '', packages)
