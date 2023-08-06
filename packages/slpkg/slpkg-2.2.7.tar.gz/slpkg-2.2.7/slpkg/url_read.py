#!/usr/bin/python
# -*- coding: utf-8 -*-

# url_read.py file is part of slpkg.

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
import urllib2

from __metadata__ import MetaData as _m


class URL(object):

    def __init__(self, link):
        self.link = link

    def reading(self):
        '''
        Open url and read
        '''
        try:
            f = urllib2.urlopen(self.link)
            return f.read()
        except (urllib2.URLError, ValueError):
            print("\n{0}Can't read file '{1}'{2}".format(
                _m.color['RED'], self.link.split('/')[-1], _m.color['ENDC']))
            return ' '
        except KeyboardInterrupt:
            print("")   # new line at exit
            sys.exit(0)
