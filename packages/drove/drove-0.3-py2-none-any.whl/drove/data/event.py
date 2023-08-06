#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""This module contains classes and definitions related with *events*.
An event is a notification emitted by some plugin to warn about any
condition.
"""

import time
from ..util.network import getfqdn

from . import Data


class Severity(object):
    """Model the severity of an event.

    >>> Severity.OKAY == 0
    >>> Severity.WARNING == 1
    >>> Severity.CRITICAL == 2
    >>> Severity.MISSING == 3
    """
    OKAY = 0
    WARNING = 1
    CRITICAL = 2
    MISSING = 3


class Event(Data):
    """Models an event for drove

    :type nodename: str
    :param nodename: the node which generate the value
    :type plugin: str
    :param plugin: the plugin namespace which generate the value
    :type value: float or int
    :param value: the value number to dispatch
    :type value_type: one of VALUE_COUNTER, VALUE_GAUGE or VALUE_TIME
    :param value_type: the type of the value
    :type timestamp: int
    :param timestamp: the timestamp when the data is created
    """
    def __init__(self,
                 plugin,
                 severity,
                 message,
                 nodename=None,
                 timestamp=None):
        self.nodename = nodename or getfqdn()
        self.plugin = plugin
        self.message = message
        self.severity = severity
        if timestamp is not None:
            self.timestamp = int(timestamp)
        else:
            self.timestamp = int(time.time())

    def dump(self):
        """Return a dump representation of the event"""
        return "E|{timestamp}|{nodename}|{plugin}|{severity}|{message}".format(
            timestamp=self.timestamp,
            nodename=self.nodename,
            plugin=self.plugin,
            severity=self.severity,
            message=self.message
        )

    def __repr__(self):
        return self.dump()
