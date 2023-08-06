#!/usr/bin/python
# -*- coding: utf-8 -*-

# repositories.py file is part of slpkg.

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

from utils import Utils
from __metadata__ import MetaData as _m


class Repo(object):

    def __init__(self):
        self.repo_file = "/etc/slpkg/custom-repositories"
        self.repositories_list = Utils().read_file(self.repo_file)

    def add(self, repo, url):
        '''
        Write custom repository name and url in a file
        '''
        repo_name = []
        if not url.endswith('/'):
            url = url + '/'
        for line in self.repositories_list.splitlines():
            line = line.lstrip()
            if line and not line.startswith("#"):
                repo_name.append(line.split()[0])
        if (repo in _m.repositories or repo in repo_name or
                repo in _m.default_repositories):
            print("\nRepository name '{0}' exist, select different name.\n"
                  "View all repositories with command 'repo-list'.\n".format(
                      repo))
            sys.exit(0)
        elif len(repo) > 6:
            print("\nMaximum repository name length must be six (6) "
                  "characters\n")
            sys.exit(0)
        elif not url.startswith('http') or url.startswith('ftp'):
            print("\nWrong type URL '{0}'\n".format(url))
            sys.exit(0)
        with open(self.repo_file, "a") as repos:
            new_line = "  {0}{1}{2}\n".format(repo, ' ' * (10 - len(repo)), url)
            repos.write(new_line)
        repos.close()
        print("\nRepository '{0}' successfully added\n".format(repo))
        sys.exit(0)

    def remove(self, repo):
        '''
        Remove custom repository
        '''
        rem_repo = False
        with open(self.repo_file, "w") as repos:
            for line in self.repositories_list.splitlines():
                repo_name = line.split()[0]
                if repo_name != repo:
                    repos.write(line + "\n")
                else:
                    print("\nRepository '{0}' successfully "
                          "removed\n".format(repo))
                    rem_repo = True
            repos.close()
        if not rem_repo:
            print("\nRepository '{0}' doesn't exist\n".format(repo))
        sys.exit(0)

    def custom_repository(self):
        '''
        Return dictionary with repo name and url
        '''
        dict_repo = {}
        for line in self.repositories_list.splitlines():
            line = line.lstrip()
            if not line.startswith("#"):
                dict_repo[line.split()[0]] = line.split()[1]
        return dict_repo

    def slack(self):
        '''
        Official slackware repository
        '''
        default = "http://mirrors.slackware.com/slackware/"
        if os.path.isfile("/etc/slpkg/slackware-mirrors"):
            mirrors = Utils().read_file(_m.conf_path + 'slackware-mirrors')
            for line in mirrors.splitlines():
                line = line.rstrip()
                if not line.startswith("#") and line:
                    default = line.split()[-1]
        return default

    def sbo(self):
        '''
        SlackBuilds.org repository
        '''
        return "http://slackbuilds.org/slackbuilds/"

    def rlw(self):
        '''
        Robby's repoisitory
        '''
        return "http://rlworkman.net/pkgs/"

    def alien(self):
        '''
        Alien's slackbuilds repository
        '''
        return "http://www.slackware.com/~alien/slackbuilds/"

    def slacky(self):
        '''
        Slacky.eu repository
        '''
        return "http://repository.slacky.eu/"

    def studioware(self):
        '''
        Studioware repository
        '''
        return "http://studioware.org/files/packages/"

    def slackers(self):
        '''
        Slackers.it repository
        '''
        return "http://www.slackers.it/repository/"

    def slackonly(self):
        '''
        Slackonly.com repository
        '''
        return "https://slackonly.com/pub/packages/"

    def ktown(self):
        '''
        Alien's ktown repository
        '''
        return "http://alien.slackbook.org/ktown/"

    def multi(self):
        '''
        Alien's multilib repository
        '''
        return "http://www.slackware.com/~alien/multilib/"

    def slacke(self):
        '''
        Slacke slacke{17|18} repository
        '''
        return "http://ngc891.blogdns.net/pub/"

    def salix(self):
        '''
        SalixOS salix repository
        '''
        return "http://download.salixos.org/"

    def slackel(self):
        '''
        Slackel.gr slackel repository
        '''
        return "http://www.slackel.gr/repo/"

    def restricted(self):
        '''
        Slackel.gr slackel repository
        '''
        return ("http://taper.alienbase.nl/mirrors/people/alien/"
                "restricted_slackbuilds/")
