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
from messages import template
from __metadata__ import (
    color,
    default_answer
)


def check_md5(pkg_md5, src_file):
    '''
    MD5 Checksum
    '''
    md5s = md5(src_file)
    if pkg_md5 != md5s:
        template(78)
        print("| MD5SUM check for {0} [ {1}FAILED{2} ]".format(
            src_file.split("/")[-1], color['RED'], color['ENDC']))
        template(78)
        print("| Expected: {0}".format(md5s))
        print("| Found: {0}".format(pkg_md5))
        template(78)
        if default_answer == "y":
            answer = default_answer
        else:
            answer = raw_input("Would you like to continue [Y/n]? ")
        if answer in ['y', 'Y']:
            print("")   # new line after answer
        else:
            sys.exit(0)
    else:
        template(78)
        print("| MD5SUM check for {0} [ {1}PASSED{2} ]".format(
            src_file.split("/")[-1], color['GREEN'], color['ENDC']))
        template(78)
        print("")   # new line after pass checksum
