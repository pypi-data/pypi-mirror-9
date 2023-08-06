#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""This module contains classes and definitions related with *values*.
A value is a metric which will sent to drove
"""

import time
from ..util.network import getfqdn

from . import Data

VALUE_GAUGE = "g"
VALUE_COUNTER = "c"
VALUE_TIME = "t"


class Value(Data):
    """Models a value for drove

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
                 value,
                 nodename=None,
                 value_type=VALUE_GAUGE,
                 timestamp=None):
        self.nodename = nodename or getfqdn()
        self.plugin = plugin
        self.value = float(value)
        self.value_id = "%s.%s" % (self.nodename, self.plugin,)
        if value_type != VALUE_GAUGE and \
           value_type != VALUE_COUNTER and \
           value_type != VALUE_TIME:
            raise ValueError("Invalid value type")
        self.value_type = value_type
        if timestamp is not None:
            self.timestamp = int(timestamp)
        else:
            self.timestamp = int(time.time())

    def dump(self):
        """Return a dump representation of the value"""
        return "V|{timestamp}|{nodename}|{plugin}|{value}|{value_type}".format(
            timestamp=self.timestamp,
            nodename=self.nodename,
            plugin=self.plugin,
            value=self.value,
            value_type=self.value_type
        )

    def __repr__(self):
        return self.dump()
