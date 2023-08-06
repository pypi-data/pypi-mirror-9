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

class NS3Client(object):
    """ Common Interface for NS3 client classes """
    def __init__(self):
        super(NS3Client, self).__init__()

    def create(self, *args, **kwargs):
        pass

    def factory(self, *args, **kwargs):
        pass

    def invoke(self, *args, **kwargs):
        pass

    def set(self, *args, **kwargs):
        pass

    def get(self, *args, **kwargs):
        pass

    def flush(self, *args, **kwargs):
        pass

    def start(self, *args, **kwargs):
        pass

    def stop(self, *args, **kwargs):
        pass

    def shutdown(self, *args, **kwargs):
        pass

