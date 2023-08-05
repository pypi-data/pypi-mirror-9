#!/usr/bin/python
# -*- coding: utf-8 -*-

# downloader.py file is part of slpkg.

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
import subprocess

from messages import Msg
from __metadata__ import MetaData as _m


class Download(object):

    def __init__(self, path, url):
        self.path = path
        self.url = url
        self.wget_options = _m.wget_options

    def start(self):
        '''
        Download files usign wget.
        '''
        for dwn in self.url:
            self.file_name = dwn.split("/")[-1]
            print("\n[ {0}Download{1} ] -->{1} {2}\n".format(_m.color['GREEN'],
                                                             _m.color['ENDC'],
                                                             self.file_name))
            try:
                subprocess.call("wget {0} --directory-prefix={1} {2}".format(
                                self.wget_options, self.path, dwn), shell=True)
                self._check_if_downloaded()
            except KeyboardInterrupt:
                print   # new line at cancel
                sys.exit(0)

    def _check_if_downloaded(self):
        if not os.path.isfile(self.path + self.file_name):
            print('')
            Msg().template(78)
            print("| Download '{0}' file {1}[ FAILED ]{2}".format(
                self.file_name, _m.color['RED'], _m.color['ENDC']))
            Msg().template(78)
            print('')
            if not Msg().answer() in ['y', 'Y']:
                sys.exit(0)
