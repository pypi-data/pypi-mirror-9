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

import base64
import socket

from optparse import OptionParser

STOP_MSG = "STOP"

def get_options():
    usage = ("usage: %prog -N <vif-name> -S <socket-name>")
    
    parser = OptionParser(usage = usage)

    parser.add_option("-N", "--vif-name", dest="vif_name",
        help = "The name of the virtual interface, or a "
                "unique numeric identifier to name the interface "
                "if GRE mode is used.",
        type="str")

    parser.add_option("-S", "--socket-name", dest="socket_name",
        help = "Name for the unix socket used to interact with this process", 
        type="str")

    (options, args) = parser.parse_args()
   
    return (options.socket_name, options.vif_name)

if __name__ == '__main__':

    (socket_name, vif_name) = get_options()

    # If a socket name is sent, send the STOP message and wait for a reply
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        sock.connect(socket_name)
        encoded = base64.b64encode(STOP_MSG)
        sock.send("%s\n" % encoded)
        reply = sock.recv(1024)
        reply = base64.b64decode(reply)
        print reply
    except:
        print "Did not properly shutdown device"

