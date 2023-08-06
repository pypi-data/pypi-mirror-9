#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""This module provide a generic plugin implementation.
"""

import os
import sys
from .util.timer import Timer
from .util.log import getLogger
from .util import importer


class PluginError(Exception):
    """Models an error related with plugins."""


class Plugin(object):
    """Models a generic plugin to be extended from subclasses. This class
    provide only a classmethod to dynamically load different plugins.

    .. note:: You need to implement the ``read`` or the ``write`` method
        for your plugin. These methods are not defined in generic class
        because if they don't exists, drove will not run any thread to
        execute it.

        The ``read`` method does not accept parameters, and will return a
        dictionary with the values readed. Check the ``cpu`` plugin for
        more information.

        The ``write`` method receives a dict as parameter which you need
        to flush wherever you want.
    """
    def __init__(self, config, channel):
        """Create a new Plugin object.

        .. note:: Do not instance objects of class Plugin directly,
           use :meth:`load` instead.
        """
        self.__channel = channel
        self.__config = config
        self.log = getLogger()
        self.read_thread = None
        self.write_thread = None

    @classmethod
    def load(cls, plugin_name, config, channel):
        """Class method to load dynamically a plugin.

        :type plugin_name: str
        :param plugin_name: the plugin name to load, must be in the plugins
            directory with proper name (plugin_name plus python extension),
            and must have a proper named class (the plugin_name in camel case
            with *Plugin* suffix.
        :type config: :class:`Config`
        :param config: a connfig object with all configuration parameters.
        :type channel: :class:`Channel`
        :param channel: a channel to intercommunicate the plugin with others.
        """
        plugin_dir = [os.path.join(os.path.dirname(__file__), "plugins")]
        plugin_dir.extend([os.path.expanduser(x) for x in
                           config.get("plugin_dir", ["/usr/lib/drove"])])
        plugin_dir.extend(sys.path)

        dir_name = plugin_name.split(".")[-1]
        kls_name = "%sPlugin" % (dir_name.title(),)
        mod_name = "%s.%s" % (plugin_name, dir_name,)

        kls = importer.load(plugin_name, kls_name, path=plugin_dir, anchor=None)

        obj = kls(config, channel)
        obj.plugin_name = plugin_name
        obj.log.info("Using plugin: %s" % (plugin_name,))
        channel.subscribe(plugin_name)

        return obj

    def emit(self, data):
        """Emit some data from reader.

        :type data: :class:`Value`
        :param data: data to be emitted.
        """
        self.__channel.publish(data)

    def _read(self):
        try:
            self.read()
        except BaseException as e:
            self.log.error("Unexpected error reading from plugin '%s': %s'" %
                           (self.plugin_name, str(e)))

    def _write(self):
        try:
            self.write(self.__channel)
        except BaseException as e:
            self.log.error("Unexpected error writing plugin '%s': %s'" %
                           (self.plugin_name, str(e)))

    def setup(self, config):
        """Setup the plugin. This method could be override to
        do some initialization stuff here.

        :type config: :class:`Config`
        :param config: the configuration object with all relevant
            config values.
        """
        pass

    def start(self):
        """Start a plugin to read/write"""
        self.setup(self.__config)
        config_prefix = "plugin.%s" % (self.plugin_name,)

        if hasattr(self, "read"):
            # TODO check if callable
            config_key = "%s.read_interval" % (config_prefix,)
            self.read_thread = Timer(self.__config.get(config_key, 20),
                                     self._read)
            self.read_thread.run()

        if hasattr(self, "write"):
            self.__channel.subscribe(self.plugin_name)
            config_key = "%s.write_interval" % (config_prefix,)
            self.write_thread = Timer(self.__config.get(config_key, 60),
                                      self._write)
            self.write_thread.run()

    def stop(self):
        """Stop a plugin to read/write"""
        if self.read_thread:
            self.read_thread.stop()
        if self.write_thread:
            self.write_thread.stop()


class PluginManager(object):
    def __init__(self, config, channel):
        """The plugin manager class provide way to handler
        all current enabled plugin, run every one in threads
        and make a communication channel between them.

        :param config: a :class:`Config` object with all configuration values.
        :param channel: a :class:`Channel` object to communicate plugins.
        """
        self.config = config
        self.channel = channel
        self.plugins = []
        for plugin in self.config.get_childs("plugin", expand_childs=True):
            self.plugins.append(Plugin.load(plugin, self.config, self.channel))

    def start_all(self):
        """Start all plugins"""
        for plugin in self.plugins:
            plugin.start()

    def stop_all(self):
        """Stop all plugins"""
        for plugin in self.plugins:
            plugin.stop()

    def __len__(self):
        return len(self.plugins)

    def __iter__(self):
        return iter(self.plugins)

    def loop(self, num=0, seconds=10):
        """Keep the process in a loop waiting for plugin data.

        :type num: int
        :param num: the number of plugins to wait for. By default 0 (wait
            for all).

        :type seconds: int
        :param seconds: the time to sleep between two consecutives checks of
            current active plugins. By default 10.
        """
        Timer.wait(num, seconds)
