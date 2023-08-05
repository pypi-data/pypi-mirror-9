.. image:: https://badge.fury.io/py/slpkg.png
    :target: http://badge.fury.io/py/slpkg
.. image:: https://travis-ci.org/dslackw/slpkg.svg?branch=master
    :target: https://travis-ci.org/dslackw/slpkg
.. image:: https://landscape.io/github/dslackw/slpkg/master/landscape.png
    :target: https://landscape.io/github/dslackw/slpkg/master
.. image:: https://pypip.in/d/slpkg/badge.png
    :target: https://pypi.python.org/pypi/slpkg
.. image:: https://pypip.in/license/slpkg/badge.png
    :target: https://pypi.python.org/pypi/slpkg

Latest Release:

- Version: 2.2.0
- `Package <https://sourceforge.net/projects/slpkg/files/slpkg/binary/>`_
- `Source <https://github.com/dslackw/slpkg/archive/v2.2.0.tar.gz>`_
- `CHANGELOG <https://github.com/dslackw/slpkg/blob/master/CHANGELOG>`_
 
.. image:: https://raw.githubusercontent.com/dslackw/images/master/slpkg/logo.png
    :target: https://github.com/dslackw/slpkg 

.. contents:: Table of Contents:

`Slpkg <https://github.com/dslackw/slpkg>`_ is a terminal multitool in order to easy use `Slackware <http://www.slackware.com/>`_ 
packages.

.. image:: https://raw.githubusercontent.com/dslackw/images/master/slpkg/open-source-logo.png
    :target: https://github.com/dslackw/slpkg 

Slpkg is `Open Source <http://en.wikipedia.org/wiki/Open_source>`_ software written in 
Python language. It's use is for managing packages in Slackware linux distribution.
Default available Repositories:

- SBo - `Reposiory <http://slackbuilds.org/>`_
  Arch: {x86, x86_64}
  Versions: {13.1, 13.37, 14.0, 14.1}
- Slack - `Repository <http://www.slackware.com/>`_
  Arch: {x86, x86_64}
  Versions: {3.3, 8.1, 9.0, 9.1, 10.0, 10.1, 10.2, 11.0, 12.0, 12.2, 13.0, 13.37, 14.0, 14.1, current}
- Alien's - `Repository <http://www.slackware.com/~alien/slackbuilds/>`_
  Arch: {x86, x86_64}
  Versions: {11.0, 12.0, 12.1, 12.2, 13.0, 13.1, 13.37, 14.0, 14.1, current}
- Slacky - `Repository <http://repository.slacky.eu/>`_
  Arch: {x86, x86_64}
  Versions: {11.0, 12.0, 12.1, 12.2, 13.0, 13.1, 13.37, 14.0, 14.1}
- Robby's - `Repository <http://rlworkman.net/pkgs/>`_
  Arch: {x86, x86_64}
  Versions: {11.0, 12.0, 12.1, 12.2, 13.0, 13.1, 13.37, 14.0, 14.1}
- Studioware - `Repository <http://studioware.org/packages>`_
  Arch: {x86, x86_64}
  Versions: {13.37, 14.0, 14.1}
- Slackers - `Repository <http://www.slackers.it/repository/>`_
  Arch: {x86_64}
  Versions: {current}
- Slackonly - `Repository <https://slackonly.com/>`_
  Arch: {x86, x86_64}
  Versions: {14.1}
- Alien's ktown - `Repository <http://alien.slackbook.org/ktown/>`_
  Arch: {x86, x86_64}
  Versions: {13.37, 14.0, 14.1, current}
- Alien's multi - `Repository <http://www.slackware.com/~alien/multilib/>`_
  Arch: {x86_64}
  Versions: {13.0, 13.1, 13.37, 14.0, 14.1, current}
- Slacke E17 and E18 - `Repository <http://ngc891.blogdns.net/pub/>`_
  Arch: {x86, x86_64, arm}
  Versions: {14.1}
- SalixOS - `Repository <http://download.salixos.org/>`_
  Arch: {x86, x86_64}
  Versions: {13.0, 13.1, 13.37, 14.0, 14.1}
