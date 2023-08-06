#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""The data module contains definitions of data used in drove
client-server communication
"""

from ..util import importer


class Data(object):
    @classmethod
    def from_dump(cls, dump_str):
        """Create a Data from a dump representation.

        The dump representation of drove object contains six fields,
        separated by pipe. This representation is used to send values and
        events over the net, and, in general, to serialize metrics and
        events of any kind.

        Formerly, the dump representation contains the following fields:

        Kind
            Must be ``V`` for values or ``E`` for events.
        Nodename
            Is the node name which generate the data.
        Plugin Namespace
            The namespace where the data must be anchor to.

        For value data, we have:

        Value
            The numeric value of the metric.
        Value Type
            The type of the metric. Can be ``g`` for gauge, ``c``
            for counter or ``t`` for time.

        For event data, we have:

        Severity
            Is an integer which indicate the severity. Lower value
            implies lower severity.
        Message
            Is a descriptive message of the event (human readable),
            encoded in UTF-8.

        For both, also have:

        Timestamp
            An integer number which represents the UNIX timestamp
            when the data was generated.

        """
        if dump_str.startswith("V|"):
            fields = dump_str.split("|", 6)
            if len(fields) < 6:
                raise ValueError("The Value has missing fields")

            timestamp, nodename, plugin, value, vtype = fields[1:]
            kls = importer.load(".value", "Value", anchor=__package__)
            return kls(plugin, value, nodename, vtype, timestamp)

        elif dump_str.startswith("E|"):
            fields = dump_str.split("|", 6)
            if len(fields) < 6:
                raise ValueError("The Event has missing fields")

            timestamp, nodename, plugin, severity, message = fields[1:]
            kls = importer.load(".event", "Event", anchor=__package__)
            return kls(plugin, int(severity), message, nodename, timestamp)

        else:
            raise ValueError("Unable to get data from dump")

    def is_value(self):
        """Return true if the data is a Value"""
        return self.__class__.__name__ == 'Value'

    def is_event(self):
        """Return true if the data is an Event"""
        return self.__class__.__name__ == 'Event'
