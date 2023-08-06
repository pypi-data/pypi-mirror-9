#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""This module contains command line endpoints to run the program from shell
"""

import os
import sys
import argparse

from .util import log
from .config import Config
from .command import Command
from . import NAME, VERSION, DESCRIPTION


DEFAULT_LOCAL_CONFIG = os.path.join(os.path.dirname(__file__),
                                    "config", "drove.conf")

DEFAULT_CONFIG_FILES = ["~/.config/drove/drove.conf",
                        "~/.drove/drove.conf",
                        "/etc/drove/drove.conf",
                        DEFAULT_LOCAL_CONFIG]


def main():
    """Base command line executable.
    """

    cmdopt = argparse.ArgumentParser(
        description="%s %s: %s" % (NAME, VERSION,
                                   DESCRIPTION,))

    cmdopt.add_argument("-C", "--config-file", action="store",
                        dest="config_file",
                        help="Main configuration file to read.",
                        type=str,
                        default=None)

    cmdopt.add_argument("-v", "--verbose", action="store_true",
                        dest="verbose",
                        help="be verbose",
                        default=False)

    cmdopt.add_argument("-s", "--set", action="append",
                        dest="set",
                        help="set config variables by hand (key=value). " +
                             "This option will override values from " +
                             "config file.",
                        default=[])

    cmdopt.add_argument("-P", "--plugin-dir", action="append",
                        dest="plugin_dir",
                        help="set the plugin dir to search plugins",
                        default=[])

    cmdopt.add_argument('-V', '--version', action='version',
                        version="%(prog)s " + VERSION)

    subparsers = cmdopt.add_subparsers(
        title="action",
        description="action to be executed by drop",
        dest='cmd')
    subparsers.required = True

    search = subparsers.add_parser("search",
                                   help="Search a plugin in repository")
    search.add_argument("-i", "--index-url",
                        action="store",
                        help="set the base url to search plugins",
                        dest="index_url",
                        default=None)

    search.add_argument("plugin", help="plugin string to search for")

    install = subparsers.add_parser("install",
                                    help="Install a plugin from repository")
    install.add_argument("-g", "--global", action="store_true",
                         dest="install_global",
                         help="Install globally")


    install.add_argument("-U", "--upgrade", action="store_true",
                         dest="upgrade",
                         help="Upgrade previous intalled plugin")

    install.add_argument("-i", "--index-url",
                        action="store",
                        help="set the base url to search plugins",
                        dest="index_url",
                        default=None)

    install.add_argument("plugin", help="plugin string to install")

    remove = subparsers.add_parser("remove",
                                   help="Remove an installed plugin")
    remove.add_argument("plugin", help="plugin string to remove")

    subparsers.add_parser("list",
                          help="List installed plugins")

    daemon = subparsers.add_parser("daemon",
                                   help="Start drove daemon")

    daemon.add_argument('-np', '--exit-if-no-plugins', action='store_true',
                        dest="exit_if_no_plugins",
                        help="if true drove exists if no plugins found",
                        default=False)

    daemon.add_argument('-f', '--foreground', action='store_true',
                        dest="foreground",
                        help="No daemonize and run in foreground.",
                        default=False)

    args = cmdopt.parse_args()

    logger = log.getDefaultLogger()

    # read configuration and start reload timer.
    if args.config_file:
        config = Config(args.config_file)
    else:
        config = Config()
        for cf in DEFAULT_CONFIG_FILES:
            cf = os.path.expanduser(cf)
            if os.path.isfile(cf):
                config = Config(cf)

    if args.set:
        for config_val in args.set:
            if "=" not in config_val:
                logger.error("--set option require a 'key=value' value.")
                sys.exit(2)
            key, val = config_val.split("=", 1)
            config[key] = val

    if args.plugin_dir:
        config["plugin_dir"] = args.plugin_dir

    try:
        Command.from_name(
            name=args.cmd,
            config=config,
            args=args,
            log=logger
        ).execute()
    except SystemExit as e:
        sys.exit(e)
    except (Exception, BaseException) as e:
        if args.verbose:
            raise
        logger.error("Unexpected error: %s" % (str(e),))
        sys.exit(128)
