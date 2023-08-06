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

import os
import time
import threading
        
class NS3DceHelper(object):
    def __init__(self, simulation):
        self.simulation = simulation

        # Lock used to synchronize usage of DceManagerHelper 
        self._dce_manager_lock = threading.Lock()
        # Lock used to synchronize usage of DceApplicationHelper
        self._dce_application_lock = threading.Lock()
   
        self._dce_manager_uuid = None
        self._dce_application_uuid = None

    @property
    def dce_manager_uuid(self):
        if not self._dce_manager_uuid:
            self._dce_manager_uuid = \
                    self.simulation.create("DceManagerHelper")

        return self._dce_manager_uuid

    @property
    def dce_application_uuid(self):
        if not self._dce_application_uuid:
            self._dce_application_uuid = \
                    self.simulation.create("DceApplicationHelper")
                        
        return self._dce_application_uuid

    @property
    def dce_manager_lock(self):
        return self._dce_manager_lock

    @property
    def dce_application_lock(self):
        return self._dce_application_lock