- Slackel - `Repository <http://www.slackel.gr/repo/>`_
  Arch: {x86, x86_64}
  Versions: {current}
- Restricted - `Repository <http://taper.alienbase.nl/mirrors/people/alien/restricted_slackbuilds/>`_
  Arch: {x86, x86_64}
  Versions: {11.0, 12.0, 12.1, 12.2, 13.0, 13.1, 13.37, 14.0, 14,1, current}


* Choose default repositories you need to work from file '/etc/slpkg/slpkg.conf' default is 
  'slack' and 'sbo' repositories and read REPOSITORIES file for each of the particularities.
  If a repository is not in the above list, manage custom repositories with commands 'repo-add'
  and 'repo-remove'.

Slpkg works in accordance with the standards of the organization slackbuilds.org 
to builds packages. Also uses the Slackware linux instructions for installation,
upgrading or removing packages. 

Slpkg must work with any Slackware based distribution such Salix and Slackel or Slax etc.

What makes slpkg to distinguish it from other tools; The user friendliness is its primary 
target as well as easy to understand and use, also use color to highlight packages and 
display warning messages, etc.

The big advantages is resolving dependencies packages from repositories and monitored for 
upgraded packages.

Also you can install official packages of your favorite distribution directly from the 
official repositories of Slackware. Even you can check for the official updates and install them.

More features come ...

.. image:: https://raw.githubusercontent.com/dslackw/images/master/slpkg/slpkg_package.png
    :target: https://github.com/dslackw/slpkg


Features
--------

- Build third party packages from source with all dependencies
- Grabs packages from repositories in real time
- Find and Download packages from repositories 
- Automatic tool build and install packages
- Check if your distribution is up to date
- Remove packages with all dependencies
- Display the contents of the packages
- Install-upgrade Slackware packages
- Build and install all in a command
- Checking for updated packages
- List all installed packages
- Support MD5SUM file check
- Find installed package
- Read SlackBuilds files
- Τracking dependencies
- Build log file
- Sum build time

It's a quick and easy way to manage your packages in `Slackware <http://www.slackware.com/>`_
to a command.

Tutorial
--------

.. image:: https://raw.githubusercontent.com/dslackw/images/master/slpkg/screenshot-1.png
    :target: https://asciinema.org/a/14145


Installation
------------

Untar the archive and run install.sh script:

.. code-block:: bash
    
    $ tar xvf slpkg-2.2.0.tar.gz
    $ cd slpkg-2.2.0
    $ ./install.sh

From SourceForge:
    
Download binary package from `SourceForge <https://sourceforge.net/projects/slpkg/>`_
    
Using pip:

.. code-block:: bash
    
    $ pip install slpkg --upgrade


Upgrade
-------

From version '2.1.4' you can update slpkg itself with '# slpkg update slpkg'.
In each slpkg upgrade should track the configuration files in the file '/etc/slpkg' for 
new updates.


Configuration files
-------------------

.. code-block:: bash

    /etc/slpkg/slpkg.conf
         General configuration of slpkg

    /etc/slpkg/blacklist
         List of packages to skip

    /etc/slpkg/slackware-mirrors
         List of Slackware Mirrors

    /etc/slpkg/custom-repositories
         List of custom repositories

Slackware Current
-----------------

For Slackware 'current' users must change the variable VERSION in '/etc/slpkg.conf' file.

.. code-block:: bash

    $ slpkg -g --config=nano


Testing
-------

The majority of trials have been made in an environment Slackware x86_64 and x86 stable version 
14.1.
Is logical tests are always to be latest versions of the distribution.
Slpkg are supported version 'current' but it is minimal tests have been done on this release.


Slackware Mirrors
-----------------

Slpkg uses the central mirror "http://mirrors.slackware.com/slackware/" 
to find the nearest one. If however for some reason this troublesome 
please edit the file in '/etc/slpkg/slackware-mirrors'.


Usage
-----

Need to run '# slpkg update' for the first time to synchronize the list of packages,
also every time you add a repository.
To add or remove repositories must edit the file '/etc/slpkg/slpkg.conf'.

Also it is good to update the list of packages by running the command '# slpkg update'
before proceeding to any installation or upgrade a new package.


