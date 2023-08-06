#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""The data module contains definitions of data used in drove
client-server communication
"""

import os
from .. import importer


class Daemon(object):
    """Generic class to model different daemonize implementations.
    To instance one, please use :meth:`create` metod.
    """
    @classmethod
    def create(cls, handler, exit_handler=None):
        """Crete a new :class:`Daemon` object, which is dynamically
        selected according to running operating system.

        :type handler: callable
        :param handler: The handler to call to daemonize the process.

        :type exit_handler: callable
        :param exit_handler: The handler to call when exit if any.
        """
        if os.name == "posix":
            mod_name = ".%s" % (os.name,)
            kls_name = "%sDaemon" % (os.name.title())

            kls = importer.load(mod_name, kls_name, anchor=__package__)
            return kls(handler, exit_handler)
        else:
            raise NotImplementedError("The platform '%s' " % (os.name,) +
                                      "is not supported yet. Please drop us " +
                                      "a line if you are interesting in " +
                                      "porting drove to this platform.")
