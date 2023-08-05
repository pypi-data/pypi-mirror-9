#!/usr/bin/python
# -*- coding: utf-8 -*-

# views.py file is part of slpkg.

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
import pydoc

from slpkg.messages import Msg
from slpkg.downloader import Download
from slpkg.__metadata__ import MetaData as _m

from slpkg.pkg.find import find_package
from slpkg.pkg.build import BuildPackage
from slpkg.pkg.manager import PackageManager

from read import Read
from remove import delete
from greps import SBoGrep
from compressed import SBoLink
from search import sbo_search_pkg


class SBoNetwork(object):

    def __init__(self, name):
        self.name = name
        Msg().reading()
        grep = SBoGrep(self.name)
        self.sbo_url = sbo_search_pkg(self.name)
        if self.sbo_url:
            self.sbo_desc = grep.description()[len(self.name) + 2:-1]
            self.source_dwn = grep.source().split()
            self.sbo_req = grep.requires()
            self.sbo_dwn = SBoLink(self.sbo_url).tar_gz()
            self.sbo_version = grep.version()
            self.dwn_srcs = self.sbo_dwn.split() + self.source_dwn
        self.space = ("\n" * 50)
        Msg().done()

    def view(self):
        '''
        View SlackBuild package, read or install them
        from slackbuilds.org
        '''
        if self.sbo_url:
            prgnam = ("{0}-{1}".format(self.name, self.sbo_version))
            self.view_sbo(
                self.name, self.sbo_url, self.sbo_desc,
                self.sbo_dwn.split("/")[-1],
                ", ".join([src.split("/")[-1] for src in self.source_dwn]),
                self.sbo_req)
            FAULT = self.error_uns()
            while True:
                choice = self.read_choice()
                if choice in ['D', 'd']:
                    Download("", self.dwn_srcs).start()
                    break
                elif choice in ['R', 'r']:
                    README = Read(self.sbo_url).readme("README")
                    fill = self.fill_pager(README)
                    pydoc.pager(README + fill)
                elif choice in ['F', 'f']:
                    info = Read(self.sbo_url).info(self.name, ".info")
                    fill = self.fill_pager(info)
                    pydoc.pager(info + fill)
                elif choice in ['S', 's']:
                    SlackBuild = Read(self.sbo_url).slackbuild(self.name,
                                                               ".SlackBuild")
                    fill = self.fill_pager(SlackBuild)
                    pydoc.pager(SlackBuild + fill)
                elif choice in ['B', 'b']:
                    self.build(FAULT)
                    delete(_m.build_path)
                    break
                elif choice in ['I', 'i']:
                    if not find_package(prgnam + _m.sp, _m.pkg_path):
                        self.build(FAULT)
                        self.install(prgnam)
                        delete(_m.build_path)
                        break
                    else:
                        Msg().template(78)
                        Msg().pkg_found(self.name, self.sbo_version)
                        Msg().template(78)
                        break
                else:
                    break
        else:
            Msg().pkg_not_found("\n", self.name, "Can't view", "\n")

    @staticmethod
    def view_sbo(*args):
        '''
        View slackbuild.org
        '''
        color = _m.color
        print("")   # new line at start
        Msg().template(78)
        print("| {0}Package {1}{2}{3} --> {4}".format(color['GREEN'],
                                                      color['CYAN'], args[0],
                                                      color['GREEN'],
                                                      color['ENDC'] + args[1]))
        Msg().template(78)
        print("| {0}Description : {1}{2}".format(color['GREEN'],
                                                 color['ENDC'], args[2]))
        print("| {0}SlackBuild : {1}{2}".format(color['GREEN'], color['ENDC'],
                                                args[3]))
        print("| {0}Sources : {1}{2}".format(color['GREEN'], color['ENDC'],
                                             args[4]))
        print("| {0}Requirements : {1}{2}".format(color['YELLOW'],
                                                  color['ENDC'],
                                                  ", ".join(args[5])))
        Msg().template(78)
        print(" {0}R{1}EADME               View the README file".format(
            color['RED'], color['ENDC']))
        print(" {0}S{1}lackBuild           View the SlackBuild file".format(
            color['RED'], color['ENDC']))
        print(" In{0}f{1}o                 View the Info file".format(
            color['RED'], color['ENDC']))
        print(" {0}D{1}ownload             Download this package".format(
            color['RED'], color['ENDC']))
        print(" {0}B{1}uild                Download and build".format(
            color['RED'], color['ENDC']))
        print(" {0}I{1}nstall              Download/Build/Install".format(
            color['RED'], color['ENDC']))
        print(" {0}Q{1}uit                 Quit\n".format(color['RED'],
                                                          color['ENDC']))

    @staticmethod
    def fill_pager(page):
        '''
        Fix pager spaces
        '''
        tty_size = os.popen('stty size', 'r').read().split()
        rows = int(tty_size[0]) - 1
        lines = sum(1 for line in page.splitlines())
        diff = rows - lines
        fill = "\n" * diff
        if diff > 0:
            return fill
        else:
            return ""

    def read_choice(self):
        '''
        Return choice
        '''
        try:
            choice = raw_input(" {0}Choose an option: {1}".format(
                _m.color['GREY'], _m.color['ENDC']))
        except KeyboardInterrupt:
            print("")   # new line at exit
            sys.exit(0)
        return choice

    def error_uns(self):
        '''
        Check if package supported by arch
        before proceed to install
        '''
        UNST = ["UNSUPPORTED", "UNTESTED"]
        if "".join(self.source_dwn) in UNST:
            return "".join(self.source_dwn)

    def build(self, FAULT):
        '''
        Only build and create Slackware package
        '''
        if FAULT:
            print("\n{0}The package {1} {2}\n".format(_m.color['RED'], FAULT,
                                                      _m.color['ENDC']))
            sys.exit(0)
        sources = []
        if not os.path.exists(_m.build_path):
            os.makedirs(_m.build_path)
        os.chdir(_m.build_path)
        Download(_m.build_path, self.dwn_srcs).start()
        script = self.sbo_dwn.split("/")[-1]
        for src in self.source_dwn:
            sources.append(src.split("/")[-1])
        BuildPackage(script, sources, _m.build_path).build()

    def install(self, prgnam):
        '''
        Install Slackware package found in /tmp
        directory.
        '''
        binary_list = []
        for search in find_package(prgnam, _m.output):
            if "_SBo" in search:
                binary_list.append(search)
            try:
                binary = (_m.output + max(binary_list)).split()
            except ValueError:
                Msg().build_FAILED(self.sbo_url, prgnam)
                sys.exit(0)
            print("[ {0}Installing{1} ] --> {2}".format(_m.color['GREEN'],
                                                        _m.color['ENDC'],
                                                        self.name))
            PackageManager(binary).upgrade()
