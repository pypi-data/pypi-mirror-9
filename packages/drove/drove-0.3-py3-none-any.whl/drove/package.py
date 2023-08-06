#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""This module contains definitions and classes to handle
plugin packages. A package is formerly a tarball file
which contains a plugin in the normalize plugin packaging
format.

A plugin package must contain a folder ``plugin``, with the
plugin code inside (which can be a module(s) or other
package(s).
"""

import os
import sys
import glob
import stat
import json
import shutil
import tarfile
import pkgutil
import contextlib

from six.moves import urllib

from .util import temp
from .util import tester
from .util import signature


class PackageError(Exception):
    """Models an error related with a malformed package"""

def find_package(path, pattern="*.*"):
    for dir in path:
        for version in glob.glob(os.path.join(os.path.expanduser(dir),
            "%s.version" % (pattern,))):
            a, p = os.path.basename(version).split(".version")[0].split(".")
            with open(version, 'r') as f:
                v = str(f.read())[0:6]
            yield Package(a, p, v, None, os.path.expanduser(dir))


class _FileSum(object):
    def __init__(self, fd):
        self.fd = fd
        self._signature = signature.Signature()

    def read(self, num):
        out = self.fd.read(num)
        self._signature.update(out)
        return out

    def tell(self, *args, **kwargs):
        return self.fd.tell(*args, **kwargs)

    def seek(self, *args, **kwargs):
        return self.fd.seek(*args, **kwargs)

    @property
    def signature(self):
        return self._signature.hexdigest()

class Package(object):

    @staticmethod
    def _copytree(src, dst):
      if not os.path.exists(dst):
        os.makedirs(dst)
        shutil.copystat(src, dst)
      lst = os.listdir(src)
      for item in lst:
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
          Package._copytree(s, d)
        else:
          shutil.copy2(s, d)

    @staticmethod
    def _get_candidates(dir):
        """Given a directory, find plugin candidates, which are
        folders that match the expression *author*-*plugin*-*version*.
        """
        candidates = glob.glob(os.path.join(dir, "*"))

        for candidate in candidates:
            if os.path.isdir(candidate):
                pdir = os.path.join(candidate, "plugin")
                if not os.path.isdir(pdir):
                    # plugin dir does not exists
                    continue
                for finder, author, ispkg in pkgutil.iter_modules([pdir]):
                    if ispkg:
                        for finder, module, ispkg in pkgutil.iter_modules(
                            [os.path.join(pdir, author)]):
                            yield (module, author, pdir)

    @classmethod
    def from_url(kls, url, plugin_dir, upgrade=False):
        with urllib.request.urlopen(url) as response:
            return kls.from_tarballfd(response, plugin_dir, upgrade)

    @classmethod
    def from_tarballfd(kls, fd, plugin_dir, upgrade=False):
        fd = _FileSum(fd)
        with temp.directory() as tmp_dir:
            with tarfile.open(mode="r:gz", fileobj=fd) as tarball:
                tarball.extractall(path=tmp_dir)

            version = fd.signature

            candidates = [x for x in Package._get_candidates(tmp_dir)]

            if len(candidates) < 1:
                raise PackageError("Package dot not contains packages " +
                                   "inside.")
            if len(candidates) > 1:
                raise PackageError("Package contains more than " +
                                   "one package inside.")

            plugin, author, pdir = candidates[0]
            package = Package(
                    author,
                    plugin,
                    version,
                    pdir,
                    plugin_dir)

            if package.is_installed():
                if not upgrade:
                    raise PackageError("Package '%s.%s' already installed"
                                       % (author, plugin,))
                elif not package.needs_upgrade():
                    # nothing to do, package does not needs upgrade
                    return package

            package.run_tests()
            package.install(version)
            return package

    @classmethod
    def from_repo(kls, name, plugin_dir, index_url, upgrade=False):
        """Create new package from repository

        :type name: str
        :param name: the name of teh plugin in the repository

        :type plugin_dir: str
        :param plugin_dir: path to install the tarball

        :type upgrade: bool
        :param upgrade: if true, upgrade the package, otherwise failed
            if package is already installed.

        :type index_url: str
        :param index_url: The index url prefix to connect to repo
        """
        request = ("%s/api/1/plugins/%s" %(index_url, name,))

        try:
            with contextlib.closing(urllib.request.urlopen(request)) as resp:
                obj = json.loads(resp.read().decode("utf-8"))
                return Package.from_url(obj["url"], plugin_dir, upgrade)
        except BaseException as e:
            raise PackageError("Unable to download: %s" % (str(e),))

    @classmethod
    def from_tarball(kls, tarball, plugin_dir, upgrade=False):
        """Create a new package from tarball file

        :type tarball: str
        :param tarball: the filename of the tarball with the plugin

        :type plugin_dir: str
        :param plugin_dir: path to install the tarball

        :type upgrade: bool
        :param upgrade: if true, upgrade the package, otherwise failed
            if package is already installed.
        """
        with open(tarball, 'rb') as f:
            return kls.from_tarballfd(f, plugin_dir, upgrade)

    def __init__(self, author, plugin, version,
            new_version_path="",
            current_version_path=""):
        self.author = author
        self.plugin = plugin
        self.version = version
        self.new_version_path = new_version_path
        self.current_version_path = current_version_path
        self.name = "%s.%s" % (author, plugin)
        self.version_file = os.path.join(
            self.current_version_path,
            "%s.%s.version" % (self.author, self.plugin,)
        )

    def is_installed(self):
        """Return true if the package is installed in any directory of the
        dirs list passed as argument.
        """
        return os.path.exists(self.version_file)

    def needs_upgrade(self):
        """Return true if the package needs upgrade or not, this function
        does not check if package is already exists. If package does not
        exists, always return true.
        """
        with open(self.version_file, 'r') as f:
            version = f.read().strip("\r\n")

            if version == self.version:
                return False
            else:
                return True

    def remove(self):
        if not self.is_installed():
            raise PackageError("Unable to remove a non-installed package")

        for finder, module, ispkg in pkgutil.iter_modules(
            [os.path.join(self.current_version_path, self.author)]
        ):
            if module == self.plugin:
                if ispkg:
                    shutil.rmtree(
                        os.path.join(finder.path, module),
                        ignore_errors=True
                    )
                else:
                    fsrc = os.path.join(finder.path, "%s.py" % (module,))

                    if os.path.isfile(fsrc):
                        os.unlink(fsrc)

                    if os.path.isfile(fsrc + "c"):
                        os.unlink(fsrc + "c")

                os.unlink(self.version_file)

    def install_requirements(self):
        """Resolve and install requirements. This function will read
        the file ``requirements.txt`` from path passed as argument, and
        then use pip to install them.
        """
        requirements = os.path.abspath(
                os.path.join(self.new_version_path, "..", "requirements.txt")
        )
        if os.path.exists(requirements):
            try:
                from pip import main as pip_main
            except ImportError:
                raise PackageError("This module needs python dependencies. " +
                                   "You need pip to install dependencies, " +
                                   "please install pip libraries before.")

            pip_main(["-q", "install", "-r", requirements])

    def install(self, version, install_global=False):
        """Install a package into definitive location"""
        self.install_requirements()
        Package._copytree(self.new_version_path, self.current_version_path)
        vfile = os.path.join(self.current_version_path,
            "%s.%s.version" % (self.author, self.plugin,))

        with open(vfile, 'w') as f:
            f.write(version)

    def run_tests(self):
        """Run tests with uniitest if exist.
        """
        test_path = os.path.abspath(os.path.join(self.new_version_path,
            ".."))

        sys.path.insert(0, self.new_version_path)
        for result in tester.run_tests(test_path):
            for error in result.errors:
                raise PackageError("Test error: %s" % (error[1],))

            if not result.wasSuccessful():
                for fail in result.failures:
                    raise PackageError("Test failure: %s" % (fail[1],))

    def __str__(self):
        return "[%s.%s]:%s" % (self.author, self.plugin, self.version[0:6],)

    def __repr__(self):
        return str(self)
