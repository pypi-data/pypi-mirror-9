# coding=utf-8
"""

# appinstance
Check if an app with the same name is running, supports parameters.
Erik de Jonge
erik@a8.nl
license: GNU-GPL2
"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from builtins import int
from builtins import open
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import object

import hashlib
import os
import psutil
import sys
from os.path import basename, join, expanduser, exists

# noinspection PyUnresolvedReferences


import __main__ as main


class AppInstanceRunning(AssertionError):
    """
    AppInstanceRunning
    """
    pass


def md5hex(uname):
    """
    @type uname: str, unicode
    @return: None
    """
    if sys.version_info.major == 3:
        # noinspection PyArgumentList
        hexd = hashlib.md5(bytes(uname, 'utf-8')).hexdigest()
    else:
        hexd = hashlib.md5(str(uname)).hexdigest()

    return hexd


class AppInstance(object):
    """
    Lockfile
    """
    def __init__(self, arguments=None, verbose=False):
        """
        @type arguments: str, unicode
        @type verbose: bool
        @return: None
        """
        self.verbose = verbose
        self.arguments = arguments
        self.name = basename(main.__file__).split(".")[0]

        if arguments is None:
            self.lockfile = join(expanduser("~"), "." + self.name + ".pid")
        else:
            uname = str(basename(self.name)) + "-" + str(arguments)
            lfname = md5hex(uname)
            self.lockfile = join(expanduser("~"), "." + self.name + "_" + lfname + ".pid")

    # noinspection PyUnusedLocal
    def __exit__(self, t, value, traceback):
        """
        @type t: str, unicode
        @type value: str, unicode
        @type traceback: str, unicode
        @return: None
        """
        if exists(self.lockfile):
            if int(open(self.lockfile).read()) == os.getpid():
                os.remove(self.lockfile)

    def __enter__(self):
        """
        __enter__
        """
        running = False

        if exists(self.lockfile):
            lfc = open(self.lockfile).read().strip()
            pid = ""

            if len(lfc) > 0:
                pid = int(lfc)

            for p in psutil.process_iter():
                if p.pid == pid:
                    cmdline = " ".join(p.as_dict()["cmdline"])

                    if self.name in str(cmdline):
                        running = True

            if running is False:
                os.remove(self.lockfile)

        if not running:
            fh = open(self.lockfile, "w")
            fh.write(str(os.getpid()))
            fh.close()

            if self.verbose is True:
                print("\033[32mInstance ok:", self.name, self.lockfile, str(os.getpid()) + "\033[0m")
        else:
            if self.verbose:
                print("\033[31mInstance error:", self.name, self.lockfile, str(os.getpid()) + "\033[0m")
            raise AppInstanceRunning(self.lockfile)

        return running
