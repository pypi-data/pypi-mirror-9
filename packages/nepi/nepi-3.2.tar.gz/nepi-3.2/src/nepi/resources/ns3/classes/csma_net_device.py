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
from nepi.resources.ns3.ns3netdevice import NS3BaseNetDevice 

@clsinit_copy
class NS3CsmaNetDevice(NS3BaseNetDevice):
    _rtype = "ns3::CsmaNetDevice"

    @classmethod
    def _register_attributes(cls):
        
        attr_address = Attribute("Address",
            "The MAC address of this device.",
            type = Types.String,
            default = "ff:ff:ff:ff:ff:ff",  
            allowed = None,
            range = None,    
            flags = Flags.Reserved | Flags.Construct)

        cls._register_attribute(attr_address)

        attr_mtu = Attribute("Mtu",
            "The MAC-level Maximum Transmission Unit",
            type = Types.Integer,
            default = "1500",  
            allowed = None,
            range = None,    
            flags = Flags.Reserved | Flags.Construct)

        cls._register_attribute(attr_mtu)

        attr_sendenable = Attribute("SendEnable",
            "Enable or disable the transmitter section of the device.",
            type = Types.Bool,
            default = "True",  
            allowed = None,
            range = None,    
            flags = Flags.Reserved | Flags.Construct)

        cls._register_attribute(attr_sendenable)

        attr_receiveenable = Attribute("ReceiveEnable",
            "Enable or disable the receiver section of the device.",
            type = Types.Bool,
            default = "True",  
            allowed = None,
            range = None,    
            flags = Flags.Reserved | Flags.Construct)

        cls._register_attribute(attr_receiveenable)



    @classmethod
    def _register_traces(cls):
        
        mactx = Trace("MacTx", "Trace source indicating a packet has arrived for transmission by this device")

        cls._register_trace(mactx)

        mactxdrop = Trace("MacTxDrop", "Trace source indicating a packet has been dropped by the device before transmission")

        cls._register_trace(mactxdrop)

        macpromiscrx = Trace("MacPromiscRx", "A packet has been received by this device, has been passed up from the physical layer and is being forwarded up the local protocol stack.  This is a promiscuous trace,")

        cls._register_trace(macpromiscrx)

        macrx = Trace("MacRx", "A packet has been received by this device, has been passed up from the physical layer and is being forwarded up the local protocol stack.  This is a non-promiscuous trace,")

        cls._register_trace(macrx)

        mactxbackoff = Trace("MacTxBackoff", "Trace source indicating a packet has been delayed by the CSMA backoff process")

        cls._register_trace(mactxbackoff)

        phytxbegin = Trace("PhyTxBegin", "Trace source indicating a packet has begun transmitting over the channel")

        cls._register_trace(phytxbegin)

        phytxend = Trace("PhyTxEnd", "Trace source indicating a packet has been completely transmitted over the channel")

        cls._register_trace(phytxend)

        phytxdrop = Trace("PhyTxDrop", "Trace source indicating a packet has been dropped by the device during transmission")

        cls._register_trace(phytxdrop)

        phyrxend = Trace("PhyRxEnd", "Trace source indicating a packet has been completely received by the device")

        cls._register_trace(phyrxend)

        phyrxdrop = Trace("PhyRxDrop", "Trace source indicating a packet has been dropped by the device during reception")

        cls._register_trace(phyrxdrop)

        sniffer = Trace("Sniffer", "Trace source simulating a non-promiscuous packet sniffer attached to the device")

        cls._register_trace(sniffer)

        promiscsniffer = Trace("PromiscSniffer", "Trace source simulating a promiscuous packet sniffer attached to the device")

        cls._register_trace(promiscsniffer)



    def __init__(self, ec, guid):
        super(NS3CsmaNetDevice, self).__init__(ec, guid)
        self._home = "ns3-csma-net-device-%s" % self.guid
