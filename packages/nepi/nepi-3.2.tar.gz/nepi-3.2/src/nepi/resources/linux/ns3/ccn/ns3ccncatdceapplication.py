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
from nepi.resources.linux.ns3.ccn.ns3ccndceapplication import LinuxNS3CCNDceApplication

@clsinit_copy
class LinuxNS3DceCCNCat(LinuxNS3CCNDceApplication):
    _rtype = "linux::ns3::dce::CCNCat"

    @classmethod
    def _register_attributes(cls):
        content_name = Attribute("contentName",
                "Content name for the requested content object. ",
                flags = Flags.Design)

        cls._register_attribute(content_name)

    def _instantiate_object(self):
        if not self.get("binary"):
            self.set("binary", "ccncat")
            
        if self.get("contentName"):
            self.set("arguments", self.get("contentName"))

        self.set("stdinFile", "")

        super(LinuxNS3DceCCNCat, self)._instantiate_object()

    @property
    def _arguments(self):
        args = ["-v", "add"]

        if self.get("uri"):
            args.append(self.get("uri"))
        if self.get("protocol"):
            args.append(self.get("protocol"))
        if self.get("host"):
            args.append(self.get("host"))
        if self.get("port"):
            args.append(self.get("port"))
        if self.get("ip"):
            args.append(self.get("ip"))

        return ";".join(args) 


