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
from nepi.resources.ns3.ns3application import NS3BaseApplication 

@clsinit_copy
class NS3PacketSink(NS3BaseApplication):
    _rtype = "ns3::PacketSink"

    @classmethod
    def _register_attributes(cls):
        
        attr_local = Attribute("Local",
            "The Address on which to Bind the rx socket.",
            type = Types.String,
            default = "00-00-00",  
            allowed = None,
            range = None,    
            flags = Flags.Reserved | Flags.Construct)

        cls._register_attribute(attr_local)

        attr_protocol = Attribute("Protocol",
            "The type id of the protocol to use for the rx socket.",
            type = Types.String,
            default = "ns3::UdpSocketFactory",  
            allowed = None,
            range = None,    
            flags = Flags.Reserved | Flags.Construct)

        cls._register_attribute(attr_protocol)

        attr_starttime = Attribute("StartTime",
            "Time at which the application will start",
            type = Types.String,
            default = "+0.0ns",  
            allowed = None,
            range = None,    
            flags = Flags.Reserved | Flags.Construct)

        cls._register_attribute(attr_starttime)

        attr_stoptime = Attribute("StopTime",
            "Time at which the application will stop",
            type = Types.String,
            default = "+0.0ns",  
            allowed = None,
            range = None,    
            flags = Flags.Reserved | Flags.Construct)

        cls._register_attribute(attr_stoptime)



    @classmethod
    def _register_traces(cls):
        
        rx = Trace("Rx", "A packet has been received")

        cls._register_trace(rx)



    def __init__(self, ec, guid):
        super(NS3PacketSink, self).__init__(ec, guid)
        self._home = "ns3-packet-sink-%s" % self.guid
