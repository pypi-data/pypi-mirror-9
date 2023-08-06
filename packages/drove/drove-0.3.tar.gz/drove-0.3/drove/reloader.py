#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""This module contains classes and functions to help
to reload plugins and configuration files on the fly.
"""

from .util.timer import Timer
from .util.log import getLogger


class Reloader(object):
    def __init__(self, elements, interval=20, log=None):
        """Create a new reloader manager.

        :type elements: list
        :param elements: a list with the object to reload. The objects must
            contain the ``reload`` method implemented.

        :type interval: int
        :param interval: the interval in seconds to reload elements.
            By default set to 20 seconds.

        :type log: :class:`Logger`
        :param log: if present used the provider logger to log,
            otherwise use default one provided by :meth:`getLogger`
        """
        self.elements = elements
        self.interval = interval
        self.log = log or getLogger()

    def reload(self):
        """Force a reload of the defined elements during reloader
        initialization.
        """
        for element in self.elements:
            fun = getattr(element, "reload", None)
            if fun and hasattr(fun, "__call__"):  # poor man iscallable
                self.log.debug("Reloading object: %s" %
                               (element.__class__.__name__,))
                fun()

    def start(self):
        """Start the reloader thread"""
        Timer(self.interval, self.reload).run()
