# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 GNS3 Technologies Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Qemu server module.
"""

import asyncio
import os
import sys
import re
import subprocess

from ...utils.asyncio import subprocess_check_output
from ..base_manager import BaseManager
from .qemu_error import QemuError
from .qemu_vm import QemuVM


class Qemu(BaseManager):
    _VM_CLASS = QemuVM

    @staticmethod
    def binary_list():
        """
        Gets QEMU binaries list available on the matchine

        :returns: Array of dictionnary {"path": Qemu binaries path, "version": Version of Qemu}
        """

        qemus = []
        paths = [os.getcwd()] + os.environ["PATH"].split(os.pathsep)
        # look for Qemu binaries in the current working directory and $PATH
        if sys.platform.startswith("win"):
            # add specific Windows paths
            if hasattr(sys, "frozen"):
                # add any qemu dir in the same location as gns3server.exe to the list of paths
                exec_dir = os.path.dirname(os.path.abspath(sys.executable))
                for f in os.listdir(exec_dir):
                    if f.lower().startswith("qemu"):
                        paths.append(os.path.join(exec_dir, f))

            if "PROGRAMFILES(X86)" in os.environ and os.path.exists(os.environ["PROGRAMFILES(X86)"]):
                paths.append(os.path.join(os.environ["PROGRAMFILES(X86)"], "qemu"))
            if "PROGRAMFILES" in os.environ and os.path.exists(os.environ["PROGRAMFILES"]):
                paths.append(os.path.join(os.environ["PROGRAMFILES"], "qemu"))
        elif sys.platform.startswith("darwin"):
            # add specific locations on Mac OS X regardless of what's in $PATH
            paths.extend(["/usr/local/bin", "/opt/local/bin"])
            if hasattr(sys, "frozen"):
                paths.append(os.path.abspath(os.path.join(os.getcwd(), "../../../qemu/bin/")))
        for path in paths:
            try:
                for f in os.listdir(path):
                    if (f.startswith("qemu-system") or f == "qemu" or f == "qemu.exe") and \
                            os.access(os.path.join(path, f), os.X_OK) and \
                            os.path.isfile(os.path.join(path, f)):
                        qemu_path = os.path.join(path, f)
                        version = yield from Qemu._get_qemu_version(qemu_path)
                        qemus.append({"path": qemu_path, "version": version})
            except OSError:
                continue

        return qemus

    @staticmethod
    @asyncio.coroutine
    def _get_qemu_version(qemu_path):
        """
        Gets the Qemu version.
        :param qemu_path: path to Qemu
        """

        if sys.platform.startswith("win"):
            return ""
        try:
            output = yield from subprocess_check_output(qemu_path, "-version")
            match = re.search("version\s+([0-9a-z\-\.]+)", output)
            if match:
                version = match.group(1)
                return version
            else:
                raise QemuError("Could not determine the Qemu version for {}".format(qemu_path))
        except subprocess.SubprocessError as e:
            raise QemuError("Error while looking for the Qemu version: {}".format(e))

    @staticmethod
    def get_legacy_vm_workdir(legacy_vm_id, name):
        """
        Returns the name of the legacy working directory name for a VM.

        :param legacy_vm_id: legacy VM identifier (integer)
        :param: VM name (not used)

        :returns: working directory name
        """

        return os.path.join("qemu", "vm-{}".format(legacy_vm_id))
