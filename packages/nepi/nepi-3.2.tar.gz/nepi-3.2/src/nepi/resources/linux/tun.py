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

from nepi.execution.resource import clsinit_copy
from nepi.resources.linux.tap import LinuxTap

import os

@clsinit_copy
class LinuxTun(LinuxTap):
    _rtype = "linux::Tun"
    _help = "Creates a TUN device on a Linux host"

    def __init__(self, ec, guid):
        super(LinuxTun, self).__init__(ec, guid)
        self._vif_prefix = "tun"
        self._vif_type = "IFF_TUN"
        self._vif_type_flag = LinuxTap.IFF_TUN
        self._home = "%s-%s" % (self.vif_prefix, self.guid)
    

