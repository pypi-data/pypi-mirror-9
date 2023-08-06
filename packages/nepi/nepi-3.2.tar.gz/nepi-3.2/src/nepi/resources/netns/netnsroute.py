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
from nepi.resources.netns.netnsbase import NetNSBase

@clsinit_copy
class NetNSIPv4Route(NetNSBase):
    _rtype = "netns::IPv4Route"

    @classmethod
    def _register_attributes(cls):
        network = Attribute("network", "Network address", flags=Flags.Design)
        prefix = Attribute("prefix", "IP prefix length", flags=Flags.Design)
        nexthop = Attribute("nexthop", "Nexthop IP", flags=Flags.Design)

        cls._register_attribute(network)
        cls._register_attribute(prefix)
        cls._register_attribute(nexthop)

    @property
    def emulation(self):
        return self.node.emulation

    @property
    def node(self):
        from nepi.resources.netns.netnsnode import NetNSNode
        node = self.get_connected(NetNSNode.get_rtype())

        if not node: 
            msg = "Route not connected to Node!!"
            self.error(msg)
            raise RuntimeError, msg

        return node[0]

    @property
    def _rms_to_wait(self):
        return [self.node]

    def _instantiate_object(self):
         self._uuid = self.emulation.invoke(self.device.uuid, "add_route",
                prefix=self.get("network"), prefix_len=self.get("prefix"),
                nexthop=self.get("nexthop"))


