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
Interface management
"""

# Third party modules
import os
import pickle
import tempfile
from threading import Thread

# Cheval modules
import chval_core as core
import chval_core.enum as enum
from chval_core import __d2c__
from chval_core import write, warning, trace

### List of available interfaces
__list__ = enum.Enum(
    "default",
    "linear",
    "dialog",
    "none",
    )

################################################################################
### Check whether a daemon answer is valid or not
################################################################################
def valid_answer(request):
    """
    Return True iff the answer sent by the daemon to the client is a valid one.
    """
    # Request is a tuple
    if (type(request) != type(())):
        warning("Request is not a tuple.")
        return False
    # Tuple has three elements
    if (len(request) != 3):
        warning("Request has not three elements")
        return False
    # First element is a string or None
    if (request[0] != None and type(request[0]) != type("")):
        warning("First element is not a string.")
        return False
    # Second element is a enum (as of class Const)
    if (type(request[1]) != enum.Enum().__enum_type__()):
        warning("Second element has a wrong type.")
        return False

    # Ok. I consider the request to be valid.
    return True

################################################################################
### Class to manage user feedback through different interfaces.
################################################################################
class Interface(object):
    """
    Class managing user feedback
    """

    def __init__(self, getmailrc, sem = None):
        """
        Arguments:
        - getmailrc: dictionary of considered getmailrc files.
          getmailrc["main"]=set(["work", "private"]) means "from daemon 'main',
          get mails for getmailrc files 'work' and 'private'".
        - sem: can be either None, in which case it is irrelevant, or a
          semaphore that will be incremented each time a daemon has been
          thoroughly processed.
        """
        self.__tmpdir = tempfile.mkdtemp()
        self.__tmpfifo = os.path.join(self.__tmpdir, 'fifo')
        self.getmailrc = getmailrc
        self.sem = sem
        os.mkfifo(self.__tmpfifo)
        self.thread = None

    def get_fifo(self):
        """
        Return the fifo object.
        Preconditions:
        - Remove has not be called.
        """
        return self.__tmpfifo

    def start(self):
        """
        Print user feedback, reading daemon progress from self.__tmpfifo.
        Basically calls child's functions child_start().
        """
        self.thread = Thread(
            target = self.child_start,
            name = "interface"
            )
        self.thread.start()


    def wait_and_clean(self):
        """
        Wait for the thread launched in self.start() to finish, and do some
        cleaning afterwards.
        """
        self.thread.join()
        self.close()
        self.remove()

    def remove(self):
        """
        Remove the file and directory that have been created by __init__
        """
        os.remove(self.__tmpfifo)
        os.rmdir(self.__tmpdir)

    def process_fifo(self):
        """
        Print content of the fifo to stdandard out (using method process_line)
        """
        read = open(self.__tmpfifo, 'r+')
        running = len(self.getmailrc.keys())
        while running > 0:
            try:
                answer = pickle.load(read)
            except EOFError:
                break
            if (not valid_answer(answer)):
                warning("Invalid message sent to client: " + str(answer))
                continue
            (daemon, msg_type, msg_value) = answer

            # Processing message
            if (msg_type == __d2c__.getmail_begin):
                # mcontent = [name of the daemon, name of the getmailrc file]
                self.process_line(__d2c__.getmail_begin, [daemon, msg_value[0]])
            elif (msg_type == __d2c__.getmail_got_message):
                # mcontent = [name of the daemon, name of the getmailrc file,
                # #email received, total number of emails]
                self.process_line(__d2c__.getmail_got_message,
                        [daemon, msg_value[0], msg_value[1], msg_value[2]])
            elif (msg_type == __d2c__.getmail_end):
                # mcontent = [name of the daemon, name of the getmailrc file,
                # number of emails received]
                self.process_line(__d2c__.getmail_end,
                        [daemon, msg_value[0], msg_value[1]])
            elif (msg_type == __d2c__.daemon_start):
                # mcontent = [name of the daemon]
                self.process_line(__d2c__.daemon_start, [daemon])
            elif (msg_type == __d2c__.daemon_stop):
                # mcontent = [name of the daemon]
                if (self.sem):
                    self.sem.release()
                self.process_line(__d2c__.daemon_stop, [daemon])
                running -= 1
            elif (msg_type == __d2c__.error):
                # mcontent = [name of the daemon, some explanation of the error]
                if (self.sem):
                    self.sem.release()
                self.process_line(__d2c__.error,
                        [daemon, msg_value])
            else:
                trace("Ignoring message %s" % __d2c__.__enum_name__(msg_type))
        read.close()

    # The following methods must be written by subclasses.
    def child_start(self):
        """
        Do some (optional) initialization, and launch function process_fifo.
        """
        self.process_fifo()

    def process_line(self, mtype, mcontent):
        """
        Print a message on the interface. The message type is "mtype" (it is
        one enumeration type of "__d2c__"); the message content (depending of
        "mtype") is "mcontent".  See code of "process_fifo()" to see which type
        and content are available for messages.
        """
        pass

    def close(self):
        """
        Automatically called when closing the interface.
        Optionaly undo some things done in self.child_start().
        """
        pass

################################################################################
### Example class used to create new interfaces.
################################################################################
class InterfaceDummy(Interface):
    """
    This class is a dummy interface, to serve as a pattern to create new
    interfaces.

    If you want to create a new interface, do not forget to add it to the list
    __list__ of interfaces, so that it can be selected in the command line.
    """

    def __init__(self, *args, **kwargs):
        """
        This method is optional. If you wish to change it, do not forget to
        call parent's initialization.
        """
        super(InterfaceDummy, self).__init__(*args, **kwargs)

    def child_start(self):
        """
        Perform initialization and launch the main function that handle
        communications with daemon.

        Note: this method is called as a thread. So the main process goes on
        while this one is run.
        """
        return super(InterfaceDummy, self).process_fifo()

    def process_line(self, mtype, mcontent):
        """
        Process one message got from the daemon.
        "mtype" is the type of the message that is received; and "mcontent" is
        some content that depends on the type. See the code of "process_fifo()"
        for details.

        This method is supposed to actually display user feedback.
        """
        print "%s %s" % (str(mtype), str(mcontent))

    def close(self):
        """
        Here things done in self.child_start() can be undone.
        """
        pass

################################################################################
### Linear interface
################################################################################
class InterfaceLinear(Interface):
    """
    Linear interface
    Information is printed on screen when it arrives, line after line.
    Should not change much, so that it can be used in scripts.
    """

    def process_line(self, mtype, mcontent):
        """
        Linear interface: each information is printed on one line, in the order
        in which it comes.
        """
        if (mtype == __d2c__.daemon_start):
            write("Processing daemon %s\n" % tuple(mcontent))
        if (mtype == __d2c__.getmail_begin):
            write("  Processing getmailrc %s.%s\n" % tuple(mcontent))
        if (mtype == __d2c__.getmail_got_message):
            write("    %s.%s: %s/%s\n" % tuple(mcontent))
        if (mtype == __d2c__.getmail_end):
            write("  getmailrc %s.%s done\n" % tuple(mcontent[0:2]))
        if (mtype == __d2c__.error):
            write("%s error: %s\n" % tuple(mcontent))
        if (mtype == __d2c__.daemon_stop):
            write("daemon %s done\n" % tuple(mcontent))

################################################################################
### Empty interface
################################################################################
class InterfaceNone(Interface):
    """
    No interface. Print nothing.
    """

################################################################################
### Classes handling progress of email fetching
################################################################################
# Enumeration type for the progress status.
# The values of items corresponds to values of items of option
# "mixedgauge" of dialog (see "man 3 dialog").
__PROGRESS_STATUS__ = enum.Enum()
__PROGRESS_STATUS__.__register__("none", 9) # Nothing began yet
__PROGRESS_STATUS__.__register__("running", 7) # Running
__PROGRESS_STATUS__.__register__("done", 3) # Completed

class GetmailrcProgress():
    """
    Gather information about the progress of downloading emails handled by one
    getmailrc file.
    """

    def __init__(self, name, propagate_percent):
        """
        Arguments:
        - name: name of the getmailrc file handled
        - propagate_percent: method to call when percent has been changed.
        """
        self.name = name
        self.propagate_percent = propagate_percent
        # status is the progress of the downloading of the getmailrc file, as a
        # __PROGRESS_STATUS__ variable;
        self.status = __PROGRESS_STATUS__.none
        # minimum is the number of the first email to be downloaded (None if
        # this information is not known yet);
        self.minimum = None
        # maximum is the number of the last  email to be downloaded (None if
        # this information is not known yet);
        self.maximum = None
        # percent is the percentage of the emails that have been downloaded.
        self.percent = 0
        # Example, if the first email that was downloaded was email 12, and we
        # just downloaded email 14 of 15, values of [minimum, maximum, percent]
        # are [12, 14, 75].

    def __str__(self):
        if (self.name):
            return self.name
        else:
            return ""

    def set_percent(self, value):
        """
        Set attribute self.percent
        Run method self.propagate_percent() so that parent's percent is updated
        as well.
        """
        self.percent = value
        self.propagate_percent()

class DaemonProgress():
    """
    Gather information about the progress of downloading emails handled by one
    daemon.
    """
    def __init__(self, name, getmailrc, propagate_percent):
        """
        Arguments:
        - name: name of the daemon
        - getmailrc_list: list of getmailrc files handled by this daemon.
        - propagate_percent: method to call when percent has been changed.
        """
        self.propagate_percent = propagate_percent
        self.name = name
        self.percent = 0
        # status is the progress of the daemon, as a __PROGRESS_STATUS__ item;
        self.status = __PROGRESS_STATUS__.none
        # getmailrc_list is a dictionary of GetmailrcProgress objects, each of
        # them representing a getmailrc file handled by the daemon.
        self.getmailrc_list = {}
        for item in getmailrc:
            self.getmailrc_list[item] = \
                    GetmailrcProgress(item, self.update_percent)

    def __str__(self):
        if (self.name):
            return self.name
        else:
            return ""

    def __getitem__(self, index):
        return self.getmailrc_list[index]

    def __setitem__(self, index, value):
        self.getmailrc_list[index] = value

    def keys(self):
        """
        Return list of keys of dictionary self.daemon_list
        """
        return self.getmailrc_list.keys()

    def values(self):
        """
        Return list of values of dictionary self.daemon_list
        """
        return self.getmailrc_list.values()

    def update_percent(self):
        """
        Update attribute self.percent.
        It is computed as: each getmailrc file has the same part of the overall
        progress (i.e. if there are 10 getmailrc files, each count for 10% of
        the overall progress).
        For example, suppose there are 5 getmailrc files (each of them have 20%
        of the overall). One of them is 50% complete, another is 10% complete,
        and the other ones have not started (0% complete). The overall progress
        is 20% * 50% + 20% * 10% + 3 * (20% * 0%) = 12%.
        """
        total = len(self.keys())
        percent = sum([g.percent for g in self.values()])
        self.percent = percent / total
        self.propagate_percent()


class OverallProgress():
    """
    Handles progress of the download of mails for each getmailrc file of each
    daemon.
    """

    def __init__(self, daemons_getmailrcs):
        """
        Arguments:
        - daemons_getmailrcs: dictonary with daemon names as keys, and list of
          getmailrc names handled by each daemon as values.
        """
        # Overall progress (in percent)
        self.percent = 0

        self.daemon_list = {}
        for item in daemons_getmailrcs.keys():
            self[item] = DaemonProgress(
                    item, daemons_getmailrcs[item], self.update_percent)

    def update_percent(self):
        """
        Update attribute self.percent.
        It is computed as: each daemon has the same part of the overall
        progress (i.e. if there are 10 daemons, each count for 10% of the
        overall progress).
        For example, suppose there are 5 daemons (each of them have 20% of the
        overall). One of them is 50% complete, another is 10% complete, and the
        other ones have not started (0% complete). The overall progress is 20%
        * 50% + 20% * 10% + 3 * (20% * 0%) = 12%.
        """
        total = len(self.keys())
        percent = sum([d.percent for d in self.values()])
        self.percent = percent / total

    def __getitem__(self, index):
        return self.daemon_list[index]

    def __setitem__(self, index, value):
        self.daemon_list[index] = value

    def keys(self):
        """
        Return list of keys of dictionary self.daemon_list
        """
        return self.daemon_list.keys()

    def values(self):
        """
        Return list of values of dictionary self.daemon_list
        """
        return self.daemon_list.values()


################################################################################
### Meta-class to be subclassed by interfaces that need to be aware of overall,
### daemon and getmailrc progress.
################################################################################
class InterfaceProgress(Interface):
    """
    Meta-class to be subclassed by interfaces that need to be aware of overall,
    daemon and getmailrc progress.
    """
    def __init__(self, *args, **kwargs):
        super(InterfaceProgress, self).__init__(*args, **kwargs)
        self.progress = OverallProgress(self.getmailrc)

    def child_start(self):
        """
        No initialization is done here.
        """
        return super(InterfaceProgress, self).process_fifo()

    def process_line(self, mtype, mcontent):
        """
        Update display according to messages got from daemon.
        """
        if (mtype in [__d2c__.daemon_start, __d2c__.daemon_stop]):
            # Daemon start and stop
            daemon = self.progress[mcontent[0]]
            if (mtype == __d2c__.daemon_start):
                daemon.status = __PROGRESS_STATUS__.running
            if (mtype == __d2c__.daemon_stop):
                daemon.status = __PROGRESS_STATUS__.done
        elif (mtype in [
            __d2c__.getmail_begin, __d2c__.getmail_got_message,
            __d2c__.getmail_end]):
            getmailrc = self.progress[mcontent[0]][mcontent[1]]
            # Getmailrc related messages
            if (mtype == __d2c__.getmail_begin):
                getmailrc.status = __PROGRESS_STATUS__.running
                getmailrc.set_percent(0)
            if (mtype == __d2c__.getmail_end):
                getmailrc.status = __PROGRESS_STATUS__.done
                getmailrc.set_percent(100)
            if (mtype == __d2c__.getmail_got_message):
                if (getmailrc.minimum == None):
                    getmailrc.minimum = int(mcontent[2])
                    getmailrc.maximum = int(mcontent[3])
                getmailrc.set_percent(100 * \
                        (int(mcontent[2]) - getmailrc.minimum + 1) / \
                        (getmailrc.maximum - getmailrc.minimum + 1))
        self.print_interface()

    def close(self):
        """
        Nothing to clean.
        """
        pass

    def print_interface(self):
        """
        Actually print the interface.
        Should be rewritten in child class (otherwise this class is not very
        interesting).
        """
        pass



################################################################################
### Prints user feedbak using program dialog.
################################################################################
class InterfaceDialog(InterfaceProgress):
    """
    Class used to print user feedback using program dialog.
    """

    def print_interface(self):
        """
        Display information:
        - build the command to launch;
        - run it.
        """
        cmd = ""
        cmd += "dialog --title \"Fetching mails\" --mixedgauge \"\" 0 0 "
        cmd += str(self.progress.percent) + " "
        for daemon in self.progress.values():
            # Each deamon has its own gauge.
            if (daemon.name != None):
                if (daemon.status == __PROGRESS_STATUS__.running):
                    status = "-" + str(daemon.percent)
                else:
                    status = str(daemon.status)
                cmd += "\"# " + str(daemon) + "\" \"" + status + "\" "
            for getmailrc in daemon.values():
                # Each getmailrc file has its own gauge.
                if (getmailrc.status == __PROGRESS_STATUS__.running):
                    status = "-" + str(getmailrc.percent)
                else:
                    status = str(getmailrc.status)
                cmd += "\"  " + str(getmailrc) + "\" \"" + status + "\" "
        # Launch it!
        os.system(cmd)

    def close(self):
        """
        Add a newline
        """
        write("\n")

################################################################################
### One line interface detailing progress of each getmailrc file
################################################################################
__NORMAL__ = '\033[0m'
__REVERSE__ = '\033[7m'
class InterfaceDefault(InterfaceProgress):
    """
    Default interface
    A little bit nicer than linear interface.
    """

    def __init__(self, *args, **kwargs):
        super(InterfaceDefault, self).__init__(*args, **kwargs)
        # Hiding cursor
        write("\033[?25l")

    def format(self, string, num, fill = " "):
        """
        Return a string having exactly "num" characters.
        If the string is bigger, cut it.
        If the string is smaller, add "fill" characters to it.
        """
        if (len(string) <= num):
            return string + fill * (num - len(string))
        else:
            return string[0:num]

    def print_interface(self):
        """
        Print the interface.

        The interface is one line, divided in one zone per getmailrc file.
        """
        terminal_width = core.get_terminal_size()[0]
        num = sum([len(d.keys()) for d in self.progress.values()])
        exact_size = (terminal_width - 2.0) / num - 1

        output = __REVERSE__ + "|" + __NORMAL__
        i = 0
        for daemon in self.progress.values():
            if (daemon.name):
                daemon_string = " (%s)" % str(daemon)
            else:
                daemon_string = ""
            for getmailrc in daemon.values():
                i += 1
                chunk = self.format("%s%s" % (str(getmailrc), daemon_string),
                        int((exact_size + 9) * i - len(output) + 1)) + "|"
                limit = (len(chunk) * getmailrc.percent) / 100
                output += \
                        __REVERSE__ + chunk[:limit] + __NORMAL__ + chunk[limit:]
        output += "\r"
        write(output)

    def close(self):
        """
        Back to normal.
        Reset normal color, display cursor, and start a new line.
        """
        write("\033[0m")
        write("\033[?25h")
        write("\n")