Issues
------

Please report any bugs in `ISSUES <https://github.com/dslackw/slpkg/issues>`_


Command Line Tool Usage
-----------------------

.. code-block:: bash

    Utility for easy management packages in Slackware

    Commands:
       update                                   update all package lists
       re-create                                recreate package lists
       repo-add [repository name] [URL]         add custom repository
       repo-remove [repository]                 remove custom repository
       repo-list                                list all repositories
       repo-info [repository]                   repository information
       update slpkg                             check and update slpkg

    Optional arguments:
      -h, --help                                show this help message and exit
      -v, --version                             print version and exit
      -a, [script.tar.gz] [source...]           auto build SBo packages
      -b, --list, [package...] --add, --remove  add, remove packages in blacklist
      -q, --list, [package...] --add, --remove  add, remove SBo packages in queue
      -q, --build, --install, --build-install   build, install packages from queue
      -g, --config, --config=[editor]           configuration file management
      -l, [repository], all                     list of installed packages
      -c, [repository] --upgrade                check for updated packages
      -s, [repository] [package]                download, build & install
      -t, [repository] [package]                tracking dependencies
      -p, [repository] [package], --color=[]    print package description
      -n, [package]                             view SBo packages through network
      -f, [package...]                          find installed packages
      -i, [package...]                          install binary packages
      -u, [package...]                          upgrade binary packages
      -o, [package...]                          reinstall binary packages
      -r, [package...]                          remove binary packages
      -d, [package...]                          display the contents


Slpkg Examples
--------------

If you use slpkg for the first time will have to create 
and update the package lists:

.. code-block:: bash

    $ slpkg update

    Update repository slack .......................Done
    Update repository sbo .............Done
    Update repository alien ...Done
    Update repository slacky .....................................Done
    Update repository studio ...................Done
    Update repository slackr .............................................Done
    Update repository slonly ...Done
    Update repository ktown ...Done
    Update repository salix ..................Done
    Update repository slacke ...Done
    Update repository slackl ...Done
    Update repository multi ...Done


Add and remove custom repositories:

.. code-block:: bash

    $ slpkg repo-add ponce http://ponce.cc/slackware/slackware64-14.1/packages/

    Repository 'ponce' successfully added


    $ slpkg repo-remove ponce

    Repository 'ponce' successfully removed

    
View information about the repositories:
    
.. code-block:: bash

    $ slpkg repo-list
    
    +==============================================================================
    | Repo id  Repo URL                                            Default   Status
    +==============================================================================
      alien    http://www.slackware.com/~alien/slackbuilds/        yes     disabled
      ktown    http://alien.slackbook.org/ktown/                   yes     disabled
      multi    http://www.slackware.com/~alien/multilib/           yes     disabled
      ponce    http://ponce.cc/slackware/slackware64-14.1/packa~   no       enabled
      rested   http://taper.alienbase.nl/mirrors/people/alien/r~   yes     disabled
      rlw      http://rlworkman.net/pkgs/                          yes     disabled
      salix    http://download.salixos.org/                        yes     disabled
      sbo      http://slackbuilds.org/slackbuilds/                 yes      enabled
      slack    http://ftp.cc.uoc.gr/mirrors/linux/slackware/       yes      enabled
      slacke   http://ngc891.blogdns.net/pub/                      yes     disabled
      slackl   http://www.slackel.gr/repo/                         yes     disabled
      slackr   http://www.slackers.it/repository/                  yes     disabled
      slacky   http://repository.slacky.eu/                        yes     disabled
      slonly   https://slackonly.com/pub/packages/                 yes     disabled
      studio   http://studioware.org/files/packages/               yes     disabled

    For enable or disable default repositories edit '/etc/slpkg/slpkg.conf' file

    $ slpkg repo-info alien

    Default: yes
    Last updated: Tue Dec 23 11:48:31 UTC 2014
    Number of packages: 3149
    Repo id: alien
    Repo url: http://www.slackware.com/~alien/slackbuilds/
    Status: enabled
    Total compressed packages: 9.3 Gb
    Total uncompressed packages: 36.31 Gb


