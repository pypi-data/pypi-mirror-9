#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
"""
Module for creating generic, callback based wrappers.

It is little bit easier (at least for me) to use than the original `daemon
module <https://pypi.python.org/pypi/python-daemon/>`_.
"""
import sys


import daemon  # python-daemon package from pypi
from daemon import runner


class DaemonRunnerWrapper(object):
    def __init__(self, pid_filename):
        """
        Generic daemon class, which allows you to daemonize your script and
        react to events in simple callbacks.

        Args:
            pid_filename (str): name of daemon's PID file, which is stored in
                                ``/tmp``. Class automatically adds ``.pid``
                                suffix.
        """
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path = '/tmp/' + pid_filename + '.pid'
        self.pidfile_timeout = 5
        self.daemon_runner = runner.DaemonRunner(self)

        # react to parameters and check if daemon is not already runnig
        if self.isRunning() and "stop" not in sys.argv and \
           "restart" not in sys.argv:
            self.onIsRunning()

    def run_daemon(self):
        """
        Used as daemon starter.

        Warning:
            DO NOT OVERRIDE THIS.
        """
        try:
            self.daemon_runner.do_action()
        except daemon.runner.DaemonRunnerStopFailureError:
            self.onStopFail()
        except SystemExit:
            self.onExit()

    def run(self):
        """
        Used to handle some exceptions.

        Note:
            No, this can't be named differently, because it is defined in
            original DaemonRunner object.

        Warning:
            DO NOT OVERRIDE THIS.
        """
        try:
            self.body()
        except:
            raise
        finally:           # this is called only if daemon was not started
            self.onExit()  # and whole app ran on foreground

    def body(self):
        """
        Here should be your code loop.

        Note:
            Loop is automatically break-ed when daemon receives one of the unix
            signals. After that, :func:`onExit` is called.
        """
        pass

    def onStopFail(self):
        """
        Called when it is not possible to stop the daemon.

        This kind of event typically occurs if there is no running instance of
        daemon and script is called with ``stop`` parameter.
        """
        print "There is no running instance to be stopped."
        sys.exit(0)

    def onIsRunning(self):
        """
        Oposite of :func:`onStopFail` - this callback is called if there is
        already a running instance of daemon.
        """
        print 'It looks like a daemon is already running!'
        sys.exit(1)

    def onExit(self):
        """
        Called when the daemon received ?SIGTERM? and is shutting down.

        Warning:
            You should probably put something here, by default is there only
            shutdown message "DaemonRunnerWrapper is shutting down."
        """
        print "DaemonRunnerWrapper is shutting down."

    def isRunning(self):
        """
        Check PID and return true, if it looks like there is already a running
        instance of daemon.

        PID timeout can be set thru :attr:`pidfile_timeout` property.
        """
        return runner.make_pidlockfile(self.pidfile_path, 1).is_locked()
