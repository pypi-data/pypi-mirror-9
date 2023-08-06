#!/usr/bin/python
# -*- coding: utf-8 -*-

# greps.py file is part of slpkg.

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

from slpkg.utils import Utils
from slpkg.toolbar import status
from slpkg.splitting import split_package
from slpkg.__metadata__ import MetaData as _m

from slpkg.slack.slack_version import slack_ver


def repo_data(PACKAGES_TXT, step, repo):
    '''
    Grap data packages
    '''
    (name, location, size, unsize,
     rname, rlocation, rsize, runsize) = ([] for i in range(8))
    index, toolbar_width = 0, 100
    for line in PACKAGES_TXT.splitlines():
        index += 1
        toolbar_width = status(index, toolbar_width, step)
        if line.startswith("PACKAGE NAME:"):
            if repo == "slackr":
                name.append(fix_slackers_pkg(line[15:]))
            else:
                name.append(line[15:].strip())
        if line.startswith("PACKAGE LOCATION:"):
            location.append(line[21:].strip())
        if line.startswith("PACKAGE SIZE (compressed):"):
            size.append(line[28:-2].strip())
        if line.startswith("PACKAGE SIZE (uncompressed):"):
            unsize.append(line[30:-2].strip())
    if repo == "rlw":
        (rname,
         rlocation,
         rsize,
         runsize
         ) = rlw_filter(name, location, size, unsize)
    elif repo == "alien" or repo == "rested":
        (rname,
         rlocation,
         rsize,
         runsize
         ) = alien_filter(name, location, size, unsize)
    elif repo == "ktown":
        (rname,
         rlocation,
         rsize,
         runsize
         ) = ktown_filter(name, location, size, unsize)
    elif repo == "multi":
        (rname,
         rlocation,
         rsize,
         runsize
         ) = multi_filter(name, location, size, unsize)
    else:
        rname, rlocation, rsize, runsize = name, location, size, unsize
    return [rname, rlocation, rsize, runsize]


def rlw_filter(name, location, size, unsize):
    '''
    Filter rlw repository data
    '''
    arch = os.uname()[4]
    if arch.startswith("i") and arch.endswith("86"):
        arch = "i486"
    (fname, flocation, fsize, funsize) = ([] for i in range(4))
    for n, l, s, u in zip(name, location, size, unsize):
        loc = l.split("/")
        if arch == loc[-1]:
            fname.append(n)
            flocation.append(l)
            fsize.append(s)
            funsize.append(u)
    return [fname, flocation, fsize, funsize]


def alien_filter(name, location, size, unsize):
    '''
    Filter Alien's repository data
    '''
    ver = slack_ver()
    if _m.slack_rel == "current":
        ver = "current"
    path_pkg = "pkg"
    if os.uname()[4] == "x86_64":
        path_pkg = "pkg64"
    (fname, flocation, fsize, funsize) = ([] for i in range(4))
    for n, l, s, u in zip(name, location, size, unsize):
        if path_pkg == l.split("/")[-2] and ver == l.split("/")[-1]:
            fname.append(n)
            flocation.append(l)
            fsize.append(s)
            funsize.append(u)
    return [fname, flocation, fsize, funsize]


def ktown_filter(name, location, size, unsize):
    '''
    Filter Alien's ktown repository data
    '''
    ver = slack_ver()
    if _m.slack_rel == "current":
        ver = "current"
    path_pkg = "x86"
    if os.uname()[4] == "x86_64":
        path_pkg = os.uname()[4]
    (fname, flocation, fsize, funsize) = ([] for i in range(4))
    for n, l, s, u in zip(name, location, size, unsize):
        if path_pkg in l and _m.ktown_kde_repo[1:-1] in l and l.startswith(ver):
            fname.append(n)
            flocation.append(l)
            fsize.append(s)
            funsize.append(u)
    return [fname, flocation, fsize, funsize]


def multi_filter(name, location, size, unsize):
    '''
    Filter Alien's multilib repository data
    '''
    ver = slack_ver()
    if _m.slack_rel == "current":
        ver = "current"
    (fname, flocation, fsize, funsize) = ([] for i in range(4))
    for n, l, s, u in zip(name, location, size, unsize):
        if l.startswith(ver):
            fname.append(n)
            flocation.append(l)
            fsize.append(s)
            funsize.append(u)
    return [fname, flocation, fsize, funsize]


def fix_slackers_pkg(name):
    '''
    Fix 'PACKAGE NAME:' from PACKAGES.TXT file
    Beacause repository slackers.it not report the full
    name in PACKAGES.TXT file use FILELIST.TXT to
    get.
    '''
    FILELIST_TXT = Utils().read_file(_m.lib_path + 'slackr_repo/FILELIST.TXT')
    for line in FILELIST_TXT.splitlines():
        if name in line and line.endswith(".txz"):
            return line.split("/")[-1].strip()
    # This trick fix spliting 'NoneType' packages
    # reference wrong name between PACKAGE.TXT and
    # FILELIST.TXT
    return ""


class Requires(object):

    def __init__(self, name, repo):
        self.name = name
        self.repo = repo

    def get_deps(self):
        '''
        Grap package requirements from repositories
        '''
        if self.repo == "rlw":
            # Robby's repository dependencies as shown in the central page
            # http://rlworkman.net/pkgs/
            dependencies = {
                "abiword": "wv",
                "claws-mail": "libetpan bogofilter html2ps",
                "inkscape": "gtkmm atkmm pangomm cairomm mm-common libsigc++ "
                            "libwpg lxml gsl numpy BeautifulSoup",
                "texlive": "libsigsegv texi2html",
                "xfburn": "libburn libisofs"
            }
            if self.name in dependencies.keys():
                return dependencies[self.name].split()
            else:
                return ""
        else:
            PACKAGES_TXT = Utils().read_file('{0}{1}_repo/PACKAGES.TXT'.format(
                _m.lib_path, self.repo))
            for line in PACKAGES_TXT.splitlines():
                if line.startswith("PACKAGE NAME:"):
                    if self.repo == "slackr":
                        pkg_name = fix_slackers_pkg(line[15:])
                    else:
                        pkg_name = split_package(line[14:].strip())[0]
                if line.startswith("PACKAGE REQUIRED:"):
                    if pkg_name == self.name:
                        if line[18:].strip():
                            return self._req_fix(line)

    def _req_fix(self, line):
        '''
        Fix slacky and salix requirements because many dependencies splitting
        with ',' and others with '|'
        '''
        deps = []
        for dep in line[18:].strip().split(','):
            dep = dep.split("|")
            if self.repo == 'slacky':
                if len(dep) > 1:
                    for d in dep:
                        deps.append(d.split()[0])
                dep = "".join(dep)
                deps.append(dep.split()[0])
            else:
                if len(dep) > 1:
                    for d in dep:
                        deps.append(d)
                deps.append(dep[0])
        return deps
