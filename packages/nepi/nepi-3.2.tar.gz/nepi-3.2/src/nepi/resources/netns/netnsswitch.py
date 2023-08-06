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
class NetNSSwitch(NetNSBase):
    _rtype = "netns::Switch"

    @classmethod
    def _register_attributes(cls):
        up = Attribute("up", "Switch up", 
                default = True,
                type = Types.Bool)

        cls._register_attribute(up)

    @property
    def emulation(self):
        return self.node.emulation

    @property
    def node(self):
        return self.interface.node

    @property
    def interface(self):
        from nepi.resources.netns.netnsinterface import NetNSInterface
        interface = self.get_connected(NetNSInterface.get_rtype())

        if not interface: 
            msg = "Switch not connected to any Interface!!"
            self.error(msg)
            raise RuntimeError, msg

        return interface[0]

    @property
    def _rms_to_wait(self):
        return [self.emulation]

    def _instantiate_object(self):
        self._uuid = self.emulation.create("Switch")
        self.emulation.emu_set(self.uuid, "up", self.get("up"))

