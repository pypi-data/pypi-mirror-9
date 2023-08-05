#!/usr/bin/python
# -*- coding: utf-8 -*-

# main.py file is part of slpkg.

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
import getpass

from utils import Utils
from messages import Msg
from desc import PkgDesc
from config import Config
from queue import QueuePkgs
from repoinfo import RepoInfo
from repolist import RepoList
from repositories import Repo
from tracking import track_dep
from blacklist import BlackList
from version import prog_version
from arguments import options, usage
from slpkg_update import it_self_update
from init import (
    Update,
    Initialization,
    check_exists_repositories
)
from __metadata__ import MetaData as _m

from pkg.build import BuildPackage
from pkg.manager import PackageManager

from sbo.check import sbo_upgrade
from sbo.views import SBoNetwork
from sbo.slackbuild import SBoInstall

from slack.patches import Patches
from binary.check import pkg_upgrade
from binary.install import BinaryInstall


class ArgParse(object):

    def __init__(self, args):
        self.args = args
        self.packages = self.args[1:]
        if len(self.args) > 1 and self.args[0] in ['-q', '-b']:
            self.packages = self.args[1:-1]
        elif len(self.packages) > 1 and self.args[0] in ['-s', '-t', '-p']:
            self.packages = self.args[2:]

        if (len(self.args) > 1 and
                self.args[0] in ['-f', '-i', '-u', '-o', '-r', '-d', '-n'] and
                self.args[1].endswith('.pkg')):
            self.packages = Utils().read_file_pkg(self.args[1])
        elif (len(self.args) >= 3 and self.args[0] in ['-s', '-t', '-p'] and
                self.args[1] in _m.repositories and
                self.args[2].endswith('.pkg')):
            self.packages = Utils().read_file_pkg(self.args[2])
        elif (len(self.args) == 3 and self.args[0] in ['-q', '-b'] and
                self.args[1].endswith('.pkg')):
            self.packages = Utils().read_file_pkg(self.args[1])

        # checking if repositories exists
        if len(self.args) > 1 and self.args[0] not in [
            '-h', '--help', '-v', '--version', 're-create', 'repo-list',
            'repo-add', 'repo-remove', 'update', 'update-slpkg'
        ]:
            check_exists_repositories()

    def help_version(self):
        """ Help and version info """
        if (len(self.args) == 1 and self.args[0] == '-h' or
                self.args[0] == '--help' and self.args[1:] == []):
            options()
        elif (len(self.args) == 1 and self.args[0] == '-v' or
                self.args[0] == '--version' and self.args[1:] == []):
            prog_version()
        else:
            usage('')

    def command_update(self):
        """ update package lists repositories """
        if len(self.args) == 1 and self.args[0] == 'update':
            Update().repository()

    def command_update_slpkg(self):
        """ slpkg it self update """
        if len(self.args) == 2 and self.args[0] == 'update-slpkg':
            it_self_update()
        else:
            usage('')

    def command_repo_list(self):
        """ repositories list """
        if len(self.args) == 1 and self.args[0] == 'repo-list':
            RepoList().repos()
        else:
            usage('')

    def command_repo_add(self):
        """ add custom repositories """
        if len(self.args) == 3 and self.args[0] == 'repo-add':
            Repo().add(self.args[1], self.args[2])
        else:
            usage('')

    def command_repo_remove(self):
        """ remove custom repositories """
        if len(self.args) == 2 and self.args[0] == 'repo-remove':
            Repo().remove(self.args[1])
        else:
            usage('')

    def command_re_create(self):
        """ re create repositories package lists """
        if len(self.args) == 1 and self.args[0] == 're-create':
            Initialization().re_create()
        else:
            usage('')

    def command_repo_info(self):
        """ repositories informations """
        if (len(self.args) == 2 and self.args[0] == 'repo-info' and
                self.args[1] in RepoList().all_repos):
            del RepoList().all_repos
            RepoInfo().view(self.args[1])
        elif (len(self.args) > 1 and self.args[0] == 'repo-info' and
                self.args[1] not in RepoList().all_repos):
            usage(self.args[1])
        else:
            usage('')

    def auto_build(self):
        """ auto built tool """
        if len(self.args) == 3 and self.args[0] == '-a':
            BuildPackage(self.args[1], self.args[2:], _m.path).build()
        else:
            usage('')

    def pkg_list(self):
        """ list of packages by repository """
        if (len(self.args) == 3 and self.args[0] == '-l' and
                self.args[1] in _m.repositories):
            if self.args[2] == '--index':
                PackageManager(None).list(self.args[1], True, False)
            elif self.args[2] == '--installed':
                PackageManager(None).list(self.args[1], False, True)
            else:
                usage('')
        elif (len(self.args) == 2 and self.args[0] == '-l' and
                self.args[1] in _m.repositories):
            PackageManager(None).list(self.args[1], False, False)
        elif (len(self.args) > 1 and self.args[0] == '-l' and
                self.args[1] not in _m.repositories):
            usage(self.args[1])
        else:
            usage('')

    def pkg_upgrade(self):
        """ check and upgrade packages by repository """
        if (len(self.args) == 3 and self.args[0] == '-c' and
                self.args[2] == '--upgrade'):
            if (self.args[1] in _m.repositories and
                    self.args[1] not in ['slack', 'sbo']):
                BinaryInstall(pkg_upgrade(self.args[1]),
                              self.args[1]).start(True)
            elif self.args[1] == 'slack':
                Patches().start()
            elif self.args[1] == 'sbo':
                SBoInstall(sbo_upgrade()).start(True)
            else:
                usage(self.args[1])
        else:
            usage('')

    def pkg_install(self):
        """ install packages by repository """
        if len(self.args) >= 3 and self.args[0] == '-s':
            if self.args[1] in _m.repositories and self.args[1] not in ['sbo']:
                BinaryInstall(self.packages, self.args[1]).start(False)
            elif self.args[1] == 'sbo':
                SBoInstall(self.packages).start(False)
            else:
                usage(self.args[1])
        else:
            usage('')

    def pkg_tracking(self):
        """ tracking package dependencies """
        packages = ''.join(self.packages)
        if len(self.packages) > 1:
            packages = self.packages[1]
            if self.args[2].endswith('.pkg'):
                packages = self.packages[0]
        if (len(self.args) == 3 and self.args[0] == '-t' and
                self.args[1] in _m.repositories):
            track_dep(packages, self.args[1])
        elif (len(self.args) > 1 and self.args[0] == '-t' and
                self.args[1] not in _m.repositories):
            usage(self.args[1])
        else:
            usage('')

    def sbo_network(self):
        """ view slackbuilds packages """
        packages = ''.join(self.packages)
        if len(self.packages) > 1:
            packages = self.packages[0]
        if (len(self.args) == 2 and self.args[0] == '-n' and
                'sbo' in _m.repositories):
            SBoNetwork(packages).view()
        else:
            usage('')

    def pkg_blacklist(self):
        """ manage blacklist packages """
        blacklist = BlackList()
        if (len(self.args) == 2 and self.args[0] == '-b' and
                self.args[1] == '--list'):
            blacklist.listed()
        elif (len(self.args) > 2 and self.args[0] == '-b' and
                self.args[-1] == '--add'):
            blacklist.add(self.packages)
        elif (len(self.args) > 2 and self.args[0] == '-b' and
                self.args[-1] == '--remove'):
            blacklist.remove(self.packages)
        else:
            usage('')

    def pkg_queue(self):
        """ manage packages in queue """
        queue = QueuePkgs()
        if (len(self.args) == 2 and self.args[0] == '-q' and
                self.args[1] == '--list'):
            queue.listed()
        elif (len(self.args) > 2 and self.args[0] == '-q' and
                self.args[-1] == '--add'):
            queue.add(self.packages)
        elif (len(self.args) > 2 and self.args[0] == '-q' and
                self.args[-1] == '--remove'):
            queue.remove(self.packages)
        elif (len(self.args) == 2 and self.args[0] == '-q' and
                self.args[1] == '--build'):
            queue.build()
        elif (len(self.args) == 2 and self.args[0] == '-q' and
                self.args[1] == '--install'):
            queue.install()
        elif (len(self.args) == 2 and self.args[0] == '-q' and
                self.args[1] == '--build-install'):
            queue.build()
            queue.install()
        else:
            usage('')

    def bin_install(self):
        """ install Slackware binary packages """
        if len(self.args) > 1 and self.args[0] == '-i':
            PackageManager(self.packages).install()
        else:
            usage('')

    def bin_upgrade(self):
        """ install-upgrade Slackware binary packages """
        if len(self.args) > 1 and self.args[0] == '-u':
            PackageManager(self.packages).upgrade()
        else:
            usage('')

    def bin_reinstall(self):
        """ reinstall Slackware binary packages """
        if len(self.args) > 1 and self.args[0] == '-o':
            PackageManager(self.packages).reinstall()
        else:
            usage('')

    def bin_remove(self):
        """ remove Slackware packages """
        if len(self.args) > 1 and self.args[0] == '-r':
            PackageManager(self.packages).remove()
        else:
            usage('')

    def bin_find(self):
        """ find installed packages """
        if len(self.args) > 1 and self.args[0] == '-f':
            PackageManager(self.packages).find()
        else:
            usage('')

    def pkg_desc(self):
        """ print slack-desc by repository"""
        packages = ''.join(self.packages)
        if len(self.packages) > 1:
            packages = self.packages[0]
        if (len(self.args) == 3 and self.args[0] == '-p' and
                self.args[1] in _m.repositories):
            PkgDesc(packages, self.args[1], '').view()
        elif (len(self.args) == 4 and self.args[0] == '-p' and
                self.args[3].startswith('--color=')):
            colors = ['red', 'green', 'yellow', 'cyan', 'grey']
            tag = self.args[3][len('--color='):]
            if self.args[1] in _m.repositories and tag in colors:
                PkgDesc(packages, self.args[1], tag).view()
            else:
                usage('')
        elif (len(self.args) > 1 and self.args[0] == '-p' and
                self.args[1] not in _m.repositories):
            usage(self.args[1])
        else:
            usage('')

    def pkg_contents(self):
        """ print packages contents """
        if len(self.args) > 1 and self.args[0] == '-d':
            PackageManager(self.packages).display()
        else:
            usage('')

    def congiguration(self):
        """ manage slpkg configuration file """
        if (len(self.args) == 2 and self.args[0] == '-g' and
                self.args[1].startswith('--config')):
            editor = self.args[1][len('--config='):]
            if self.args[1] == '--config':
                Config().view()
            elif editor:
                Config().edit(editor)
            else:
                usage('')
        else:
            usage('')


