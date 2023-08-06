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
from nepi.resources.ns3.ns3errormodel import NS3BaseErrorModel 

@clsinit_copy
class NS3RateErrorModel(NS3BaseErrorModel):
    _rtype = "ns3::RateErrorModel"

    @classmethod
    def _register_attributes(cls):
        
        attr_errorunit = Attribute("ErrorUnit",
            "The error unit",
            type = Types.Enumerate,
            default = "ERROR_UNIT_BYTE",  
            allowed = ["ERROR_UNIT_BIT","ERROR_UNIT_BYTE","ERROR_UNIT_PACKET"],
            range = None,    
            flags = Flags.Reserved | Flags.Construct)

        cls._register_attribute(attr_errorunit)

        attr_errorrate = Attribute("ErrorRate",
            "The error rate.",
            type = Types.Double,
            default = "0",  
            allowed = None,
            range = None,    
            flags = Flags.Reserved | Flags.Construct)

        cls._register_attribute(attr_errorrate)

        attr_ranvar = Attribute("RanVar",
            "The decision variable attached to this error model.",
            type = Types.String,
            default = "ns3::UniformRandomVariable[Min=0.0|Max=1.0]",  
            allowed = None,
            range = None,    
            flags = Flags.Reserved | Flags.Construct)

        cls._register_attribute(attr_ranvar)

        attr_isenabled = Attribute("IsEnabled",
            "Whether this ErrorModel is enabled or not.",
            type = Types.Bool,
            default = "True",  
            allowed = None,
            range = None,    
            flags = Flags.Reserved | Flags.Construct)

        cls._register_attribute(attr_isenabled)



    @classmethod
    def _register_traces(cls):
        pass

    def __init__(self, ec, guid):
        super(NS3RateErrorModel, self).__init__(ec, guid)
        self._home = "ns3-rate-error-model-%s" % self.guid
