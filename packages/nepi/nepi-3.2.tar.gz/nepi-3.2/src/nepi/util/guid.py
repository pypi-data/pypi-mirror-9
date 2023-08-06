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

# FIXME: This class is not thread-safe. 
# Should it be made thread-safe?
class GuidGenerator(object):
    def __init__(self):
        self._last_guid = 0

    def next(self, guid = None):
        if guid == None:
            guid = self._last_guid + 1

        self._last_guid = self._last_guid if guid <= self._last_guid else guid

        return guid

