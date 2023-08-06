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
import sys
import getpass


def s_user(user):
    '''
    Check for root user
    '''
    if user != "root":
        print("\nslpkg: error: must have root privileges\n")
        sys.exit(0)


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


def grab_sub_repo(repositories, repos):
    '''
    Grab SUB_REPOSITORY
    '''
    for i, repo in enumerate(repositories):
        if repos in repo:
            sub = repositories[i].replace(repos, '')
            repositories[i] = repos
            return sub


def select_slack_release(slack_rel):
    '''
    Warning message if Slackware release not defined or
    defined wrong
    '''
    if slack_rel not in ['stable', 'current']:
        print("\n  You have not specified the Slackware release.\n"
              "  Edit file '/etc/slpkg/slpkg.conf' and change the \n"
              "  value of the variable RELEASE.\n")


class MetaData(object):

    __all__ = "slpkg"
    __author__ = "dslackw"
    __version_info__ = (2, 2, 5)
    __version__ = "{0}.{1}.{2}".format(*__version_info__)
    __license__ = "GNU General Public License v3 (GPLv3)"
    __email__ = "d.zlatanidis@gmail.com"

    s_user(getpass.getuser())

    # Default Slackware release
    slack_rel = 'stable'

    # Configuration path
    conf_path = "/etc/{0}/".format(__all__)

    # tmp paths
    tmp = "/tmp/"
    tmp_path = "{0}{1}/".format(tmp, __all__)

    # Default configuration values
    _conf_slpkg = {
        'RELEASE': 'stable',
        'REPOSITORIES': ['slack', 'sbo', 'rlw', 'alien',
                         'slacky', 'studio', 'slackr', 'slonly',
                         'ktown{latest}', 'multi', 'slacke{18}',
                         'salix', 'slackl', 'rested'],
        'BUILD_PATH': '/tmp/slpkg/build/',
        'SBO_CHECK_MD5': 'on',
        'PACKAGES': '/tmp/slpkg/packages/',
        'PATCHES': '/tmp/slpkg/patches/',
        'DEL_ALL': 'on',
        'DEL_BUILD': 'off',
        'SBO_BUILD_LOG': 'on',
        'DEFAULT_ANSWER': 'n',
        'REMOVE_DEPS_ANSWER': 'n',
        'SKIP_UNST': 'n',
        'DEL_DEPS': 'off',
        'USE_COLORS': 'on',
        'WGET_OPTIONS': '-c -N'
    }

    default_repositories = ['slack', 'sbo', 'rlw', 'alien', 'slacky', 'studio',
                            'slackr', 'slonly', 'ktown', 'multi', 'slacke',
                            'salix', 'slackl', 'rested']

    if os.path.isfile('%s%s' % (conf_path, 'slpkg.conf')):
        f = open('%s%s' % (conf_path, 'slpkg.conf'), 'r')
        conf = f.read()
        f.close()
        for line in conf.splitlines():
            line = line.lstrip()
            if line and not line.startswith('#'):
                _conf_slpkg[line.split('=')[0]] = line.split('=')[1]

    # Set values from configuration file
    slack_rel = _conf_slpkg['RELEASE']
    if isinstance(_conf_slpkg['REPOSITORIES'], basestring):
        repositories = _conf_slpkg['REPOSITORIES'].split(',')
    else:
        repositories = _conf_slpkg['REPOSITORIES']
    build_path = _conf_slpkg['BUILD_PATH']
    slpkg_tmp_packages = _conf_slpkg['PACKAGES']
    slpkg_tmp_patches = _conf_slpkg['PATCHES']
    del_all = _conf_slpkg['DEL_ALL']
    sbo_check_md5 = _conf_slpkg['SBO_CHECK_MD5']
    del_build = _conf_slpkg['DEL_BUILD']
    sbo_build_log = _conf_slpkg['SBO_BUILD_LOG']
    default_answer = _conf_slpkg['DEFAULT_ANSWER']
    remove_deps_answer = _conf_slpkg['REMOVE_DEPS_ANSWER']
    skip_unst = _conf_slpkg['SKIP_UNST']
    del_deps = _conf_slpkg['DEL_DEPS']
    use_colors = _conf_slpkg['USE_COLORS']
    wget_options = _conf_slpkg['WGET_OPTIONS']

    # Remove any gaps
    repositories = [repo.strip() for repo in repositories]

    # Check Slackware release
    select_slack_release(slack_rel)

    # Grap sub repositories
    ktown_kde_repo = grab_sub_repo(repositories, 'ktown')
    slacke_sub_repo = grab_sub_repo(repositories, 'slacke')

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
