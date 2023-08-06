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
Classes and functions related to command line parsing.
"""

# Third party modules
import argparse
import os
import textwrap

# Cheval modules
import chval_core as core
from chval_core import interfaces
from chval_core import warning, error
from chval_core.config_file import get_global_config
from chval_core.daemon import list_daemons

def format_string(string):
    """
    Format strings so that help strings in argument description can be 80
    characters long, and still appear nicely on screen when calling "chval
    --help".

    The format used is the following.
    - If all lines begin with the same number of spaces or tabs, they are
      removed (this is a simple call to textwrap.dedent().
    - A line beginning with a space is joined to the previous line.
    - Each line is wrapped not to be too long. In this case, if the original
      line began with tabs, every line but the first one begin with one more
      tab.
    """
    def spaces(string):
        "Return the number of leading spaces."
        return len(string) - len(string.lstrip(" "))
    def tabs(string):
        "Return the number of leading tabs"
        return len(string) - len(string.lstrip("\t"))

    original = textwrap.dedent(string).splitlines()
    joined = [original[0]]
    for line in original[1:]:
        if (spaces(line) == 0):
            joined.append(line)
        else:
            joined[-1] = joined[-1] + " " + line.lstrip(" ")
    wrapped = []
    for line in joined:
        if (tabs(line) == 0):
            indent = 0
        else:
            indent = tabs(line) + 1
        wrapper = textwrap.TextWrapper(subsequent_indent = "\t" * indent)
        wrapped.extend(wrapper.wrap(line))
    return "\n".join(wrapped)

class GetmailOptionsAction(argparse.Action):
    """
    Action used to convert '+' signs of option --getmail into '-'.
    Consider for example the following command line.
    $ chval getmail --options +q +d
    The options will be converted into "-q -d".
    """
    def __call__(self, parser, namespace, values, option_string=None):
        new = []
        for option in values:
            if (len(option) >= 2):
                if (option[0:2] == "++"):
                    new.append("--" + option[2:])
                elif (option[0] == "+"):
                    new.append("-" + option[1:])
                else:
                    new.append(option)
            elif (len(option) >= 1):
                if (option[0] == "+"):
                    new.append("-" + option[1:])
                else:
                    new.append(option)
            else:
                new.append(option)
        setattr(namespace, "getmail_options", new)

def parse(rundir, command_line):
    """
    Parse command line, and return "options", as returned by the argparse
    module.
    "rundir" is the name of the directory containing fifos for communication between daemons and clients.
    """

    # Global arguments
    args_global = argparse.ArgumentParser(add_help=False)
    args_global.add_argument('--version', help='Show version', action='version',
            version='%(prog)s ' + core.__version__)
    args_global.add_argument('--chvaldir', action='store', dest='chvaldir',
            default = core.__chvaldir__,
            help = format_string("""\
                    Use CHVALDIR for configuration and data files of chval.
                    """)
            )

    # Main parser
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Call getmail, using encrypted passwords.',
        parents=[args_global],
        epilog=format_string("""\
                Every getmailrc file name (files in which configuration of mail
                boxes to get mail from) must begin with 'getmailrc-'. This is
                forced because chval has no way to guess which files are
                getmairc files, and which are not. This convention helps it to
                tell apart getmailrc files and other files.
                """),
        )


    # Each of the following variable is a list of arguments that are relevant
    # for this function. These variable are used so that, when defining an
    # argument relevant to several options, we can put them in the right one.
    args_add = [args_global]
    args_clean = [args_global]
    args_client = [args_global]
    args_daemon = [args_global]
    args_fill = [args_global]
    args_getmail = [args_global]
    args_kill = [args_global]
    args_list = [args_global]
    args_passwords = [args_global]
    args_remove = [args_global]
    args_scan = [args_global]

    # Argument --getmaildir
    getmaildir = argparse.ArgumentParser(add_help = False)
    getmaildir.add_argument('--getmaildir', action='store', dest='getmaildir',
            default = get_global_config("options", "getmaildir"),
            help=format_string("""\
                    Use GETMAILDIR for configuration and data files of getmail.
                    """)
            )
    args_daemon.append(getmaildir)
    args_fill.append(getmaildir)
    args_getmail.append(getmaildir)

    # Argument --interface
    interface_argument = argparse.ArgumentParser(add_help = False)
    interface_argument.add_argument('-i', '--interface', action='store',
            dest='interface', type=str, choices=interfaces.__list__.__names__(),
            default=get_global_config("options", "interface"),
            help=format_string("""\
                    Set layout of user feedback. Available choices are: %s
                    """ %
                    reduce(
                        lambda x, y: x + " " + y,
                        interfaces.__list__.__names__())
                    )
            )
    args_client.append(interface_argument)
    args_getmail.append(interface_argument)

    # Argument --parallel
    parallel_argument = argparse.ArgumentParser(add_help = False)
    parallel_argument.add_argument('-p', '--parallel', action='store',
            dest='parallel', type=str,
            choices=['none', 'daemons', 'getmail', 'all'],
            default=get_global_config("options", "parallel"),
            help=format_string("""\
                    Set degree of parallelism:
                    \tnone: no parallelism;
                    \tdaemons: call all daemons in parallel (with \"client\"
                        only);
                    \tgetmail: within each daemon, getmail calls are done in
                        parallel (with \"--daemon\" or \"--getmail\" only);
                    \tall: all parallelism listed above.
                    Default is read from config file. If none is given, it is
                    \"none\".
                    """)
            )
    args_getmail.append(parallel_argument)
    args_daemon.append(parallel_argument)
    args_client.append(parallel_argument)

    # Argument --gap:
    gap_argument = argparse.ArgumentParser(add_help = False)
    gap_argument.add_argument('-g', '--gap', action='store', dest='gap',
            type=int, default=get_global_config("options", "gap"),
            help=format_string("""\
                Set the time interval between two calls of getmail. This is
                done so that, if you have ten accounts to get mail from, you
                will not launch ten instances of getmail at the same time, but
                leave a small time interval between two calls. Default is
                0.""")
            )
    args_getmail.append(gap_argument)
    args_daemon.append(gap_argument)

    # Argument --options
    options_argument = argparse.ArgumentParser(add_help = False)
    options_argument.add_argument('-o', '--options', dest='getmail_options',
            default = get_global_config("options", "getmail_options").split(),
            action=GetmailOptionsAction, nargs='*', help=format_string("""\
                    Arguments following this option will be transmitted to
                    \"getmail\". These arguments must begin with \'+\' instead
                    of the usual '-', to prevent to be mixed up with %(prog)s
                    arguments.""")
            )
    args_daemon.append(options_argument)
    args_getmail.append(options_argument)

    ## Subparsers
    subparsers = parser.add_subparsers(title='Subcommands',
            description='Choose one of the subcommands below')
    # Add
    parser_add = subparsers.add_parser('add', prog=core.__program_name__,
            help='Add a new password.', parents=args_add,
            formatter_class=argparse.RawTextHelpFormatter)
    parser_add.add_argument('getmail_files', metavar='GETMAILRC',
            action='store', nargs='+', help=format_string("""\
                    List of getmailrc files for which a password is to be
                    added.""")
            )
    parser_add.set_defaults(command = 'add')
    # Clean
    parser_clean = subparsers.add_parser('clean', prog=core.__program_name__,
            help='Remove dead daemons.', parents=args_clean,
            formatter_class=argparse.RawTextHelpFormatter)
    parser_clean.set_defaults(command = 'clean')
    # Client
    parser_client = subparsers.add_parser('client', prog=core.__program_name__,
            help='Ask daemon to download mail.', parents=args_client,
            formatter_class=argparse.RawTextHelpFormatter)
    parser_client.add_argument('-a', '--auth', action='store_true', dest='auth',
            help=format_string("""\
                    Do not get mails, but ask passwords for daemons that are
                    waiting for theirs.""")
            )
    parser_client.add_argument('daemons', metavar='DAEMONS', action='store',
            nargs='*', help=format_string("""\
                    List of daemons, or getmailrc files handled by daemons to
                    ask to download mails. If no daemon is given, perform
                    action on all getmailrc files of all available daemons.
                    Special forms are available (where DAEMON and GETMAILRC are
                    to be replaced by relevant values):
                    \tDAEMON: Get mail from this daemon.
                    \tDAEMON/: Equivalent to DAEMON.
                    \tDAEMON/GETMAILRC: get mail from GETMAILRC file handled by
                        DAEMON.
                    \t/GETMAILRC: get mail from GETMAILRC files from daemons
                        that handle such a file.""")
            )
    parser_client.set_defaults(command = 'client')
    # Daemon
    parser_daemon = subparsers.add_parser('daemon', prog=core.__program_name__,
            help='Run in daemon mode.', parents=args_daemon,
            formatter_class=argparse.RawTextHelpFormatter)
    parser_daemon.add_argument('-n', '--name', action='store', type=str,
            dest='daemon_name', metavar='NAME', help=format_string("""\
                    Name of the daemon (default is PID).""")
            )
    parser_daemon.add_argument('-d', '--delay', action='store', type=int,
            dest='daemon_delay',
            default=get_global_config("options", "daemon_cycle_time", int),
            metavar='DELAY',
            help=format_string("""\
                    Time (in minutes) between two succesive calls of
                    getmail. A value of 0 means that no automatic call to
                    \"getmail\" is performed.""")
            )
    parser_daemon.add_argument('-a', '--auth', action='store_true', dest='auth',
            help=format_string("""\
                    Cause daemon to ask for password as soon as it is started.
                    """)
            )
    parser_daemon.add_argument('getmail_files', metavar='GETMAILRC',
            action='store', nargs='*', help=format_string("""\
                    List of getmailrc files handled by this daemon. If none is
                    given, all getmailrc files for which a password is known,
                    and that are not already handled by another daemon, are
                    considered.""")
            )
    parser_daemon.set_defaults(command = 'daemon')
    # Fill
    parser_fill = subparsers.add_parser('fill', prog=core.__program_name__,
            help=format_string("""\
                    Ask for missing passwords ("fill in the blanks")."""),
            parents = args_fill,
            formatter_class=argparse.RawTextHelpFormatter)
    parser_fill.set_defaults(command = 'fill')
    # Getmail
    parser_getmail = subparsers.add_parser('getmail', help='Get mails.',
            prog=core.__program_name__, parents=args_getmail,
            formatter_class=argparse.RawTextHelpFormatter)
    parser_getmail.add_argument('getmail_files', metavar='GETMAILRC',
            action='store', nargs='*', help=format_string("""\
                    Fetch mail for getmailrc files specifyed in argument. If
                    none is given, get mail for every getmailrc file.""")
            )
    parser_getmail.set_defaults(command = 'getmail')
    # Kill
    parser_kill = subparsers.add_parser('kill', prog=core.__program_name__,
            help='Kill daemon.', parents = args_kill,
            formatter_class=argparse.RawTextHelpFormatter)
    parser_kill.add_argument('daemons', metavar='DAEMONS', action='store',
            nargs='*', help=format_string("""\
                    List of daemons to kill. If no daemon is given, kill all
                    available daemons.""")
            )
    parser_kill.set_defaults(command = 'kill')
    # List
    parser_list = subparsers.add_parser('list', prog=core.__program_name__,
            help=format_string("""\
            List getmail config files for which passwords are stored."""),
            parents=args_list, formatter_class=argparse.RawTextHelpFormatter)
    parser_list.add_argument('getmail_files', metavar='GETMAILRC',
            action='store', nargs='*', help=format_string("""\
                    List of getmailrc files to list.""")
            )
    parser_list.set_defaults(command = 'list')
    # Passwords
    parser_passwords = subparsers.add_parser('passwords',
            prog=core.__program_name__,
            help='Show stored passwords.', parents=args_passwords,
            formatter_class=argparse.RawTextHelpFormatter)
    parser_passwords.add_argument('getmail_files', metavar='GETMAILRC',
            action='store', nargs='*', help="List of getmailrc files to list.")
    parser_passwords.set_defaults(command = 'passwords')
    # Remove
    parser_remove = subparsers.add_parser('remove', prog=core.__program_name__,
            help='Remove (forget) a stored password.', parents=args_remove,
            formatter_class=argparse.RawTextHelpFormatter)
    parser_remove.add_argument('getmail_files', metavar='GETMAILRC',
            action='store', nargs='+', help=format_string("""\
                    List of getmailrc files for which password has to be
                    forgotten.""")
            )
    parser_remove.set_defaults(command = 'remove')
    # Scan
    parser_scan = subparsers.add_parser('scan', prog=core.__program_name__,
        help="Scan available daemons and list them.", parents = args_scan,
        formatter_class=argparse.RawTextHelpFormatter)
    parser_scan.add_argument('-d', '--daemon', action='store', default=None,
            dest='scan_daemons', nargs='*', help=format_string("""\
                    List of daemons to scan. If set, return the list of
                    getmailrc files handled by each of the daemons.

                    If no argument is given, return the list of getmailrc files
                    for all daemons.
                    """)
            )
    parser_scan.add_argument("-o", "--only", action='store_true', dest='only',
            help=format_string("""\
                    With option "-d", only print a list of getmailrc files,
                    without the daemon names.
                    """)
            )
    parser_scan.set_defaults(command = 'scan')

    # Special case: if no sub command is given, "artificially" assign a
    # subcommand: either client, or getmail.
    # If (at least) one daemon is running: consider subcommand "client".
    # Otherwise (no daemon are running): consider subcommand "getmail".
    no_subcommand = False
    if (len(command_line) == 0):
        no_subcommand = True
    elif (command_line[0] not in subparsers.choices.keys()
            and command_line[0] not in parser._option_string_actions.keys()):
        no_subcommand = True
    if (no_subcommand):
        if (list_daemons(rundir)):
            command_line.insert(0, "client")
        else:
            command_line.insert(0, "getmail")

    options = parser.parse_args(command_line)

    # Converting --parallel value from string to set
    if (hasattr(options, "parallel")):
        if (options.parallel == "none"):
            options.parallel = set([])
        elif (options.parallel == "getmail"):
            options.parallel = set([core.__parallel__.getmail])
        elif (options.parallel == "daemons"):
            options.parallel = set([core.__parallel__.daemons])
        elif (options.parallel == "all"):
            options.parallel = set(
                    [core.__parallel__.daemons, core.__parallel__.getmail]
                    )

    # Default value for --getmaildir and --chvaldir, and expanding ~ directory
    # if necessary
    if (hasattr(options, "getmaildir")):
        options.getmaildir = os.path.expanduser(options.getmaildir)
    if (hasattr(options, "chvaldir")):
        options.chvaldir = os.path.expanduser(options.chvaldir)

    # Converting value of --interface from string to the object that will later
    # be used as the interface.
    if (hasattr(options, "interface")):
        class_name = "Interface%s%s" % (
                options.interface[0].upper(), options.interface[1:])
        options.interface = getattr(interfaces, class_name)

    # With "chval scan", option "--only" is irrelevant without option
    # "--daemon"
    if (options.command == "scan"):
        if (options.only and options.scan_daemons == None):
            warning('Option "--only" is irrelevant without option "--daemon". '
                    'Continuing anyway.')

    return options

def search_chvaldir(command_line):
    """
    Look for a --chvaldir option in the command line, and return the argument
    (or default location of chvaldir if no option is given.
    """
    word = "--chvaldir"
    index = 0
    while(index < len(command_line)):
        if (command_line[index] == word):
            if (index == len(command_line) - 1):
                error("chval: error: missing argument for option %s." % word)
            else:
                return command_line[index + 1]
        if (command_line[index][0:len(word)] == word + "="):
            return command_line[index][len(word):]
        index += 1
    return core.__chvaldir__

if __name__ == '__main__':
    error("This module is not meant to be run alone.")
