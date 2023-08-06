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

from nepi.execution.attribute import Attribute, Flags, Types
from nepi.execution.resource import clsinit_copy
from nepi.resources.ns3.ns3base import NS3Base
from nepi.resources.ns3.ns3wifinetdevice import WIFI_STANDARDS

@clsinit_copy
class NS3BaseWifiMac(NS3Base):
    _rtype = "abstract::ns3::WifiMac"

    @classmethod
    def _register_attributes(cls):
        standard = Attribute("Standard", "Wireless standard",
                default = "WIFI_PHY_STANDARD_80211a",
                allowed = WIFI_STANDARDS.keys(),
                type = Types.Enumerate,
                flags = Flags.Design)

        cls._register_attribute(standard)

    @property
    def node(self):
        return self.device.node

    @property
    def device(self):
        from nepi.resources.ns3.ns3wifinetdevice import NS3BaseWifiNetDevice
        devices = self.get_connected(NS3BaseWifiNetDevice.get_rtype())

        if not devices: 
            msg = "WifiMac not connected to device"
            self.error(msg)
            raise RuntimeError, msg

        return devices[0]

    @property
    def _rms_to_wait(self):
        rms = set()
        rms.add(self.device)
        return rms

    def _connect_object(self):
        device = self.device
        if device.uuid not in self.connected:
            self._connected.add(device.uuid)

            self.simulation.invoke(device.uuid, "SetMac", self.uuid)

            standard = self.get("Standard")
            self.simulation.invoke(self.uuid, "ConfigureStandard", WIFI_STANDARDS[standard])

            # Delayed configuration of MAC address
            mac = device.get("mac")
            if mac:
                mac_uuid = self.simulation.create("Mac48Address", mac)
            else:
                mac_uuid = self.simulation.invoke("singleton::Mac48Address", "Allocate")

            self.simulation.invoke(self.uuid, "SetAddress", mac_uuid)


