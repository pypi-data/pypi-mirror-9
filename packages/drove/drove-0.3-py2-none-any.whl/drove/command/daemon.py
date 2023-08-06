#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

import sys

from . import Command
from .. import VERSION
from ..util import log
from ..channel import Channel
from ..reloader import Reloader
from ..plugin import PluginManager
from ..util.daemon import Daemon
from ..util.network import getfqdn

"""This module contains the command ``daemon`` which is invoked from the
command line to run drove as agent, running plugins in background.

For more information run drove:

.. code-block:: sh

    $ drove daemon -h

"""


class DaemonCommand(Command):
    """This class extends :class:`Command` to implement ``daemon`` command.
    """

    def _exit_handler(self):
        if self.log:
            self.log.error("Received TERM signal. Try to exit gently...")
        if self.plugins:
            self.plugins.stop_all()
        sys.exit(15)

    def _daemon(self):
        try:
            self.plugins.start_all()

            # starting reload thread
            self.log.debug("Starting reloader")
            reloader = Reloader([getfqdn, self.config] +
                                [x for x in self.plugins],
                                interval=self.config.get("reload", 60))
            reloader.start()

            # wait until all plugins stop
            self.log.info("Entering data gathering loop")
            self.plugins.loop()

        except KeyboardInterrupt:
            self.log.fatal("Received a Keyboard Interrupt. Exit silently.")
            sys.exit(15)
        except BaseException as e:
            if self.args.verbose:
                raise
            self.log.fatal("Unexpected error happened during drove " +
                           "execution: {message}".format(message=str(e)))
            sys.exit(1)

    def execute(self):
        """When invoked run drove as daemon (usually in background)
        """
        # ensure that config has nodename or create nodename for this node
        if self.config.get("nodename", None) is None:
            self.config["nodename"] = getfqdn

        # configure log, which is a singleton, no need to use parameters
        # in self.log in any other places.
        self.log = log.getLogger(
            syslog=self.config.get("syslog", True),
            console=self.config.get("logconsole", False),
            logfile=self.config.get("logfile", None),
            logfile_size=self.config.get("logfile_size", 0),
            logfile_keep=self.config.get("logfile_keep", 0))

        if self.args.verbose:
            self.log.setLevel(log.DEBUG)

        try:
            from setproctitle import setproctitle
            setproctitle("drove %s" % " ".join(sys.argv[1:]))
        except ImportError:
            pass

        self.log.info("Starting drove daemon (%s)" % (VERSION,))
        self.log.info("Using configuration file: %s" %
                      (self.config.config_file,))

        # create a common channel to communicate the plugins
        self.log.debug("Creating channel")
        channel = Channel()

        # starting plugins
        self.log.debug("Starting plugins")
        self.plugins = PluginManager(self.config, channel)

        if len(self.plugins) == 0:
            self.log.warning("No plugins installed... " +
                             "drove has no work to do.")
            if self.args.exit_if_no_plugins:
                sys.exit(0)

        # setup daemon, but not necessary run in background
        daemon = Daemon.create(
            self._daemon,
            self._exit_handler)
        if self.args.foreground:
            # starting daemon in foreground if flag is preset
            daemon.foreground()
        else:
            # or start it as daemon
            return daemon.start()
