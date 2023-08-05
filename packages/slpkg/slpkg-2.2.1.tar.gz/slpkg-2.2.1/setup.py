#!/usr/bin/python
# -*- coding: utf-8 -*-

# setup.py file is part of slpkg.

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
import gzip
import shutil

from slpkg.__metadata__ import MetaData as _m
from slpkg.md5sum import md5


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="slpkg",
    packages=["slpkg", "slpkg/sbo", "slpkg/pkg", "slpkg/slack",
              "slpkg/binary"],
    scripts=["bin/slpkg"],
    version=_m.__version__,
    description="Python tool to manage Slackware packages",
    keywords=["slackware", "slpkg", "upgrade", "install", "remove",
              "view", "slackpkg", "tool", "build"],
    author=_m.__author__,
    author_email=_m.__email__,
    url="https://github.com/dslackw/slpkg",
    package_data={"": ["LICENSE", "README.rst", "CHANGELOG"]},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Unix Shell",
        "Topic :: Software Development :: Build Tools",
        "Topic :: System :: Archiving :: Packaging",
        "Topic :: System :: Software Distribution",
        "Topic :: Utilities"],
    long_description=open("README.rst").read()
    )

# install man page and blacklist configuration
# file if not exists.
if "install" in sys.argv:
    man_path = "/usr/man/man8/"
    os.system("mkdir -p {0}".format(man_path))
    if os.path.exists(man_path):
        man_page = "man/slpkg.8"
        gzip_man = "man/slpkg.8.gz"
        print("Installing '{0}' man pages".format(gzip_man.split('/')[1]))
        f_in = open(man_page, "rb")
        f_out = gzip.open(gzip_man, 'wb')
        f_out.writelines(f_in)
        f_out.close()
        f_in.close()
        shutil.copy2(gzip_man, man_path)
        os.chmod(man_path, int("444", 8))

    conf_file = [
        'conf/slpkg.conf',
        'conf/blacklist',
        'conf/slackware-mirrors',
        'conf/custom-repositories'
    ]
    if not os.path.exists(_m.conf_path):
        os.system("mkdir -p {0}".format(_m.conf_path))
    print("Installing '{0}' file".format(conf_file[0].split('/')[1]))
    shutil.copy2(conf_file[0], _m.conf_path + conf_file[0].split('/')[1])
    for conf in conf_file[1:]:
        filename = conf.split("/")[-1]
        print("Installing '{0}' file".format(filename))
        if os.path.isfile(_m.conf_path + filename):
            old = md5(_m.conf_path + filename)
            new = md5(conf)
            if old != new:
                shutil.copy2(conf, _m.conf_path + filename + ".new")
        else:
            shutil.copy2(conf, _m.conf_path)
