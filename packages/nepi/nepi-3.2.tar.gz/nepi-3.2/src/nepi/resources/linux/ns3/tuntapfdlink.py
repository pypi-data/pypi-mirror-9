#
#    NEPI, a framework to manage network experiments
#    Copyright (C) 2014 INRIA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 2 as
#    published by the Free Software Foundation;
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Alina Quereilhac <alina.quereilhac@inria.fr>
from nepi.execution.resource import ResourceState, clsinit_copy
from nepi.resources.linux.application import LinuxApplication

import base64
import fcntl
import os
import socket
import struct

@clsinit_copy
class LinuxTunTapFdLink(LinuxApplication):
    """ Interconnects a TAP or TUN Linux device to a FdNetDevice
    """
    _rtype = "linux::ns3::TunTapFdLink"

    def __init__(self, ec, guid):
        super(LinuxTunTapFdLink, self).__init__(ec, guid)
        self._tap = None
        self._fdnetdevice = None
        self._fd_node = None
        self.send_address = None
        self._home = "tuntap-link-%s" % self.guid

    @property
    def fdnetdevice(self):
        if not self._fdnetdevice:
            from nepi.resources.ns3.ns3fdnetdevice import NS3BaseFdNetDevice
            devices = self.get_connected(NS3BaseFdNetDevice.get_rtype())
            if not devices or len(devices) != 1: 
                msg = "TunTapFdLink must be connected to exactly one FdNetDevice"
                self.error(msg)
                raise RuntimeError, msg

            self._fdnetdevice = devices[0]
        
            simu = self._fdnetdevice.simulation
            from nepi.resources.linux.node import LinuxNode
            nodes = simu.get_connected(LinuxNode.get_rtype())
            self._fd_node = nodes[0]
        
        return self._fdnetdevice

    @property
    def fdnode(self):
        return self._fd_node

    @property
    def tap(self):
        if not self._tap:
            from nepi.resources.linux.tap import LinuxTap
            devices = self.get_connected(LinuxTap.get_rtype())
            if not devices or len(devices) != 1: 
                msg = "TunTapLink must be connected to exactly one Tap or Tun"
                self.error(msg)
                raise RuntimeError, msg

            self._tap = devices[0]
        
        return self._tap

    @property
    def tapnode(self):
        return self.tap.node

    @property
    def node(self):
        return self.tapnode

    def upload_sources(self):
        scripts = []

        # vif-passfd python script
        linux_passfd = os.path.join(os.path.dirname(__file__),
                "..",
                "scripts",
                "linux-tap-passfd.py")

        scripts.append(linux_passfd)
        
        # Upload scripts
        scripts = ";".join(scripts)

        self.node.upload(scripts,
                os.path.join(self.node.src_dir),
                overwrite = False)

    def upload_start_command(self):
        if self.tapnode.get("hostname") != \
                self.fdnode.get("hostname"):
            msg = "Tap and FdNetDevice are not in the same host"
            self.error(msg)
            raise RuntimeError, msg

        self.send_address = self.fdnetdevice.recv_fd()
        self.set("command", self._start_command)

        command = self.get("command")

        shfile = os.path.join(self.app_home, "start.sh")
        self.node.run_and_wait(command, self.run_home,
                shfile=shfile,
                wait_run=False,
                overwrite=True)
        
    def do_deploy(self):
        if self.tap.state < ResourceState.READY or \
                self.fdnetdevice.state < ResourceState.READY:
            self.debug("---- RESCHEDULING DEPLOY ---- ")
            self.ec.schedule(self.reschedule_delay, self.deploy)
        else:
            self.do_discover()
            self.do_provision()

            self.set_ready()

    def do_start(self):
        if self.state == ResourceState.READY:
            command = self.get("command")
            self.info("Starting command '%s'" % command)

            self.set_started()
        else:
            msg = " Failed to execute command '%s'" % command
            self.error(msg, out, err)
            raise RuntimeError, msg

    @property
    def _start_command(self):
        address = base64.b64encode(self.send_address)

        command = []
        # Use tap-passfd.py to send fd from TAP to FdNetDevice
        command.append("sudo -S")
        command.append("PYTHONPATH=$PYTHONPATH:${SRC}")
        command.append("python ${SRC}/linux-tap-passfd.py")
        command.append("-a %s" % address)
        command.append("-S %s " % self.tap.sock_name)

        command = " ".join(command)
        command = self.replace_paths(command)

        return command