Find packages from repository download, 
build and install with all dependencies :

.. code-block:: bash
    
    $ slpkg -s sbo brasero
    Reading package lists ......Done
    
    The following packages will be automatically installed or upgraded 
    with new version:
    
    +==============================================================================
    | Package                                 Version         Arch       Repository
    +==============================================================================
    Installing:
      brasero                                 3.11.3          x86_64     SBo
    Installing for dependencies:
      orc                                     0.4.19          x86_64     SBo
      gstreamer1                              1.2.2           x86_64     SBo
      gst1-plugins-base                       1.2.2           x86_64     SBo
      gst1-plugins-bad                        1.2.2           x86_64     SBo
      libunique                               1.1.6           x86_64     SBo

    Installing summary
    ===============================================================================
    Total 6 packages.
    6 packages will be installed, 0 allready installed and 0 package
    will be upgraded.

    Would you like to continue [Y/n]? y
    
    
    $ slpkg -s sbo fmpeg
    Reading package lists ....Done

    Packages with name matching [ fmpeg ]

    +==============================================================================
    | Package                              Version          Arch         Repository
    +==============================================================================
    Matching:
     ffmpegthumbnailer                     2.0.8            x86_64       SBo
     ffmpeg                                2.1.5            x86_64       SBo
     ffmpeg2theora                         0.29             x86_64       SBo
     gst-ffmpeg                            0.10.13          x86_64       SBo

    Installing summary
    ===============================================================================
    Total found 4 matching packages.
    0 installed package and 4 uninstalled packages.
    
    
Install Slackware official packages:

.. code-block:: bash

    $ slpkg -s slack mozilla

    Packages with name matching [ mozilla ]
    Reading package lists ..............................Done

    +==============================================================================
    | Package                   Version          Arch     Build  Repos         Size
    +==============================================================================
    Installing:
      mozilla-firefox           24.1.0esr        x86_64   1      Slack     23524  K
      mozilla-nss               3.15.2           x86_64   2      Slack      1592  K
      mozilla-thunderbird       24.1.0           x86_64   1      Slack     24208  K

    Installing summary
    ===============================================================================
    Total 3 packages.
    0 package will be installed, 3 will be upgraded and 0 will be resettled.
    Need to get 48.17 Mb of archives.
    After this process, 125.75 Mb of additional disk space will be used.

    Would you like to continue [Y/n]?

Tracking all dependencies of packages,
and also displays installed packages:

.. code-block:: bash

    $ slpkg -t sbo brasero
    Reading package lists ......Done

    +=========================
    | brasero dependencies   :
    +=========================
    \ 
     +---[ Tree of dependencies ]
     |
     +--1 orc
     |
     +--2 gstreamer1
     |
     +--3 gst1-plugins-base
     |
     +--4 gst1-plugins-bad
     |
     +--5 libunique

Check if your packages is up to date:

.. code-block:: bash

    $ slpkg -c sbo --upgrade
    Reading package lists ...Done

    These packages need upgrading:

    +==============================================================================
    | Package                             New version       Arch         Repository
    +==============================================================================
    Upgrading:
      six-1.7.1                           1.7.3             x86_64       SBo
      pysetuptools-3.4                    3.6               x86_64       SBo
      Jinja2-2.7.0                        2.7.2             x86_64       SBo
      pysed-0.3.0                         0.3.1             x86_64       SBo
      Pafy-0.3.56                         0.3.58            x86_64       SBo
      MarkupSafe-0.21                     0.23              x86_64       SBo
      pip-1.5.3                           1.5.6             x86_64       SBo
      colored-1.1.1                       1.1.4             x86_64       SBo
                
    Installing summary
    ===============================================================================
    Total 8 packages will be upgraded and 0 package will be installed.
                
    Would you like to continue [Y/n]?

Check if your Slackware distribution is up to date:

