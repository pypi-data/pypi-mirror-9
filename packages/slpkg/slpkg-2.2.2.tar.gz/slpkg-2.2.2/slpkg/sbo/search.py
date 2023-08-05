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
from slpkg.repositories import Repo
from slpkg.blacklist import BlackList
from slpkg.__metadata__ import MetaData as _m

from slpkg.slack.slack_version import slack_ver


def sbo_search_pkg(name):
    '''
    Search for package path from SLACKBUILDS.TXT file
    '''
    try:
        repo = Repo().sbo()
        blacklist = BlackList().packages()
        sbo_url = "{0}{1}/".format(repo, slack_ver())
        SLACKBUILDS_TXT = Utils().read_file(
            _m.lib_path + "sbo_repo/SLACKBUILDS.TXT")
        for line in SLACKBUILDS_TXT.splitlines():
            if line.startswith("SLACKBUILD LOCATION"):
                sbo_name = (line[23:].split("/")[-1].replace("\n", "")).strip()
                if name == sbo_name and name not in blacklist:
                    return (sbo_url + line[23:].strip() + "/")
    except KeyboardInterrupt:
        print("")   # new line at exit
        sys.exit(0)
