#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""This module contains classes and methods to import dynamically modules
from specified paths."""

import sys
import importlib

from . import temp


def load(module,
         attr_name=None,
         anchor=__package__,
         path=[]):
    """Load a module or an attribute from the specific module.

    >>> load("sys")
    >>> load("sys.environ")
    >>> load(".importer")

    :type module: str
    :param module: The module name to load

    :type attr_name: str
    :param attr_name: The name of the attribute of the module to load (if
        any). If not present, returns the module itself.

    :type anchor: str
    :param anchor: The anchor module to resolve relative module paths. By
        default uses ``__package__``.

    :type path: list
    :param path: a list with paths to search the module
    """
    path = path or sys.path

    with temp.variables({'sys.path': path}):
        mod = importlib.import_module(module, anchor)
        if attr_name:
            return getattr(mod, "%s" % (attr_name,))
        else:
            return mod
