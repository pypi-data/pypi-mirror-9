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
from nepi.resources.linux.ns3.tuntapfdlink import LinuxTunTapFdLink

import base64
import fcntl
import os
import socket
import struct

@clsinit_copy
class PlanetlabTunTapFdLink(LinuxTunTapFdLink):
    """ Interconnects a TAP or TUN PlanetLab device to a FdNetDevice
    """
    _rtype = "planetlab::ns3::TunTapFdLink"

    def __init__(self, ec, guid):
        super(PlanetlabTunTapFdLink, self).__init__(ec, guid)

    @property
    def fdnetdevice(self):
        if not self._fdnetdevice:
            from nepi.resources.ns3.ns3fdnetdevice import NS3BaseFdNetDevice
            devices = self.get_connected(NS3BaseFdNetDevice.get_rtype())
            if not devices or len(devices) != 1: 
                msg = "planetlab::ns3::TunTapFdLink must be connected to exactly one FdNetDevice"
                self.error(msg)
                raise RuntimeError, msg

            self._fdnetdevice = devices[0]

            # Set PI headers on
            self._fdnetdevice.set("EncapsulationMode", "DixPi")
        
            simu = self._fdnetdevice.simulation
            from nepi.resources.planetlab.node import PlanetlabNode
            nodes = simu.get_connected(PlanetlabNode.get_rtype())
            self._fd_node = nodes[0]
        
        return self._fdnetdevice

    @property
    def tap(self):
        if not self._tap:
            from nepi.resources.planetlab.tap import PlanetlabTap
            devices = self.get_connected(PlanetlabTap.get_rtype())

            if not devices or len(devices) != 1: 
                msg = "planetlab::ns3::TunTapFdLink must be connected to exactly one PlanetlabTap"
                self.error(msg)
                raise RuntimeError, msg

            self._tap = devices[0]
        
        return self._tap

    def upload_sources(self):
        scripts = []

        # vif-passfd python script
        pl_vif_passfd = os.path.join(os.path.dirname(__file__), 
                "..", "..",
                "linux",
                "scripts",
                "linux-tap-passfd.py")

        scripts.append(pl_vif_passfd)
        
        # Upload scripts
        scripts = ";".join(scripts)

        self.node.upload(scripts,
                os.path.join(self.node.src_dir),
                overwrite = False)

