#!/usr/bin/python
# -*- coding: utf-8 -*-

# check.py file is part of slpkg.

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

from slpkg.pkg.find import find_package
from slpkg.pkg.build import BuildPackage
from slpkg.pkg.manager import PackageManager

from slpkg.toolbar import status
from slpkg.downloader import Download
from slpkg.splitting import split_package
from slpkg.messages import (
    template,
    build_FAILED
)
from slpkg.__metadata__ import (
    tmp,
    pkg_path,
    build_path,
    default_answer,
    color,
    sp
)

from greps import SBoGrep
from remove import delete
from compressed import SBoLink
from search import sbo_search_pkg
from dependency import sbo_dependencies_pkg


class SBoCheck(object):

    def __init__(self):
        self.done = "{0}Done{1}\n".format(color['GREY'], color['ENDC'])
        sys.stdout.write("{0}Reading package lists ...{1}".format(
            color['GREY'], color['ENDC']))
        sys.stdout.flush()
        self.installed = []
        self.index, self.toolbar_width = 0, 3

    def start(self):
        '''
        Upgrade all slackbuilds packages from slackbuilds.org
        repository.
        NOTE: This functions check packages by version not by build
        tag because build tag not reported the SLACKBUILDS.TXT file,
        but install the package with maximum build tag if find the
        some version in /tmp directory.
        '''
        try:
            if self.sbo_list():
                upg_name = self.exists()
                sys.stdout.write(self.done)
                data = []
                if upg_name:
                    sys.stdout.write("{0}Resolving dependencies ...{1}".format(
                                     color['GREY'], color['ENDC']))
                    sys.stdout.flush()
                    # upgrade name = data[0]
                    # package for upgrade = data[1]
                    # upgrade version = data[2]
                    # upgrade arch = data[3]
                    data = store(order_list(upg_name))
                    sys.stdout.write(self.done)
                if data:
                    # count installed = count[0]
                    # count upgraded = count[1]
                    # message install = msg[0]
                    # message upgrade = msg[1]
                    count, msg = view_packages(data[1], data[2], data[3])
                    if default_answer == "y":
                        answer = default_answer
                    else:
                        answer = raw_input("Would you like to continue [Y/n]? ")
                    if answer in ['y', 'Y']:
                        os.chdir(build_path)
                        for name, version in zip(data[0], data[2]):
                            prgnam = ("{0}-{1}".format(name, version))
                            sbo_url = sbo_search_pkg(name)
                            sbo_dwn = SBoLink(sbo_url).tar_gz()
                            src_dwn = SBoGrep(name).source().split()
                            script = sbo_dwn.split("/")[-1]
                            dwn_srcs = sbo_dwn.split() + src_dwn
                            Download(build_path, dwn_srcs).start()
                            sources = filenames(src_dwn)
                            BuildPackage(script, sources, build_path).build()
                            # Searches the package name and version in /tmp to
                            # install.If find two or more packages e.g. to build
                            # tag 2 or 3 will fit most.
                            binary_list = search_in_tmp(prgnam)
                            try:
                                binary = (tmp + max(binary_list)).split()
                            except ValueError:
                                build_FAILED(sbo_url, prgnam)
                                sys.exit(0)
                            if find_package(name + sp, pkg_path):
                                print("[ {0}Upgrading{1} ] --> {2}".format(
                                    color['YELLOW'], color['ENDC'], name))
                            else:
                                print("[ {0}Installing{1} ] --> {2}".format(
                                    color['GREEN'], color['ENDC'], name))
                                # Use this list to pick out what
                                # packages will be installed
                                self.installed.append(name)
                            PackageManager(binary).upgrade()
                        reference(data[0], data[1], data[2], count[0], count[1],
                                  msg[0], msg[1], self.installed)
                        delete(build_path)
                else:
                    print("\nTotal {0} SBo packages are up to date\n".format(
                        len(self.sbo_list())))
            else:
                sys.stdout.write(self.done)
                print("\nNo SBo packages found\n")
        except KeyboardInterrupt:
            print("")   # new line at exit
            sys.exit(0)

    def sbo_list(self):
        '''
        Return all SBo packages
        '''
        sbo_packages = []
        for pkg in os.listdir(pkg_path):
            if pkg.endswith("_SBo"):
                sbo_packages.append(pkg)
        return sbo_packages

    def exists(self):
        '''
        Search packages if exists in the repository
        and it gets to avoidable modified packages
        from the user with the tag _SBo
        '''
        upgrade_names = []
        for pkg in self.sbo_list():
            self.index += 1
            self.toolbar_width = status(self.index, self.toolbar_width, 4)
            name = split_package(pkg)[0]
            if sbo_search_pkg(name):
                sbo_package = ("{0}-{1}".format(name, SBoGrep(name).version()))
                package = ("{0}-{1}".format(name, split_package(pkg)[1]))
                if sbo_package > package:
                    upgrade_names.append(name)
        return upgrade_names


def deps(upgrade_names):
    '''
    Of the packages found to need upgrading,
    stored in a series such as reading from the
    file .info.
    '''
    for upg in upgrade_names:
        dependencies = sbo_dependencies_pkg(upg)
    return dependencies


