#!/usr/bin/python
# -*- coding: utf-8 -*-

# manager.py file is part of slpkg.

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

from slpkg.utils import Utils
from slpkg.messages import Msg
from slpkg.__metadata__ import MetaData as _m

from slpkg.pkg.find import find_package

from slpkg.binary.greps import fix_slackers_pkg


class PackageManager(object):
    '''
    Package manager class for install, upgrade,
    reinstall, remove, find and display packages.
    '''
    def __init__(self, binary):
        self.binary = binary

    def install(self):
        '''
        Install Slackware binary packages
        '''
        for pkg in self.binary:
            try:
                print(subprocess.check_output("installpkg {0}".format(
                                              pkg), shell=True))
                print("Completed!\n")
            except subprocess.CalledProcessError:
                self._not_found("Can't install", self.binary, pkg)

    def upgrade(self):
        '''
        Upgrade Slackware binary packages
        '''
        for pkg in self.binary:
            try:
                print(subprocess.check_output("upgradepkg --install-new "
                                              "{0}".format(pkg), shell=True))
                print("Completed!\n")
            except subprocess.CalledProcessError:
                self._not_found("Can't upgrade", self.binary, pkg)

    def reinstall(self):
        '''
        Reinstall Slackware binary packages
        '''
        for pkg in self.binary:
            try:
                print(subprocess.check_output(
                    "upgradepkg --reinstall {0}".format(pkg), shell=True))
                print("Completed!\n")
            except subprocess.CalledProcessError:
                self._not_found("Can't reinstall", self.binary, pkg)

    def _not_found(self, message, binary, pkg):
        if len(binary) > 1:
            bol = eol = ""
        else:
            bol = eol = "\n"
        Msg().pkg_not_found(bol, pkg, message, eol)

    def remove(self):
        '''
        Remove Slackware binary packages
        '''
        dep_path = _m.log_path + "dep/"
        dependencies, rmv_list = [], []
        removed = self._view_removed()
        if not removed:
            print("")   # new line at end
        else:
            msg = "package"
            if len(removed) > 1:
                msg = msg + "s"
            try:
                if _m.default_answer == "y":
                    remove_pkg = _m.default_answer
                else:
                    remove_pkg = raw_input(
                        "\nAre you sure to remove {0} {1} [Y/n]? ".format(
                            str(len(removed)), msg))
            except KeyboardInterrupt:
                print("")   # new line at exit
                sys.exit(0)
            if remove_pkg in ['y', 'Y']:
                for rmv in removed:
                    # If package build and install with 'slpkg -s sbo <package>'
                    # then look log file for dependencies in /var/log/slpkg/dep,
                    # read and remove all else remove only the package.
                    if os.path.isfile(dep_path + rmv) and _m.del_deps == "on":
                        dependencies = self._view_deps(dep_path, rmv)
                        if self._rmv_deps_answer() in ['y', 'Y']:
                            rmv_list += (self._rmv_deps(dependencies, dep_path,
                                                        rmv))
                        else:
                            rmv_list += self._rmv_pkg(rmv)
                            os.remove(dep_path + rmv)
                    else:
                        rmv_list += self._rmv_pkg(rmv)
                # Prints all removed packages
                self._reference_rmvs(rmv_list)

    def _rmv_deps_answer(self):
        '''
        Remove dependencies answer
        '''
        if _m.remove_deps_answer == "y":
            remove_dep = _m.remove_deps_answer
        else:
            try:
                remove_dep = raw_input(
                    "\nRemove dependencies (maybe used by "
                    "other packages) [Y/n]? ")
            except KeyboardInterrupt:
                print("")  # new line at exit
                sys.exit(0)
        return remove_dep

    def _view_removed(self):
        '''
        View packages before removed
        '''
        removed = []
        print("\nPackages with name matching [ {0}{1}{2} ]\n".format(
            _m.color['CYAN'], ", ".join(self.binary), _m.color['ENDC']))
        for pkg in self.binary:
            pkgs = find_package(pkg + _m.sp, _m.pkg_path)
            if pkgs:
                print("[ {0}delete{1} ] --> {2}".format(
                    _m.color['RED'], _m.color['ENDC'],
                    "\n               ".join(pkgs)))
                removed.append(pkg)
            else:
                Msg().pkg_not_found("", pkg, "Can't remove", "")
        return removed

    def _view_deps(self, path, package):
        '''
        View dependencies for before remove
        '''
        dependencies = Utils().read_file(path + package)
        print("")   # new line at start
        Msg().template(78)
        print("| Found dependencies for package {0}:".format(package))
        Msg().template(78)
        for dep in dependencies.splitlines():
            print("| {0}{1}{2}".format(_m.color['RED'], dep, _m.color['ENDC']))
        Msg().template(78)
        return dependencies

    def _rmv_deps(self, dependencies, path, package):
        '''
        Remove dependencies
        '''
        removes = []
        deps = dependencies.split()
        deps.append(package)
        for dep in deps:
            if find_package(dep + _m.sp, _m.pkg_path):
                print(subprocess.check_output("removepkg {0}".format(dep),
                                              shell=True))
                removes.append(dep)
        os.remove(path + package)
        return removes

    def _rmv_pkg(self, package):
        '''
        Remove one signle package
        '''
        if find_package(package + _m.sp, _m.pkg_path):
            print(subprocess.check_output("removepkg {0}".format(package),
                                          shell=True))
        return package.split()

    def _reference_rmvs(self, removes):
        '''
        Prints all removed packages
        '''
        Msg().template(78)
        print("| Total {0} packages removed".format(len(removes)))
        Msg().template(78)
        for pkg in removes:
            if not find_package(pkg + _m.sp, _m.pkg_path):
                print("| Package {0} removed".format(pkg))
            else:
                print("| Package {0} not found".format(pkg))
        Msg().template(78)
        print("")   # new line at end

    def find(self):
        '''
        Find installed Slackware packages
        '''
        matching = size = 0
        print("\nPackages with matching name [ {0}{1}{2} ]\n".format(
              _m.color['CYAN'], ', '.join(self.binary), _m.color['ENDC']))
        for pkg in self.binary:
            for match in find_package('', _m.pkg_path):
                if pkg in match:
                    matching += 1
                    print("[ {0}installed{1} ] - {2}".format(
                        _m.color['GREEN'], _m.color['ENDC'], match))
                    data = Utils().read_file(_m.pkg_path + match)
                    for line in data.splitlines():
                        if line.startswith("UNCOMPRESSED PACKAGE SIZE:"):
                            if "M" in line[26:]:
                                size += float(line[26:-1]) * 1024
                            else:
                                size += float(line[26:-1])
                            break
        if matching == 0:
            message = "Can't find"
            Msg().pkg_not_found("", ", ".join(self.binary), message, "\n")
        else:
            print("\n{0}Total found {1} matching packages.{2}".format(
                _m.color['GREY'], matching, _m.color['ENDC']))
            unit = "Kb"
            if size > 1024:
                unit = "Mb"
                size = (size / 1024)
            print("{0}Size of installed packages {1} {2}.{3}\n".format(
                _m.color['GREY'], round(size, 2), unit, _m.color['ENDC']))

    def display(self):
        '''
        Print the Slackware packages contents
        '''
        for pkg in self.binary:
            find = find_package(pkg + _m.sp, _m.pkg_path)
            if find:
                package = Utils().read_file(_m.pkg_path + "".join(find))
                for line in package.splitlines():
                    print(line).strip()
                print("")   # new line per file
            else:
                message = "Can't dislpay"
                if len(self.binary) > 1:
                    bol = eol = ""
                else:
                    bol = eol = "\n"
                Msg().pkg_not_found(bol, pkg, message, eol)

    def list(self, repo, INDEX, installed):
        '''
        List with the installed packages
        '''
        tty_size = os.popen('stty size', 'r').read().split()
        row = int(tty_size[0]) - 2
        try:
            index, page, pkg_list = 0, row, []
            r = self._list_lib(repo)
            pkg_list = self._list_greps(repo, r)
            print('')
            for pkg in sorted(pkg_list):
                pkg = self._slackr_repo(repo, pkg)
                if INDEX:
                    index += 1
                    pkg = self._list_color_tag(pkg)
                    print("{0}{1}:{2} {3}".format(_m.color['GREY'], index,
                                                  _m.color['ENDC'], pkg))
                    if index == page:
                        read = raw_input("\nPress {0}Enter{1} to "
                                         "continue... ".format(
                                             _m.color['CYAN'],
                                             _m.color['ENDC']))
                        if read in ['Q', 'q']:
                            break
                        print("")   # new line after page
                        page += row
                elif installed:
                    if self._list_of_installed(pkg):
                        print('{0}{1}{2}'.format(_m.color['GREEN'], pkg,
                                                 _m.color['ENDC']))
                else:
                    print(pkg)
            print("")   # new line at end
        except KeyboardInterrupt:
            print("")   # new line at exit
            sys.exit(0)

    def _list_greps(self, repo, packages):
        '''
        Grep packages
        '''
        pkg_list = []
        for line in packages.splitlines():
            if repo == 'sbo':
                if line.startswith("SLACKBUILD NAME: "):
                    pkg_list.append(line[17:].strip())
            else:
                if line.startswith("PACKAGE NAME: "):
                    pkg_list.append(line[15:].strip())
        return pkg_list

    def _list_lib(self, repo):
        '''
        Return package lists
        '''
        if repo == 'sbo':
            if (os.path.isfile(
                    _m.lib_path + '{0}_repo/SLACKBUILDS.TXT'.format(repo))):
                packages = Utils().read_file(_m.lib_path + '{0}_repo/'
                                             'SLACKBUILDS.TXT'.format(repo))
        else:
            if (os.path.isfile(_m.lib_path + '{0}_repo/PACKAGES.TXT'.format(
                    repo))):
                packages = Utils().read_file(_m.lib_path + '{0}_repo/'
                                             'PACKAGES.TXT'.format(repo))
        return packages

    def _slackr_repo(self, repo, pkg):
        '''
        Fix slackers packages
        '''
        if repo == 'slackr':
            return fix_slackers_pkg(pkg)
        return pkg

    def _list_color_tag(self, pkg):
        '''
        Tag with color installed packages
        '''
        find = pkg + '-'
        if pkg.endswith('.txz') or pkg.endswith('.tgz'):
            find = pkg[:-4]
        if find_package(find, _m.pkg_path):
            pkg = '{0}{1}{2}'.format(_m.color['GREEN'], pkg,
                                     _m.color['ENDC'])
        return pkg

    def _list_of_installed(self, pkg):
        '''
        Return installed packages
        '''
        find = pkg + '-'
        if pkg.endswith('.txz') or pkg.endswith('.tgz'):
            find = pkg[:-4]
        if find_package(find, _m.pkg_path):
            return pkg
