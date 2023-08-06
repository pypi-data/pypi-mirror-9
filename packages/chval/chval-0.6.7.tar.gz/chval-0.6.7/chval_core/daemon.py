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
Module related to communication between daemons and clients.

Important classes are:
    - Daemon: manage a daemon
    - Communication: communicate with a daemon (client side)
"""

# Third party modules
import lockfile
import os
import pexpect
import pickle
import Queue
import sys
import time
import traceback
from subprocess import Popen, PIPE
from threading import Thread, Semaphore, Timer

# Cheval modules
import chval_core as core
import chval_core.enum as enum
from chval_core import __d2c__
from chval_core import warning, trace, error
from chval_core.config_file import get_global_config

################################################################################
### Constants, classes and functions related to interprocess management
################################################################################
# States of the daemon
__daemon_state__ = enum.Enum(
    "none", # Daemon is not ready yet
    "password", # Waiting for password
    "running", # Running
    )

# Daemon and client use named pipes to communicate.
# The daemon runs two to three threads: a reader, a timer, and a worker.
# * Reader
#   Its purpose is to read from the daemon's fifo, and process what it gets. It
#   actually runs client's orders.
# * Timer
#   Every 'delay' minutes ('delay' being set by command line or configuration
#   file), it sends a message to the reader, to get mails.
# * Worker
#   Is created by the Reader whenever it has to get mails. Only get mails once.
#
# The Worker and the Timer are launched by the Reader, once a valid password
# has been provided
#
# There are one named pipe for the daemon, with name "PID.daemon", or
# "name.daemon", depending if a name has been provided for the daemon. This
# pipe is used by clients to send messages to the daemon.
# Each client trying to communicate with daemon creates a named pipe "PID.PID",
# where the first PID is the one of the daemon, and the second is the one of
# the client.
#
# Communication from client to daemon is done using package pickle. Each
# message sent to the daemon is a tuple (client, function, arguments), where:
# - client is the filename corresponding to the client. The answer will be sent
#   there.
# - function is the name of the method of the daemon to call. To restrict the
#   range of methods that can possibly be called by client, it can only call
#   methods beginning with "client_".
# - arguments is a (possibly empty) list of the arguments to be passed to the
#   method.
# Return value of function (there must be one) is returned through fifo
# "client". If an error occured, "None" is returned.
#
# Communication from daemon to client is done using package pickle. Each
# message sent to the client is a tuple (daemon, type, value), where:
# - daemon identifies the daemon (to know which daemon has sent the message)
# - type is the type of the message. They are listed in enumeration type
#   chval_core.__d2c__
# - value is the content of the message. Its (Python) type depends on the
#   second element of the tuple.

def valid_request(request):
    """
    Return True iff the request of the client to the daemon is a valid one.
    """
    # Request is a tuple
    if (type(request) != type(())):
        warning("Request is not a tuple.")
        return False
    # Tuple has three elements
    if (len(request) != 3):
        warning("Request has not three elements")
        return False
    # First element is a string
    if (type(request[0]) != type("")):
        warning("First element is not a string.")
        return False
    # File exist
    if (not os.path.exists(request[0])):
        warning("File %s does not exist." % request[0])
        return False
    # Second element is a string
    if (type(request[1]) != type("")):
        warning("Second element is not a string.")
        return False
    some = Daemon(None, None, None, None)
    # Second element is a method of the daemon
    try:
        if (type(getattr(some, request[1])) != type(getattr(some, "__init__"))):
            warning("Method asked does not exist.")
            return False
    except AttributeError:
        warning("Method asked does not exist.")
        return False
    # Second element is a method that can be called by client
    if (not request[1].startswith("client_")):
        warning("Client is not allowed to run this method.")
        return False
    # Last element is a list
    if (type(request[2]) != type([])):
        warning("Last element is not a list.")
        return False

    # Ok. I consider the request to be valid.
    return True

def list_daemons(run_dir, clean = False):
    """
    Return the list of available daemons. The list that is actually returned is
    the list of named pipes corresponding to daemons.
    Only returns daemons that answer to ping.
    If argument 'clean' is True, remove files corresponding to dead daemons.
    """
    def ping(com, queue, sem):
        """
        Check if daemon of Communication object 'com' answers to ping.
        If ping is answered, put daemon name (com.daemon) in the queue.
        """
        if (com.open()):
            com.ping()
            com.close()
            queue.put(com.daemon)
        sem.release()

    # Candidates is the list of all possible daemons (based on existing files
    # in .chval/run)
    filtre = lambda name: name.endswith(".daemon")
    candidates = [full_name[:-7] for full_name in
            [item for item in os.listdir(run_dir) if filtre(item)]]

    # For each possible daemon, run ping() in a Thread. This function put
    # daemon name in the queue "answer" as soon as daemon has answered to ping,
    # and increments the semaphore.
    answer = Queue.Queue()
    sem = Semaphore(0)
    com_list = {}
    for daemon in candidates:
        com_list[daemon] = Communication(run_dir, daemon)
        item = Thread(target = ping, kwargs =
                {'com' : com_list[daemon], 'queue' : answer, 'sem' : sem},
                name = "ping %s" % daemon)
        if (hasattr(item, "daemon")):
            item.daemon = True
        else:
            item.setDaemon(True)
        item.start()

    # Wait until either:
    # - semaphore count is equal to the number of candidates: they all have
    #   answered to ping.
    # - __daemon_timeout__ is passed: some daemons have not answered; they are
    #   considered dead. When this condition is met, we fill the semaphore to
    #   match the first condition.
    timers = []
    for i in candidates:
        timers.append(Timer(core.__daemon_timeout__, sem.release))
        timers[len(timers) - 1].start()
    for i in candidates:
        sem.acquire()
    for i in timers:
        i.cancel()

    # Names in the queue "answer" are names of daemons that answered ping.
    # Other daemons are considered dead
    result = []
    while (not answer.empty()):
        alive = answer.get()
        result.append(alive)
        candidates.remove(alive)
    for dead in candidates:
        if (clean):
            warning("Removing dead daemon '%s'." % dead)
            com_list[dead].clean()

    return result

class Communication():
    """Called by a client: handle communication with a daemon"""

    def __init__(self, rundir, daemon):
        self.daemon = daemon
        self.rundir = rundir
        self.client_fifo = os.path.join(
                self.rundir, daemon + "." + str(os.getpid()))
        self.from_daemon = None
        self.to_daemon = None

    def open(self):
        """
        Open communication: create pipe to receive answers, and open pipes.

        Return True iff no error was detected.
        """
        try:
            os.mkfifo(self.client_fifo)
            self.from_daemon = open(self.client_fifo, 'r+')
            self.to_daemon = open(
                    os.path.join(self.rundir, self.daemon + ".daemon"), 'w', 0)
        except:
            return False
        return True

    def close(self):
        """
        Close communication: close and delete pipe created with self.open()
        """
        if (self.from_daemon):
            self.from_daemon.close()
        if (self.to_daemon):
            self.to_daemon.close()
        if (os.path.exists(self.client_fifo)):
            os.remove(self.client_fifo)

    def clean(self):
        """
        Clean files related to this daemon.
        Preconditions:
        - daemon is not running;
        - either self.open() has not been called, or self.close() has been
          called.
        """
        filtre = lambda name: name.startswith(self.daemon)
        for fifo in [
                item for item in os.listdir(self.rundir) if filtre(item)]:
            os.remove(os.path.join(self.rundir, fifo))



    def call(self, function, arguments):
        """
        Send message to the daemon, so that it executes function given in
        arguments, using the arguments list provided.
        Note: the function must be one of the methods of Daemon, beginning with
        "client_". This is done to prevent clients to execute *any* Daemon
        method.
        """
        locked_write(self.to_daemon, (self.client_fifo, function, arguments))
        return pickle.load(self.from_daemon)

    def ping(self):
        """
        Ping daemon.
        Return True.
        """
        daemon_version = self.call("client_ping", [])
        if (daemon_version != core.__version__):
            warning("Versions of client (%s) and daemon (%s) are different. "
                    "This may lead to errors. Continuing anyway." %
                    (core.__version__, daemon_version))
        return daemon_version

    def get_state(self):
        "Get daemon's state"
        return self.call("client_get_state", [])

    def get_key(self):
        "Get daemon's public key"
        return self.call("client_get_key", [])

    def send_password(self, password):
        """
        Send password to daemon.
        Return True iff password is correct.
        """
        return self.call("client_send_password", [password])

    def get_mail(self, logfile, getmailrc):
        """
        Ask daemon to return a signal to launch a worker.
        Arguments:
        - logfile: filename in which to send some user feedback.
        - getmailrc: list of getmailrc file names to get mail from.
        """
        return self.call("client_get_mail", [logfile, getmailrc])

    def kill(self):
        """
        Ask daemon to stop.
        """
        self.call("client_stop", [])
        self.clean()
        return True

    def get_getmailrc(self):
        """
        Return a list of getmailrc files handled by the daemon.
        """
        return self.call("client_get_getmailrc", [])

class Daemon():
    """
    Class handling a daemon: create it, start it, etc.
    """
    def __init__(self, crypt, passwords, files, options):
        """
        "options" must have attribute "rundir" which is the name of the
        directory holding fifos.
        """
        self.state = __daemon_state__.none
        self.crypt = crypt
        self.passwords = passwords
        self.files = files
        self.options = options
        self.fifo_out = {}
        self.fifo_in = None
        self.name_in = ""
        if (options):
            self.rundir = options.rundir

    def prepare(self):
        """
        Prepare daemon, that is:
        - check that name is unique
        - create fifo.

        Return True iff no errors occured, False otherwise
        """
        trace("Preparing daemon...")
        # Listing existing (dead or alive) daemons
        daemons = list_daemons(self.rundir)
        # Checking that no daemon with the same name already exists
        if (self.options.name in daemons):
            warning("Error: A running daemon already exists with this name.")
            return False

        # Creating fifo to receive data
        self.name_in = os.path.join(
                self.rundir, self.options.name + ".daemon")
        if (os.path.exists(self.name_in)):
            warning("Error: A dead daemon already exists with this name. Run "
                    "\"chval clean\" to delete it.")
            return False
        try:
            os.mkfifo(self.name_in)
        except:
            return False
        return True

    def launch_reader(self):
        """
        Main method of the daemon: launch the reader, that reads daemon's fifo,
        and answer requests it get.
        """
        if (self.passwords):
            # At least one getmailrc passwords is unknown. Need main password
            # to decrypt this getmailrc password.
            self.state = __daemon_state__.password
        else:
            # All getmailrc passwords are known. No need to know the main
            # password.
            self.state = __daemon_state__.running
        self.fifo_in = open(self.name_in, 'r+')
        trace("Daemon started.")
        while True:
            request = pickle.load(self.fifo_in)
            trace("Request: " + str(request) + "...", False)
            # Ignoring invalid request
            if (not valid_request(request)):
                warning("Invalid request sent to daemon: " + str(request))
                continue
            # Answering request
            fifo = open(request[0], 'w')
            # Special case: asking to stop the daemon
            if (request[1] == "client_stop"):
                locked_write(fifo, True)
                fifo.close()
                warning("Daemon killed by client.")
                sys.exit(0)
            else:
                locked_write(fifo, getattr(self, request[1])(request[2]))
                trace(" Answered.")
                fifo.close()

    def launch_timer(self):
        "Launch thread calling getmail every 'options.delay' minutes"""
        if (self.options.delay != 0):
            timer = Thread(
                    target = thread_timer, args=(),
                    kwargs={'delay' : self.options.delay,
                        'fifo_name' : self.name_in, 'getmailrc' : self.files},
                    name = "timer"
                    )
            if (hasattr(timer, "daemon")):
                timer.daemon = True
            else:
                timer.setDaemon(True)
            timer.start()


    # Function callable by clients
    def client_ping(self, __args__):
        """
        Ping: return version to say 'Hey! I'm alive!'
        Can be also used to get the version of the daemon.
        Arguments are irrelevant.
        """
        return core.__version__

    def client_get_state(self, __args__):
        """
        Return daemon's state
        Arguments are irrelevant.
        """
        return self.state

    def client_get_key(self, __args__):
        """
        Return daemon's public key
        Arguments are irrelevant.
        """
        return self.crypt.rsa.publickey()

    def client_send_password(self, args):
        """
        Method by which client send to the daemon the password that the user
        gave.
        Check password, and launch the timer thread.
        Arguments: a list of one element, this element (a string), being the
        (encoded) password sent by the client (thus, sent by the user).
        Return True iff password was right
        """
        if (type(args) != type([])):
            return False
        if (len(args) != 1):
            return False

        password =  self.crypt.rsa.decrypt(args[0])
        if (self.crypt.check_password(password)):
            self.state = __daemon_state__.running
            trace("Password ok.")
            self.launch_timer()
        else:
            trace("Wrong password sent.")
            return False
        return True

    def client_get_mail(self, args):
        """
        Send the signal to get mail.
        Argument: a list of two elements:
        - the first one is a string, this string representing the filename in
          which to print userfeedback (usually a fifo read by some other thread
          or process).
        - the second one is the list of getmailrc files to get mail from.
        """
        if (len(args) != 2):
            return False
        if (type(args[0]) != type("") and type(args[1] != type([]))):
            return False
        feedback = args[0]
        getmailrc = args[1]

        Thread(
                target = thread_worker, args=(),
                kwargs={
                    'crypt' : self.crypt, 'passwords' : self.passwords,
                    'files' : getmailrc, 'options' : self.options,
                    'feedback' : feedback, 'daemon' : self.options.name},
                name = "worker"
                ).start()
        return True

    def client_stop(self, args):
        """
        Special method: does nothing.
        It is still here so that function "valid_request", that checks is
        client is authorized to run the asked method, will not fail when client
        asks to run "client_stop". But this method is never ran, as this
        request is a special case of "launch_reader" (of class Daemon).
        """
        pass

    def client_get_getmailrc(self, __args__):
        """
        Return the list of getmailrc files handled by this daemon.
        """
        return self.files


