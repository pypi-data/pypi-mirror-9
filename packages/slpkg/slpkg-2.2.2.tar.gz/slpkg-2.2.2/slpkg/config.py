#!/usr/bin/python
# -*- coding: utf-8 -*-

# config.py file is part of slpkg.

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

import subprocess

from utils import Utils
from __metadata__ import MetaData as _m


class Config(object):

    def __init__(self):
        self.config_file = "/etc/slpkg/slpkg.conf"

    def view(self):
        '''
        View slpkg config file
        '''
        print("")   # new line at start
        conf_args = [
            'VERSION',
            'REPOSITORIES',
            'BUILD_PATH',
            'SBO_CHECK_MD5',
            'PACKAGES',
            'PATCHES',
            'DEL_ALL',
            'DEL_BUILD',
            'SBO_BUILD_LOG',
            'DEFAULT_ANSWER',
            'REMOVE_DEPS_ANSWER',
            'SKIP_UNST',
            'DEL_DEPS',
            'USE_COLORS',
            'WGET_OPTIONS'
        ]
        read_conf = Utils().read_file(self.config_file)
        for line in read_conf.splitlines():
            if not line.startswith("#") and line.split("=")[0] in conf_args:
                print(line)
            else:
                print("{0}{1}{2}".format(_m.color['CYAN'], line,
                                         _m.color['ENDC']))
        print("")   # new line at end

    def edit(self, editor):
        '''
        Edit configuration file
        '''
        subprocess.call("{0} {1}".format(editor, self.config_file), shell=True)
