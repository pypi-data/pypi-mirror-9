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

from nepi.execution.attribute import Attribute, Flags, Types
from nepi.execution.resource import clsinit_copy, ResourceState
from nepi.resources.linux.udptunnel import LinuxUdpTunnel
from nepi.util.sshfuncs import ProcStatus
from nepi.util.timefuncs import tnow, tdiffsec

import base64
import os
import socket
import time

@clsinit_copy
class LinuxNs3FdUdpTunnel(LinuxUdpTunnel):
    _rtype = "linux::ns3::FdUdpTunnel"
    _help = "Constructs a tunnel between two Ns-3 FdNetdevices " \
            "located in remote Linux nodes using a UDP connection "
    _platform = "linux::ns3"

    @classmethod
    def _register_attributes(cls):
        cipher = Attribute("cipher",
               "Cipher to encript communication. "
                "One of PLAIN, AES, Blowfish, DES, DES3. ",
                default = None,
                allowed = ["PLAIN", "AES", "Blowfish", "DES", "DES3"],
                type = Types.Enumerate, 
                flags = Flags.Design)

        cipher_key = Attribute("cipherKey",
                "Specify a symmetric encryption key with which to protect "
                "packets across the tunnel. python-crypto must be installed "
                "on the system." ,
                flags = Flags.Design)

        txqueuelen = Attribute("txQueueLen",
                "Specifies the interface's transmission queue length. "
                "Defaults to 1000. ", 
                type = Types.Integer, 
                flags = Flags.Design)

        bwlimit = Attribute("bwLimit",
                "Specifies the interface's emulated bandwidth in bytes "
                "per second.",
                type = Types.Integer, 
                flags = Flags.Design)

        cls._register_attribute(cipher)
        cls._register_attribute(cipher_key)
        cls._register_attribute(txqueuelen)
        cls._register_attribute(bwlimit)

    def __init__(self, ec, guid):
        super(LinuxUdpTunnel, self).__init__(ec, guid)
        self._home = "fd-udp-tunnel-%s" % self.guid
        self._pids = dict()
        self._fd1 = None
        self._fd1node = None
        self._fd2 = None
        self._fd2node = None
        self._pi = False

    def log_message(self, msg):
        self.get_endpoints()
        return " guid %d - %s - %s - %s " % (self.guid, 
                self.node1.get("hostname"), 
                self.node2.get("hostname"), 
                msg)

    def get_endpoints(self):
        """ Returns the list of RM that are endpoints to the tunnel 
        """
        if not self._fd2 or not self._fd1:
            from nepi.resources.ns3.ns3fdnetdevice import NS3BaseFdNetDevice
            devices = self.get_connected(NS3BaseFdNetDevice.get_rtype())
            if not devices or len(devices) != 2: 
                msg = "linux::ns3::TunTapFdLink must be connected to exactly one FdNetDevice"
                self.error(msg)
                raise RuntimeError, msg

            self._fd1 = devices[0]
            self._fd2 = devices[1]
        
            simu = self._fd1.simulation
            from nepi.resources.linux.node import LinuxNode
            nodes = simu.get_connected(LinuxNode.get_rtype())
            self._fd1node = nodes[0]
     
            simu = self._fd2.simulation
            from nepi.resources.linux.node import LinuxNode
            nodes = simu.get_connected(LinuxNode.get_rtype())
            self._fd2node = nodes[0]

            if self._fd1node.get("hostname") == \
                    self._fd2node.get("hostname"):
                msg = "linux::ns3::FdUdpTunnel requires endpoints on different hosts"
                self.error(msg)
                raise RuntimeError, msg

        return [self._fd1, self._fd2]

    @property
    def pi(self):
        return self._pi

    @property
    def endpoint1(self):
        return self._fd1

    @property
    def endpoint2(self):
        return self._fd2

    @property
    def node1(self):
        return self._fd1node

    @property
    def node2(self):
        return self._fd2node

    def endpoint_node(self, endpoint):
        node = None
        if endpoint == self.endpoint1:
            node = self.node1
        else:
            node = self.node2

        return node
 
    def app_home(self, endpoint):
        node = self.endpoint_node(endpoint)
        return os.path.join(node.exp_home, self._home)

    def run_home(self, endpoint):
        return os.path.join(self.app_home(endpoint), self.ec.run_id)

    def upload_sources(self, endpoint):
        scripts = []

        # vif-passfd python script
        linux_passfd = os.path.join(os.path.dirname(__file__),
                "..",
                "scripts",
                "fd-udp-connect.py")

        scripts.append(linux_passfd)
       
        # tunnel creation python script
        tunchannel = os.path.join(os.path.dirname(__file__), 
                "..", 
                "scripts", 
                "tunchannel.py")

        scripts.append(tunchannel)

        # Upload scripts
        scripts = ";".join(scripts)

        node = self.endpoint_node(endpoint)
        node.upload(scripts,
                os.path.join(node.src_dir),
                overwrite = False)

    def endpoint_mkdir(self, endpoint):
        node = self.endpoint_node(endpoint) 
        run_home = self.run_home(endpoint)
        node.mkdir(run_home)

    def initiate_connection(self, endpoint, remote_endpoint):
        cipher = self.get("cipher")
        cipher_key = self.get("cipherKey")
        bwlimit = self.get("bwLimit")
        txqueuelen = self.get("txQueueLen")

        # Upload the tunnel creating script
        self.upload_sources(endpoint)

        # Request an address to send the file descriptor to the ns-3 simulation
        address = endpoint.recv_fd()

        # execute the tunnel creation script
        node = self.endpoint_node(remote_endpoint) 
        port = self.initiate(endpoint, remote_endpoint, address, cipher, 
                cipher_key, bwlimit, txqueuelen)

        return port

    def establish_connection(self, endpoint, remote_endpoint, port):
        self.establish(endpoint, remote_endpoint, port)

    def verify_connection(self, endpoint, remote_endpoint):
        self.verify(endpoint)

    def terminate_connection(self, endpoint, remote_endpoint):
        # Nothing to do
        return

    def check_state_connection(self):
        # Make sure the process is still running in background
        # No execution errors occurred. Make sure the background
        # process with the recorded pid is still running.

        node1 = self.endpoint_node(self.endpoint1) 
        node2 = self.endpoint_node(self.endpoint2) 
        run_home1 = self.run_home(self.endpoint1)
        run_home2 = self.run_home(self.endpoint1)
        (pid1, ppid1) = self._pids[endpoint1]
        (pid2, ppid2) = self._pids[endpoint2]
        
        status1 = node1.status(pid1, ppid1)
        status2 = node2.status(pid2, ppid2)

        if status1 == ProcStatus.FINISHED and \
                status2 == ProcStatus.FINISHED:

            # check if execution errors occurred
            (out1, err1), proc1 = node1.check_errors(run_home1)
            (out2, err2), proc2 = node2.check_errors(run_home2)

            if err1 or err2: 
                msg = "Error occurred in tunnel"
                self.error(msg, err1, err2)
                self.fail()
            else:
                self.set_stopped()

    def wait_local_port(self, endpoint):
        """ Waits until the local_port file for the endpoint is generated, 
        and returns the port number 
        
        """
        return self.wait_file(endpoint, "local_port")

    def wait_result(self, endpoint):
        """ Waits until the return code file for the endpoint is generated 
        
        """ 
        return self.wait_file(endpoint, "ret_file")
 
    def wait_file(self, endpoint, filename):
        """ Waits until file on endpoint is generated """
        result = None
        delay = 1.0
        
        node = self.endpoint_node(endpoint) 
        run_home = self.run_home(endpoint)

        for i in xrange(20):
            (out, err), proc = node.check_output(run_home, filename)

            if out:
                result = out.strip()
                break
            else:
                time.sleep(delay)
                delay = delay * 1.5
        else:
            msg = "Couldn't retrieve %s" % filename
            self.error(msg, out, err)
            raise RuntimeError, msg

        return result

    def initiate(self, endpoint, remote_endpoint, address, cipher, cipher_key, 
            bwlimit, txqueuelen):

        command = self._initiate_command(endpoint, remote_endpoint, 
                address, cipher, cipher_key, bwlimit, txqueuelen)

        node = self.endpoint_node(endpoint) 
        run_home = self.run_home(endpoint)
        app_home = self.app_home(endpoint)

        # upload command to connect.sh script
        shfile = os.path.join(app_home, "fd-udp-connect.sh")
        node.upload_command(command,
                shfile = shfile,
                overwrite = False)

        # invoke connect script
        cmd = "bash %s" % shfile
        (out, err), proc = node.run(cmd, run_home) 
             
        # check if execution errors occurred
        msg = "Failed to connect endpoints "
        
        if proc.poll():
            self.error(msg, out, err)
            raise RuntimeError, msg
    
        # Wait for pid file to be generated
        pid, ppid = node.wait_pid(run_home)

        self._pids[endpoint] = (pid, ppid)
        
        # Check for error information on the remote machine
        (out, err), proc = node.check_errors(run_home)
        # Out is what was written in the stderr file
        if err:
            msg = " Failed to start command '%s' " % command
            self.error(msg, out, err)
            raise RuntimeError, msg

        port = self.wait_local_port(endpoint)

        return port

    def _initiate_command(self, endpoint, remote_endpoint, address,
            cipher, cipher_key, bwlimit, txqueuelen):
        local_node = self.endpoint_node(endpoint) 
        local_run_home = self.run_home(endpoint)
        local_app_home = self.app_home(endpoint)
        remote_node = self.endpoint_node(remote_endpoint) 

        local_ip = local_node.get("ip")
        remote_ip = remote_node.get("ip")

        local_port_file = os.path.join(local_run_home, "local_port")
        remote_port_file = os.path.join(local_run_home,  "remote_port")
        ret_file = os.path.join(local_run_home, "ret_file")

        address = base64.b64encode(address)
        
        command = [""]
        command.append("PYTHONPATH=$PYTHONPATH:${SRC}")
        command.append("python ${SRC}/fd-udp-connect.py")
        command.append("-a %s" % address)
        command.append("-p %s" % local_port_file)
        command.append("-P %s" % remote_port_file)
        command.append("-o %s" % local_ip)
        command.append("-O %s" % remote_ip)
        command.append("-R %s" % ret_file)
        command.append("-t %s" % "IFF_TAP")
        if self.pi:
            command.append("-n")
        if cipher:
            command.append("-c %s" % cipher)
        if cipher_key:
            command.append("-k %s " % cipher_key)
        if txqueuelen:
            command.append("-q %s " % txqueuelen)
        if bwlimit:
            command.append("-b %s " % bwlimit)

        command = " ".join(command)
        command = self.replace_paths(command, node=local_node, 
                app_home=local_app_home, run_home=local_run_home)

        return command

    def establish(self, endpoint, remote_endpoint, port):
        node = self.endpoint_node(endpoint) 
        run_home = self.run_home(endpoint)

        # upload remote port number to file
        remote_port = "%s\n" % port
        node.upload(remote_port,
                os.path.join(run_home, "remote_port"),
                text = True, 
                overwrite = False)

    def verify(self, endpoint):
        self.wait_result(endpoint)

