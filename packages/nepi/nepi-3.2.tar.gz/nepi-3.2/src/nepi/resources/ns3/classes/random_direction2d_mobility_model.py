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
from nepi.resources.ns3.ns3mobilitymodel import NS3BaseMobilityModel 

@clsinit_copy
class NS3RandomDirection2dMobilityModel(NS3BaseMobilityModel):
    _rtype = "ns3::RandomDirection2dMobilityModel"

    @classmethod
    def _register_attributes(cls):
        
        attr_bounds = Attribute("Bounds",
            "The 2d bounding area",
            type = Types.String,
            default = "-100|100|-100|100",  
            allowed = None,
            range = None,    
            flags = Flags.Reserved | Flags.Construct)

        cls._register_attribute(attr_bounds)

        attr_speed = Attribute("Speed",
            "A random variable to control the speed (m/s).",
            type = Types.String,
            default = "ns3::UniformRandomVariable[Min=1.0|Max=2.0]",  
            allowed = None,
            range = None,    
            flags = Flags.Reserved | Flags.Construct)

        cls._register_attribute(attr_speed)

        attr_pause = Attribute("Pause",
            "A random variable to control the pause (s).",
            type = Types.String,
            default = "ns3::ConstantRandomVariable[Constant=2.0]",  
            allowed = None,
            range = None,    
            flags = Flags.Reserved | Flags.Construct)

        cls._register_attribute(attr_pause)

        attr_position = Attribute("Position",
            "The current position of the mobility model.",
            type = Types.String,
            default = "0:0:0",  
            allowed = None,
            range = None,    
            flags = Flags.Reserved)

        cls._register_attribute(attr_position)

        attr_velocity = Attribute("Velocity",
            "The current velocity of the mobility model.",
            type = Types.String,
            default = "0:0:0",  
            allowed = None,
            range = None,    
            flags = Flags.Reserved | Flags.NoWrite)

        cls._register_attribute(attr_velocity)



    @classmethod
    def _register_traces(cls):
        
        coursechange = Trace("CourseChange", "The value of the position and/or velocity vector changed")

        cls._register_trace(coursechange)



    def __init__(self, ec, guid):
        super(NS3RandomDirection2dMobilityModel, self).__init__(ec, guid)
        self._home = "ns3-random-direction2d-mobility-model-%s" % self.guid
