#!/usr/bin/python
# -*- coding: utf-8 -*-

# build.py file is part of slpkg.

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
import re
import sys
import time
import shutil
import tarfile
import subprocess

from slpkg.checksum import check_md5
from slpkg.messages import pkg_not_found
from slpkg.__metadata__ import (
    log_path,
    sbo_build_log,
    sbo_check_md5
)

from slpkg.sbo.greps import SBoGrep


class BuildPackage(object):

    def __init__(self, script, sources, path):
        self.script = script
        self.sources = sources
        self.path = path
        self.prgnam = self.script[:-7]
        self.log_file = "build_{0}_log".format(self.prgnam)
        self.sbo_logs = log_path + "sbo/"
        self.build_logs = self.sbo_logs + "build_logs/"
        self.start_log_time = time.strftime("%H:%M:%S")
        self.start_time = time.time()
        if not os.path.exists(log_path):
            os.mkdir(log_path)
        if not os.path.exists(self.sbo_logs):
            os.mkdir(self.sbo_logs)
        if not os.path.exists(self.build_logs):
            os.mkdir(self.build_logs)

    def build(self):
        '''
        Build package from source and create log
        file in path /var/log/slpkg/sbo/build_logs/.
        Also check md5sum calculates.
        '''
        try:
            tar = tarfile.open(self.script)
            tar.extractall()
            tar.close()
            sbo_md5_list = SBoGrep(self.prgnam).checksum()
            for src, sbo_md5 in zip(self.sources, sbo_md5_list):
                # fix build sources with spaces
                src = src.replace("%20", " ")
                if sbo_check_md5 == "on":
                    check_md5(sbo_md5, src)
                shutil.copy2(src, self.prgnam)
            os.chdir(self.path + self.prgnam)
            # change permissions
            subprocess.call("chmod +x {0}.SlackBuild".format(self.prgnam),
                            shell=True)
            if sbo_build_log == "on":
                if os.path.isfile(self.build_logs + self.log_file):
                    os.remove(self.build_logs + self.log_file)
                # start log write
                log_head(self.build_logs, self.log_file, self.start_log_time)
                subprocess.Popen("./{0}.SlackBuild 2>&1 | tee -a {1}{2}".format(
                    self.prgnam, self.build_logs, self.log_file), shell=True,
                    stdout=sys.stdout).communicate()
                sum_time = build_time(self.start_time)
                # write end in log file
                log_end(self.build_logs, self.log_file, sum_time)
                print("Total build time for package {0} : {1}\n".format(
                    self.prgnam, sum_time))
            else:
                subprocess.call("./{0}.SlackBuild".format(self.prgnam,
                                                          shell=True))
            os.chdir(self.path)
        except (OSError, IOError):
            pkg_not_found("\n", self.prgnam, "Wrong file", "\n")
        except KeyboardInterrupt:
            print("")   # new line at exit
            sys.exit(0)


def log_head(path, log_file, log_time):
    '''
    write headers to log file
    '''
    with open(path + log_file, "w") as log:
        log.write("#" * 79 + "\n\n")
        log.write("File : " + log_file + "\n")
        log.write("Path : " + path + "\n")
        log.write("Date : " + time.strftime("%d/%m/%Y") + "\n")
        log.write("Time : " + log_time + "\n\n")
        log.write("#" * 79 + "\n\n")
        log.close()


def log_end(path, log_file, sum_time):
    '''
    append END tag to a log file
    '''
    with open(path + log_file, "a") as log:
        log.seek(2)
        log.write("#" * 79 + "\n\n")
        log.write("Time : " + time.strftime("%H:%M:%S") + "\n")
        log.write("Total build time : {0}\n".format(sum_time))
        log.write(" " * 38 + "E N D\n\n")
        log.write("#" * 79 + "\n\n")
        log.close()


def build_time(start_time):
    '''
    Calculate build time per package
    '''
    diff_time = round(time.time() - start_time, 2)
    if diff_time <= 59.99:
        sum_time = str(diff_time) + " Sec"
    elif diff_time > 59.99 and diff_time <= 3599.99:
        sum_time = round(diff_time / 60, 2)
        sum_time_list = re.findall(r"\d+", str(sum_time))
        sum_time = ("{0} Min {1} Sec".format(sum_time_list[0],
                                             sum_time_list[1]))
    elif diff_time > 3599.99:
        sum_time = round(diff_time / 3600, 2)
        sum_time_list = re.findall(r"\d+", str(sum_time))
        sum_time = ("{0} Hours {1} Min".format(sum_time_list[0],
                                               sum_time_list[1]))
    return sum_time
