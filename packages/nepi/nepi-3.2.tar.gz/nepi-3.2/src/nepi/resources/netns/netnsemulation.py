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

class NetNSEmulation(object):
    @property
    def client(self):
        return self._client

    def create(self, *args, **kwargs):
        return self.client.create(*args, **kwargs)

    def invoke(self, *args, **kwargs):
        return self.client.invoke(*args, **kwargs)

    def emu_set(self, *args, **kwargs):
        return self.client.set(*args, **kwargs)

    def emu_get(self, *args, **kwargs):
        return self.client.get(*args, **kwargs)

    def flush(self, *args, **kwargs):
        return self.client.flush(*args, **kwargs)

    def shutdown(self, *args, **kwargs):
        return self.client.shutdown(*args, **kwargs)

