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
from nepi.execution.resource import clsinit_copy, ResourceState
from nepi.resources.ns3.ns3application import NS3BaseApplication
from nepi.execution.trace import TraceAttr

from nepi.resources.ns3.ns3wrapper import SIMULATOR_UUID

import os
import time
import threading
        
@clsinit_copy
class NS3BaseDceApplication(NS3BaseApplication):
    _rtype = "abstract::ns3::DceApplication"

    @classmethod
    def _register_attributes(cls):
        binary = Attribute("binary", 
                "Name of binary to execute",
                flags = Flags.Design)

        stack_size = Attribute("stackSize", 
                "Stack Size for DCE",
                type = Types.Integer,
                default = 1<<20,                
                flags = Flags.Design)

        arguments = Attribute("arguments", 
                "Semi-colon separated list of arguments for the application",
                flags = Flags.Design)

        environment = Attribute("environment", 
                "Semi-colon separated list of 'key=value' pairs to set as "
                "DCE environment variables.",
                flags = Flags.Design)

        use_dlm = Attribute("useDlmLoader",
                "Use ns3::DlmLoaderFactory as library loader",
                type = Types.Bool,
                flags = Flags.Design)
        
        starttime = Attribute("StartTime",
            "Time at which the application will start",
            default = "+0.0ns",  
            flags = Flags.Reserved | Flags.Construct)

        stoptime = Attribute("StopTime",
            "Time at which the application will stop",
            default = "+0.0ns",  
            flags = Flags.Reserved | Flags.Construct)

        cls._register_attribute(binary)
        cls._register_attribute(stack_size)
        cls._register_attribute(arguments)
        cls._register_attribute(environment)
        cls._register_attribute(use_dlm)
        cls._register_attribute(stoptime)
        cls._register_attribute(starttime)

    def __init__(self, ec, guid):
        super(NS3BaseDceApplication, self).__init__(ec, guid)
        self._pid = None

    @property
    def pid(self):
        return self._pid

    def _instantiate_object(self):
        pass

    def _connect_object(self):
        node = self.node
        if node.uuid not in self.connected:
            self._connected.add(node.uuid)

            # Preventing concurrent access to the DceApplicationHelper
            # from different DceApplication RMs
            dce_helper = self.simulation.dce_helper

            with dce_helper.dce_application_lock:
                dce_app_uuid = dce_helper.dce_application_uuid

                self.simulation.invoke(dce_app_uuid, "ResetArguments") 

                self.simulation.invoke(dce_app_uuid, "ResetEnvironment") 

                self.simulation.invoke(dce_app_uuid, 
                        "SetBinary", self.get("binary")) 

                self.simulation.invoke(dce_app_uuid, 
                        "SetStackSize", self.get("stackSize")) 

                arguments = self.get("arguments")
                if arguments:
                    for arg in map(str.strip, arguments.split(";")):
                        self.simulation.invoke(dce_app_uuid, 
                            "AddArgument", arg)

                environment = self.get("environment")
                if environment:
                    for env in map(str.strip, environment.split(";")):
                        key, val = env.split("=")
                        self.simulation.invoke(dce_app_uuid, 
                            "AddEnvironment", key, val)

                apps_uuid = self.simulation.invoke(dce_app_uuid, 
                        "InstallInNode", self.node.uuid)

            self._uuid = self.simulation.invoke(apps_uuid, "Get", 0)

            if self.has_changed("StartTime"):
                self.simulation.ns3_set(self.uuid, "StartTime", self.get("StartTime"))

            if self.has_changed("StopTime"):
                self.simulation.ns3_set(self.uuid, "StopTime", self.get("StopTime"))

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
            is_app_started = self.simulation.invoke(self.uuid, "isAppStarted")

            if is_app_started or self.simulation.state > ResourceState.STARTED:
                super(NS3BaseApplication, self).do_start()
                self._start_time = self.simulation.start_time
            else:
                # Reschedule until dce application is actually started
                self.debug("---- RESCHEDULING START ----" )
                self.ec.schedule(self.reschedule_delay, self.start)

    def trace(self, name, attr = TraceAttr.ALL, block = 512, offset = 0):
        self._configure_traces()
        return super(NS3BaseDceApplication, self).trace(name, attr = attr, 
                block = block, offset = offset)

    def _configure_traces(self):
        if self.pid is not None:
            return 

        # Using lock to prevent concurrent access to the DceApplicationHelper
        # from different DceApplication RMs
        dce_helper = self.simulation.dce_helper

        with dce_helper.dce_application_lock:
            dce_app_uuid = dce_helper.dce_application_uuid

            self._pid = self.simulation.invoke(dce_app_uuid, 
                    "GetPid", self.uuid)

        node_id = self.node.node_id 
        self._trace_filename["stdout"] = "files-%s/var/log/%s/stdout" % (node_id, self.pid)
        self._trace_filename["stderr"] = "files-%s/var/log/%s/stderr" % (node_id, self.pid)
        self._trace_filename["status"] = "files-%s/var/log/%s/status" % (node_id, self.pid)
        self._trace_filename["cmdline"] = "files-%s/var/log/%s/cmdline" % (node_id, self.pid)