.. code-block:: bash

    $ slpkg -c slack --upgrade
    Reading package lists .......Done

    These packages need upgrading:
    
    +==============================================================================
    | Package                   Version          Arch     Build  Repos         Size
    +==============================================================================
    Upgrading:
      dhcpcd-6.0.5              6.0.5            x86_64   3      Slack         92 K
      samba-4.1.0               4.1.11           x86_64   1      Slack       9928 K
      xscreensaver-5.22         5.29             x86_64   1      Slack       3896 K

    Installing summary
    ===============================================================================
    Total 3 package will be upgrading.
    Need to get 13.58 Mb of archives.
    After this process, 76.10 Mb of additional disk space will be used.
    
    Would you like to continue [Y/n]?

Find packages from slackbuilds.org:

.. code-block:: bash

    $ slpkg -n bitfighter
    Reading package lists ...Done
    
    +===============================================================================
    | Package bitfighter --> http://slackbuilds.org/repository/14.1/games/bitfighter/
    +===============================================================================
    | Description : multi-player combat game
    | SlackBuild : bitfighter.tar.gz
    | Sources : bitfighter-019c.tar.gz, classic_level_pack.zip 
    | Requirements : OpenAL, SDL2, speex, libmodplug
    +===============================================================================
     README               View the README file
     SlackBuild           View the SlackBuild file
     Info                 View the Info file
     Download             Download this package
     Build                Download and build this package
     Install              Download/Build/Install
     Quit                 Quit
     
     Choose an option: _

Auto tool to build package:

.. code-block:: bash

    Two files termcolor.tar.gz and termcolor-1.1.0.tar.gz
    must be in the same directory.
    (slackbuild script & source code or extra sources if needed)

    $ slpkg -a termcolor.tar.gz termcolor-1.1.0.tar.gz

    termcolor/
    termcolor/slack-desc
    termcolor/termcolor.info
    termcolor/README
    termcolor/termcolor.SlackBuild
    termcolor-1.1.0/
    termcolor-1.1.0/CHANGES.rst
    termcolor-1.1.0/COPYING.txt
    termcolor-1.1.0/README.rst
    termcolor-1.1.0/setup.py
    termcolor-1.1.0/termcolor.py
    termcolor-1.1.0/PKG-INFO
    running install
    running build
    running build_py
    creating build
    creating build/lib
    copying termcolor.py -> build/lib
    running install_lib
    creating /tmp/SBo/package-termcolor/usr
    creating /tmp/SBo/package-termcolor/usr/lib64
    creating /tmp/SBo/package-termcolor/usr/lib64/python2.7
    creating /tmp/SBo/package-termcolor/usr/lib64/python2.7/site-packages
    copying build/lib/termcolor.py -> 
    /tmp/SBo/package-termcolor/usr/lib64/python2.7/site-packages
    byte-compiling /tmp/SBo/package-termcolor/usr/lib64/python2.7/site-packages/termcolor.py 
    to termcolor.pyc
    running install_egg_info
    Writing 
    /tmp/SBo/package-termcolor/usr/lib64/python2.7/site-packages/termcolor-1.1.0-py2.7.egg-info

    Slackware package maker, version 3.14159.

    Searching for symbolic links:

    No symbolic links were found, so we wont make an installation script.
    You can make your own later in ./install/doinst.sh and rebuild the
    package if you like.

    This next step is optional - you can set the directories in your package
    to some sane permissions. If any of the directories in your package have
    special permissions, then DO NOT reset them here!

    Would you like to reset all directory permissions to 755 (drwxr-xr-x) and
    directory ownerships to root.root ([y]es, [n]o)? n

    Creating Slackware package:  /tmp/termcolor-1.1.0-x86_64-1_SBo.tgz

    ./
    usr/
    usr/lib64/
    usr/lib64/python2.7/
    usr/lib64/python2.7/site-packages/
    usr/lib64/python2.7/site-packages/termcolor.py
    usr/lib64/python2.7/site-packages/termcolor.pyc
    usr/lib64/python2.7/site-packages/termcolor-1.1.0-py2.7.egg-info
    usr/doc/
    usr/doc/termcolor-1.1.0/
    usr/doc/termcolor-1.1.0/termcolor.SlackBuild
    usr/doc/termcolor-1.1.0/README.rst
    usr/doc/termcolor-1.1.0/CHANGES.rst
    usr/doc/termcolor-1.1.0/PKG-INFO
    usr/doc/termcolor-1.1.0/COPYING.txt
    install/
    install/slack-desc

    Slackware package /tmp/termcolor-1.1.0-x86_64-1_SBo.tgz created.

    Total build time for package termcolor : 1 Sec

