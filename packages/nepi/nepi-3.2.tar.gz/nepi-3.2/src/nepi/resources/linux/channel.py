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

from nepi.execution.attribute import Attribute, Flags
from nepi.execution.resource import ResourceManager, clsinit_copy, \
        ResourceState

@clsinit_copy
class LinuxChannel(ResourceManager):
    _rtype = "linux::Channel"
    _help = "Represents a wireless channel on a network of Linux hosts"
    _platform = "linux"

    def __init__(self, ec, guid):
        super(LinuxChannel, self).__init__(ec, guid)

    def log_message(self, msg):
        return " guid %d - %s " % (self.guid, msg)

    def valid_connection(self, guid):
        # TODO: Validate!
        return True

