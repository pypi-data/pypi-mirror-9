#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""This module contains classes to parse configuration files and
create python dictionary based class to handle it.
"""

import os
import wcfg
import glob


class ConfigError(Exception):
    """Models an exception reading config."""


CONFIG_UNSET = (None,)


class Config(dict):
    def __init__(self, config_file=None):
        """Parse a config file and create an object to get the paramters,
        with the ability to reload the config online.

        :param config_file: the main configuration file to load.
            If not set you need to populate the config using the
            :meth:`reload`
        """
        self.config_file = config_file

        if config_file is not None:
            self.reload()

    def reloadfd(self, fd, path):
        """Reload the config.

        :type fd: file object
        :param fd: A file descriptor to read config from. This function is
            not designed to be call directly, but use :meth:`reload`
            instead.
        :type path: str
        :param path: A path to search relative include files if any.
        """
        contents = wcfg.load(fd)
        self.update(contents)

        if "include" in self:
            if self["include"][0] != '/':
                include = os.path.join(
                    path, self["include"]
                )
            else:
                include = self["include"]
            for f in glob.glob(include):
                self.reload(f)

    def reload(self, config_file=None):
        """Reload the config.

        :param config_file: if set populate config from this config
            file. If not use the config defined in constructor.
        """
        config_file = config_file or self.config_file
        with open(config_file, 'rb') as f:
            self.reloadfd(f, os.path.dirname(config_file))

    def get(self, key, default=CONFIG_UNSET):
        """Return a value for a key in the config. If
        this key is not found and no default value is
        provided, raises a :class:`ConfigError` exception.
        If default value is provided and key not found,
        the default value is returned.

        :type key: str
        :param key: the key to search in config
        :type default: *any object*
        :param default: the default value to return
            in case that key not found in config.
        """
        if key in self:
            return dict.get(self, key)
        elif "." in key:
            try:
                parent, _, key = key.rsplit(".", 2)
                return self.get(parent + "." + key, default)
            except ValueError:
                parent, key = key.split(".", 1)
                return self.get(key, default)
        elif default != CONFIG_UNSET:
            return default
        else:
            raise ConfigError("Required config parameter " +
                              "'%s' not found" % (key,))

    def get_childs(self, prefix, expand_childs=False):
        """Get the keys which hirarchically depends of prefix
        passed by argument.

        For example:

        >>> x = Config()
        >>> x["namespace.key"] = 1
        >>> x.get_childs("namespace") == ['namespace']

        :type prefix: str
        :param prefix: a string to search keys under that prefix.
        :type expand_childs: bool
        :param expand_childs: if true each grandchilds should be threated
            as childs.
        """
        prefix = prefix if prefix[-1] == "." else (prefix + ".")
        childs = set()
        for key in self:
            if key.startswith(prefix):
                suffix = key.replace(prefix, "")
                if "." in suffix and not expand_childs:
                    childs.add(suffix.split(".")[0])
                else:
                    childs.add(suffix)
        return childs

    def __getitem__(self, key):
        return self.get(key)
