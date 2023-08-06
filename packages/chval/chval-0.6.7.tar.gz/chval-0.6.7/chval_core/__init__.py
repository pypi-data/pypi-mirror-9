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
Module related to daemon.
"""

# Third party modules
import ConfigParser
import inspect
import os
import sys

# Cheval modules
import chval_core.enum as enum

################################################################################
### Some functions defining paths
################################################################################
def __passwords__(chvaldir):
    return os.path.join(chvaldir, "passwords")

def __config__(chvaldir):
    return os.path.join(chvaldir, "chvalrc")

def __run_dir__(chvaldir):
    return os.path.join(chvaldir, "run")

################################################################################
### Some global variables
################################################################################
# Constants
__program_name__ = "chval"
__version__ = "0.6.7"
__getmaildir__ = os.path.join(os.path.expanduser("~"), ".getmail")
__chvaldir__ = os.path.join(os.path.expanduser("~"), ".chval")
__sendmail__ = "/usr/sbin/sendmail" # sendmail location
__daemon_timeout__ = 3 # Time before the daemon is considered dead if it does
                       # not answer.
# Possible types of messages from daemon to clients (and meaning of associated
# values) are:
# - none: No type or value.
# - getmail_begin: Getmail has been launched. Value is list containing a single
#   element: a string which is the name of the getmailrc file being processed.
# - getmail_got_message: One message got. Value is a list [getmailrc, X, Y],
#   which mean: message X of Y got for config file getmailrc.
# - getmail_end: Getmail has finished. Value is a list [getmailrc, number]
#   where getmailrc is the name of the file being processed, and number is the
#   number of downloaded emails.
# - error: An error occured, and thread was stopped. Value is a list
#   [getmailrc, cause] where "cause" is a string explaining the error.
# - deamon_start: Daemon is started. Value is None.
# - deamon_stop: Deamon is closed. Value is None.
__d2c__ = enum.Enum(
    "none",
    "getmail_begin",
    "getmail_got_message",
    "getmail_end",
    "error",
    "daemon_start",
    "daemon_stop",
    )

################################################################################
### Some enumeration
################################################################################
__parallel__ = enum.Enum(
    "daemons", # Option --parallel=daemons
    "getmail", # Option --parallel=getmail
    )

################################################################################
### I/O functions
################################################################################
def error(string, code = 1):
    "Print the error and exit."
    sys.stderr.write(string)
    sys.stderr.write("\n")
    sys.stderr.flush()
    sys.exit(code)

def warning(string):
    "Print the warning."
    sys.stderr.write(string)
    sys.stderr.write("\n")
    sys.stderr.flush()

def write(string):
    "Print to standard output"
    sys.stdout.write(string)
    sys.stdout.flush()

def trace(string = None, newline = True):
    """
    Print string on standard error, ending it by a new line if "newline" is
    true.
    If no string is given, print current line.
    """
    if (string):
        sys.stderr.write(string)
        if (newline):
            sys.stderr.write("\n")
            sys.stderr.flush()
    else:
        caller = inspect.stack()[1]
        sys.stderr.write(
                "%s(%s): %s" % (caller[1], caller[3], caller[2]) + "\n")
        sys.stderr.flush()

def trace_stack():
    """
    Print the stack of calls of the caller's.
    """
    sys.stderr.write("\n".join(["%15s%4s (%20s): %s" %
        (i[1].split("/")[-1], i[2], i[3], i[4][0].strip())
        for i in inspect.stack()[1:]]))

def read_letter(choice):
    """
    Read one letter from keyboard, and keep asking user for a letter until the
    given letter is one of the list 'choice'.
    """
    answer = ""
    while (answer not in set(choice)):
        write(" ")
        answer = sys.stdin.readline()
        if (answer == ''):
            raise EOFError
        answer = answer[:-1]
        if (answer not in choice):
            write("Please choose one of [")
            for char in choice:
                write(char)
            write("].")
    return answer

def TODO(string = ""):
    "Print a warning for a part of program not written yet"
    warning("TODO: " + string)

################################################################################
### Some checks about files and directories
################################################################################
def check_getmail_directory(getmaildir):
    """
    Check that some files and directories exist
    - ~/GETMAILDIR: raise error if non-existent
    """

    # GETMAILDIR
    failed = True
    if (os.path.exists(getmaildir)):
        if (os.path.isdir(getmaildir)):
            failed = False
    if (failed):
        error('Directory %s does not exist.' % getmaildir)

def check_chval_directories(chvaldir):
    """
    Check that some files and directories exist
    - CHVALDIR: create it if non-existent
    - CHVALDIR/passwords: create it (empty) if non-existent
    - CHVALDIR/chvalrc: create it, containing the empty section "options" if
      non-existent
    Arguments:
    - chvaldir: string representing the path of the chval configuration directory
    """

    # .chval
    failed = True
    if (os.path.exists(chvaldir)):
        if (os.path.isdir(chvaldir)):
            failed = False
    if (failed):
        os.mkdir(chvaldir)

    # CHVALDIR/passwords
    failed = True
    if (os.path.exists(__passwords__(chvaldir))):
        if (os.path.isfile(__passwords__(chvaldir))):
            failed = False
    if (failed):
        open(__passwords__(chvaldir), 'wb').close()

    # CHVALDIR/chvalrc
    failed = True
    if (os.path.exists(__config__(chvaldir))):
        if (os.path.isfile(__config__(chvaldir))):
            failed = False
    if (failed):
        config = ConfigParser.SafeConfigParser()
        config.add_section("options")
        config_file = open(__config__(chvaldir), 'wb')
        config.write(config_file)
        config_file.close()

    # CHVALDIR/run
    failed = True
    if (os.path.exists(__run_dir__(chvaldir))):
        if (os.path.isdir(__run_dir__(chvaldir))):
            failed = False
    if (failed):
        os.mkdir(__run_dir__(chvaldir))

################################################################################
### Miscallenous
################################################################################
class NameSpace():
    """
    Used as a C struct.
    """
    def __init__(self):
        pass

def get_terminal_size():
    """
    Return terminal size.
    This function has been found on the internet. I did not tried to undersand
    it.
    """
    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct
            cr = struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ,
        '1234'))
        except:
            return None
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        try:
            cr = (os.environ['LINES'], os.environ['COLUMNS'])
        except:
            cr = (25, 80)
    return int(cr[1]), int(cr[0])

if __name__ == '__main__':
    error("This module is not meant to be run alone.")
