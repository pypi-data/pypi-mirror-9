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

from nepi.execution.attribute import Attribute, Flags, Types
from nepi.resources.netns.netnsbase import NetNSBase
from nepi.execution.resource import clsinit_copy, ResourceState

import shlex

@clsinit_copy
class NetNSApplication(NetNSBase):
    _rtype = "netns::Application"

    def __init__(self, ec, guid):
        super(NetNSApplication, self).__init__(ec, guid)
        self._traces = dict()

    @classmethod
    def _register_attributes(cls):
        command = Attribute("command", "Command to execute", flags=Flags.Design)
        cls._register_attribute(command)

    @property
    def emulation(self):
        return self.node.emulation

    @property
    def node(self):
        from nepi.resources.netns.netnsnode import NetNSNode
        node = self.get_connected(NetNSNode.get_rtype())

        if not node: 
            msg = "Route not connected to Node!!"
            self.error(msg)
            raise RuntimeError, msg

        return node[0]

    @property
    def _rms_to_wait(self):
        return [self.node]

    def do_start(self):
        if self.emulation.state < ResourceState.STARTED:
            self.debug("---- RESCHEDULING START ----" )
            self.ec.schedule(self.reschedule_delay, self.start)
        else:
            self._configure_traces()

            command = shlex.split(self.get("command"))
            stdout = self._traces["stdout"]
            stderr = self._traces["stderr"]
            self._uuid = self.emulation.invoke(self.node.uuid, 
                    "Popen", command, stdout = stdout, 
                    stderr = stderr)

            super(NetNSApplication, self).do_start()
            self._start_time = self.emulation.start_time

    def _configure_traces(self):
        stdout = "%s/%d.stdout" % (self.emulation.run_home, self.guid)
        stderr = "%s/%d.stderr" % (self.emulation.run_home, self.guid)
        self._trace_filename["stdout"] = stdout 
        self._trace_filename["stderr"] = stderr
        self._traces["stdout"] = self.emulation.create("open", stdout, "w")
        self._traces["stderr"] = self.emulation.create("open", stderr, "w")

    @property
    def state(self):
        if self._state == ResourceState.STARTED:
            retcode = self.emulation.invoke(self.uuid, "poll")
   
            if retcode is not None:
                if retcode == 0:
                    self.set_stopped()
                else:
                    out = ""
                    msg = " Failed to execute command '%s'" % self.get("command")
                    err = self.trace("stderr")
                    self.error(msg, out, err)
                    self.do_fail()

        return self._state

