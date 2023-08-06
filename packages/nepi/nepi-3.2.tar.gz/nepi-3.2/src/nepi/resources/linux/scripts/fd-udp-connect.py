import base64
import errno
import os
import passfd
import signal
import socket
import time
import tunchannel

from optparse import OptionParser

IFF_TUN     = 0x0001
IFF_TAP     = 0x0002

# Trak SIGTERM, and set global termination flag instead of dying
TERMINATE = []
STARTED = False

def _finalize(sig,frame):
    global TERMINATE
    global STARTED
    
    if STARTED:
        TERMINATE.append(None)
    else:
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        os.kill(os.getpid(), signal.SIGTERM)

signal.signal(signal.SIGTERM, _finalize)

# SIGUSR1 suspends forwading, SIGUSR2 resumes forwarding
SUSPEND = []
def _suspend(sig,frame):
    global SUSPEND
    if not SUSPEND:
        SUSPEND.append(None)
signal.signal(signal.SIGUSR1, _suspend)

def _resume(sig,frame):
    global SUSPEND
    if SUSPEND:
        SUSPEND.remove(None)
signal.signal(signal.SIGUSR2, _resume)

def get_options():
    usage = ("usage: %prog -a <address> -t <vif-type> -n "
            "-b <bwlimit> -c <cipher> -k <cipher-key> "
            "-q <txqueuelen> -p <local-port-file> -P <remote-port-file> "
            "-o <local-ip> -O <remote-ip> -r <ret-file> ")
    
    parser = OptionParser(usage = usage)

    parser.add_option("-a", "--address", dest="address",
        help="Socket address to send file descriptor to", type="str")
    parser.add_option("-t", "--vif-type", dest="vif_type",
        help="Virtual interface type. Either IFF_TAP or IFF_TUN. "
            "Defaults to IFF_TAP. ", default=IFF_TAP, type="str")
    parser.add_option("-n", "--pi", dest="pi", action="store_true", 
            default=False, help="Enable PI header")

    parser.add_option("-b", "--bwlimit", dest="bwlimit",
        help="Specifies the interface's emulated bandwidth in bytes ",
        default=None, type="int")
    parser.add_option("-q", "--txqueuelen", dest="txqueuelen",
        help="Specifies the interface's transmission queue length. ",
        default=1000, type="int")
    parser.add_option("-c", "--cipher", dest="cipher",
        help="Cipher to encript communication. "
            "One of PLAIN, AES, Blowfish, DES, DES3. ",
        default=None, type="str")
    parser.add_option("-k", "--cipher-key", dest="cipher_key",
        help="Specify a symmetric encryption key with which to protect "
            "packets across the tunnel. python-crypto must be installed "
            "on the system." ,
        default=None, type="str")

    parser.add_option("-p", "--local-port-file", dest="local_port_file",
        help = "File where to store the local binded UDP port number ", 
        default = "local_port_file", type="str")
    parser.add_option("-P", "--remote-port-file", dest="remote_port_file",
        help = "File where to read the remote UDP port number to connect to", 
        default = "remote_port_file", type="str")
    parser.add_option("-o", "--local-ip", dest="local_ip",
        help = "Local host IP", type="str")
    parser.add_option("-O", "--remote-ip", dest="remote_ip",
        help = "Remote host IP", type="str")
    parser.add_option("-R", "--ret-file", dest="ret_file",
        help = "File where to store return code (success of connection) ", 
        default = "ret_file", type="str")

    (options, args) = parser.parse_args()
            
    vif_type = IFF_TAP
    if options.vif_type and options.vif_type == "IFF_TUN":
        vif_type = IFF_TUN
  
    address = base64.b64decode(options.address)

    return (address,  vif_type, options.pi, 
            options.local_port_file, options.remote_port_file, 
            options.local_ip, options.remote_ip, options.ret_file, 
            options.bwlimit, options.cipher, options.cipher_key, 
            options.txqueuelen)

if __name__ == '__main__':

    (address, vif_type, pi, local_port_file, remote_port_file, 
            local_ip, remote_ip, ret_file, bwlimit, cipher, cipher_key, 
            txqueuelen) = get_options()

    # Create a local socket to stablish the tunnel connection
    rsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
    rsock.bind((local_ip, 0))
    (local_host, local_port) = rsock.getsockname()

    # Save local port information to file
    f = open(local_port_file, 'w')
    f.write("%d\n" % local_port)
    f.close()

    # Wait until remote port information is available
    while not os.path.exists(remote_port_file):
        time.sleep(2)

    remote_port = ''
    # Read remote port from file
    # Try until something is read...
    # xxx: There seems to be a weird behavior where
    #       even if the file exists and had the port number,
    #       the read operation returns empty string!
    #       Maybe a race condition?
    for i in xrange(10):
        f = open(remote_port_file, 'r')
        remote_port = f.read()
        f.close()

        if remote_port:
            break
        
        time.sleep(2)
    
    remote_port = remote_port.strip()
    remote_port = int(remote_port)

    # Connect local socket to remote port
    rsock.connect((remote_ip, remote_port))
    remote = os.fdopen(rsock.fileno(), 'r+b', 0)

    # create local socket to pass to fd-net-device, the other is for the tunnel
    fd, tun = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM, 0)

    # pass one end of the socket pair to the fd-net-device
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    sock.connect(address)
    passfd.sendfd(sock, fd, '0')

    # TODO: Test connectivity!    

    # Create a ret_file to indicate success
    f = open(ret_file, 'w')
    f.write("0")
    f.close()

    STARTED = True

    # Establish tunnel
    tunchannel.tun_fwd(tun, remote,
        with_pi = pi, 
        ether_mode = (vif_type == IFF_TAP),
        udp = True,
        cipher_key = cipher_key,
        cipher = cipher,
        TERMINATE = TERMINATE,
        SUSPEND = SUSPEND,
        tunqueue = txqueuelen,
        tunkqueue = 500,
        bwlimit = bwlimit
    ) 
 
