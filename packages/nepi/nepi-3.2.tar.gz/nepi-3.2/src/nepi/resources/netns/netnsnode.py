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
class NetNSNode(NetNSBase):
    _rtype = "netns::Node"

    @property
    def emulation(self):
        from nepi.resources.netns.netnsemulation import NetNSEmulation

        for guid in self.connections:
            rm = self.ec.get_resource(guid)
            if isinstance(rm, NetNSEmulation):
                return rm

        msg = "Node not connected to Emulation"
        self.error(msg)
        raise RuntimeError, msg
 
    @property
    def _rms_to_wait(self):
        return [self.emulation]

    def _instantiate_object(self):
        self._uuid = self.emulation.create("Node")


