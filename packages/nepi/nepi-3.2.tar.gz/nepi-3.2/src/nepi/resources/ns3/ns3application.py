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

from nepi.execution.resource import clsinit_copy, ResourceState
from nepi.resources.ns3.ns3base import NS3Base

@clsinit_copy
class NS3BaseApplication(NS3Base):
    _rtype = "abstract::ns3::Application"

    def __init__(self, ec, guid):
        super(NS3BaseApplication, self).__init__(ec, guid)
        self._node = None
 
    @property
    def node(self):
        if not self._node:
            from nepi.resources.ns3.ns3node import NS3BaseNode
            nodes = self.get_connected(NS3BaseNode.get_rtype())

            if not nodes: 
                msg = "Application not connected to node"
                self.error(msg)
                raise RuntimeError, msg

            self._node = nodes[0]

        return self._node

    @property
    def _rms_to_wait(self):
        rms = set()
        rms.add(self.node)
        return rms

    def _connect_object(self):
        node = self.node
        if node.uuid not in self.connected:
            self.simulation.invoke(node.uuid, "AddApplication", self.uuid)
            self._connected.add(node.uuid)

    def do_stop(self):
        if self.state == ResourceState.STARTED:
            # No need to do anything, simulation.Destroy() will stop every object
            self.info("Stopping command '%s'" % command)
            self.simulation.invoke(self.uuid, "Stop")
            self.set_stopped()

    def do_start(self):
        if self.simulation.state < ResourceState.STARTED:
            self.debug("---- RESCHEDULING START ----" )
            self.ec.schedule(self.reschedule_delay, self.start)
        else:
            super(NS3BaseApplication, self).do_start()
            self._start_time = self.simulation.start_time

    @property
    def state(self):
        if self._state == ResourceState.STARTED:
            try:
                is_running = self.simulation.invoke(self.uuid, "isAppRunning")
                
                if not is_running:
                    self.set_stopped()
            except:
                msg = "Application failed. Can not retrieve state"
                out = ""

                import traceback
                err = traceback.format_exc()
                self.error(msg, out, err)
                self.do_fail()

        return self._state

