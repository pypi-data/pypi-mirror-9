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

from slpkg.sizes import units
from slpkg.remove import delete
from slpkg.toolbar import status
from slpkg.repositories import Repo
from slpkg.messages import template
from slpkg.checksum import check_md5
from slpkg.blacklist import BlackList
from slpkg.downloader import Download
from slpkg.grep_md5 import pkg_checksum
from slpkg.splitting import split_package
from slpkg.__metadata__ import (
    pkg_path,
    lib_path,
    slpkg_tmp_packages,
    default_answer,
    color,
    slacke_sub_repo,
    default_repositories
)

from slpkg.pkg.find import find_package
from slpkg.pkg.manager import PackageManager

from slpkg.slack.slack_version import slack_ver

from greps import repo_data


class OthersUpgrade(object):

    def __init__(self, repo, version):
        self.repo = repo
        self.version = version
        self.tmp_path = slpkg_tmp_packages
        sys.stdout.write("{0}Reading package lists ...{1}".format(
            color['GREY'], color['ENDC']))
        sys.stdout.flush()
        self.step = 700

        if repo in default_repositories:
            exec('self._init_{0}()'.format(self.repo))
        else:
            exec('self._init_custom()')

        f = open(self.lib, "r")
        self.PACKAGES_TXT = f.read()
        f.close()

    def _init_custom(self):
        self.lib = lib_path + "{0}_repo/PACKAGES.TXT".format(self.repo)
        self.mirror = "{0}".format(Repo().custom_repository()[self.repo])

    def _init_rlw(self):
        self.lib = lib_path + "rlw_repo/PACKAGES.TXT"
        self.mirror = "{0}{1}/".format(Repo().rlw(), slack_ver())

    def _init_alien(self):
        self.lib = lib_path + "alien_repo/PACKAGES.TXT"
        self.mirror = Repo().alien()
        self.step = self.step * 2

    def _init_slacky(self):
        self.lib = lib_path + "slacky_repo/PACKAGES.TXT"
        arch = ""
        if os.uname()[4] == "x86_64":
            arch = "64"
        self.mirror = "{0}slackware{1}-{2}/".format(Repo().slacky(), arch,
                                                    slack_ver())
        self.step = self.step * 2

    def _init_studio(self):
        self.lib = lib_path + "studio_repo/PACKAGES.TXT"
        arch = ""
        if os.uname()[4] == "x86_64":
            arch = "64"
        self.mirror = "{0}slackware{1}-{2}/".format(Repo().studioware(),
                                                    arch, slack_ver())
        self.step = self.step * 2

    def _init_slackr(self):
        self.lib = lib_path + "slackr_repo/PACKAGES.TXT"
        self.mirror = Repo().slackers()
        self.step = self.step * 2

    def _init_slonly(self):
        self.lib = lib_path + "slonly_repo/PACKAGES.TXT"
        arch = "{0}-x86".format(slack_ver())
        if os.uname()[4] == "x86_64":
            arch = "{0}-x86_64".format(slack_ver())
        self.mirror = "{0}{1}/".format(Repo().slackonly(), arch)
        self.step = self.step * 3

    def _init_ktown(self):
        self.lib = lib_path + "ktown_repo/PACKAGES.TXT"
        self.mirror = Repo().ktown()
        self.step = self.step * 2

    def _init_multi(self):
        self.lib = lib_path + "multi_repo/PACKAGES.TXT"
        self.mirror = Repo().multi()
        self.step = self.step * 2

    def _init_slacke(self):
        arch = ""
        if os.uname()[4] == "x86_64":
            arch = "64"
        elif os.uname()[4] == "arm":
            arch = "arm"
        self.lib = lib_path + "slacke_repo/PACKAGES.TXT"
        self.mirror = "{0}slacke{1}/slackware{2}-{3}/".format(
            Repo().slacke(), slacke_sub_repo[1:-1], arch, slack_ver())
        self.step = self.step * 2

    def _init_salix(self):
        arch = "i486"
        if os.uname()[4] == "x86_64":
            arch = "x86_64"
        self.lib = lib_path + "salix_repo/PACKAGES.TXT"
        self.mirror = "{0}{1}/{2}/".format(Repo().salix(), arch, slack_ver())
        self.step = self.step * 2

    def _init_slackl(self):
        arch = "i486"
        if os.uname()[4] == "x86_64":
            arch = "x86_64"
        self.lib = lib_path + "slackl_repo/PACKAGES.TXT"
        self.mirror = "{0}{1}/current/".format(Repo().slackel(), arch)
        self.step = self.step * 2

    def _init_rested(self):
        self.lib = lib_path + "rested_repo/PACKAGES.TXT"
        self.mirror = Repo().restricted()
        self.step = self.step * 2

    def start(self):
        '''
        Install packages from official Slackware distribution
        '''
        try:
            (pkg_for_upgrade, dwn_links, upgrade_all, comp_sum,
             uncomp_sum) = self.store()
            sys.stdout.write("{0}Done{1}\n".format(color['GREY'],
                                                   color['ENDC']))
            print("")   # new line at start
            if upgrade_all:
                template(78)
                print("{0}{1}{2}{3}{4}{5}{6}{7}{8}{9}{10}".format(
                    "| Package", " " * 17,
                    "New version", " " * 9,
                    "Arch", " " * 4,
                    "Build", " " * 2,
                    "Repos", " " * 9,
                    "Size"))
                template(78)
                print("Upgrading:")
                views(pkg_for_upgrade, upgrade_all, comp_sum, self.repo)
                unit, size = units(comp_sum, uncomp_sum)
                msg = msgs(upgrade_all)
                print("\nInstalling summary")
                print("=" * 79)
                print("{0}Total {1} {2} will be upgraded.".format(
                    color['GREY'], len(upgrade_all), msg))
                print("Need to get {0} {1} of archives.".format(size[0],
                                                                unit[0]))
                print("After this process, {0} {1} of additional disk "
                      "space will be used.{2}".format(size[1], unit[1],
                                                      color['ENDC']))
                if default_answer == "y":
                    answer = default_answer
                else:
                    answer = raw_input("\nWould you like to continue [Y/n]? ")
                if answer in ['y', 'Y']:
                    upgrade_all.reverse()
                    Download(self.tmp_path, dwn_links).start()
                    upgrade(self.tmp_path, upgrade_all, self.repo, self.version)
                    delete(self.tmp_path, upgrade_all)
            else:
                print("No new updates from repository '{0}'\n".format(
                    self.repo))
        except KeyboardInterrupt:
            print("")   # new line at exit
            sys.exit(0)

    def store(self):
        '''
        Store and return packages for install
        '''
        pkg_for_upgrade, dwn, install, comp_sum, uncomp_sum = (
            [] for i in range(5))
        # name = data[0]
        # location = data[1]
        # size = data[2]
        # unsize = data[3]
        data = repo_data(self.PACKAGES_TXT, self.step, self.repo, self.version)
        index, toolbar_width = 0, 700
        for pkg in self.installed():
            index += 1
            toolbar_width = status(index, toolbar_width, 10)
            for name, loc, comp, uncomp in zip(data[0], data[1], data[2],
                                               data[3]):
                inst_pkg = split_package(pkg)
                if name:    # this tips because some pkg_name is empty
                    repo_pkg = split_package(name[:-4])
                if (repo_pkg[0] == inst_pkg[0] and
                        repo_pkg[1] > inst_pkg[1] and
                        inst_pkg[0] not in BlackList().packages()):
                    # store downloads packages by repo
                    dwn.append("{0}{1}/{2}".format(self.mirror, loc, name))
                    install.append(name)
                    comp_sum.append(comp)
                    uncomp_sum.append(uncomp)
                    pkg_for_upgrade.append('{0}-{1}'.format(
                        inst_pkg[0], inst_pkg[1]))
        return [pkg_for_upgrade, dwn, install, comp_sum, uncomp_sum]

    def installed(self):
        '''
        Return all installed packages
        '''
        return find_package('', pkg_path)


