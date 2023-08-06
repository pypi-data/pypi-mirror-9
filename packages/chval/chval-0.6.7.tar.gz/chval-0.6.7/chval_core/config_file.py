#!/usr/bin/env python

# Copyright 2010 Louis Paternault

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Functions for reading from and writing to configuration files
"""

# Third party modules
import ConfigParser
import os

# Cheval modules
import chval_core as core
from chval_core import error

# Description of file "GETMAILDIR/chvalrc"
__allowedSections__ = ["options"] # Sections (possibly) contained in this file
__defaultConfig__ = { # Default values for options
        # Time (in second) before which 'getmail' is considered to no longer
        # answer
        'getmail_timeout' : str(5 * 60),
        # Default options given to getmail. Options given in the command line
        # are appended to these one.
        'getmail_options' : "-n",
        # Default time (in minutes) to wait between two successive calls to
        # getmail. If time is 0, no automatic calls are done.
        'daemon_cycle_time' : str(60),
        # Default parallel mode.
        'parallel' : "none",
        # Default time interval between two calls of getmail
        'gap' : str(0),
        # Default location of getmailrc files
        'getmaildir' : core.__getmaildir__,
        # Default interface
        'interface' : "default",
        }
__global__ = ConfigParser.SafeConfigParser(__defaultConfig__)

def read_passwords(chvaldir):
    """
    Read configuration file ~/.chval/passwords (which is supposed to
    exist), and return the dictionary of its content.
    - Keys are names of getmail config files (that is, "NAME" for config file
      ~/GETMAILDIR/getmailrc-NAME)
    - Values are encrypted passwords (as they appear in the file).
    """
    config = ConfigParser.SafeConfigParser()
    config.read(core.__passwords__(chvaldir))
    passwords = {}

    if (not config.has_option("sum", "sum")):
        checksum = None
    else:
        checksum = config.get("sum", "sum")

    if (not config.has_section("passwords")):
        return checksum, passwords
    for (key, value) in config.items("passwords"):
        passwords[key] = value
    return checksum, passwords

def write_passwords(chvaldir, passwords, checksum):
    """
    This function writes passwords in the configuration file.
    Arguments:
    - passwords: dictionary of (encrypted) passwords
    - checksum: sum of main password
    """
    config = ConfigParser.SafeConfigParser()
    config.add_section("passwords")
    for (key, value) in passwords.iteritems():
        config.set("passwords", key, value)
    if (checksum != None):
        config.add_section("sum")
        config.set("sum", "sum", checksum)
    config.write(open(core.__passwords__(chvaldir), 'wb'))

def read_global_config(chvaldir):
    """
    Read config file __config__(chvaldir), and check that it contains no more sections
    and options than those specified by variables "__allowedSections__" and
    "__defaultConfig__".
    Does not return anything, but as a side effect, update variable
    "__global__".
    """
    __global__.read(core.__config__(chvaldir))
    if (not __global__.has_section('options')):
        __global__.add_section('options')
    # Checking that no extra section or option exist in config file
    for section in __global__.sections():
        if (section not in __allowedSections__):
            error("Unknown section \"%s\" in file \"%s\"."
                    % (section, core.__config__(chvaldir)))
    for (item, __ignored__) in __global__.items("options"):
        if (item not in __defaultConfig__.keys()):
            error("Unknown option \"%s\" in file \"%s\"."
                    % (item, core.__config__(chvaldir)))

def get_global_config(section, option, typ = None):
    """
    Get value for "option", in "section", for the global config file.
    If a type is specifyed with argument "typ", take it into account to return
    a variable of this type.  Currently, only "None" and "int" are supported.
    """
    if (typ == int):
        return __global__.getint(section, option)
    else:
        return __global__.get(section, option)

def getmail_config_files(getmaildir):
    """
    Return the list of names of getmail configuration rc files.
    That is, return (NAME, ...) for files ~/GETMAILDIR/getmailrc-NAME
    """
    files = os.listdir(getmaildir)
    names = []
    for item in files:
        if (len(item) > 10):
            if (item[0:10] == "getmailrc-"):
                names.append(item[10:])
    return names

def check_getmail_config_files(getmaildir, files):
    """
    Arguments:
    - getmaildir: location of getmail configuration and data files.
    - files: a list of files, which may be the name of getmail configuration
      files.

    Return a couple of two lists:
    - the first one is the list of items of "files" that are the name of a
      configuration file;
    - the second one is the list of items of "files" that are not.
    """
    file_list = getmail_config_files(getmaildir)
    good = []
    bad = []
    for name in files:
        if (name in file_list):
            good.append(name)
        else:
            bad.append(name)
    return (good, bad)

def getmailrc_has_password(getmailrc):
    """
    Arguments:
    - getmailrc: path to a getmailrc file.

    Returns:
    True if a password is stored in this file (respecting "getmail"
    configuration file syntax), False otherwise.
    """
    getmail_config = ConfigParser.RawConfigParser()
    if (getmail_config.read(getmailrc)):
        return getmail_config.has_option("retriever", "password")
    return False

if __name__ == '__main__':
    error("This module is not meant to be run alone.")
