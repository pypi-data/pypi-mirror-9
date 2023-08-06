import base64
import errno
import os
import passfd
import socket

from optparse import OptionParser

PASSFD_MSG = "PASSFD"

def get_options():
    usage = ("usage: %prog -a <address> -S <vif-socket> ")
    
    parser = OptionParser(usage = usage)

    parser.add_option("-a", "--address", dest="address",
        help = "Socket address to send file descriptor to", type="str")
    parser.add_option("-S", "--vif-socket", dest="vif_socket",
        help = "Name for the unix socket to request the TAP file descriptor", 
        default = "tap.sock", type="str")

    (options, args) = parser.parse_args()
       
    return (options.address, options.vif_socket)

if __name__ == '__main__':

    (address, vif_socket) = get_options()
  
    # This script sends a message (PASSFD_MSG) to the process that created 
    # the TUN/TAP device to request that it sens the file descriptor associated
    # to the TUN/TAP to another process. The other process is waiting for
    # the file descriptor on 'address'
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(vif_socket)
    emsg = base64.b64encode(PASSFD_MSG)
    eargs = address
    encoded = "%s|%s\n" % (emsg, eargs)
    sock.send(encoded)