def one_for_all(upgrade_names):
    '''
    Because there are dependencies that depend on other
    dependencies are created lists into other lists.
    Thus creating this loop create one-dimensional list.
    '''
    requires = []
    dependencies = deps(upgrade_names)
    for dep in dependencies:
        requires += dep
    # Inverting the list brings the
    # dependencies in order to be installed.
    requires.reverse()
    return requires


def remove_dbs(upgrade_names):
    '''
    Many packages use the same dependencies, in this loop
    creates a new list by removing duplicate dependencies but
    without spoiling the line must be installed.
    '''
    dependencies = []
    requires = one_for_all(upgrade_names)
    for duplicate in requires:
        if duplicate not in dependencies:
            dependencies.append(duplicate)
    return dependencies


def order_list(upgrade_names):
    '''
    Last and after the list is created with the correct number
    of dependencies that must be installed, and add the particular
    packages that need to be upgraded if they are not already on
    the list in end to list.
    '''
    dependencies = remove_dbs(upgrade_names)
    for upg in upgrade_names:
        if upg not in dependencies:
            dependencies.append(upg)
    return dependencies


def store(dependencies):
    '''
    In the end last a check of the packages that are on the list
    are already installed.
    '''
    (upgrade_name,
     package_for_upgrade,
     upgrade_version,
     upgrade_arch
     ) = ([] for i in range(4))
    for pkg in dependencies:
        ver = SBoGrep(pkg).version()
        prgnam = ("{0}-{1}".format(pkg, ver))
        # if package not installed
        # take version from repository
        pkg_version = ver
        arch = os.uname()[4]
        if arch.startswith("i") and arch.endswith("86"):
            arch = "i486"
        if find_package(prgnam, pkg_path) == []:
            for sbo in os.listdir(pkg_path):
                if (sbo.startswith(pkg + sp) and
                        sbo.endswith("_SBo")):
                    # search if packages installed
                    # if yes grab package name and version
                    pkg_version = split_package(sbo)[1]
            upgrade_name.append(pkg)
            package_for_upgrade.append("{0}-{1}".format(pkg, pkg_version))
            upgrade_version.append(ver)
            upgrade_arch.append(arch)
    return [upgrade_name, package_for_upgrade, upgrade_version, upgrade_arch]


def view_packages(package_for_upgrade, upgrade_version, upgrade_arch):
    '''
    View packages for upgrade
    '''
    print("\nThese packages need upgrading:\n")
    template(78)
    print("{0}{1}{2}{3}{4}{5}{6}".format(
        "| Package", " " * 30, "New version", " " * 6,
        "Arch", " " * 9, "Repository"))
    template(78)
    print("Upgrading:")
    count_upgraded = count_installed = 0
    for upg, ver, arch in zip(package_for_upgrade, upgrade_version,
                              upgrade_arch):
        if find_package(upg[:-len(ver)], pkg_path):
            COLOR = color['YELLOW']
            count_upgraded += 1
        else:
            COLOR = color['RED']
            count_installed += 1
        print(" {0}{1}{2}{3} {4}{5}{6} {7}{8}{9}{10}".format(
            COLOR, upg, color['ENDC'], " " * (37-len(upg)), color['GREEN'],
            ver, color['ENDC'], " " * (16-len(ver)), arch,
            " " * (13-len(arch)), "SBo"))
    msg_upg = "package"
    msg_ins = msg_upg
    if count_upgraded > 1:
        msg_upg = msg_upg + "s"
    if count_installed > 1:
        msg_ins = msg_ins + "s"
    print("\nInstalling summary")
    print("=" * 79)
    print("{0}Total {1} {2} will be upgraded and {3} {4} will be "
          "installed.{5}\n".format(color['GREY'], count_upgraded, msg_upg,
                                   count_installed, msg_ins, color['ENDC']))
    return [count_installed, count_upgraded], [msg_ins, msg_upg]


def filenames(sources):
    '''
    Download sources and return filenames
    '''
    filename = []
    for src in sources:
        filename.append(src.split("/")[-1])
    return filename


def search_in_tmp(prgnam):
    '''
    Search for binarys packages in /tmp directory
    '''
    binary = []
    for search in find_package(prgnam, tmp):
        if "_SBo" in search:
            binary.append(search)
    return binary


def reference(*args):
    # reference(data[0], data[1], data[2], count[0], count[1],
    #           msg[0], msg[1], installed)
    '''
    Print results
    '''
    if len(args[1]) > 1:
        template(78)
        print("| Total {0} {1} upgraded and {2} {3} "
              "installed".format(args[4], args[6],
                                 args[3], args[5]))
        template(78)
        for pkg, upg, ver in zip(args[1], args[0], args[2]):
            upgraded = ("{0}-{1}".format(upg, ver))
            if find_package(upgraded, pkg_path):
                if upg in args[7]:
                    print("| Package {0} installed".format(pkg))
                else:
                    print("| Package {0} upgraded with new "
                          "package {1}-{2}".format(pkg, upg, ver))
        template(78)
