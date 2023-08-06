#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""This module contain the implementation of temporary cache,
used by drove to keep data from readers and dispatch them to writers
in a synchronized way.
"""

from six.moves.queue import Queue


class Channel(object):
    def __init__(self):
        """Models an internal and in-memory pubsub mechanism.
        All plugins will subscrib to the channel, and they can receive
        (get pending messages) and pubñish new ones.

        >>> x = Channel()
        >>> x.subscribe("topic1")
        >>> x.publish("value")
        >>> x.receive("topic1")
        """
        self.queues = {}

    def subscribe(self, topic):
        """Create a new topic

        :type topic: any indexable
        :param topic: the topic id
        """
        if topic not in self.queues:
            self.queues[topic] = Queue()
        return self

    def publish(self, value, topic=None):
        """Send a value to topics

        :type value: any
        :param value: the value to send
        :type topic: list
        :param topic: a list with topics ids to send the message
            or if not present send to all topics.
        """
        if topic:
            self.queues[topic].put(value)
        else:
            for queue in self.queues.values():
                queue.put(value)

    def receive(self, topic):
        """Get messages enqueued for one topic

        :type topic: any indexable
        :param topic: the topic to get messages for
        """
        while self.queues[topic].qsize() > 0:
            yield self.queues[topic].get_nowait()
