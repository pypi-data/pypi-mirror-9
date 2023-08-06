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
from nepi.resources.linux.application import LinuxApplication
from nepi.util.timefuncs import tnow

import os

@clsinit_copy
class LinuxMtr(LinuxApplication):
    _rtype = "linux::Mtr"

    @classmethod
    def _register_attributes(cls):
        report_cycles = Attribute("reportCycles",
            "sets mtr --report-cycles (-c) option. Determines the number of "
            "pings sent to determine both machines in the networks. Each "
            "cycle lasts one sencond.",
            flags = Flags.Design)

        no_dns = Attribute("noDns",
            "sets mtr --no-dns (-n) option. Forces mtr to display IPs intead of "
            "trying to resolve to host names ",
            type = Types.Bool,
            default = True,
            flags = Flags.Design)

        address = Attribute("address",
            "sets mtr --address (-a) option. Binds the socket to send outgoing "
            "packets to the interface of the specified address, so that any "
            "any packets are sent through this interface. ",
            flags = Flags.Design)

        interval = Attribute("interval",
            "sets mtr --interval (-i) option. Specifies the number of seconds "
            "between ICMP ECHO requests. Default value is one second ",
            flags = Flags.Design)

        countinuous = Attribute("continuous",
            "Run mtr in a while loop",
            type = Types.Bool,
            default = False,
            flags = Flags.Design)

        print_timestamp = Attribute("printTimestamp",
            "Print timestamp before running mtr",
            type = Types.Bool,
            default = False,
            flags = Flags.Design)

        target = Attribute("target",
            "mtr target host (host that will be pinged)",
            flags = Flags.Design)

        early_start = Attribute("earlyStart",
            "Start ping as early as deployment. ",
            type = Types.Bool,
            default = False,
            flags = Flags.Design)

        cls._register_attribute(report_cycles)
        cls._register_attribute(no_dns)
        cls._register_attribute(address)
        cls._register_attribute(interval)
        cls._register_attribute(countinuous)
        cls._register_attribute(print_timestamp)
        cls._register_attribute(target)
        cls._register_attribute(early_start)

    def __init__(self, ec, guid):
        super(LinuxMtr, self).__init__(ec, guid)
        self._home = "mtr-%s" % self.guid
        self._sudo_kill = True

    def upload_start_command(self):
        super(LinuxMtr, self).upload_start_command()
        
        if self.get("earlyStart") == True:
            self._run_in_background()

    def do_deploy(self):
        if not self.get("command"):
            self.set("command", self._start_command)

        if not self.get("env"):
            self.set("env", "PATH=$PATH:/usr/sbin/")

        if not self.get("depends"):
            self.set("depends", "mtr")

        super(LinuxMtr, self).do_deploy()

    def do_start(self):
        if self.get("earlyStart") == True:
            if self.state == ResourceState.READY:
                command = self.get("command")
                self.info("Starting command '%s'" % command)

                self.set_started()
            else:
                msg = " Failed to execute command '%s'" % command
                self.error(msg, out, err)
                raise RuntimeError, msg
        else:
           super(LinuxMtr, self).do_start()

    @property
    def _start_command(self):
        args = []
        if self.get("continuous") == True:
            args.append("while true; do ")
        if self.get("printTimestamp") == True:
            args.append("""echo "`date +'%Y%m%d%H%M%S'`";""")
        args.append("sudo -S mtr --report")
        if self.get("reportCycles"):
            args.append("-c %s" % self.get("reportCycles"))
        if self.get("noDns") == True:
            args.append("-n")
        if self.get("address"):
            args.append("-a %s" % self.get("address"))
        args.append(self.get("target"))
        if self.get("continuous") == True:
            args.append("; done ")

        command = " ".join(args)

        return command

    def valid_connection(self, guid):
        # TODO: Validate!
        return True

