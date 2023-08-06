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
class NS3OkumuraHataPropagationLossModel(NS3BasePropagationLossModel):
    _rtype = "ns3::OkumuraHataPropagationLossModel"

    @classmethod
    def _register_attributes(cls):
        
        attr_frequency = Attribute("Frequency",
            "The propagation frequency in Hz",
            type = Types.Double,
            default = "2.16e+09",  
            allowed = None,
            range = None,    
            flags = Flags.Reserved | Flags.Construct)

        cls._register_attribute(attr_frequency)

        attr_environment = Attribute("Environment",
            "Environment Scenario",
            type = Types.Enumerate,
            default = "Urban",  
            allowed = ["Urban","SubUrban","OpenAreas"],
            range = None,    
            flags = Flags.Reserved | Flags.Construct)

        cls._register_attribute(attr_environment)

        attr_citysize = Attribute("CitySize",
            "Dimension of the city",
            type = Types.Enumerate,
            default = "Large",  
            allowed = ["Small","Medium","Large"],
            range = None,    
            flags = Flags.Reserved | Flags.Construct)

        cls._register_attribute(attr_citysize)



    @classmethod
    def _register_traces(cls):
        pass

    def __init__(self, ec, guid):
        super(NS3OkumuraHataPropagationLossModel, self).__init__(ec, guid)
        self._home = "ns3-okumura-hata-propagation-loss-model-%s" % self.guid
