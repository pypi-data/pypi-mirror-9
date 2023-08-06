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
from nepi.resources.linux.application import LinuxApplication
from nepi.resources.linux.node import LinuxNode
from nepi.util.timefuncs import tnow, tdiffsec

import os
import time

PYTHON_VSYS_VERSION = "1.0"

@clsinit_copy
class LinuxTap(LinuxApplication):
    _rtype = "linux::Tap"
    _help = "Creates a TAP device on a Linux host"

    IFF_TUN = 0x0001
    IFF_TAP = 0x0002

    @classmethod
    def _register_attributes(cls):
        ip = Attribute("ip", "IPv4 Address",
              flags = Flags.Design)

        mac = Attribute("mac", "MAC Address",
                flags = Flags.Design)

        prefix = Attribute("prefix", "IPv4 network prefix",
                flags = Flags.Design)

        mtu = Attribute("mtu", "Maximum transmition unit for device",
                type = Types.Integer)

        devname = Attribute("deviceName", 
                "Name of the network interface (e.g. eth0, wlan0, etc)",
                flags = Flags.NoWrite)

        up = Attribute("up", "Link up", default=True,
                type = Types.Bool)
        
        pointopoint = Attribute("pointopoint", "Peer IP address", 
                flags = Flags.Design)

        txqueuelen = Attribute("txqueuelen", "Length of transmission queue", 
                flags = Flags.Design)

        txqueuelen = Attribute("txqueuelen", "Length of transmission queue", 
                flags = Flags.Design)

        gre_key = Attribute("greKey", 
                "GRE key to be used to configure GRE tunnel", 
                default = "1",
                flags = Flags.Design)

        gre_remote = Attribute("greRemote", 
                "Public IP of remote endpoint for GRE tunnel", 
                flags = Flags.Design)

        pi = Attribute("pi", "Add PI (protocol information) header", 
                default = False,
                type = Types.Bool)
 
        tear_down = Attribute("tearDown", 
                "Bash script to be executed before releasing the resource",
                flags = Flags.Design)

        cls._register_attribute(ip)
        cls._register_attribute(mac)
        cls._register_attribute(prefix)
        cls._register_attribute(mtu)
        cls._register_attribute(devname)
        cls._register_attribute(up)
        cls._register_attribute(pointopoint)
        cls._register_attribute(txqueuelen)
        cls._register_attribute(gre_key)
        cls._register_attribute(gre_remote)
        cls._register_attribute(pi)
        cls._register_attribute(tear_down)

    def __init__(self, ec, guid):
        super(LinuxTap, self).__init__(ec, guid)
        self._gre_enabled = None
        self._vif_prefix = "tap"
        self._vif_type = "IFF_TAP"
        self._vif_type_flag = LinuxTap.IFF_TAP
        self._home = "%s-%s" % (self.vif_prefix, self.guid)
 
    @property
    def node(self):
        node = self.get_connected(LinuxNode.get_rtype())
        if node: return node[0]
        raise RuntimeError, "linux::TAP/TUN devices must be connected to a linux::Node"

    @property
    def gre_enabled(self):
        if self._gre_enabled is None:
            from nepi.resources.linux.gretunnel import LinuxGRETunnel
            gre = self.get_connected(LinuxGRETunnel.get_rtype())
            if gre: self._gre_enabled = True

        return self._gre_enabled

    def upload_sources(self):
        scripts = []

        # udp-connect python script
        udp_connect = os.path.join(os.path.dirname(__file__), "scripts",
                "linux-udp-connect.py")
        
        scripts.append(udp_connect)

        tap_create = os.path.join(os.path.dirname(__file__), "scripts",
                "linux-tap-create.py")
        
        scripts.append(tap_create)

        tap_delete = os.path.join(os.path.dirname(__file__), "scripts",
                "linux-tap-delete.py")
        
        scripts.append(tap_delete)

        # tunnel creation python script
        tunchannel = os.path.join(os.path.dirname(__file__), "scripts", 
                "tunchannel.py")

        scripts.append(tunchannel)

        # Upload scripts
        scripts = ";".join(scripts)

        self.node.upload(scripts,
                os.path.join(self.node.src_dir),
                overwrite = False)

        # upload stop.sh script
        stop_command = self.replace_paths(self._stop_command)

        self.node.upload(stop_command,
                os.path.join(self.app_home, "stop.sh"),
                text = True,
                # Overwrite file every time. 
                # The stop.sh has the path to the socket, which should change
                # on every experiment run.
                overwrite = True)

    def upload_start_command(self):
        # If GRE mode is enabled, TAP creation is delayed until the
        # tunnel is established
        if not self.gre_enabled:
            # We want to make sure the device is up and running
            # before the deploy is over, so we execute the 
            # start script now and wait until it finishes. 
            command = self.get("command")
            command = self.replace_paths(command)

            shfile = os.path.join(self.app_home, "start.sh")
            self.node.run_and_wait(command, self.run_home,
                shfile = shfile,
                overwrite = True)

    def upload_start_command(self):
        # If GRE mode is enabled, TAP creation is delayed until the
        # tunnel is established
        if not self.gre_enabled:
            # Overwrite file every time. 
            # The start.sh has the path to the socket, wich should change
            # on every experiment run.
            command = self.get("command")
            
            self.info("Uploading command '%s'" % command)
            
            # replace application specific paths in the command
            command = self.replace_paths(command)
            
            # replace application specific paths in the environment
            env = self.get("env")
            env = env and self.replace_paths(env)

            shfile = os.path.join(self.app_home, "start.sh")

            self.node.upload_command(command, 
                    shfile = shfile,
                    env = env,
                    overwrite = True)

            # We want to make sure the device is up and running
            # before the deploy finishes, so we execute now the 
            # start script. We run it in background, because the 
            # TAP will live for as long as the process that 
            # created it is running, and wait until the TAP  
            # is created. 
            self._run_in_background()
            
    def do_deploy(self):
        if not self.node or self.node.state < ResourceState.PROVISIONED:
            self.ec.schedule(self.reschedule_delay, self.deploy)
        else:
            if self.gre_enabled:
                self._vif_prefix = "gre"
                self._home = "%s-%s" % (self.vif_prefix, self.guid)

            if not self.get("deviceName"):
                self.set("deviceName", "%s%d" % (self.vif_prefix, self.guid)) 

            if not self.get("command"):
                self.set("command", self._start_command)

            if not self.get("depends"):
                self.set("depends", self._dependencies)

            if not self.get("install"):
                self.set("install", self._install)

            self.do_discover()
            self.do_provision()

            self.set_ready()

    def do_start(self):
        if self.state == ResourceState.READY:
            command = self.get("command")
            self.info("Starting command '%s'" % command)

            self.set_started()
        else:
            msg = " Failed to execute command '%s'" % command
            self.error(msg, out, err)
            raise RuntimeError, msg

    def do_stop(self):
        command = self.get('command') or ''
        
        if self.state == ResourceState.STARTED:
            self.info("Stopping command '%s'" % command)

            command = "bash %s" % os.path.join(self.app_home, "stop.sh")
            (out, err), proc = self.execute_command(command,
                    blocking = True)

            if err:
                msg = " Failed to stop command '%s' " % command
                self.error(msg, out, err)

            self.set_stopped()

    @property
    def state(self):
        state_check_delay = 0.5
        if self._state == ResourceState.STARTED and \
                tdiffsec(tnow(), self._last_state_check) > state_check_delay:

            if self.get("deviceName"):
                (out, err), proc = self.node.execute("ifconfig")

                if out.strip().find(self.get("deviceName")) == -1: 
                    # tap is not running is not running (socket not found)
                    self.set_stopped()

            self._last_state_check = tnow()

        return self._state

    def do_release(self):
        # Node needs to wait until all associated RMs are released
        # to be released
        from nepi.resources.linux.tunnel import LinuxTunnel
        rms = self.get_connected(LinuxTunnel.get_rtype())

        for rm in rms:
            if rm.state < ResourceState.STOPPED:
                self.ec.schedule(self.reschedule_delay, self.release)
                return 

        super(LinuxTap, self).do_release()

    def gre_connect(self, remote_endpoint, connection_app_home,
            connection_run_home):
        gre_connect_command = self._gre_connect_command(remote_endpoint,
                connection_app_home, connection_run_home)

        # upload command to connect.sh script
        shfile = os.path.join(connection_app_home, "gre-connect.sh")
        self.node.upload_command(gre_connect_command,
                shfile = shfile,
                overwrite = False)

        # invoke connect script
        cmd = "bash %s" % shfile
        (out, err), proc = self.node.run(cmd, connection_run_home,
                pidfile = "gre_connect_pidfile",
                stdout = "gre_connect_stdout",
                stderr = "gre_connect_stderr", 
                )
             
        # check if execution errors occurred
        msg = " Failed to connect endpoints "
        
        if proc.poll() or err:
            self.error(msg, out, err)
            raise RuntimeError, msg
    
        # Wait for pid file to be generated
        pid, ppid = self.node.wait_pid(connection_run_home, 
                pidfile = "gre_connect_pidfile")
        
        # If the process is not running, check for error information
        # on the remote machine
        if not pid or not ppid:
            (out, err), proc = self.node.check_errors(connection_run_home,
                    stderr = "gre_connect_stderr") 

            # Out is what was written in the stderr file
            if err:
                msg = " Failed to start command '%s' " % command
                self.error(msg, out, err)
                raise RuntimeError, msg
        
        return True

    def initiate_udp_connection(self, remote_endpoint, connection_app_home, 
            connection_run_home, cipher, cipher_key, bwlimit, txqueuelen):
        port = self.udp_connect(remote_endpoint, connection_app_home, 
            connection_run_home, cipher, cipher_key, bwlimit, txqueuelen)
        return port

    def udp_connect(self, remote_endpoint, connection_app_home, 
            connection_run_home, cipher, cipher_key, bwlimit, txqueuelen):
        udp_connect_command = self._udp_connect_command(
                remote_endpoint, connection_app_home, connection_run_home,
                cipher, cipher_key, bwlimit, txqueuelen)

        # upload command to connect.sh script
        shfile = os.path.join(connection_app_home, "udp-connect.sh")
        self.node.upload_command(udp_connect_command,
                shfile = shfile,
                overwrite = False)

        # invoke connect script
        cmd = "bash %s" % shfile
        (out, err), proc = self.node.run(cmd, connection_run_home,
               pidfile = "udp_connect_pidfile",
               stdout = "udp_connect_stdout",
               stderr = "udp_connect_stderr", 
                ) 
             
        # check if execution errors occurred
        msg = "Failed to connect endpoints "
        
        if proc.poll():
            self.error(msg, out, err)
            raise RuntimeError, msg
    
        # Wait for pid file to be generated
        self._pid, self._ppid = self.node.wait_pid(
                connection_run_home,
                pidfile = "udp_connect_pidfile")
        
        # If the process is not running, check for error information
        # on the remote machine
        if not self._pid or not self._ppid:
            (out, err), proc = self.node.check_errors(
                    connection_run_home,
                    stderr = "udp_connect_stderr")

            # Out is what was written in the stderr file
            if err:
                msg = " Failed to start command '%s' " % command
                self.error(msg, out, err)
                raise RuntimeError, msg

        return self.wait_file(connection_run_home, "local_port")

    def establish_udp_connection(self, remote_endpoint,
            connection_app_home, connection_run_home, port):
        # upload remote port number to file
        rem_port = "%s\n" % port
        self.node.upload(rem_port,
                os.path.join(connection_run_home, "remote_port"),
                text = True, 
                overwrite = False)

    def verify_connection(self, remote_endpoint,
            connection_app_home, connection_run_home):

        return self.wait_file(connection_run_home, "ret_file")

    def terminate_connection(self, remote_endpoint,
            connection_app_home, connection_run_home):
        if  self._pid and self._ppid:
            (out, err), proc = self.node.kill(self._pid, self._ppid, 
                    sudo = True) 

            # check if execution errors occurred
            if proc.poll() and err:
                msg = " Failed to Kill the Tap"
                self.error(msg, out, err)
                raise RuntimeError, msg

    def check_status(self):
        return self.node.status(self._pid, self._ppid)

    def wait_file(self, home, filename):
        """ Waits until file on endpoint is generated """
        result = None
        delay = 1.0

        for i in xrange(20):
            (out, err), proc = self.node.check_output(home, filename)
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

    @property
    def _start_command(self):
        if self.gre_enabled:
            command = []
        else:
            command = ["sudo -S "]
            command.append("PYTHONPATH=$PYTHONPATH:${SRC}")
            command.append("python ${SRC}/linux-tap-create.py")
            command.append("-t %s" % self.vif_type)
            command.append("-a %s" % self.get("ip"))
            command.append("-n %s" % self.get("prefix"))
            command.append("-N %s " % self.get("deviceName"))
            command.append("-S %s " % self.sock_name)
            if self.get("pi"):
                command.append("-p")

        return " ".join(command)

    @property
    def _stop_command(self):
        if self.gre_enabled:
            command = self._stop_gre_command
        else:
            command = ["sudo -S "]
            command.append("PYTHONPATH=$PYTHONPATH:${SRC}")
            command.append("python ${SRC}/linux-tap-delete.py")
            command.append("-N %s " % self.get("deviceName"))
            command.append("-S %s " % self.sock_name)
            command = " ".join(command)

        return command

    def _gre_connect_command(self, remote_endpoint, 
            connection_app_home, connecrion_app_home):
        # Set the remote endpoint to (private) device IP
        self.set("pointopoint", remote_endpoint.get("ip"))
        ## public node IP
        self.set("greRemote", remote_endpoint.node.get("ip"))

        # Generate GRE connect command
        command = ["("]
        command.append(self._stop_gre_command)
        command.append(") ; (")
        command.append(self._start_gre_command)
        command.append(")")

        command = " ".join(command)
        command = self.replace_paths(command)

        return command

    @property
    def _start_gre_command(self):
        command = []
        command.append("sudo -S modprobe ip_gre")
        command.append("sudo -S ip tunnel add %s mode gre remote %s local %s ttl 255 csum key %s" % (
                self.get("deviceName"),
                self.get("greRemote"),
                self.node.get("ip"),
                self.get("greKey")
            ))
        command.append("sudo -S ip addr add %s/%s peer %s/%s dev %s" % (
                self.get("ip"),
                self.get("prefix"),
                self.get("pointopoint"),
                self.get("prefix"),
                self.get("deviceName"),
                ))
        command.append("sudo -S ip link set %s up " % self.get("deviceName"))

        return ";".join(command)

    @property
    def _stop_gre_command(self):
        command = []
        command.append("sudo -S modprobe -r ip_gre")
        command.append("sudo -S ip link set down dev %s" % (
                self.get("deviceName"),
            ))
        command.append("sudo -S ip link del dev %s" % (
                self.get("deviceName"),
                ))

        return ";".join(command)

    def _udp_connect_command(self, remote_endpoint, 
            connection_app_home, connection_run_home,
            cipher, cipher_key, bwlimit, txqueuelen):

        # Set the remote endpoint to the IP of the device
        self.set("pointopoint", remote_endpoint.get("ip"))
        
        # Public IP of the remote NODE to stablish tunnel
        remote_ip = remote_endpoint.node.get("ip")
        local_ip = self.node.get("ip")

        local_port_file = os.path.join(connection_run_home, 
                "local_port")

        remote_port_file = os.path.join(connection_run_home, 
                "remote_port")

        ret_file = os.path.join(connection_run_home, 
                "ret_file")

        # Generate UDP connect command
        # Use the start command to configure TAP with peer info
        start_command = self._start_command
        
        command = [""]
        # Use pl-vid-udp-connect.py to stablish the tunnel between endpoints
        command.append("sudo -S")
        command.append("PYTHONPATH=$PYTHONPATH:${SRC}")
        command.append("python ${SRC}/linux-udp-connect.py")
        command.append("-t %s" % self.vif_type)
        command.append("-S %s " % self.sock_name)
        command.append("-p %s " % local_port_file)
        command.append("-P %s " % remote_port_file)
        command.append("-o %s " % local_ip)
        command.append("-O %s " % remote_ip)
        command.append("-R %s " % ret_file)
        if self.get("pi"):
            command.append("-n")
        if cipher:
            command.append("-c %s " % cipher)
        if cipher_key:
            command.append("-k %s " % cipher_key)
        if txqueuelen:
            command.append("-q %s " % txqueuelen)
        if bwlimit:
            command.append("-b %s " % bwlimit)

        command = " ".join(command)
        command = self.replace_paths(command)

        return command
    
    @property
    def _dependencies(self):
        return "mercurial make gcc"

    @property
    def _install(self):
        # Install python-vsys and python-passfd
        install_passfd = ( " ( python -c 'import passfd' ) "
                    " || "
                    " ( "
                    "   cd ${SRC} ; "
                    "   hg clone http://nepi.inria.fr/code/python-passfd ; "
                    "   cd python-passfd ; "
                    "   make all ; "
                    "   sudo -S make install "
                    " )" )

        return install_passfd

    def valid_connection(self, guid):
        # TODO: Validate!
        return True

    @property
    def vif_type(self):
        return self._vif_type

    @property
    def vif_type_flag(self):
        return self._vif_type_flag
 
    @property
    def vif_prefix(self):
        return self._vif_prefix

    @property
    def sock_name(self):
        return os.path.join(self.run_home, "%s.sock" % self.vif_prefix)

    def valid_connection(self, guid):
        # TODO: Validate!
        return True

