#!/usr/bin/python
# -*- coding: utf-8 -*-

# patches.py file is part of slpkg.

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

from slpkg.sizes import units
from slpkg.url_read import URL
from slpkg.remove import delete
from slpkg.messages import template
from slpkg.checksum import check_md5
from slpkg.blacklist import BlackList
from slpkg.downloader import Download
from slpkg.grep_md5 import pkg_checksum
from slpkg.splitting import split_package
from slpkg.__metadata__ import (
    pkg_path,
    slpkg_tmp_patches,
    default_answer,
    color
)

from slpkg.pkg.find import find_package
from slpkg.pkg.manager import PackageManager

from mirrors import mirrors
from greps import slack_data
from slack_version import slack_ver


class Patches(object):

    def __init__(self, version):
        self.version = version
        self.patch_path = slpkg_tmp_patches
        sys.stdout.write("{0}Reading package lists ...{1}".format(
            color['GREY'], color['ENDC']))
        sys.stdout.flush()
        if self.version == "stable":
            self.PACKAGES_TXT = URL(mirrors("PACKAGES.TXT",
                                            "patches/")).reading()
            self.step = 10
        else:
            self.PACKAGES_TXT = URL(mirrors("PACKAGES.TXT", "")).reading()
            self.step = 700

    def start(self):
        '''
        Install new patches from official Slackware mirrors
        '''
        try:
            (pkg_for_upgrade, dwn_links, upgrade_all, comp_sum,
             uncomp_sum) = self.store()
            sys.stdout.write("{0}Done{1}\n".format(color['GREY'],
                                                   color['ENDC']))
            if upgrade_all:
                print("\nThese packages need upgrading:\n")
                template(78)
                print("{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}{10}".format(
                    "| Package", " " * 17,
                    "Version", " " * 12,
                    "Arch", " " * 4,
                    "Build", " " * 2,
                    "Repos", " " * 10,
                    "Size"))
                template(78)
                print("Upgrading:")
                views(pkg_for_upgrade, upgrade_all, comp_sum)
                unit, size = units(comp_sum, uncomp_sum)
                print("\nInstalling summary")
                print("=" * 79)
                print("{0}Total {1} {2} will be upgraded.".format(
                    color['GREY'], len(upgrade_all), msgs(upgrade_all)))
                print("Need to get {0} {1} of archives.".format(size[0],
                                                                unit[0]))
                print("After this process, {0} {1} of additional disk space "
                      "will be used.{2}".format(size[1], unit[1],
                                                color['ENDC']))
                if default_answer == "y":
                    answer = default_answer
                else:
                    answer = raw_input("\nWould you like to continue [Y/n]? ")
                if answer in ['y', 'Y']:
                    Download(self.patch_path, dwn_links).start()
                    upgrade(self.patch_path, upgrade_all)
                    kernel(upgrade_all)
                    delete(self.patch_path, upgrade_all)
            else:
                slack_arch = ""
                if os.uname()[4] == "x86_64":
                    slack_arch = 64
                print("\nSlackware{0} '{1}' v{2} distribution is up to "
                      "date\n".format(slack_arch, self.version, slack_ver()))
        except KeyboardInterrupt:
            print("")   # new line at exit
            sys.exit(0)

    def store(self):
        '''
        Store and return packages for upgrading
        '''
        (pkg_for_upgrade, dwn, upgrade, comp_sum,
         uncomp_sum) = ([] for i in range(5))
        data = slack_data(self.PACKAGES_TXT, self.step)
        black = BlackList().packages()
        for name, loc, comp, uncomp in zip(data[0], data[1], data[2], data[3]):
            inst_pkg = find_package(split_package(name)[0] + "-", pkg_path)
            if (inst_pkg and not os.path.isfile(pkg_path + name[:-4]) and
                    split_package(''.join(inst_pkg[0])) not in black):
                dwn.append("{0}{1}/{2}".format(mirrors("", ""), loc, name))
                comp_sum.append(comp)
                uncomp_sum.append(uncomp)
                upgrade.append(name)
                pkg_for_upgrade.append('{0}-{1}'.format(
                    split_package(''.join(inst_pkg[0]))[0],
                    split_package(''.join(inst_pkg[0]))[1]))
        return [pkg_for_upgrade, dwn, upgrade, comp_sum, uncomp_sum]


def views(pkg_for_upgrade, upgrade_all, comp_sum):
    '''
    Views packages
    '''
    for upg, upgrade, size in sorted(zip(pkg_for_upgrade, upgrade_all,
                                         comp_sum)):
        pkg_split = split_package(upgrade[:-4])
        print(" {0}{1}{2}{3} {4}{5} {6}{7}{8}{9}{10}{11:>12}{12}".format(
            color['YELLOW'], upg, color['ENDC'],
            " " * (24-len(upg)), pkg_split[1],
            " " * (18-len(pkg_split[1])), pkg_split[2],
            " " * (8-len(pkg_split[2])), pkg_split[3],
            " " * (7-len(pkg_split[3])), "Slack",
            size, " K"))


def msgs(upgrade_all):
    '''
    Print singular plural
    '''
    msg_pkg = "package"
    if len(upgrade_all) > 1:
        msg_pkg = msg_pkg + "s"
    return msg_pkg


def upgrade(patch_path, upgrade_all):
    '''
    Upgrade packages
    '''
    for pkg in upgrade_all:
        check_md5(pkg_checksum(pkg, "slack_patches"), patch_path + pkg)
        print("[ {0}upgrading{1} ] --> {2}".format(color['YELLOW'],
                                                   color['ENDC'], pkg[:-4]))
        PackageManager((patch_path + pkg).split()).upgrade()


def kernel(upgrade_all):
    '''
    Check if kernel upgraded if true
    then reinstall 'lilo'
    '''
    for core in upgrade_all:
        if "kernel" in core:
            if default_answer == "y":
                answer = default_answer
            else:
                print("")
                template(78)
                print("| {0}*** HIGHLY recommended reinstall 'LILO' "
                      "***{1}".format(color['RED'], color['ENDC']))
                template(78)
                answer = raw_input("\nThe kernel has been upgraded, "
                                   "reinstall `LILO` [Y/n]? ")
            if answer in ['y', 'Y']:
                subprocess.call("lilo", shell=True)
                break
