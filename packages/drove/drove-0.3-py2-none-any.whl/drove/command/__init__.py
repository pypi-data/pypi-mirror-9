#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""The generic command module provides a generic way to load
specific drove client commands.
"""

from ..util import importer


class CommandError(Exception):
    """Models an error running a client command"""


class Command(object):
    def __init__(self, config, args, log):
        """Generic Command

        :type config: :class:`Config`
        :param config: the configuration object for drove

        :type args: :class:`argparse.Namespace`
        :param args: the namespace contains arguments parsed by
            :mod:`argparse`.

        :type log: :class:`logging.Logger`
        :param log: a logger provided by the application to display
            messages.

        .. note:: You probably want to use the class method
            :meth:`from_name` to instanciate specific commands instead of
            initialization of generic ones.
        """
        self.config = config
        self.args = args
        self.log = log

    @classmethod
    def from_name(cls, name, config, args, log):
        """Instanciate specific command

        :type name: str
        :param name: the name of the command which may match with specific
            command submodule.

        :type config: :class:`Config`
        :param config: the configuration object for drove

        :type args: :class:`argparse.Namespace`
        :param args: the namespace contains arguments parsed by
            :mod:`argparse`.

        :type log: :class:`logging.Logger`
        :param log: a logger provided by the application to display
            messages.
        """
        mod_name = ".%s" % (name,)
        kls_name = "%sCommand" % (name.title(),)

        kls = importer.load(mod_name, kls_name, anchor=__package__)
        return kls(config, args, log)
