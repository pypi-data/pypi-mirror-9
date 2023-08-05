#!/usr/bin/python
# -*- coding: utf-8 -*-

# slackbuild.py file is part of slpkg.

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
from slpkg.messages import Msg
from slpkg.toolbar import status
from slpkg.blacklist import BlackList
from slpkg.log_deps import write_deps
from slpkg.downloader import Download
from slpkg.splitting import split_package
from slpkg.__metadata__ import MetaData as _m

from slpkg.pkg.find import find_package
from slpkg.pkg.build import BuildPackage
from slpkg.pkg.manager import PackageManager

from greps import SBoGrep
from remove import delete
from compressed import SBoLink
from dependency import Requires
from search import sbo_search_pkg


class SBoInstall(object):

    def __init__(self, slackbuilds):
        self.slackbuilds = slackbuilds
        self.unst = ["UNSUPPORTED", "UNTESTED"]
        self.master_packages = []
        self.deps = []
        self.dependencies = []
        self.package_not_found = []
        self.package_found = []
        self.deps_dict = {}
        self.toolbar_width, self.index = 2, 0
        self.answer = ''
        Msg().reading()

    def start(self, if_upgrade):
        try:
            self.if_upgrade, self.pkg_ver = if_upgrade, []
            self.view_version()
            if self.if_upgrade:
                self.slackbuilds, self.pkg_ver = (self.slackbuilds[0],
                                                  self.slackbuilds[1])
            tagc, match = '', False
            count_ins = count_upg = count_uni = 0
            self._remove_blacklist()
            for sbo in self.slackbuilds:
                self.index += 1
                self.toolbar_width = status(self.index, self.toolbar_width, 4)
                if sbo_search_pkg(sbo):
                    sbo_deps = Requires().sbo(sbo)
                    self.deps += sbo_deps
                    self.deps_dict[sbo] = self.one_for_all(sbo_deps)
                    self.package_found.append(sbo)
                else:
                    self.package_not_found.append(sbo)
            if not self.package_found:
                match = True
                self.package_found = self.matching(self.package_not_found)
            self.master_packages, mas_src = self.sbo_version_source(
                self.package_found)
            Msg().done()
            Msg().resolving()
            self.dependencies, dep_src = self.sbo_version_source(
                self.one_for_all(self.deps))
            Msg().done()
            self.master_packages = self.clear_masters()
            if self.package_found:
                print("\nThe following packages will be automatically "
                      "installed or upgraded \nwith new version:\n")
                self.top_view()
                Msg().upg_inst(self.if_upgrade)
                # view master packages
                for sbo, ver, ar in zip(self.master_packages, self.pkg_ver,
                                        mas_src):
                    tagc, count_ins, count_upg, count_uni = self.tag(
                        sbo, count_ins, count_upg, count_uni)
                    name = '-'.join(sbo.split('-')[:-1]) + '-' + ver
                    if not if_upgrade:
                        name = '-'.join(sbo.split('-')[:-1])
                    self.view_packages(tagc, name, sbo.split('-')[-1],
                                       self.select_arch(ar))
                self._view_installing_for_deps(match)
                # view dependencies
                for dep, ar in zip(self.dependencies, dep_src):
                    tagc, count_ins, count_upg, count_uni = self.tag(
                        dep, count_ins, count_upg, count_uni)
                    name = '-'.join(dep.split('-')[:-1])
                    self.view_packages(tagc, name, dep.split('-')[-1],
                                       self.select_arch(ar))
                count_total = (count_ins + count_upg + count_uni)
                print("\nInstalling summary")
                print("=" * 79)
                print("{0}Total {1} {2}.".format(
                    _m.color['GREY'], count_total, Msg().pkg(count_total)))
                print("{0} {1} will be installed, {2} allready installed and "
                      "{3} {4}".format(count_uni, Msg().pkg(count_uni),
                                       count_ins, count_upg,
                                       Msg().pkg(count_upg)))
                print("will be upgraded.{0}\n".format(_m.color['ENDC']))
                self._continue_to_install()
            else:
                Msg().not_found(if_upgrade)
        except KeyboardInterrupt:
            print("")   # new line at exit
            sys.exit(0)

    def _remove_blacklist(self):
        '''
        Remove packages in blacklist
        '''
        rmv_black = []
        for sbo in self.slackbuilds:
            if sbo not in BlackList().packages():
                rmv_black.append(sbo)
        self.slackbuilds = rmv_black

    def _continue_to_install(self):
        '''
        Continue to install
        '''
        if self.master_packages and Msg().answer() in ['y', 'Y']:
            b_ins = self.build_install()
            Msg().reference(b_ins[0], b_ins[1])
            write_deps(self.deps_dict)
            delete(_m.build_path)

    def _view_installing_for_deps(self, match):
        '''
        View installing for dependencies message
        '''
        if not match and self.dependencies:
            print("Installing for dependencies:")

    def clear_masters(self):
        '''
        Clear master slackbuilds if already exist in dependencies
        or if added to install two or more times
        '''
        slackbuilds = []
        for mas in Utils().remove_dbs(self.master_packages):
            if mas not in self.dependencies:
                slackbuilds.append(mas)
        return slackbuilds

    def matching(self, sbo_not_found):
        '''
        Return matching SBo
        '''
        sbo_matching = []
        f = open(_m.lib_path + "sbo_repo/SLACKBUILDS.TXT", "r")
        SLACKBUILDS_TXT = f.read()
        f.close()
        for sbo in sbo_not_found:
            for line in SLACKBUILDS_TXT.splitlines():
                if line.startswith("SLACKBUILD NAME: ") and sbo in line[17:]:
                    sbo_matching.append(line[17:])
        return sbo_matching

    def sbo_version_source(self, slackbuilds):
        '''
        Create sbo name with version
        '''
        sbo_versions, sources = [], []
        for sbo in slackbuilds:
            self.index += 1
            self.toolbar_width = status(self.index, self.toolbar_width, 4)
            sbo_ver = '{0}-{1}'.format(sbo, SBoGrep(sbo).version())
            sbo_versions.append(sbo_ver)
            sources.append(SBoGrep(sbo).source())
        return [sbo_versions, sources]

    def one_for_all(self, deps):
        '''
        Because there are dependencies that depend on other
        dependencies are created lists into other lists.
        Thus creating this loop create one-dimensional list.
        '''
        requires, dependencies = [], []
        requires = Utils().dimensional_list(deps)
        # Inverting the list brings the
        # dependencies in order to be installed.
        requires.reverse()
        dependencies = Utils().remove_dbs(requires)
        return dependencies

    def top_view(self):
        '''
        View top template
        '''
        Msg().template(78)
        print("{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}{10}".format(
            "| Package", " " * 17,
            "Version", " " * 12,
            "Arch", " " * 4,
            "Build", " " * 2,
            "Repos", " " * 10,
            "Size"))
        Msg().template(78)

    def view_version(self):
        '''
        Create empty seats if not upgrade
        '''
        if not self.if_upgrade:
            self.pkg_ver = [''] * len(self.slackbuilds)

    def view_packages(self, *args):
        '''
        View slackbuild packages with version and arch
        args[0] package color
        args[1] package
        args[2] version
        args[3] arch
        '''
        print(" {0}{1}{2}{3} {4}{5} {6}{7}{8}{9}{10}{11:>11}{12}".format(
            args[0], args[1], _m.color['ENDC'],
            " " * (24-len(args[1])), args[2],
            " " * (18-len(args[2])), args[3],
            " " * (15-len(args[3])), "",
            "", "SBo", "", ""))

    def tag(self, sbo, count_ins, count_upg, count_uni):
        '''
        Tag with color green if package already installed,
        color yellow for packages to upgrade and color red
        if not installed.
        '''
        if find_package(sbo, _m.pkg_path):
            paint = _m.color['GREEN']
            count_ins += 1
        elif find_package('-'.join(sbo.split('-')[:-1]) + '-', _m.pkg_path):
            paint = _m.color['YELLOW']
            count_upg += 1
        else:
            paint = _m.color['RED']
            count_uni += 1
        return paint, count_ins, count_upg, count_uni

    def select_arch(self, src):
        '''
        Looks if sources unsupported or untested
        from arch else select arch
        '''
        arch = os.uname()[4]
        if arch.startswith("i") and arch.endswith("86"):
            arch = "i486"
        for item in self.unst:
            if item in src:
                arch = item
        return arch

    def filenames(self, sources):
        '''
        Return filenames from sources
        '''
        filename = []
        for src in sources:
            # get file from source
            filename.append(src.split("/")[-1])
        return filename

    def search_in_tmp(self, prgnam):
        '''
        Search for binary packages in /tmp directory
        '''
        binary = []
        for search in find_package(prgnam, _m.output):
            if "_SBo" in search:
                binary.append(search)
        return binary

    def build_install(self):
        '''
        Searches the package name and version in /tmp to
        install. If find two or more packages e.g. to build
        tag 2 or 3 will fit most
        '''
        slackbuilds = self.dependencies + self.master_packages
        installs, upgraded, = [], []
        if not os.path.exists(_m.build_path):
            os.makedirs(_m.build_path)
        os.chdir(_m.build_path)
        for sbo in slackbuilds:
            pkg = '-'.join(sbo.split('-')[:-1])
            ver = sbo.split('-')[-1]
            prgnam = ("{0}-{1}".format(pkg, ver))
            sbo_file = "".join(find_package(prgnam, _m.pkg_path))
            src_link = SBoGrep(pkg).source().split()
            if sbo_file:
                Msg().template(78)
                Msg().pkg_found(pkg, split_package(sbo_file)[1])
                Msg().template(78)
            elif self.unst[0] in src_link or self.unst[1] in src_link:
                Msg().template(78)
                print("| Package {0} {1}{2}{3}".format(sbo, _m.color['RED'],
                                                       ''.join(src_link),
                                                       _m.color['ENDC']))
                Msg().template(78)
            else:
                sbo_url = sbo_search_pkg(pkg)
                sbo_link = SBoLink(sbo_url).tar_gz()
                script = sbo_link.split("/")[-1]
                dwn_srcs = sbo_link.split() + src_link
                Download(_m.build_path, dwn_srcs).start()
                sources = self.filenames(src_link)
                BuildPackage(script, sources, _m.build_path).build()
                binary_list = self.search_in_tmp(prgnam)
                try:
                    binary = (_m.output + max(binary_list)).split()
                except ValueError:
                    Msg().build_FAILED(sbo_url, prgnam)
                    sys.exit(0)
                if find_package(pkg + '-', _m.pkg_path):
                    print("{0}[ Upgrading ] --> {1}{2}".format(
                        _m.color['YELLOW'], _m.color['ENDC'], pkg))
                    upgraded.append(prgnam)
                else:
                    print("{0}[ Installing ] --> {1}{2}".format(
                        _m.color['GREEN'], _m.color['ENDC'], pkg))
                    installs.append(prgnam)
                PackageManager(binary).upgrade()
        return [installs, upgraded]
