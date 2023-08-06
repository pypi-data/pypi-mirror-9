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
VirtualBox server module.
"""

import os
import sys
import shutil
import asyncio
import subprocess
import logging

log = logging.getLogger(__name__)

from ..base_manager import BaseManager
from .virtualbox_vm import VirtualBoxVM
from .virtualbox_error import VirtualBoxError


class VirtualBox(BaseManager):

    _VM_CLASS = VirtualBoxVM

    def __init__(self):

        super().__init__()
        self._vboxmanage_path = None

    @property
    def vboxmanage_path(self):
        """
        Returns the path to VBoxManage.

        :returns: path
        """

        return self._vboxmanage_path

    def find_vboxmanage(self):

        # look for VBoxManage
        vboxmanage_path = self.config.get_section_config("VirtualBox").get("vboxmanage_path")
        if not vboxmanage_path:
            if sys.platform.startswith("win"):
                if "VBOX_INSTALL_PATH" in os.environ:
                    vboxmanage_path = os.path.join(os.environ["VBOX_INSTALL_PATH"], "VBoxManage.exe")
                elif "VBOX_MSI_INSTALL_PATH" in os.environ:
                    vboxmanage_path = os.path.join(os.environ["VBOX_MSI_INSTALL_PATH"], "VBoxManage.exe")
            elif sys.platform.startswith("darwin"):
                vboxmanage_path = "/Applications/VirtualBox.app/Contents/MacOS/VBoxManage"
            else:
                vboxmanage_path = shutil.which("vboxmanage")

        if not vboxmanage_path:
            raise VirtualBoxError("Could not find VBoxManage")
        if not os.path.isfile(vboxmanage_path):
            raise VirtualBoxError("VBoxManage {} is not accessible".format(vboxmanage_path))
        if not os.access(vboxmanage_path, os.X_OK):
            raise VirtualBoxError("VBoxManage is not executable")
        if os.path.basename(vboxmanage_path) not in ["VBoxManage", "VBoxManage.exe", "vboxmanage"]:
            raise VirtualBoxError("Invalid VBoxManage executable name {}".format(os.path.basename(vboxmanage_path)))

        self._vboxmanage_path = vboxmanage_path
        return vboxmanage_path

    @asyncio.coroutine
    def execute(self, subcommand, args, timeout=60):

        vboxmanage_path = self.vboxmanage_path
        if not vboxmanage_path:
            vboxmanage_path = self.find_vboxmanage()
        command = [vboxmanage_path, "--nologo", subcommand]
        command.extend(args)
        log.debug("Executing VBoxManage with command: {}".format(command))
        try:
            vbox_user = self.config.get_section_config("VirtualBox").get("vbox_user")
            if vbox_user:
                # TODO: test & review this part
                sudo_command = "sudo -i -u {}".format(vbox_user) + " ".join(command)
                process = yield from asyncio.create_subprocess_shell(sudo_command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            else:
                process = yield from asyncio.create_subprocess_exec(*command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        except (OSError, subprocess.SubprocessError) as e:
            raise VirtualBoxError("Could not execute VBoxManage: {}".format(e))

        try:
            stdout_data, stderr_data = yield from asyncio.wait_for(process.communicate(), timeout=timeout)
        except asyncio.TimeoutError:
            raise VirtualBoxError("VBoxManage has timed out after {} seconds!".format(timeout))

        if process.returncode:
            # only the first line of the output is useful
            vboxmanage_error = stderr_data.decode("utf-8", errors="ignore")
            raise VirtualBoxError("VirtualBox has returned an error: {}".format(vboxmanage_error))

        return stdout_data.decode("utf-8", errors="ignore").splitlines()

    @asyncio.coroutine
    def get_list(self):
        """
        Gets VirtualBox VM list.
        """

        vms = []
        result = yield from self.execute("list", ["vms"])
        for line in result:
            vmname, _ = line.rsplit(' ', 1)
            vmname = vmname.strip('"')
            if vmname == "<inaccessible>":
                continue  # ignore inaccessible VMs
            extra_data = yield from self.execute("getextradata", [vmname, "GNS3/Clone"])
            if not extra_data[0].strip() == "Value: yes":
                # get the amount of RAM
                info_results = yield from self.execute("showvminfo", [vmname, "--machinereadable"])
                for info in info_results:
                    try:
                        name, value = info.split('=', 1)
                        if name.strip() == "memory":
                            ram = int(value.strip())
                            break
                    except ValueError:
                        continue
                vms.append({"vmname": vmname, "ram": ram})
        return vms

    @staticmethod
    def get_legacy_vm_workdir(legacy_vm_id, name):
        """
        Returns the name of the legacy working directory name for a VM.

        :param legacy_vm_id: legacy VM identifier (not used)
        :param name: VM name

        :returns: working directory name
        """

        return os.path.join("vbox", "{}".format(name))
