#
#    NEPI, a framework to manage network experiments
#    Copyright (C) 2013 INRIA
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

from nepi.execution.attribute import Attribute, Flags, Types
from nepi.execution.resource import clsinit_copy, ResourceState
from nepi.resources.linux.ns3.fdudptunnel import LinuxNs3FdUdpTunnel
from nepi.util.sshfuncs import ProcStatus
from nepi.util.timefuncs import tnow, tdiffsec

import base64
import os
import socket
import time

@clsinit_copy
class PlanetlabNs3FdUdpTunnel(LinuxNs3FdUdpTunnel):
    _rtype = "planetlab::ns3::FdUdpTunnel"
    _help = "Constructs a tunnel between two Ns-3 FdNetdevices " \
            "located in remote PlanetLab nodes using a UDP connection "
    _platform = "planetlab::ns3"

    def get_endpoints(self):
        """ Returns the list of RM that are endpoints to the tunnel 
        """
        if not self._fd2 or not self._fd1:
            from nepi.resources.ns3.ns3fdnetdevice import NS3BaseFdNetDevice
            devices = self.get_connected(NS3BaseFdNetDevice.get_rtype())
            if not devices or len(devices) != 2: 
                msg = "Tunnel must be connected to exactly two FdNetDevices"
                self.error(msg)
                raise RuntimeError, msg

            self._fd1 = devices[0]
            self._fd2 = devices[1]
            self._pi = True
 
            # Set PI headers on
            self._fd1.set("EncapsulationMode", "DixPi")
            self._fd2.set("EncapsulationMode", "DixPi")
        
            simu = self._fd1.simulation
            from nepi.resources.linux.node import LinuxNode
            nodes = simu.get_connected(LinuxNode.get_rtype())
            self._fd1node = nodes[0]
     
            simu = self._fd2.simulation
            from nepi.resources.linux.node import LinuxNode
            nodes = simu.get_connected(LinuxNode.get_rtype())
            self._fd2node = nodes[0]

            if self._fd1node.get("hostname") == \
                    self._fd2node.get("hostname"):
                msg = "Tunnel requires endpoints on different hosts"
                self.error(msg)
                raise RuntimeError, msg

        return [self._fd1, self._fd2]


