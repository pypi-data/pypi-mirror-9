#!/usr/bin/python
# -*- coding: utf-8 -*-

# init.py file is part of slpkg.

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

from url_read import URL
from toolbar import status
from repositories import Repo
from file_size import FileSize
from __metadata__ import (
    color,
    log_path,
    lib_path,
    tmp_path,
    conf_path,
    build_path,
    repositories,
    slpkg_tmp_packages,
    slpkg_tmp_patches,
    slacke_sub_repo,
    default_repositories
)

from slack.mirrors import mirrors
from slack.slack_version import slack_ver


class Initialization(object):

    def __init__(self):
        if not os.path.exists(conf_path):
            os.mkdir(conf_path)
        if not os.path.exists(log_path):
            os.mkdir(log_path)
        if not os.path.exists(lib_path):
            os.mkdir(lib_path)
        if not os.path.exists(tmp_path):
            os.mkdir(tmp_path)
        if not os.path.exists(build_path):
            os.makedirs(build_path)
        if not os.path.exists(slpkg_tmp_packages):
            os.makedirs(slpkg_tmp_packages)
        if not os.path.exists(slpkg_tmp_patches):
            os.makedirs(slpkg_tmp_patches)

    def custom(self, name):
        '''
        Creating user select repository local library
        '''
        repo = Repo().custom_repository()[name]
        log = log_path + name + "/"
        lib = lib_path + "{0}_repo/".format(name)
        lib_file = "PACKAGES.TXT"
        lst_file = ""
        md5_file = "CHECKSUMS.md5"
        log_file = "ChangeLog.txt"
        if not os.path.exists(log):
            os.mkdir(log)
        if not os.path.exists(lib):
            os.mkdir(lib)
        packages_txt = "{0}{1}".format(repo, lib_file)
        filelist_txt = ""
        checksums_md5 = "{0}{1}".format(repo, md5_file)
        changelog_txt = "{0}{1}".format(repo, log_file)
        self.write(lib, lib_file, packages_txt)
        self.write(lib, md5_file, checksums_md5)
        self.write(log, log_file, changelog_txt)
        self.remote(log, log_file, changelog_txt, lib, lib_file,
                    packages_txt, md5_file, checksums_md5, lst_file,
                    filelist_txt)

    def slack(self):
        '''
        Creating slack local libraries
        '''
        log = log_path + "slack/"
        lib = lib_path + "slack_repo/"
        lib_file = "PACKAGES.TXT"
        lst_file = ""
        md5_file = "CHECKSUMS.md5"
        log_file = "ChangeLog.txt"
        if not os.path.exists(log):
            os.mkdir(log)
        if not os.path.exists(lib):
            os.mkdir(lib)
        packages = mirrors(lib_file, "")
        filelist_txt = ""
        pkg_checksums = mirrors(md5_file, "")
        extra = mirrors(lib_file, "extra/")
        ext_checksums = mirrors(md5_file, "extra/")
        pasture = mirrors(lib_file, "pasture/")
        pas_checksums = mirrors(md5_file, "pasture/")
        patches_txt = mirrors(lib_file, "patches/")
        patches_md5 = mirrors(md5_file, "patches/")
        packages_txt = ("{0} {1} {2} {3}".format(packages, extra, pasture,
                                                 patches_txt))
        checksums_md5 = ("{0} {1} {2} {3}".format(pkg_checksums, ext_checksums,
                                                  pas_checksums, patches_md5))
        changelog_txt = mirrors(log_file, "")
        self.write(lib, lib_file, packages_txt)
        self.write(lib, md5_file, checksums_md5)
        self.write(log, log_file, changelog_txt)
        self.remote(log, log_file, changelog_txt, lib, lib_file, packages_txt,
                    md5_file, checksums_md5, lst_file, filelist_txt)

    def sbo(self):
        '''
        Creating sbo local library
        '''
        repo = Repo().sbo()
        log = log_path + "sbo/"
        lib = lib_path + "sbo_repo/"
        lib_file = "SLACKBUILDS.TXT"
        lst_file = ""
        md5_file = ""
        log_file = "ChangeLog.txt"
        if not os.path.exists(log):
            os.mkdir(log)
        if not os.path.exists(lib):
            os.mkdir(lib)
        packages_txt = "{0}{1}/{2}".format(repo, slack_ver(), lib_file)
        filelist_txt = ""
        checksums_md5 = ""
        changelog_txt = "{0}/{1}/{2}".format(repo, slack_ver(), log_file)
        self.write(lib, lib_file, packages_txt)
        self.write(log, log_file, changelog_txt)
        self.remote(log, log_file, changelog_txt, lib, lib_file, packages_txt,
                    md5_file, checksums_md5, lst_file, filelist_txt)

    def rlw(self):
        '''
        Creating rlw local library
        '''
        repo = Repo().rlw()
        log = log_path + "rlw/"
        lib = lib_path + "rlw_repo/"
        lib_file = "PACKAGES.TXT"
        lst_file = ""
        md5_file = "CHECKSUMS.md5"
        log_file = "ChangeLog.txt"
        if not os.path.exists(log):
            os.mkdir(log)
        if not os.path.exists(lib):
            os.mkdir(lib)
        packages_txt = "{0}{1}/{2}".format(repo, slack_ver(), lib_file)
        filelist_txt = ""
        checksums_md5 = "{0}{1}/{2}".format(repo, slack_ver(), md5_file)
        changelog_txt = "{0}{1}/{2}".format(repo, slack_ver(), log_file)
        self.write(lib, lib_file, packages_txt)
        self.write(lib, md5_file, checksums_md5)
        self.write(log, log_file, changelog_txt)
        self.remote(log, log_file, changelog_txt, lib, lib_file, packages_txt,
                    md5_file, checksums_md5, lst_file, filelist_txt)

    def alien(self):
        '''
        Creating alien local library
        '''
        repo = Repo().alien()
        log = log_path + "alien/"
        lib = lib_path + "alien_repo/"
        lib_file = "PACKAGES.TXT"
        lst_file = ""
        md5_file = "CHECKSUMS.md5"
        log_file = "ChangeLog.txt"
        if not os.path.exists(log):
            os.mkdir(log)
        if not os.path.exists(lib):
            os.mkdir(lib)
        packages_txt = "{0}{1}".format(repo, lib_file)
        filelist_txt = ""
        checksums_md5 = "{0}{1}".format(repo, md5_file)
        changelog_txt = "{0}{1}".format(repo, log_file)
        self.write(lib, lib_file, packages_txt)
        self.write(lib, md5_file, checksums_md5)
        self.write(log, log_file, changelog_txt)
        self.remote(log, log_file, changelog_txt, lib, lib_file, packages_txt,
                    md5_file, checksums_md5, lst_file, filelist_txt)

    def slacky(self):
        '''
        Creating alien local library
        '''
        ar = ""
        arch = os.uname()[4]
        repo = Repo().slacky()
        log = log_path + "slacky/"
        lib = lib_path + "slacky_repo/"
        lib_file = "PACKAGES.TXT"
        lst_file = ""
        md5_file = "CHECKSUMS.md5"
        log_file = "ChangeLog.txt"
        if not os.path.exists(log):
            os.mkdir(log)
        if not os.path.exists(lib):
            os.mkdir(lib)
        if arch == "x86_64":
            ar = "64"
        packages_txt = "{0}slackware{1}-{2}/{3}".format(repo, ar, slack_ver(),
                                                        lib_file)
        filelist_txt = ""
        checksums_md5 = "{0}slackware{1}-{2}/{3}".format(repo, ar, slack_ver(),
                                                         md5_file)

        changelog_txt = "{0}slackware{1}-{2}/{3}".format(repo, ar, slack_ver(),
                                                         log_file)
        self.write(lib, lib_file, packages_txt)
        self.write(lib, md5_file, checksums_md5)
        self.write(log, log_file, changelog_txt)
        self.remote(log, log_file, changelog_txt, lib, lib_file, packages_txt,
                    md5_file, checksums_md5, lst_file, filelist_txt)

    def studio(self):
        '''
        Creating alien local library
        '''
        ar = ""
        arch = os.uname()[4]
        repo = Repo().studioware()
        log = log_path + "studio/"
        lib = lib_path + "studio_repo/"
        lib_file = "PACKAGES.TXT"
        lst_file = ""
        md5_file = "CHECKSUMS.md5"
        log_file = "ChangeLog.txt"
        if not os.path.exists(log):
            os.mkdir(log)
        if not os.path.exists(lib):
            os.mkdir(lib)
        if arch == "x86_64":
            ar = "64"
        packages_txt = "{0}slackware{1}-{2}/{3}".format(repo, ar, slack_ver(),
                                                        lib_file)
        filelist_txt = ""
        checksums_md5 = "{0}slackware{1}-{2}/{3}".format(repo, ar, slack_ver(),
                                                         md5_file)
        changelog_txt = "{0}slackware{1}-{2}/{3}".format(repo, ar, slack_ver(),
                                                         log_file)
        self.write(lib, lib_file, packages_txt)
        self.write(lib, md5_file, checksums_md5)
        self.write(log, log_file, changelog_txt)
        self.remote(log, log_file, changelog_txt, lib, lib_file, packages_txt,
                    md5_file, checksums_md5, lst_file, filelist_txt)

    def slackr(self):
        '''
        Creating slackers local library
        '''
        repo = Repo().slackers()
        log = log_path + "slackr/"
        lib = lib_path + "slackr_repo/"
        lib_file = "PACKAGES.TXT"
        lst_file = "FILELIST.TXT"
        md5_file = "CHECKSUMS.md5"
        log_file = "ChangeLog.txt"
        if not os.path.exists(log):
            os.mkdir(log)
        if not os.path.exists(lib):
            os.mkdir(lib)
        packages_txt = "{0}{1}".format(repo, lib_file)
        filelist_txt = "{0}{1}".format(repo, lst_file)
        checksums_md5 = "{0}{1}".format(repo, md5_file)
        changelog_txt = "{0}{1}".format(repo, log_file)
        self.write(lib, lib_file, packages_txt)
        self.write(lib, lst_file, filelist_txt)
        self.write(lib, md5_file, checksums_md5)
        self.write(log, log_file, changelog_txt)
        self.remote(log, log_file, changelog_txt, lib, lib_file, packages_txt,
                    md5_file, checksums_md5, lst_file, filelist_txt)

    def slonly(self):
        '''
        Creating slackers local library
        '''
        ar = "{0}-x86".format(slack_ver())
        arch = os.uname()[4]
        repo = Repo().slackonly()
        log = log_path + "slonly/"
        lib = lib_path + "slonly_repo/"
        lib_file = "PACKAGES.TXT"
        lst_file = "FILELIST.TXT"
        md5_file = "CHECKSUMS.md5"
        log_file = "ChangeLog.txt"
        if not os.path.exists(log):
            os.mkdir(log)
        if not os.path.exists(lib):
            os.mkdir(lib)
        if arch == "x86_64":
            ar = "{0}-x86_64".format(slack_ver())
        packages_txt = "{0}{1}/{2}".format(repo, ar, lib_file)
        filelist_txt = "{0}{1}/{2}".format(repo, ar, lst_file)
        checksums_md5 = "{0}{1}/{2}".format(repo, ar, md5_file)
        # ChangeLog.txt file available only for x86 arch
        changelog_txt = "{0}{1}-x86/{2}".format(repo, slack_ver(), log_file)
        self.write(lib, lib_file, packages_txt)
        self.write(lib, lst_file, filelist_txt)
        self.write(lib, md5_file, checksums_md5)
        self.write(log, log_file, changelog_txt)
        self.remote(log, log_file, changelog_txt, lib, lib_file, packages_txt,
                    md5_file, checksums_md5, lst_file, filelist_txt)

    def ktown(self):
        '''
        Creating alien ktown local library
        '''
        repo = Repo().ktown()
        log = log_path + "ktown/"
        lib = lib_path + "ktown_repo/"
        lib_file = "PACKAGES.TXT"
        lst_file = ""
        md5_file = "CHECKSUMS.md5"
        log_file = "ChangeLog.txt"
        if not os.path.exists(log):
            os.mkdir(log)
        if not os.path.exists(lib):
            os.mkdir(lib)
        packages_txt = "{0}{1}".format(repo, lib_file)
        filelist_txt = ""
        checksums_md5 = "{0}{1}".format(repo, md5_file)
        changelog_txt = "{0}{1}".format(repo, log_file)
        self.write(lib, lib_file, packages_txt)
        self.write(lib, md5_file, checksums_md5)
        self.write(log, log_file, changelog_txt)
        self.remote(log, log_file, changelog_txt, lib, lib_file, packages_txt,
                    md5_file, checksums_md5, lst_file, filelist_txt)

    def multi(self):
        '''
        Creating alien multilib local library
        '''
        repo = Repo().multi()
        log = log_path + "multi/"
        lib = lib_path + "multi_repo/"
        lib_file = "PACKAGES.TXT"
        lst_file = ""
        md5_file = "CHECKSUMS.md5"
        log_file = "ChangeLog.txt"
        if not os.path.exists(log):
            os.mkdir(log)
        if not os.path.exists(lib):
            os.mkdir(lib)
        packages_txt = "{0}{1}".format(repo, lib_file)
        filelist_txt = ""
        checksums_md5 = "{0}{1}".format(repo, md5_file)
        changelog_txt = "{0}{1}".format(repo, log_file)
        self.write(lib, lib_file, packages_txt)
        self.write(lib, md5_file, checksums_md5)
        self.write(log, log_file, changelog_txt)
        self.remote(log, log_file, changelog_txt, lib, lib_file, packages_txt,
                    md5_file, checksums_md5, lst_file, filelist_txt)

    def slacke(self):
        '''
        Creating Slacke local library
        '''
        ar = ""
        arch = os.uname()[4]
        repo = Repo().slacke()
        log = log_path + "slacke/"
        lib = lib_path + "slacke_repo/"
        lib_file = "PACKAGES.TXT"
        lst_file = ""
        md5_file = "CHECKSUMS.md5"
        log_file = "ChangeLog.txt"
        if not os.path.exists(log):
            os.mkdir(log)
        if not os.path.exists(lib):
            os.mkdir(lib)
        if arch == "x86_64":
            ar = "64"
        elif arch == "arm":
            ar = "arm"
        packages_txt = "{0}slacke{1}/slackware{2}-{3}/{4}".format(
            repo, slacke_sub_repo[1:-1], ar, slack_ver(), lib_file)
        filelist_txt = ""
        checksums_md5 = "{0}slacke{1}/slackware{2}-{3}/{4}".format(
            repo, slacke_sub_repo[1:-1], ar, slack_ver(), md5_file)
        changelog_txt = "{0}slacke{1}/slackware{2}-{3}/{4}".format(
            repo, slacke_sub_repo[1:-1], ar, slack_ver(), log_file)
        self.write(lib, lib_file, packages_txt)
        self.write(lib, md5_file, checksums_md5)
        self.write(log, log_file, changelog_txt)
        self.remote(log, log_file, changelog_txt, lib, lib_file, packages_txt,
                    md5_file, checksums_md5, lst_file, filelist_txt)

    def salix(self):
        '''
        Creating SalixOS local library
        '''
        ar = "i486"
        arch = os.uname()[4]
        repo = Repo().salix()
        log = log_path + "salix/"
        lib = lib_path + "salix_repo/"
        lib_file = "PACKAGES.TXT"
        lst_file = ""
        md5_file = "CHECKSUMS.md5"
        log_file = "ChangeLog.txt"
        if not os.path.exists(log):
            os.mkdir(log)
        if not os.path.exists(lib):
            os.mkdir(lib)
        if arch == "x86_64":
            ar = "x86_64"
        packages_txt = "{0}{1}/{2}/{3}".format(repo, ar, slack_ver(), lib_file)
        filelist_txt = ""
        checksums_md5 = "{0}{1}/{2}/{3}".format(repo, ar, slack_ver(), md5_file)
        changelog_txt = "{0}{1}/{2}/{3}".format(repo, ar, slack_ver(), log_file)
        self.write(lib, lib_file, packages_txt)
        self.write(lib, md5_file, checksums_md5)
        self.write(log, log_file, changelog_txt)
        self.remote(log, log_file, changelog_txt, lib, lib_file, packages_txt,
                    md5_file, checksums_md5, lst_file, filelist_txt)

    def slackl(self):
        '''
        Creating SalixOS local library
        '''
        ar = "i486"
        arch = os.uname()[4]
        repo = Repo().slackel()
        log = log_path + "slackl/"
        lib = lib_path + "slackl_repo/"
        lib_file = "PACKAGES.TXT"
        lst_file = ""
        md5_file = "CHECKSUMS.md5"
        log_file = "ChangeLog.txt"
        if not os.path.exists(log):
            os.mkdir(log)
        if not os.path.exists(lib):
            os.mkdir(lib)
        if arch == "x86_64":
            ar = "x86_64"
        packages_txt = "{0}{1}/current/{2}".format(repo, ar, lib_file)
        filelist_txt = ""
        checksums_md5 = "{0}{1}/current/{2}".format(repo, ar, md5_file)
        changelog_txt = "{0}{1}/current/{2}".format(repo, ar, log_file)
        self.write(lib, lib_file, packages_txt)
        self.write(lib, md5_file, checksums_md5)
        self.write(log, log_file, changelog_txt)
        self.remote(log, log_file, changelog_txt, lib, lib_file, packages_txt,
                    md5_file, checksums_md5, lst_file, filelist_txt)

    def rested(self):
        '''
        Creating alien local library
        '''
        repo = Repo().restricted()
        log = log_path + "rested/"
        lib = lib_path + "rested_repo/"
        lib_file = "PACKAGES.TXT"
        lst_file = ""
        md5_file = "CHECKSUMS.md5"
        log_file = "ChangeLog.txt"
        if not os.path.exists(log):
            os.mkdir(log)
        if not os.path.exists(lib):
            os.mkdir(lib)
        packages_txt = "{0}{1}".format(repo, lib_file)
        filelist_txt = ""
        checksums_md5 = "{0}{1}".format(repo, md5_file)
        changelog_txt = "{0}{1}".format(repo, log_file)
        self.write(lib, lib_file, packages_txt)
        self.write(lib, md5_file, checksums_md5)
        self.write(log, log_file, changelog_txt)
        self.remote(log, log_file, changelog_txt, lib, lib_file, packages_txt,
                    md5_file, checksums_md5, lst_file, filelist_txt)

    @staticmethod
    def write(path, data_file, file_url):
        '''
        Write repositories files in /var/lib/slpkg
        and /var/log/slpkg
        '''
        FILE_TXT = ""
        if not os.path.isfile(path + data_file):
            for fu in file_url.split():
                FILE_TXT += URL(fu).reading()
            with open("{0}{1}".format(path, data_file), "w") as f:
                toolbar_width, index = 2, 0
                for line in FILE_TXT.splitlines():
                    index += 1
                    toolbar_width = status(index, toolbar_width, 700)
                    f.write(line + "\n")
                f.close()

    @staticmethod
    def remote(*args):
        '''
        args[0] = log
        args[1] = log_file
        args[2] = changelog_txt
        args[3] = lib
        args[4] = lib_file
        args[5] = packages_txt
        args[6] = md5_file
        args[7] = checksums_md5
        args[8] = lst_file
        args[9] = filelist_txt

        We take the size of ChangeLog.txt from the server and locally.
        If the two files differ in size delete and replace all files with new.
        '''
        PACKAGES_TXT = ""
        toolbar_width, index = 2, 0
        server = FileSize(args[2]).server()
        local = FileSize(args[0] + args[1]).local()
        if server != local:
            # remove PACKAGES.txt
            os.remove("{0}{1}".format(args[3], args[4]))
            # remove Changelog.txt
            os.remove("{0}{1}".format(args[0], args[1]))
            # remove CHECKSUMS.md5
            if args[6]:
                os.remove("{0}{1}".format(args[3], args[6]))
            # remove FILELIST.TXT
            if args[8]:
                os.remove("{0}{1}".format(args[3], args[8]))
            # read URL's
            for fu in args[5].split():
                PACKAGES_TXT += URL(fu).reading()
            CHANGELOG_TXT = URL(args[2]).reading()
            # create CHECKSUMS.md5 file
            if args[6]:
                CHECKSUMS_md5 = URL(args[7]).reading()
                with open("{0}{1}".format(args[3], args[6]), "w") as f:
                    for line in CHECKSUMS_md5.splitlines():
                        index += 1
                        toolbar_width = status(index, toolbar_width, 700)
                        f.write(line + "\n")
                    f.close()
            # create PACKAGES.txt file
            with open("{0}{1}".format(args[3], args[4]), "w") as f:
                for line in PACKAGES_TXT.splitlines():
                    index += 1
                    toolbar_width = status(index, toolbar_width, 700)
                    f.write(line + "\n")
                f.close()
            # create ChangeLog.txt file
            with open("{0}{1}".format(args[0], args[1]), "w") as f:
                for line in CHANGELOG_TXT.splitlines():
                    index += 1
                    toolbar_width = status(index, toolbar_width, 700)
                    f.write(line + "\n")
                f.close()
            # create FILELIST.TXT file
            if args[8]:
                FILELIST_TXT = URL(args[9]).reading()
                with open("{0}{1}".format(args[3], args[8]), "w") as f:
                    for line in FILELIST_TXT.splitlines():
                        index += 1
                        toolbar_width = status(index, toolbar_width, 700)
                        f.write(line + "\n")
                    f.close()

    def re_create(self):
        '''
        Remove all package lists with changelog and checksums files
        and create lists again
        '''
        for repo in repositories:
            changelogs = '{0}{1}{2}'.format(log_path, repo, '/ChangeLog.txt')
            if os.path.isfile(changelogs):
                os.remove(changelogs)
            for f in os.listdir(lib_path + '{0}_repo/'.format(repo)):
                packages = '{0}{1}_repo/{2}'.format(lib_path, repo, f)
                if os.path.isfile(packages):
                    os.remove(packages)
        Update().repository()