def thread_timer(delay, fifo_name, getmailrc):
    """
    Call getmail every "delay" minutes.
    Arguments:
    - delay: time between two calls
    - fifo_name: name of the daemon fifo
    - getmailrc: list of getmailrc file names to get mail from.

    Precondition:
        The state of the calling daemon must be __daemon_state__.running
    """
    to_daemon = open(fifo_name, 'w', 0)
    while (True):
        warning("Next call of \"getmail\" on %s."
                % time.ctime(time.time() + delay * 60))
        time.sleep(delay * 60)
        locked_write(to_daemon,
                (os.devnull, "client_get_mail", ["", getmailrc]))

def send_error_message(daemon, getmailrc, feedback_file, error_messages):
    """
    Send an email to warn user that there was an error during call of getmail.

    Arguments:
    - daemon: name of the daemon that failed (None for no daemon).
    - getmailrc: name of the getmailrc file that failed.
    - feedback_file: destination of log messages (possibly None).
    - error_messages: couple of a short and long messages explaining the error.
    """
    try:
        locked_write(feedback_file, (daemon, 
                __d2c__.error, "%s: %s" % (getmailrc, error_messages[0])))
    except IOError:
        warning('Warning: Could not send error message to client.')
    if (daemon):
        # Send to user a notice that script ended for unexpected reasons
        warning('Error while getting mails')
        # Sending email to notify user
        call = Popen(
                [core.__sendmail__, "-i", os.getlogin()], stdin = PIPE)
        call.stdin.write("Subject: [chval] Getmail error\n")
        call.stdin.write("\n") # blank line separating headers from body
        call.stdin.write(error_messages[1])
        call.stdin.close()
        sts = call.wait()
        if sts != 0:
            error("Error while sending email to notify daemon error. "
                "Sounds bad, isn't it?")