Upgrade, install package:

.. code-block:: bash

    $ slpkg -u /tmp/termcolor-1.1.0-x86_64-1_SBo.tgz

    +==============================================================================
    | Installing new package ./termcolor-1.1.0-x86_64-1_SBo.tgz
    +==============================================================================

    Verifying package termcolor-1.1.0-x86_64-1_SBo.tgz.
    Installing package termcolor-1.1.0-x86_64-1_SBo.tgz:
    PACKAGE DESCRIPTION:
    # termcolor (ANSII Color formatting for output in terminal)
    #
    # termcolor allows you to format your output in terminal.
    #
    # Project URL: https://pypi.python.org/pypi/termcolor
    #
    Package termcolor-1.1.0-x86_64-1_SBo.tgz installed.

Install mass-packages:

.. code-block:: bash

    $ slpkg -u *.t?z
    
    or 

    $ slpkg -i *.t?z

Find installed packages:

.. code-block:: bash

    $ slpkg -f apr

    Packages with matching name [ apr ] 
    
    [ installed ] - apr-1.5.0-x86_64-1_slack14.1
    [ installed ] - apr-util-1.5.3-x86_64-1_slack14.1
    [ installed ] - xf86dgaproto-2.1-noarch-1
    [ installed ] - xineramaproto-1.2.1-noarch-1

    Total found 4 matcing packages
    Size of installed packages 1.61 Mb

Display the contents of the packages:

.. code-block:: bash

    $ slpkg -d termcolor lua

    PACKAGE NAME:     termcolor-1.1.0-x86_64-1_SBo
    COMPRESSED PACKAGE SIZE:     8.0K
    UNCOMPRESSED PACKAGE SIZE:     60K
    PACKAGE LOCATION: ./termcolor-1.1.0-x86_64-1_SBo.tgz
    PACKAGE DESCRIPTION:
    termcolor: termcolor (ANSII Color formatting for output in terminal)
    termcolor:
    termcolor: termcolor allows you to format your output in terminal.
    termcolor:
    termcolor:
    termcolor: Project URL: https://pypi.python.org/pypi/termcolor
    termcolor:
    termcolor:
    termcolor:
    termcolor:
    FILE LIST:
    ./
    usr/
    usr/lib64/
    usr/lib64/python2.7/
    usr/lib64/python2.7/site-packages/
    usr/lib64/python2.7/site-packages/termcolor.py
    usr/lib64/python2.7/site-packages/termcolor.pyc
    usr/lib64/python2.7/site-packages/termcolor-1.1.0-py2.7.egg-info
    usr/lib64/python3.3/
    usr/lib64/python3.3/site-packages/
    usr/lib64/python3.3/site-packages/termcolor-1.1.0-py3.3.egg-info
    usr/lib64/python3.3/site-packages/__pycache__/
    usr/lib64/python3.3/site-packages/__pycache__/termcolor.cpython-33.pyc
    usr/lib64/python3.3/site-packages/termcolor.py
    usr/doc/
    usr/doc/termcolor-1.1.0/
    usr/doc/termcolor-1.1.0/termcolor.SlackBuild
    usr/doc/termcolor-1.1.0/README.rst
    usr/doc/termcolor-1.1.0/CHANGES.rst
    usr/doc/termcolor-1.1.0/PKG-INFO
    usr/doc/termcolor-1.1.0/COPYING.txt
    install/
    install/slack-desc
    
    No such package lua: Cant find

Remove packages:

.. code-block:: bash

    $ slpkg -r termcolor
    
    Packages with name matching [ termcolor ]
    
    [ delete ] --> termcolor-1.1.0-x86_64-1_SBo

    Are you sure to remove 1 package(s) [Y/n]? y

    Package: termcolor-1.1.0-x86_64-1_SBo
        Removing... 

    Removing package /var/log/packages/termcolor-1.1.0-x86_64-1_SBo...
        Removing files:
    --> Deleting /usr/doc/termcolor-1.1.0/CHANGES.rst
    --> Deleting /usr/doc/termcolor-1.1.0/COPYING.txt
    --> Deleting /usr/doc/termcolor-1.1.0/PKG-INFO
    --> Deleting /usr/doc/termcolor-1.1.0/README.rst
    --> Deleting /usr/doc/termcolor-1.1.0/termcolor.SlackBuild
    --> Deleting /usr/lib64/python2.7/site-packages/termcolor-1.1.0-py2.7.egg-info
    --> Deleting /usr/lib64/python2.7/site-packages/termcolor.py
    --> Deleting /usr/lib64/python2.7/site-packages/termcolor.pyc
    --> Deleting /usr/lib64/python3.3/site-packages/__pycache__/termcolor.cpython-33.pyc
    --> Deleting /usr/lib64/python3.3/site-packages/termcolor-1.1.0-py3.3.egg-info
    --> Deleting /usr/lib64/python3.3/site-packages/termcolor.py
    --> Deleting empty directory /usr/lib64/python3.3/site-packages/__pycache__/
    WARNING: Unique directory /usr/lib64/python3.3/site-packages/ contains new files
    WARNING: Unique directory /usr/lib64/python3.3/ contains new files
    --> Deleting empty directory /usr/doc/termcolor-1.1.0/

    +==============================================================================
    | Package: termcolor removed
    +==============================================================================

Remove packages with all dependencies:
(presupposes facility with the option 'slpkg -s <repository> <package>)

.. code-block:: bash

    $ slpkg -r Flask

    Packages with name matching [ Flask ]

    [ delete ] --> Flask-0.10.1-x86_64-1_SBo

    Are you sure to remove 1 package [Y/n]? y

    +==============================================================================
    | Found dependencies for package Flask:
    +==============================================================================
    | pysetuptools
    | MarkupSafe
    | itsdangerous
    | Jinja2
    | werkzeug
    +==============================================================================

    Remove dependencies (maybe used by other packages) [Y/n]? y
    .
    .
    .
    +==============================================================================
    | Package Flask removed
    | Package pysetuptools removed
    | Package MarkupSafe removed
    | Package itsdangerous removed
    | Package Jinja2 removed
    | Package werkzeug removed
    +==============================================================================



Build and install packages that have added to the queue:

.. code-block:: bash

    $ slpkg -q roxterm SDL2 CEGUI --add
    
    Add packages in queue:

    roxterm
    SDL2
    CEGUI

    
    $ slpkg -q roxterm --remove (or 'slpkg -q all --remove' remove all packages from queue)
    
    Remove packages from queue:

    roxterm

    
    $ slpkg -q --list

    Packages in queue:

    SDL2
    CEGUI
    
    
    $ slpkg -q --build (build only packages from queue)

    $ slpkg -q --install (install packages from queue)

    $ slpkg -q --build-install (build and install)

Add packages in blacklist file manually from 
/etc/slpkg/blacklist or with the following options:

.. code-block:: bash
    
    $ slpkg -b live555 speex faac --add

    Add packages in blacklist: 

    live555
    speex
    faac


    $ slpkg -b speex --remove

    Remove packages from blacklist:

    speex


    $ slpkg -b --list

    Packages in blacklist:

    live555
    faac

    
Print package description:

.. code-block:: bash

    $ slpkg -p alien vlc --color=green

    vlc (multimedia player for various audio and video formats)

    VLC media player is a highly portable multimedia player for various
    audio and video formats (MPEG-1, MPEG-2, MPEG-4, DivX, mp3, ogg, ...)
    as well as DVDs, VCDs, and various streaming protocols.
    It can also be used as a server to stream in unicast or multicast in
    IPv4 or IPv6 on a high-bandwidth network.


    vlc home: http://www.videolan.org/vlc/


Man page it is available for full support:

.. code-block:: bash

    $ man slpkg


Donate
--------
If you feel satisfied with this project and want to thank me go
to `Slackware <https://store.slackware.com/cgi-bin/store/slackdonation>`_ and make a donation or visit the `store <https://store.slackware.com/cgi-bin/store>`_.
