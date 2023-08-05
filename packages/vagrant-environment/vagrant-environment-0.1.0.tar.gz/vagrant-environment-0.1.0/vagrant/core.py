# Copyright (c) 2015 Carlos Valiente
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""Utilities for working with Vagrant environments."""

import os
import logging
import subprocess


__all__ = [
    "destroy",
    "up",
]


class up(object):

    """Context manager that brings up a Vagrant environment on start.

    """

    log = logging.getLogger("vagrant")

    def __init__(self, dname=None):
        """Constructor.

        Parameters:

            dname
                Path to the directory containing the Vagrantfile. Defaults to
                the current working directory if not given.

        """
        self._dname = os.getcwd() if dname is None else dname
        self._vagrantfile = os.path.join(self._dname, "Vagrantfile")
        if not os.access(self._vagrantfile, os.F_OK):
            raise Exception("%s: Not found" % (self._vagrantfile,))
        self._hosts = None

    def __enter__(self):
        for (host, status) in self._status():
            if status != "running":
                self._vagrant("up", host)
        return self

    def __exit__(self, *exc_info):
        pass

    @property
    def hosts(self):
        """Tuple of Vagrant nodes in this Vagrant environment.

        """
        if self._hosts is None:
            self._hosts = []
            for line in self._vagrant("status --machine-readable"):
                bits = line.split(",")
                if bits[2] == "state":
                    self._hosts.append(bits[1])
            self._hosts = tuple(self._hosts)
        return self._hosts

    def provision(self):
        """Provisions all nodes in this Vagrant environment.

        """
        return self._vagrant("provision")

    def ssh(self, node, cmd):
        """Executes the given command in the given hosts.

        Raises an error if the return code of ``vagrant ssh`` is non-zero.

        Returns a list containing the output of ``vagrant ssh`` (both stdout
        and stderr).

        """
        return self._vagrant('ssh -c "%s"' % (cmd,), node)

    def _status(self):
        ret = []
        for line in self._vagrant("status --machine-readable"):
            bits = line.split(",")
            if bits[2] == "state":
                ret.append((bits[1], bits[3]))
        if self._hosts is None:
            self._hosts = tuple(h for (h, _) in ret)
        return ret

    def _vagrant(self, *args):
        cmdline = ["vagrant"]
        cmdline.extend(args)
        cmdline = " ".join(cmdline)
        self.log.debug("Executing: %s", cmdline)
        p = subprocess.Popen(cmdline,
                             shell=True,
                             cwd=self._dname,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        stdout, _ = p.communicate()
        if p.returncode:
            raise Exception(stdout)
        return stdout.strip().split("\n")


LOG = logging.getLogger("vagrant")


def destroy(dname=None):
    """Destroys the Vagrant environment.

    Arguments:

        dname
        Path to the directory containing the Vagrantfile. Defaults to the
        current working directory if not given.

    """
    dname = os.getcwd() if dname is None else dname
    vagrantfile = os.path.join(dname, "Vagrantfile")
    if not os.access(vagrantfile, os.F_OK):
        raise Exception("%s: Not found" % (vagrantfile,))

    cmdline = "vagrant destroy --force"
    LOG.debug("Executing: %s", cmdline)
    p = subprocess.Popen(cmdline,
                         shell=True,
                         cwd=dname,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    stdout, _ = p.communicate()
    if p.returncode:
        raise Exception(stdout)
    LOG.debug(stdout)
