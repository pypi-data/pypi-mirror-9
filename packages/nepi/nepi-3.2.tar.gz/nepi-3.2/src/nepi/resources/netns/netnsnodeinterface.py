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
from nepi.resources.netns.netnsinterface import NetNSInterface

@clsinit_copy
class NetNSNodeInterface(NetNSInterface):
    _rtype = "netns::NodeInterface"

    @classmethod
    def _register_attributes(cls):
        up = Attribute("up", "Interface up", 
                default = True,
                type = Types.Bool)

        cls._register_attribute(up)

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
    def switch(self):
        from nepi.resources.netns.netnsswitch import NetNSSwitch
        switch = self.get_connected(NetNSSwitch.get_rtype())
        if switch: return switch[0]
        return None

    @property
    def _rms_to_wait(self):
        return [self.node, self.switch]

    def _instantiate_object(self):
        self._uuid = self.emulation.invoke(self.node.uuid, "add_if")
        self.emulation.invoke(self.switch.uuid, "connect", self.uuid)
        self.emulation.emu_set(self.uuid, "up", self.get("up"))


