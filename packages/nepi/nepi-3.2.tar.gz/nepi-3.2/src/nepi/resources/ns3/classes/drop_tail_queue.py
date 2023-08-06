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
from nepi.resources.ns3.ns3queue import NS3BaseQueue 

@clsinit_copy
class NS3DropTailQueue(NS3BaseQueue):
    _rtype = "ns3::DropTailQueue"

    @classmethod
    def _register_attributes(cls):
        
        attr_maxpackets = Attribute("MaxPackets",
            "The maximum number of packets accepted by this DropTailQueue.",
            type = Types.Integer,
            default = "100",  
            allowed = None,
            range = None,    
            flags = Flags.Reserved | Flags.Construct)

        cls._register_attribute(attr_maxpackets)

        attr_maxbytes = Attribute("MaxBytes",
            "The maximum number of bytes accepted by this DropTailQueue.",
            type = Types.Integer,
            default = "6553500",  
            allowed = None,
            range = None,    
            flags = Flags.Reserved | Flags.Construct)

        cls._register_attribute(attr_maxbytes)



    @classmethod
    def _register_traces(cls):
        
        enqueue = Trace("Enqueue", "Enqueue a packet in the queue.")

        cls._register_trace(enqueue)

        dequeue = Trace("Dequeue", "Dequeue a packet from the queue.")

        cls._register_trace(dequeue)

        drop = Trace("Drop", "Drop a packet stored in the queue.")

        cls._register_trace(drop)



    def __init__(self, ec, guid):
        super(NS3DropTailQueue, self).__init__(ec, guid)
        self._home = "ns3-drop-tail-queue-%s" % self.guid
