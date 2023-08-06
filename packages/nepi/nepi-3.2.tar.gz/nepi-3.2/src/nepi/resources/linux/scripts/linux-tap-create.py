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
import fcntl
import errno
import passfd
import os
import socket
import subprocess
import struct
from optparse import OptionParser

STOP_MSG = "STOP"
PASSFD_MSG = "PASSFD"

IFF_NO_PI       = 0x1000
IFF_TUN         = 0x0001
IFF_TAP         = 0x0002
IFF_UP          = 0x1
IFF_RUNNING     = 0x40
TUNSETIFF       = 0x400454ca
SIOCGIFFLAGS    =  0x8913
SIOCSIFFLAGS    =  0x8914
SIOCGIFADDR     = 0x8915
SIOCSIFADDR     = 0x8916
SIOCGIFNETMASK  = 0x891B
SIOCSIFNETMASK  = 0x891C


def create_socket(socket_name):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(socket_name)
    return sock

def recv_msg(conn):
    msg = []
    chunk = ''

    while '\n' not in chunk:
        try:
            chunk = conn.recv(1024)
        except (OSError, socket.error), e:
            if e[0] != errno.EINTR:
                raise
            # Ignore eintr errors
            continue

        if chunk:
            msg.append(chunk)
        else:
            # empty chunk = EOF
            break

    msg = ''.join(msg).split('\n')[0]
    # The message might have arguments that will be appended
    # as a '|' separated list after the message type
    args = msg.split("|")
    msg = args.pop(0)

    dmsg = base64.b64decode(msg)
    dargs = []
    for arg in args:
        darg = base64.b64decode(arg)
        dargs.append(darg.rstrip())

    return (dmsg.rstrip(), dargs)

def send_reply(conn, reply):
    encoded = base64.b64encode(reply)
    conn.send("%s\n" % encoded)

def set_ifupdown(vif_name, up):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # get flags
    ifreq = struct.pack("16sH", vif_name, 0)
    ifr = fcntl.ioctl(sock.fileno(), SIOCGIFFLAGS, ifreq)

    if ifr < 0:
        os.close(sock)
        raise RuntimeError("Could not set device %s UP" % vif_name)

    name, flags = struct.unpack("16sH", ifr)
    if up:
        flags = flags | IFF_UP | IFF_RUNNING
    else:
        flags = flags & ~IFF_UP & ~IFF_RUNNING
    
    # set flags
    ifreq = struct.pack("16sH", vif_name, flags)
    ifr = fcntl.ioctl(sock.fileno(), SIOCSIFFLAGS, ifreq)

    if ifr < 0:
        os.close(sock)
        raise RuntimeError("Could not set device %s UP" % vif_name)

def set_ifaddr(vif_name, ip, prefix):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # configure IP
    ifreq = struct.pack("16sH2s4s8s", vif_name, socket.AF_INET, "\x00"*2, 
            socket.inet_aton(ip), "\x00"*8)
    ifr = fcntl.ioctl(sock.fileno(), SIOCSIFADDR, ifreq)

    if ifr < 0:
        os.close(sock)
        raise RuntimeError("Could not set IP address for device %s" % vif_name)

    netmask = socket.inet_ntoa(struct.pack(">I", (0xffffffff << (32 - prefix)) & 0xffffffff))
    ifreq = struct.pack("16sH2s4s8s", vif_name, socket.AF_INET, "\x00"*2,
            socket.inet_aton(netmask), "\x00"*8)
    ifr = fcntl.ioctl(sock.fileno(), SIOCSIFNETMASK, ifreq)

    if ifr < 0:
        os.close(sock)
        raise RuntimeError("Could not set IP mask for device %s" % vif_name)

def create_tap(vif_name, vif_type, pi):
    flags = 0
    flags |= vif_type
 
    if not pi:
        flags |= IFF_NO_PI
 
    fd = os.open("/dev/net/tun", os.O_RDWR)
 
    ifreq = struct.pack("16sH", vif_name, flags)
    ifr = fcntl.ioctl(fd, TUNSETIFF, ifreq)
    if ifr < 0:
        os.close(fd)
        raise RuntimeError("Could not configure device %s" % vif_name)

    return fd

def passfd_action(fd, args):
    """ Sends the file descriptor associated to the TAP device 
    to another process through a unix socket.
    """
    address = args.pop(0)
    print address
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    sock.connect(address)
    passfd.sendfd(sock, fd, '0')

    return "PASSFD-ACK"

def down_action(fd, vif_name):
    updown_action(fd, vif_name, False)
    return "STOP-ACK"

def get_options():
    usage = ("usage: %prog -t <vif-type> -a <ip-address> -n <prefix> "
        "-N <device-name> -p <pi> -S <socket-name>")
    
    parser = OptionParser(usage = usage)

    parser.add_option("-t", "--vif-type", dest="vif_type",
        help = "Virtual interface type. Either IFF_TAP or IFF_TUN. "
            "Defaults to IFF_TAP. ", type="str")

    parser.add_option("-a", "--ip-address", dest="ip_address",
        help = "IPv4 address to assign to interface.",
        type="str")

    parser.add_option("-n", "--prefix", dest="prefix",
        help = "IPv4 network prefix for the interface. ",
        type="int")

    parser.add_option("-N", "--vif-name", dest="vif_name",
        help="The name of the virtual interface", type="str")

    parser.add_option("-p", "--pi", dest="pi", action="store_true", 
            default=False, help="Enable PI header")

    parser.add_option("-S", "--socket-name", dest="socket_name",
        help = "Name for the unix socket used to interact with this process", 
        type="str")

    (options, args) = parser.parse_args()
    
    vif_type = IFF_TAP
    if options.vif_type and options.vif_type == "IFF_TUN":
        vif_type = IFF_TUN

    return (vif_type, options.vif_name, options.ip_address, options.prefix, 
            options.pi, options.socket_name)

if __name__ == '__main__':

    (vif_type, vif_name, ip_address, prefix, pi, socket_name) = get_options()

    # create and configure the virtual device 
    fd = create_tap(vif_name, vif_type, pi)
    set_ifaddr(vif_name, ip_address, prefix)
    set_ifupdown(vif_name, True)

    # create unix socket to receive instructions
    sock = create_socket(socket_name)
    sock.listen(0)

    # wait for messages to arrive and process them
    stop = False

    while not stop:
        conn, addr = sock.accept()
        conn.settimeout(5)

        while not stop:
            try:
                (msg, args) = recv_msg(conn)
            except socket.timeout, e:
                # Ingore time-out
                continue

            if not msg:
                # Ignore - connection lost
                break

            if msg == STOP_MSG:
                stop = True
                reply = stop_action(vif_name)
            elif msg == PASSFD_MSG:
                reply = passfd_action(fd, args)

            try:
                send_reply(conn, reply)
            except socket.error:
                break