def views(pkg_for_upgrade, upgrade_all, comp_sum, repository):
    '''
    Views packages
    '''
    upg_sum = 0
    # fix repositories align
    repository = repository + (' ' * (6 - (len(repository))))
    for upg, pkg, comp in zip(pkg_for_upgrade, upgrade_all, comp_sum):
        pkg_split = split_package(pkg[:-4])
        upg_sum += 1
        print(" {0}{1}{2}{3} {4}{5} {6}{7}{8}{9}{10}{11:>10}{12}".format(
            color['YELLOW'], upg, color['ENDC'],
            " " * (24-len(upg)), pkg_split[1],
            " " * (19-len(pkg_split[1])), pkg_split[2],
            " " * (8-len(pkg_split[2])), pkg_split[3],
            " " * (7-len(pkg_split[3])), repository,
            comp, " K"))
    return upg_sum


def msgs(upgrade_all):
    '''
    Print singular plural
    '''
    msg_pkg = "package"
    if len(upgrade_all) > 1:
        msg_pkg = msg_pkg + "s"
    return msg_pkg


def upgrade(tmp_path, upgrade_all, repo, version):
    '''
    Install or upgrade packages
    '''
    for pkg in upgrade_all:
        package = (tmp_path + pkg).split()
        if repo == "alien" and version == "stable":
            check_md5(pkg_checksum("/" + slack_ver() + "/" + pkg, repo),
                      tmp_path + pkg)
        elif repo == "alien" and version == "current":
            check_md5(pkg_checksum("/" + version + "/" + pkg, repo),
                      tmp_path + pkg)
        else:
            check_md5(pkg_checksum(pkg, repo), tmp_path + pkg)
        print("[ {0}upgrading{1} ] --> {2}".format(color['YELLOW'],
                                                   color['ENDC'], pkg[:-4]))
        PackageManager(package).upgrade()
