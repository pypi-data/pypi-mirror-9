#!/usr/bin/python
# -*- coding: utf-8 -*-

# install.py file is part of slpkg.

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

from slpkg.utils import Utils
from slpkg.sizes import units
from slpkg.messages import Msg
from slpkg.remove import delete
from slpkg.checksum import check_md5
from slpkg.blacklist import BlackList
from slpkg.downloader import Download
from slpkg.log_deps import write_deps
from slpkg.grep_md5 import pkg_checksum
from slpkg.splitting import split_package
from slpkg.__metadata__ import MetaData as _m

from slpkg.pkg.find import find_package
from slpkg.pkg.manager import PackageManager

from slpkg.slack.slack_version import slack_ver

from greps import repo_data
from search import search_pkg
from repo_init import RepoInit
from dependency import Dependencies


class BinaryInstall(object):

    def __init__(self, packages, repo):
        self.packages = packages
        self.repo = repo
        self.version = _m.slack_rel
        self.tmp_path = _m.slpkg_tmp_packages
        self.dwn, self.dep_dwn = [], []
        self.install, self.dep_install = [], []
        self.comp_sum, self.dep_comp_sum = [], []
        self.uncomp_sum, self.dep_uncomp_sum = [], []
        self.dependencies = []
        self.deps_dict = {}
        self.answer = ''
        Msg().reading()
        self.PACKAGES_TXT, self.mirror = RepoInit(self.repo).fetch()
        num_lines = sum(1 for line in self.PACKAGES_TXT)
        self.step = (num_lines / (100 * len(self.packages)))

    def start(self, if_upgrade):
        '''
        Install packages from official Slackware distribution
        '''
        try:
            # fix if packages is for upgrade
            self.if_upgrade, self.pkg_ver = if_upgrade, []
            if self.if_upgrade:
                self.packages, ver = self.packages[0], self.packages[1]
                self.pkg_ver = ver
                self.pkg_ver.reverse()
            mas_sum = dep_sum = sums = [0, 0, 0]
            self.pkg_exist()
            Msg().done()
            self.dependencies = self.resolving_deps()
            (self.dep_dwn, self.dep_install, self.dep_comp_sum,
             self.dep_uncomp_sum) = self.store(self.dependencies)
            self.packages = self.clear_masters()
            (self.dwn, self.install, self.comp_sum,
             self.uncomp_sum) = self.store(self.packages)
            Msg().done()
            if self.install:
                print("\nThe following packages will be automatically "
                      "installed or upgraded \nwith new version:\n")
                self.top_view()
                Msg().upg_inst(self.if_upgrade)
                mas_sum = self.views(self.install, self.comp_sum, False)
                if self.dependencies:
                    print("Installing for dependencies:")
                    dep_sum = self.views(self.dep_install, self.dep_comp_sum,
                                         True)
                # sums[0] --> installed
                # sums[1] --> upgraded
                # sums[2] --> uninstall
                sums = [sum(i) for i in zip(mas_sum, dep_sum)]
                unit, size = units(self.comp_sum, self.uncomp_sum)
                print("\nInstalling summary")
                print("=" * 79)
                print("{0}Total {1} {2}.".format(_m.color['GREY'], sum(sums),
                                                 Msg().pkg(sum(sums))))
                print("{0} {1} will be installed, {2} will be upgraded and "
                      "{3} will be reinstalled.".format(sums[2],
                                                        Msg().pkg(sums[2]),
                                                        sums[1], sums[0]))
                print("Need to get {0} {1} of archives.".format(size[0],
                                                                unit[0]))
                print("After this process, {0} {1} of additional disk "
                      "space will be used.{2}".format(size[1], unit[1],
                                                      _m.color['ENDC']))
                print("")
                if Msg().answer() in ['y', 'Y']:
                    self.install.reverse()
                    Download(self.tmp_path, (self.dep_dwn + self.dwn)).start()
                    self.dep_install = Utils().check_downloaded(
                        self.tmp_path, self.dep_install)
                    self.install = Utils().check_downloaded(
                        self.tmp_path, self.install)
                    ins, upg = self.install_packages()
                    Msg().reference(ins, upg)
                    write_deps(self.deps_dict)
                    delete(self.tmp_path, self.install)
            else:
                Msg().not_found(self.if_upgrade)
        except KeyboardInterrupt:
            print("")   # new line at exit
            sys.exit(0)

    def pkg_exist(self):
        '''
        Search if package exist
        '''
        pkg_found, pkg_not_found = [], []
        for pkg in self.packages:
            if search_pkg(pkg, self.repo):
                pkg_found.append(pkg)
            else:
                pkg_not_found.append(pkg)
        if pkg_found:
            self.packages = pkg_found
        else:
            self.packages = pkg_not_found

    def clear_masters(self):
        '''
        Clear master packages if already exist in dependencies
        or if added to install two or more times
        '''
        packages = []
        for mas in Utils().remove_dbs(self.packages):
            if mas not in self.dependencies:
                packages.append(mas)
        return packages

    def install_packages(self):
        '''
        Install or upgrade packages
        '''
        installs, upgraded = [], []
        for inst in (self.dep_install + self.install):
            package = (self.tmp_path + inst).split()
            pkg_ver = '{0}-{1}'.format(split_package(inst)[0],
                                       split_package(inst)[1])
            self.checksums(inst)
            if os.path.isfile(_m.pkg_path + inst[:-4]):
                print("[ {0}reinstalling{1} ] --> {2}".format(_m.color['GREEN'],
                                                              _m.color['ENDC'],
                                                              inst))
                installs.append(pkg_ver)
                PackageManager(package).reinstall()
            elif find_package(split_package(inst)[0] + "-", _m.pkg_path):
                print("[ {0}upgrading{1} ] --> {2}".format(_m.color['YELLOW'],
                                                           _m.color['ENDC'],
                                                           inst))
                upgraded.append(pkg_ver)
                PackageManager(package).upgrade()
            else:
                print("[ {0}installing{1} ] --> {2}".format(_m.color['GREEN'],
                                                            _m.color['ENDC'],
                                                            inst))
                installs.append(pkg_ver)
                PackageManager(package).upgrade()
        return [installs, upgraded]

    def checksums(self, install):
        '''
        Checksums before install
        '''
        if self.repo == "alien" and self.version == "stable":
            check_md5(pkg_checksum("/" + slack_ver() + "/" + install,
                                   self.repo), self.tmp_path + install)
        elif self.repo == "alien" and self.version == "current":
            check_md5(pkg_checksum("/" + self.version + "/" + install,
                                   self.repo), self.tmp_path + install)
        else:
            check_md5(pkg_checksum(install, self.repo), self.tmp_path + install)

    def resolving_deps(self):
        '''
        Return package dependencies
        '''
        requires = []
        Msg().resolving()
        for dep in self.packages:
            dep_ver = '-'.join(dep.split('-')[:-1])     # fix if input pkg name
            if not len(dep_ver) == 0:                   # with version
                dep = dep_ver
            dependencies = []
            dependencies = Utils().dimensional_list(Dependencies(
                self.PACKAGES_TXT, self.repo).binary(dep))
            requires += dependencies
            self.deps_dict[dep] = Utils().remove_dbs(dependencies)
        return Utils().remove_dbs(requires)

    def view_masters(self, packages):
        '''
        Create empty seats if not upgrade
        '''
        if not self.if_upgrade:
            self.pkg_ver = [''] * len(packages)

    def views(self, install, comp_sum, is_deps):
        '''
        Views packages
        '''
        pkg_sum = uni_sum = upg_sum = 0
        self.view_masters(install)
        # fix repositories align
        repo = self.repo + (' ' * (6 - (len(self.repo))))
        if is_deps:     # fix avoid view version if dependencies
            self.pkg_ver = [''] * len(install)
        for pkg, ver, comp in zip(install, self.pkg_ver, comp_sum):
            pkg_split = split_package(pkg[:-4])
            if find_package(pkg[:-4], _m.pkg_path):
                pkg_sum += 1
                COLOR = _m.color['GREEN']
            elif find_package(pkg_split[0] + "-", _m.pkg_path):
                COLOR = _m.color['YELLOW']
                upg_sum += 1
            else:
                COLOR = _m.color['RED']
                uni_sum += 1
            print(" {0}{1}{2}{3} {4}{5} {6}{7}{8}{9}{10}{11:>11}{12}".format(
                COLOR, pkg_split[0] + ver, _m.color['ENDC'],
                " " * (24-len(pkg_split[0] + ver)), pkg_split[1],
                " " * (18-len(pkg_split[1])), pkg_split[2],
                " " * (8-len(pkg_split[2])), pkg_split[3],
                " " * (7-len(pkg_split[3])), repo,
                comp, " K"))
        return [pkg_sum, upg_sum, uni_sum]

    def top_view(self):
        Msg().template(78)
        print("{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}{10}".format(
            "| Package", " " * 17,
            "Version", " " * 12,
            "Arch", " " * 4,
            "Build", " " * 2,
            "Repos", " " * 10,
            "Size"))
        Msg().template(78)

    def store(self, packages):
        '''
        Store and return packages for install
        '''
        dwn, install, comp_sum, uncomp_sum = ([] for i in range(4))
        black = BlackList().packages()
        # name = data[0]
        # location = data[1]
        # size = data[2]
        # unsize = data[3]
        data = repo_data(self.PACKAGES_TXT, self.step, self.repo)
        for pkg in packages:
            for name, loc, comp, uncomp in zip(data[0], data[1], data[2],
                                               data[3]):
                if (name and name.startswith(pkg) and name not in install and
                        pkg not in black):
                    dwn.append("{0}{1}/{2}".format(self.mirror, loc, name))
                    install.append(name)
                    comp_sum.append(comp)
                    uncomp_sum.append(uncomp)
        if not install:
            for pkg in packages:
                for name, loc, comp, uncomp in zip(data[0], data[1], data[2],
                                                   data[3]):
                    if (name and pkg in split_package(name)[0]
                            and pkg not in black):
                        dwn.append("{0}{1}/{2}".format(self.mirror, loc, name))
                        install.append(name)
                        comp_sum.append(comp)
                        uncomp_sum.append(uncomp)
        dwn.reverse()
        install.reverse()
        comp_sum.reverse()
        uncomp_sum.reverse()
        return [dwn, install, comp_sum, uncomp_sum]