class Update(object):

    def __init__(self):
        self._init = 'Initialization()'

    def repository(self):
        '''
        Update all repositories lists
        '''
        print("\nCheck and update repositories:\n")
        for repo in repositories:
            sys.stdout.write("{0}Update repository {1} ...{2}".format(
                color['GREY'], repo, color['ENDC']))
            sys.stdout.flush()
            if repo in default_repositories:
                exec('{0}.{1}()'.format(self._init, repo))
            else:
                Initialization().custom(repo)
            sys.stdout.write("{0}Done{1}\n".format(color['GREY'],
                                                   color['ENDC']))
        print("")   # new line at end
        sys.exit(0)


def check_exists_repositories():
    '''
    Checking if repositories exists by PACKAGES.TXT file
    '''
    update = False
    pkg_list = "PACKAGES.TXT"
    for repo in repositories:
        pkg_list = "PACKAGES.TXT"
        if repo == "sbo":
            pkg_list = "SLACKBUILDS.TXT"
        if not os.path.isfile("{0}{1}{2}".format(lib_path, repo,
                                                 "_repo/{0}".format(pkg_list))):
            update = True
    if update:
        print("\n  Please update packages lists. Run 'slpkg update'.\n" +
              "  This command should be used to synchronize packages\n" +
              "  lists from the repositories are enabled.\n")
        sys.exit(0)
