#!/usr/bin/python
# -*- coding: utf-8 -*-

# messages.py file is part of slpkg.

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

from __metadata__ import MetaData as _m

from slpkg.pkg.find import find_package


class Msg(object):

    def pkg_not_found(self, bol, pkg, message, eol):
        '''
        Print message when package not found
        '''
        print("{0}No such package {1}: {2}{3}".format(bol, pkg, message, eol))

    def pkg_found(self, pkg, version):
        '''
        Print message when package found
        '''
        print("| Package {0}-{1} is already installed".format(pkg, version))

    def pkg_installed(self, pkg):
        '''
        Print message when package installed
        '''
        print("| Package {0} installed".format(pkg))

    def s_user(self, user):
        '''
        Check for root user
        '''
        if user != "root":
            print("\nslpkg: error: must have root privileges\n")
            sys.exit(0)

    def build_FAILED(self, sbo_url, prgnam):
        '''
        Print error message if build failed
        '''
        self.template(78)
        print("| Build package {0} [ {1}FAILED{2} ]".format(prgnam,
                                                            _m.color['RED'],
                                                            _m.color['ENDC']))
        self.template(78)
        print("| See log file in '{0}/var/log/slpkg/sbo/build_logs{1}' "
              "directory or read README".format(_m.color['CYAN'],
                                                _m.color['ENDC']))
        print("| file: {0}{1}".format(sbo_url, "README"))
        self.template(78)
        print   # new line at end

    def template(self, max_len):
        '''
        Print template
        '''
        print("+" + "=" * max_len)

    def checking(self):
        '''
        Message checking
        '''
        sys.stdout.write("{0}Checking ...{1}".format(_m.color['GREY'],
                                                     _m.color['ENDC']))
        sys.stdout.flush()

    def reading(self):
        '''
        Message reading
        '''
        sys.stdout.write("{0}Reading package lists ...{1}".format(
            _m.color['GREY'], _m.color['ENDC']))
        sys.stdout.flush()

    def resolving(self):
        '''
        Message resolving
        '''
        sys.stdout.write("{0}Resolving dependencies ...{1}".format(
            _m.color['GREY'], _m.color['ENDC']))
        sys.stdout.flush()

    def done(self):
        '''
        Message done
        '''
        sys.stdout.write("{0}Done{1}\n".format(_m.color['GREY'],
                                               _m.color['ENDC']))

    def pkg(self, count):
        '''
        Print singular plural
        '''
        message = "package"
        if count > 1:
            message = message + "s"
        return message

    def not_found(self, if_upgrade):
        '''
        Message not found packages
        '''
        if if_upgrade:
            print('\nNot found packages for upgrade\n')
        else:
            print('\nNot found packages for installation\n')

    def upg_inst(self, if_upgrade):
        '''
        Message installing or upgrading
        '''
        if not if_upgrade:
            print("Installing:")
        else:
            print("Upgrading:")

    def answer(self):
        '''
        Message answer
        '''
        if _m.default_answer == "y":
            answer = _m.default_answer
        else:
            answer = raw_input("Would you like to continue [Y/n]? ")
        return answer

    def reference(self, install, upgrade):
        '''
        Reference list with packages installed
        and upgraded
        '''
        self.template(78)
        print("| Total {0} {1} installed and {2} {3} upgraded".format(
            len(install), self.pkg(len(install)),
            len(upgrade), self.pkg(len(upgrade))))
        self.template(78)
        for installed in (install + upgrade):
            name = '-'.join(installed.split('-')[:-1])
            if find_package(installed, _m.pkg_path):
                if installed in upgrade:
                    print("| Package {0} upgraded successfully".format(name))
                else:
                    print("| Package {0} installed successfully".format(name))
            else:
                print("| Package {0} NOT installed".format(name))
        self.template(78)
