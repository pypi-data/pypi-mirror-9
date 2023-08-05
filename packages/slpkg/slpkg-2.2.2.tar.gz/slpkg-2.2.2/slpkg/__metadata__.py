#!/usr/bin/python
# -*- coding: utf-8 -*-

# __metadata__.py file is part of slpkg.

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


def remove_repositories(repositories, default_repositories):
    '''
    Remove no default repositories
    '''
    repos = []
    for repo in repositories:
        if repo in default_repositories:
            repos.append(repo)
    return repos


def update_repositories(repositories, conf_path):
    '''
    Upadate with user custom repositories
    '''
    repo_file = "{0}custom-repositories".format(conf_path)
    if os.path.isfile(repo_file):
        f = open(repo_file, "r")
        repositories_list = f.read()
        f.close()
        for line in repositories_list.splitlines():
            line = line.lstrip()
            if line and not line.startswith("#"):
                repositories.append(line.split()[0])
    return repositories


def ktown_repo(repositories):
    '''
    Find if ktown repositories enabled then
    take SUB_REPOSITORY
    '''
    for i, repo in enumerate(repositories):
        if 'ktown' in repo:
            sub = repositories[i].replace('ktown', '')
            repositories[i] = 'ktown'
            return sub


def slacke_repo(repositories):
    '''
    Find if slacke repositories enabled then
    take SUB_REPOSITORY
    '''
    for i, repo in enumerate(repositories):
        if 'slacke' in repo:
            sub = repositories[i].replace('slacke', '')
            repositories[i] = 'slacke'
            return sub


class MetaData(object):

    __all__ = "slpkg"
    __author__ = "dslackw"
    __version_info__ = (2, 2, 2)
    __version__ = "{0}.{1}.{2}".format(*__version_info__)
    __license__ = "GNU General Public License v3 (GPLv3)"
    __email__ = "d.zlatanidis@gmail.com"

    # Default configuration values
    slack_rel = "stable"

    # Configuration path
    conf_path = "/etc/{0}/".format(__all__)

    repositories = [
        'slack',
        'sbo',
        'rlw',
        'alien',
        'slacky',
        'studio',
        'slackr',
        'slonly',
        'ktown{latest}',
        'multi',
        'slacke{18}',
        'salix',
        'slackl',
        'rested'
    ]

    default_repositories = repositories[8] = 'ktown'
    default_repositories = repositories[10] = 'slacke'
    default_repositories = repositories

    tmp = "/tmp/"
    tmp_path = "{0}{1}/".format(tmp, __all__)
    build_path = "/tmp/slpkg/build/"
    slpkg_tmp_packages = tmp + "slpkg/packages/"
    slpkg_tmp_patches = tmp + "slpkg/patches/"
    del_all = "on"
    sbo_check_md5 = "on"
    del_build = "off"
    sbo_build_log = "on"
    default_answer = "n"
    remove_deps_answer = "n"
    skip_unst = "n"
    del_deps = "off"
    use_colors = "on"
    wget_options = '-c -N'

    if os.path.isfile(conf_path + "slpkg.conf"):
        f = open(conf_path + "slpkg.conf", "r")
        conf = f.read()
        f.close()
        for line in conf.splitlines():
            line = line.lstrip()
            if line.startswith("VERSION"):
                slack_rel = line[8:].strip()
                if not slack_rel:
                    slack_rel = "stable"
            if line.startswith("REPOSITORIES"):
                repositories = line[13:].strip().split(",")
            if line.startswith("BUILD_PATH"):
                build_path = line[11:].strip()
            if line.startswith("PACKAGES"):
                slpkg_tmp_packages = line[9:].strip()
            if line.startswith("PATCHES"):
                slpkg_tmp_patches = line[8:].strip()
            if line.startswith("DEL_ALL"):
                del_all = line[8:].strip()
            if line.startswith("DEL_BUILD"):
                del_build = line[10:].strip()
            if line.startswith("SBO_CHECK_MD5"):
                sbo_check_md5 = line[14:].strip()
            if line.startswith("SBO_BUILD_LOG"):
                sbo_build_log = line[14:].strip()
            if line.startswith("DEFAULT_ANSWER"):
                default_answer = line[15:].strip()
            if line.startswith("REMOVE_DEPS_ANSWER"):
                remove_deps_answer = line[19:].strip()
            if line.startswith("SKIP_UNST"):
                skip_unst = line[10:].strip()
            if line.startswith("DEL_DEPS"):
                del_deps = line[9:].strip()
            if line.startswith("USE_COLORS"):
                use_colors = line[11:].strip()
            if line.startswith("WGET_OPTIONS"):
                wget_options = line[13:].strip()

    ktown_kde_repo = ktown_repo(repositories)
    slacke_sub_repo = slacke_repo(repositories)
    # remove no default repositories
    repositories = remove_repositories(repositories, default_repositories)
    # add custom repositories
    update_repositories(repositories, conf_path)

    color = {
        'RED': '\x1b[31m',
        'GREEN': '\x1b[32m',
        'YELLOW': '\x1b[33m',
        'CYAN': '\x1b[36m',
        'GREY': '\x1b[38;5;247m',
        'ENDC': '\x1b[0m'
    }

    if use_colors == "off":
        color = {
            'RED': '',
            'GREEN': '',
            'YELLOW': '',
            'CYAN': '',
            'GREY': '',
            'ENDC': ''
        }

    CHECKSUMS_link = ("https://raw.githubusercontent.com/{0}/{1}/"
                      "master/CHECKSUMS.md5".format(__author__, __all__))

    # file spacer
    sp = "-"

    # current path
    path = os.getcwd() + "/"

    # library path
    lib_path = "/var/lib/slpkg/"

    # log path
    log_path = "/var/log/slpkg/"

    # packages log files path
    pkg_path = "/var/log/packages/"

    # computer architecture
    arch = os.uname()[4]

    # get sbo OUTPUT enviroment variable
    try:
        output = os.environ['OUTPUT']
    except KeyError:
        output = tmp
    if not output.endswith('/'):
        output = output + '/'
