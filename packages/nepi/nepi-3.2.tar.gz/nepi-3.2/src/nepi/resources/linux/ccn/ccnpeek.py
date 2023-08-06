#
#    NEPI, a framework to manage network experiments
#    Copyright (C) 2013 INRIA
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
from nepi.execution.resource import clsinit_copy, ResourceState
from nepi.resources.linux.ccn.ccnapplication import LinuxCCNApplication

import os

@clsinit_copy
class LinuxCCNPeek(LinuxCCNApplication):
    _rtype = "linux::CCNPeek"

    @classmethod
    def _register_attributes(cls):
        content_name = Attribute("contentName",
            "Content name for the content to peek",
            flags = Flags.Design)

        cls._register_attribute(content_name)

    def __init__(self, ec, guid):
        super(LinuxCCNPeek, self).__init__(ec, guid)
        self._home = "ccnpeek-%s" % self.guid

    def do_deploy(self):
        if not self.ccnd or self.ccnd.state < ResourceState.READY:
            self.debug("---- RESCHEDULING DEPLOY ---- node state %s " % self.node.state )
            self.ec.schedule(self.reschedule_delay, self.deploy)
        else:
            command = self.get("command")
            if not command:
                command = "ccnpeek %s" % self.get("contentName")
                self.set("command", command) 

            self.info("Deploying command '%s' " % command)
            
            if not self.get("env"):
                self.set("env", self._environment)

            self.do_discover()
            self.do_provision()

            self.set_ready()

    def valid_connection(self, guid):
        # TODO: Validate!
        return True

