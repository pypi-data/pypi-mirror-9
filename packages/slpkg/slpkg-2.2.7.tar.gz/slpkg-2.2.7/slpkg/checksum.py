#!/usr/bin/python
# -*- coding: utf-8 -*-

# checksum.py file is part of slpkg.

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

from md5sum import md5
from messages import Msg
from __metadata__ import MetaData as _m


def check_md5(pkg_md5, src_file):
    '''
    MD5 Checksum
    '''
    print('')
    md5s = md5(src_file)
    if pkg_md5 != md5s:
        Msg().template(78)
        print("| MD5SUM check for {0} [ {1}FAILED{2} ]".format(
            src_file.split("/")[-1], _m.color['RED'], _m.color['ENDC']))
        Msg().template(78)
        print("| Expected: {0}".format(md5s))
        print("| Found: {0}".format(pkg_md5))
        Msg().template(78)
        print('')
        if not Msg().answer() in ['y', 'Y']:
            sys.exit(0)
    else:
        Msg().template(78)
        print("| MD5SUM check for {0} [ {1}PASSED{2} ]".format(
            src_file.split("/")[-1], _m.color['GREEN'], _m.color['ENDC']))
        Msg().template(78)
    print('')   # new line after pass checksum