def thread_worker(crypt, passwords, files, options, feedback, daemon):
    """
    Get mails (using 'getmail' for files 'files')
    Arguments:
    - crypt: object used to encrypt/decrypt strings
    - passwords: dictionary of (encrypted) passwords
    - files: list of getmail config files to perform getmail on (they actually
      are keys of dictionary 'passwords')
    - feedback: filename in which to write user feedback. None for no feedback
    - daemon: caller's name if caller is a daemon, None otherwise
    - options: a class that is supposed to have the following attributes:
        - parallel: True iff system calls to getmail are to be launched in
          parallel
        - options: options to be passed to getmail
        - gap: time between two successive calls of getmail.

    Precondition:
        - If caller is a daemon, its state must be __daemon_state__.running
        - crypt.check_password must have been called successfully.
    """
    def call_system_getmail(config_file, options, crypt, passwords,
            feedback_file, logfile):
        """
        Perform system call to getmail, and analyse result using pexpect.

        Arguments:
        - daemon: caller's name if caller is a daemon, None otherwise
        - config_file: getmailrc file (without the leading "getmailrc-") used
          to get mails.
        - crypt: object used to encrypt/decrypt strings.
        - passwords: dictionary of (encrypted) passwords.
        - feedback_file: file in which to print feedback, for client (possibly
          None if no feedback is asked).
        - logfile: file in which to write log.
        - options: an object containing at least the following attributes:
            - options: list of options to give to getmail in the command line.
            - getmaildir: location of getmail configuration and data files.
        """
        if (daemon):
            full_name = "%s.%s" % (daemon, config_file)
        else:
            full_name = "%s" % config_file

        command = "getmail "
        for item in options.options:
            command += " " + item
        if (options.getmaildir):
            command += " --getmaildir " + options.getmaildir
        command += " --rcfile "
        command += os.path.join(options.getmaildir, "getmailrc-" + config_file)
        locked_write(feedback_file,
                (daemon, __d2c__.getmail_begin, [config_file]))
        try:
            child = pexpect.spawn(command,
                  logfile = logfile,
                  timeout = get_global_config(
                      "options", "getmail_timeout", int))
            downloaded = 0
            while True:
                i = child.expect(['Enter password for.*:.*:.*:  ',
                    r'msg [0-9]+\/[0-9]+ .*delivered', r'[0-9]+ messages',
                    pexpect.EOF])
                if (i == 0):
                    child.logfile = None
                    child.sendline(
                            crypt.decrypt(passwords[config_file], config_file)
                            + '\r')
                    child.logfile = logfile
                if (i == 1):
                    locked_write(feedback_file, (
                            daemon, __d2c__.getmail_got_message,
                            [config_file] +
                            child.match.group().split(" ")[1].split("/")))
                if (i == 2):
                    downloaded = child.match.group().split(" ")[0]
                if (i == 3):
                    child.expect(pexpect.EOF)
                    locked_write(feedback_file, (daemon,
                            __d2c__.getmail_end, [config_file, downloaded]))
                    break
        except Exception as execp:
            trace("Exception: %s" % str(execp))
            trace(traceback.format_exc(None))
            send_error_message(daemon, config_file, feedback_file,
                    (str(execp), traceback.format_exc(None)))


    if (daemon):
        logfile = sys.stdout
    else:
        logfile = None
    if (feedback):
        feedback_file = open(feedback, 'w', 0)
    else:
        feedback_file = None

    try:
        locked_write(feedback_file, (daemon, __d2c__.daemon_start, None))
        if (options.parallel):
            # Creating threads
            threads = [Thread(target = call_system_getmail, kwargs={
                'config_file' : config_file,
                'options' : options, 'crypt' : crypt,
                'passwords' : passwords, 'feedback_file' : feedback_file,
                'logfile' : logfile},
                name = "getmail %s" % config_file)
                for config_file in files]
            # Launching threads
            for item in threads:
                item.start()
                time.sleep(options.gap)
            # Waiting for threads
            for item in threads:
                item.join()
        else:
            for config_file in files:
                call_system_getmail(config_file, options, crypt,
                    passwords, feedback_file, logfile)
                time.sleep(options.gap)
        locked_write(feedback_file, (daemon, __d2c__.daemon_stop, None))
    except KeyboardInterrupt:
        warning('Operation aborted by user (keyboard interrupt)\n')
        sys.exit(0)
    except Exception, excep:
        send_error_message(feedback, None, feedback_file,
                (str(excep), traceback.format_exc(None)))
    if (feedback_file):
        feedback_file.close()

def locked_write(dest, message):
    """
    Write "message" to fifo "dest" (using pickle), using a lock.

    If "dest" is None, do nothing.
    """
    if (dest):
        lock = lockfile.SQLiteFileLock(dest.name + ".lock")
        while True:
            try:
                lock.acquire(timeout = 60)
            except lockfile.LockTimeout:
                warning("Error: Could not acquire lock \"%s\". Breacking it."
                        % lock.path)
                lock.break_lock()
                continue
            break
        pickle.dump(message, dest)
        try:
            lock.release()
        except lockfile.NotLocked:
            pass

if __name__ == '__main__':
    error("This module is not meant to be run alone.")
