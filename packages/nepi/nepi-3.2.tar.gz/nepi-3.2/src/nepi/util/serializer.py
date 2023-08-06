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

import datetime
import os

class SFormats:
    XML = "xml"
    
class ECSerializer(object):
    def load(self, filepath, format = SFormats.XML):
        if format == SFormats.XML:
            from nepi.util.parsers.xml_parser import ECXMLParser
            
            parser = ECXMLParser()
            f = open(filepath, "r")
            xml = f.read()
            f.close()

            ec = parser.from_xml(xml)

        return ec

    def serialize(self, ec, format = SFormats.XML):
        if format == SFormats.XML:
            from nepi.util.parsers.xml_parser import ECXMLParser
            
            parser = ECXMLParser()
            sec = parser.to_xml(ec)

        return sec

    def save(self, ec, dirpath, format = SFormats.XML):
        date = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        filename = "%s_%s" % (ec.exp_id, date)

        if format == SFormats.XML:
            filepath = os.path.join(dirpath, "%s.xml" % filename)
            sec = self.serialize(ec, format = format)
            f = open(filepath, "w")
            f.write(sec)
            f.close()

        return filepath

