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

from nepi.execution.resource import ResourceManager, clsinit_copy, \
        ResourceState
from nepi.execution.attribute import Flags
from nepi.execution.trace import TraceAttr

@clsinit_copy
class NS3Base(ResourceManager):
    _rtype = "abstract::ns3::Object"
    _platform = "ns3"

    def __init__(self, ec, guid):
        super(NS3Base, self).__init__(ec, guid)
        self._uuid = None
        self._connected = set()
        self._trace_filename = dict()
        self._node = None

    @property
    def connected(self):
        return self._connected

    @property
    def uuid(self):
        return self._uuid

    @property
    def simulation(self):
        return self.node.simulation

    @property
    def node(self):
        if not self._node:
            from nepi.resources.ns3.ns3node import NS3BaseNode
            nodes = self.get_connected(NS3BaseNode.get_rtype())
            if nodes: self._node = nodes[0]

        return self._node

    def trace(self, name, attr = TraceAttr.ALL, block = 512, offset = 0):
        filename = self._trace_filename.get(name)
        if not filename:
            self.error("Can not resolve trace %s. Did you enabled it?" % name)
            return ""

        return self.simulation.trace(filename, attr, block, offset)

    @property
    def _rms_to_wait(self):
        """ Returns the collection of ns-3 RMs that this RM needs to
        wait for before start

        This method should be overriden to wait for other ns-3
        objects to be deployed before proceeding with the deployment

        """
        rms = set()
        node = self.node
        if node: rms.add(node)
        return rms

    def _instantiate_object(self):
        if self.uuid:
            return 

        kwargs = dict()
        for attr in self._attrs.values():
            if not ( attr.has_flag(Flags.Construct) and attr.has_changed ):
                continue

            kwargs[attr.name] = attr._value

        self._uuid = self.simulation.factory(self.get_rtype(), **kwargs)

    def _configure_object(self):
        pass

    def _connect_object(self):
        node = self.node
        if node and node.uuid not in self.connected:
            self.simulation.invoke(node.uuid, "AggregateObject", self.uuid)
            self._connected.add(node.uuid)

    def _wait_rms(self):
        """ Returns True if dependent RMs are not yer READY, False otherwise"""
        for rm in self._rms_to_wait:
            if rm.state < ResourceState.READY:
                return True
        return False

    def do_provision(self):
        self._instantiate_object()
        self._connect_object()
        self._configure_object()
      
        self.info("Provisioning finished")

        super(NS3Base, self).do_provision()

    def do_deploy(self):
        if self._wait_rms():
            self.debug("---- RESCHEDULING DEPLOY ----" )
            self.ec.schedule(self.reschedule_delay, self.deploy)
        else:
            self.do_discover()
            self.do_provision()

            self.set_ready()

    def do_start(self):
        if self.state == ResourceState.READY:
            # No need to do anything, simulation.Run() will start every object
            self.info("Starting")
            self.set_started()
        else:
            msg = "Failed"
            self.error(msg, out, err)
            raise RuntimeError, msg

    def do_stop(self):
        if self.state == ResourceState.STARTED:
            # No need to do anything, simulation.Destroy() will stop every object
            self.info("Stopping")
            self.set_stopped()
    
    @property
    def state(self):
        return self._state

    def get(self, name):
        if self.state in [ResourceState.READY, ResourceState.STARTED] and \
                self.has_flag(name, Flags.Reserved) and \
                not self.has_flag(name, Flags.NoRead): 
            return self.simulation.ns3_get(self.uuid, name)
        else:
            value = super(NS3Base, self).get(name)

        return value

    def set(self, name, value):
        if self.state in [ResourceState.READY, ResourceState.STARTED] and \
                self.has_flag(name, Flags.Reserved) and \
                not (self.has_flag(Flags.NoWrite) or self.has_flag(name, Flags.Design)): 
            self.simulation.ns3_set(self.uuid, name, value)
        
        value = super(NS3Base, self).set(name, value)

        return value

