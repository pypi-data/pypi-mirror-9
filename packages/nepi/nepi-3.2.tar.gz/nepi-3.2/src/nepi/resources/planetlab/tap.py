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
from nepi.resources.linux.tap import LinuxTap
from nepi.resources.planetlab.node import PlanetlabNode
from nepi.util.timefuncs import tnow, tdiffsec

import os
import time

PYTHON_VSYS_VERSION = "1.0"

@clsinit_copy
class PlanetlabTap(LinuxTap):
    _rtype = "planetlab::Tap"
    _help = "Creates a TAP device on a PlanetLab host"
    _platform = "planetlab"

    @classmethod
    def _register_attributes(cls):
        snat = Attribute("snat", "Set SNAT=1", 
                type = Types.Bool,
                flags = Flags.Design)
        
        cls._register_attribute(snat)

    def __init__(self, ec, guid):
        super(PlanetlabTap, self).__init__(ec, guid)
        self._home = "tap-%s" % self.guid
        self._gre_enabled = False

    @property
    def node(self):
        node = self.get_connected(PlanetlabNode.get_rtype())
        if node: return node[0]
        raise RuntimeError, "TAP/TUN devices must be connected to Node"

    def upload_sources(self):
        scripts = []

        # vif-creation python script
        pl_vif_create = os.path.join(os.path.dirname(__file__), "scripts",
                "pl-vif-create.py")

        scripts.append(pl_vif_create)
        
        # vif-up python script
        pl_vif_up = os.path.join(os.path.dirname(__file__), "scripts",
                "pl-vif-up.py")
        
        scripts.append(pl_vif_up)

        # vif-down python script
        pl_vif_down = os.path.join(os.path.dirname(__file__), "scripts",
                "pl-vif-down.py")
        
        scripts.append(pl_vif_down)

        # udp-connect python script
        udp_connect = os.path.join(os.path.dirname(__file__), 
                "..",
                "linux",
                "scripts",
                "linux-udp-connect.py")
        
        scripts.append(udp_connect)

        # tunnel creation python script
        tunchannel = os.path.join(os.path.dirname(__file__), 
                "..", 
                "linux",
                "scripts", 
                "tunchannel.py")

        scripts.append(tunchannel)

        # Upload scripts
        scripts = ";".join(scripts)

        self.node.upload(scripts,
                os.path.join(self.node.src_dir),
                overwrite = False)

        # upload stop.sh script
        stop_command = self.replace_paths(self._stop_command)

        self.node.upload_command(stop_command,
                shfile = os.path.join(self.app_home, "stop.sh"),
                # Overwrite file every time. 
                # The stop.sh has the path to the socket, which should change
                # on every experiment run.
                overwrite = True)

    def upload_start_command(self):
        super(PlanetlabTap, self).upload_start_command()

        # Planetlab TAPs always add a PI header
        self.set("pi", True)

        if not self.gre_enabled:
            # After creating the TAP, the pl-vif-create.py script
            # will write the name of the TAP to a file. We wait until
            # we can read the interface name from the file.
            vif_name = self.wait_vif_name()
            self.set("deviceName", vif_name) 

    def wait_vif_name(self, exec_run_home = None):
        """ Waits until the vif_name file for the command is generated, 
            and returns the vif_name for the device """
        vif_name = None
        delay = 0.5

        # The vif_name file will be created in the tap-home, while the
        # current execution home might be elsewhere to check for errors
        # (e.g. could be a tunnel-home)
        if not exec_run_home:
            exec_run_home = self.run_home

        for i in xrange(20):
            (out, err), proc = self.node.check_output(self.run_home, "vif_name")

            if proc.poll() > 0:
                (out, err), proc = self.node.check_errors(exec_run_home)
                
                if err.strip():
                    raise RuntimeError, err

            if out:
                vif_name = out.strip()
                break
            else:
                time.sleep(delay)
                delay = delay * 1.5
        else:
            msg = "Couldn't retrieve vif_name"
            self.error(msg, out, err)
            raise RuntimeError, msg

        return vif_name

    def gre_connect(self, remote_endpoint, connection_app_home,
            connection_run_home):
        super(PlanetlabTap, self).gre_connect(remote_endpoint, 
                connection_app_home, connection_run_home)
         # After creating the TAP, the pl-vif-create.py script
        # will write the name of the TAP to a file. We wait until
        # we can read the interface name from the file.
        vif_name = self.wait_vif_name(exec_run_home = connection_run_home)
        self.set("deviceName", vif_name) 

        return True

    def _gre_connect_command(self, remote_endpoint, connection_app_home, 
            connection_run_home): 
        # Set the remote endpoint, (private) IP of the device
        self.set("pointopoint", remote_endpoint.get("ip"))
        # Public IP of the node
        self.set("greRemote", remote_endpoint.node.get("ip"))

        # Generate GRE connect command

        # Use vif_down command to first kill existing TAP in GRE mode
        vif_down_command = self._vif_down_command

        # Use pl-vif-up.py script to configure TAP with peer info
        vif_up_command = self._vif_up_command
        
        command = ["("]
        command.append(vif_down_command)
        command.append(") ; (")
        command.append(vif_up_command)
        command.append(")")

        command = " ".join(command)
        command = self.replace_paths(command)

        return command

    @property
    def _start_command(self):
        if self.gre_enabled:
            command = []
        else:
            command = ["sudo -S python ${SRC}/pl-vif-create.py"]
            
            command.append("-t %s" % self.vif_type)
            command.append("-a %s" % self.get("ip"))
            command.append("-n %s" % self.get("prefix"))
            command.append("-f %s " % self.vif_name_file)
            command.append("-S %s " % self.sock_name)

            if self.get("snat") == True:
                command.append("-s")

            if self.get("pointopoint"):
                command.append("-p %s" % self.get("pointopoint"))
            
            if self.get("txqueuelen"):
                command.append("-q %s" % self.get("txqueuelen"))

        return " ".join(command)

    @property
    def _stop_command(self):
        if self.gre_enabled:
            command = self._vif_down_command
        else:
            command = ["sudo -S "]
            command.append("PYTHONPATH=$PYTHONPATH:${SRC}")
            command.append("python ${SRC}/pl-vif-down.py")
            command.append("-S %s " % self.sock_name)
            command = " ".join(command)

        return command

    @property
    def _vif_up_command(self):
        if self.gre_enabled:
            device_name = "%s" % self.guid
        else:
            device_name = self.get("deviceName")

        # Use pl-vif-up.py script to configure TAP
        command = ["sudo -S "]
        command.append("PYTHONPATH=$PYTHONPATH:${SRC}")
        command.append("python ${SRC}/pl-vif-up.py")
        command.append("-u %s" % self.node.get("username"))
        command.append("-N %s" % device_name)
        command.append("-t %s" % self.vif_type)
        command.append("-a %s" % self.get("ip"))
        command.append("-n %s" % self.get("prefix"))

        if self.get("snat") == True:
            command.append("-s")

        if self.get("pointopoint"):
            command.append("-p %s" % self.get("pointopoint"))
        
        if self.get("txqueuelen"):
            command.append("-q %s" % self.get("txqueuelen"))

        if self.gre_enabled:
            command.append("-g %s" % self.get("greKey"))
            command.append("-G %s" % self.get("greRemote"))
        
        command.append("-f %s " % self.vif_name_file)

        return " ".join(command)

    @property
    def _vif_down_command(self):
        if self.gre_enabled:
            device_name = "%s" % self.guid
        else:
            device_name = self.get("deviceName")

        command = ["sudo -S "]
        command.append("PYTHONPATH=$PYTHONPATH:${SRC}")
        command.append("python ${SRC}/pl-vif-down.py")
        command.append("-N %s " % device_name)
        
        if self.gre_enabled:
            command.append("-u %s" % self.node.get("username"))
            command.append("-t %s" % self.vif_type)
            command.append("-D")

        return " ".join(command)

    @property
    def vif_name_file(self):
        return os.path.join(self.run_home, "vif_name")

    @property
    def _install(self):
        # Install python-vsys and python-passfd
        install_vsys = ( " ( "
                    "   python -c 'import vsys, os;  vsys.__version__ == \"%(version)s\" or os._exit(1)' "
                    " ) "
                    " || "
                    " ( "
                    "   cd ${SRC} ; "
                    "   hg clone http://nepi.inria.fr/code/python-vsys ; "
                    "   cd python-vsys ; "
                    "   make all ; "
                    "   sudo -S make install "
                    " )" ) % ({
                        "version": PYTHON_VSYS_VERSION
                        })

        install_passfd = ( " ( python -c 'import passfd' ) "
                    " || "
                    " ( "
                    "   cd ${SRC} ; "
                    "   hg clone http://nepi.inria.fr/code/python-passfd ; "
                    "   cd python-passfd ; "
                    "   make all ; "
                    "   sudo -S make install "
                    " )" )

        return "%s ; %s" % ( install_vsys, install_passfd )

    def valid_connection(self, guid):
        # TODO: Validate!
        return True

