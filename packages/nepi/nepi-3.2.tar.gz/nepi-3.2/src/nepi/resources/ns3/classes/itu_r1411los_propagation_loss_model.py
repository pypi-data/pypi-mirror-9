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

from nepi.execution.attribute import Attribute, Flags, Types
from nepi.execution.trace import Trace, TraceAttr
from nepi.execution.resource import ResourceManager, clsinit_copy, \
        ResourceState
from nepi.resources.ns3.ns3propagationlossmodel import NS3BasePropagationLossModel 

@clsinit_copy
class NS3ItuR1411LosPropagationLossModel(NS3BasePropagationLossModel):
    _rtype = "ns3::ItuR1411LosPropagationLossModel"

    @classmethod
    def _register_attributes(cls):
        pass

    @classmethod
    def _register_traces(cls):
        pass

    def __init__(self, ec, guid):
        super(NS3ItuR1411LosPropagationLossModel, self).__init__(ec, guid)
        self._home = "ns3-itu-r1411los-propagation-loss-model-%s" % self.guid
