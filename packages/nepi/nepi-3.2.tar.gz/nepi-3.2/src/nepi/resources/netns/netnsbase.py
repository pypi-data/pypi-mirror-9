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
class NetNSBase(ResourceManager):
    _rtype = "abstract::netns::Object"
    _platform = "netns"

    def __init__(self, ec, guid):
        super(NetNSBase, self).__init__(ec, guid)
        self._uuid = None
        self._connected = set()
        self._trace_filename = dict()

    @property
    def connected(self):
        return self._connected

    @property
    def uuid(self):
        return self._uuid

    def trace(self, name, attr = TraceAttr.ALL, block = 512, offset = 0):
        filename = self._trace_filename.get(name)
        if not filename:
            self.error("Can not resolve trace %s. Did you enabled it?" % name)
            return ""

        return self.emulation.trace(filename, attr, block, offset)

    @property
    def _rms_to_wait(self):
        """ Returns the collection of RMs that this RM needs to
        wait for before start

        This method should be overriden to wait for other
        objects to be deployed before proceeding with the deployment

        """
        raise RuntimeError, "No dependencies defined!"

    def _instantiate_object(self):
        pass

    def _wait_rms(self):
        rms = set()
        for rm in self._rms_to_wait:
            if rm is not None:
                rms.add(rm)

        """ Returns True if dependent RMs are not yer READY, False otherwise"""
        for rm in rms:
            if rm.state < ResourceState.READY:
                return True
        return False

    def do_provision(self):
        self._instantiate_object()
      
        self.info("Provisioning finished")

        super(NetNSBase, self).do_provision()

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
            # No need to do anything, emulation.Run() will start every object
            self.info("Starting")
            self.set_started()
        else:
            msg = " Failed "
            self.error(msg, out, err)
            raise RuntimeError, msg

    def do_stop(self):
        if self.state == ResourceState.STARTED:
            # No need to do anything, emulation.Destroy() will stop every object
            self.set_stopped()
    
    @property
    def state(self):
        return self._state

    def get(self, name):
        #flags = Flags.NoWrite | Flags.NoRead | Flags.Design
        flags = Flags.Design
        if self._state in [ResourceState.READY, ResourceState.STARTED] \
                and not self.has_flag(name, flags):
            return self.emulation.emu_get(self.uuid, name)
        
        value = super(NetNSBase, self).get(name)
        return value

    def set(self, name, value):
        flags = Flags.Design
        if (self._state > ResourceState.NEW and \
                self.has_flag(name, Flags.Design)) or \
                self.has_flag(name, Flags.NoWrite):
            out = err = ""
            msg = " Cannot change Design only attribue %s" % name
            self.error(msg, out, err)
            return 

        if self._state in [ResourceState.READY, ResourceState.STARTED]:
            self.emulation.emu_set(self.uuid, name, value)
        
        value = super(NetNSBase, self).set(name, value)

        return value

