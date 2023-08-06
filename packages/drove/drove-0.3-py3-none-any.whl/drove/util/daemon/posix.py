#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""Generic linux daemon base class for python 3.x.

.. note::
    Most of this module is heavly based on the `work of Lone Wolves`_

.. _`work of Lone Wolves`: http://www.jejik.com/files/examples/daemon3x.py

"""

import sys
import os
import signal

from . import Daemon


class PosixDaemon(Daemon):
    def __init__(self, handler, exit_handler=None):
        """Implement a daemon for posix systems using generic posix
        daemon class.

        :type handler: callable
        :param handler: The handler to call to daemonize the process.

        :type exit_handler: callable
        :param exit_handler: The handler to call when exit the process if
            any.
        """
        self.handler = handler
        self.pid = 0

        if exit_handler:
            self.set_exit_handler(exit_handler)

        Daemon.__init__(self)

    def set_exit_handler(self, func):
        """Dynamically sets the exit_handler to specified function passed as
        argument.
        """
        signal.signal(signal.SIGTERM, func)

    def foreground(self):
        """Run the handler in foreground"""
        self.handler()

    def start(self):
        """Start the daemon

        :rtype: int
        :return: The PID of the child process which is running the handler.
        """
        self.pid = os.fork()
        if self.pid:
            # parent
            return self.pid
        else:
            # child
            sys.stdin = open(os.devnull, 'r')
            sys.stdout = open(os.devnull, 'a+')
            sys.stderr = open(os.devnull, 'a+')

            self.handler()

    def stop(self):
        """Stop the daemon"""
        if self.pid:
            os.kill(self.pid, 2)
            self.pid = 0

    def restart(self):
        """Restart the daemon

        :rtype: int
        :return: The PID of the child process which is running the handler.
        """
        self.stop()
        return self.start()