def main():

    Msg().s_user(getpass.getuser())
    args = sys.argv
    args.pop(0)

    argparse = ArgParse(args)

    if len(args) == 0:
        usage('')

    if len(args) == 2 and args[0] == 'update' and args[1] == 'slpkg':
        args[0] = 'update-slpkg'

    arguments = {
        '-h': argparse.help_version,
        '--help': argparse.help_version,
        '-v': argparse.help_version,
        '--version': argparse.help_version,
        'update': argparse.command_update,
        'update-slpkg': argparse.command_update_slpkg,
        'repo-list': argparse.command_repo_list,
        'repo-add': argparse.command_repo_add,
        'repo-remove': argparse.command_repo_remove,
        're-create': argparse.command_re_create,
        'repo-info': argparse.command_repo_info,
        '-a': argparse.auto_build,
        '-l': argparse.pkg_list,
        '-c': argparse.pkg_upgrade,
        '-s': argparse.pkg_install,
        '-t': argparse.pkg_tracking,
        '-n': argparse.sbo_network,
        '-b': argparse.pkg_blacklist,
        '-q': argparse.pkg_queue,
        '-i': argparse.bin_install,
        '-u': argparse.bin_upgrade,
        '-o': argparse.bin_reinstall,
        '-r': argparse.bin_remove,
        '-f': argparse.bin_find,
        '-p': argparse.pkg_desc,
        '-d': argparse.pkg_contents,
        '-g': argparse.congiguration
    }
    try:
        arguments[args[0]]()
    except KeyError:
        usage('')


if __name__ == '__main__':
    main()
