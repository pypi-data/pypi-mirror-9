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

from slpkg.messages import Msg
from slpkg.toolbar import status
from slpkg.blacklist import BlackList
from slpkg.splitting import split_package
from slpkg.__metadata__ import MetaData as _m

from slpkg.pkg.find import find_package

from repo_init import RepoInit
from greps import repo_data


def pkg_upgrade(repo):
    '''
    Checking packages for upgrade
    '''
    Msg().checking()
    PACKAGES_TXT = RepoInit(repo).fetch()[0]
    pkgs_for_upgrade = []
    ver_for_upgrade = []
    # name = data[0]
    # location = data[1]
    # size = data[2]
    # unsize = data[3]
    data = repo_data(PACKAGES_TXT, 2000, repo)
    index, toolbar_width = 0, 1000
    for pkg in installed():
        index += 1
        toolbar_width = status(index, toolbar_width, 30)
        inst_pkg = split_package(pkg)
        for name in data[0]:
            if name:    # this tips because some pkg_name is empty
                repo_pkg = split_package(name[:-4])
            if (((repo_pkg[0] == inst_pkg[0] and repo_pkg[1] > inst_pkg[1]
                    and repo_pkg[3] == inst_pkg[3]) or
                    (repo_pkg[0] == inst_pkg[0] and repo_pkg[1] == inst_pkg[1]
                        and repo_pkg[3] > inst_pkg[3]))
                    and inst_pkg[0] not in BlackList().packages()):
                pkgs_for_upgrade.append('{0}-{1}'.format(repo_pkg[0],
                                                         repo_pkg[1]))
                ver_for_upgrade.append('-' + inst_pkg[1])
    Msg().done()
    return pkgs_for_upgrade, ver_for_upgrade


def installed():
    '''
    Return all installed packages
    '''
    return find_package('', _m.pkg_path)
