#!/usr/bin/python
# -*- coding: utf-8 -*-

# arguments.py file is part of slpkg.

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


from repolist import RepoList
from __metadata__ import MetaData as _m


def options():
    arguments = [
        "\nslpkg - version {0}, set: {1}\n".format(_m.__version__,
                                                   _m.slack_rel),
        "Slpkg is a user-friendly package manager for Slackware "
        "installations\n",
        "Commands:",
        "   update                                   update all package "
        "lists",
        "   re-create                                recreate package lists",
        "   repo-add [repository name] [URL]         add custom repository",
        "   repo-remove [repository]                 remove custom repository",
        "   repo-list                                list all repositories",
        "   repo-info [repository]                   repository information",
        "   update slpkg                             check and update slpkg\n",
        "Optional arguments:",
        "  -h, --help                                show this help message "
        "and exit",
        "  -v, --version                             print version and exit",
        "  -a, [script.tar.gz] [source...]           auto build SBo packages",
        "  -b, --list, [package...] --add, --remove  add, remove packages in "
        "blacklist",
        "  -q, --list, [package...] --add, --remove  add, remove SBo packages "
        "in queue",
        "  -q, --build, --install, --build-install   build, install packages "
        "from queue",
        "  -g, --config, --config=[editor]           configuration file "
        "management",
        "  -l, [repository], --index, --installed    list of repositories "
        "packages",
        "  -c, [repository] --upgrade                check for updated "
        "packages",
        "  -s, [repository] [package...]             download, build & install "
        "packages",
        "  -t, [repository] [package]                package tracking "
        "dependencies",
        "  -p, [repository] [package], --color=[]    print package description",
        "  -n, [package]                             view SBo packages "
        "through network",
        "  -f, [package...]                          find installed packages",
        "  -i, [package...]                          install binary packages",
        "  -u, [package...]                          upgrade binary packages",
        "  -o, [package...]                          reinstall binary packages",
        "  -r, [package...]                          remove binary packages",
        "  -d, [package...]                          display the contents\n",
    ]
    for opt in arguments:
        print(opt)


def usage(repo):
    error_repo = ""
    if repo and repo not in _m.repositories:
        all_repos = RepoList().all_repos
        del RepoList().all_repos
        if repo in all_repos:
            error_repo = ("slpkg: error: repository '{0}' is not activated"
                          "\n".format(repo))
        else:
            error_repo = ("slpkg: error: repository '{0}' does not exist"
                          "\n".format(repo))
    view = [
        "\nslpkg - version {0}, set: {1}\n".format(_m.__version__,
                                                   _m.slack_rel),
        "Usage: slpkg Commands:",
        "             [update] [re-create] [repo-add [repository name] [URL]]",
        "             [repo-remove [repository]] [repo-list]",
        "             [repo-info [repository]] [update [slpkg]]\n",
        "             Optional arguments:",
        "             [-h] [-v] [-a [script.tar.gz] [sources...]]",
        "             [-b --list, [...] --add, --remove]",
        "             [-q --list, [...] --add, --remove]",
        "             [-q --build, --install, --build-install]",
        "             [-g --config, --config=[editor]]",
        "             [-l [repository], --index, --installed]",
        "             [-c [repository] --upgrade]",
        "             [-s [repository] [package...]",
        "             [-t [repository] [package]",
        "             [-p [repository] [package], --color=[]]",
        "             [-n] [-f [...]] [-i [...]] [-u [...]]",
        "             [-o  [...]] [-r [...]] [-d [...]]\n",
        error_repo,
        "For more information try 'slpkg --help' or view manpage\n"
    ]
    for usg in view:
        print(usg)
