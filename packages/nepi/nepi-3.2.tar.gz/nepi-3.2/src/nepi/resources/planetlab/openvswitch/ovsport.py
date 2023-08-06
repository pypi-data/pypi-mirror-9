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
# Authors: Alina Quereilhac <alina.quereilhac@inria.fr>
#         Alexandros Kouvakas <alexandros.kouvakas@inria.fr>
#         Julien Tribino <julien.tribino@inria.fr>

from nepi.execution.attribute import Attribute, Flags, Types
from nepi.execution.resource import ResourceManager, clsinit_copy, \
        ResourceState
from nepi.resources.planetlab.openvswitch.ovs import PlanetlabOVSSwitch        
from nepi.resources.planetlab.node import PlanetlabNode        
from nepi.resources.linux.application import LinuxApplication

import os

@clsinit_copy                 
class PlanetlabOVSPort(LinuxApplication):
    """
    .. class:: Class Args :
      
        :param ec: The Experiment controller
        :type ec: ExperimentController
        :param guid: guid of the RM
        :type guid: int

    """
    
    _rtype = "planetlab::OVSPort"
    _help = "Runs an OpenVSwitch on a PlanetLab host"
    _platform = "planetlab"

    _authorized_connections = ["planetlab::OVSSwitch", "linux::UdpTunnel", "linux::Tunnel"]      

    @classmethod
    def _register_attributes(cls):
        """ Register the attributes of OVSPort RM 

        """
        port_name = Attribute("port_name", "Name of the port",
            flags = Flags.Design)			
        ip = Attribute("ip", "IP of the endpoint. This is the attribute " 
                                "you should use to establish a tunnel or a remote "
                                "connection between endpoint",
            flags = Flags.Design)
        network = Attribute("network", "Network used by the port",
            flags = Flags.Design)	

        cls._register_attribute(port_name)
        cls._register_attribute(ip)
        cls._register_attribute(network)

    def __init__(self, ec, guid):
        """
        :param ec: The Experiment controller
        :type ec: ExperimentController
        :param guid: guid of the RM
        :type guid: int
    
        """
        super(PlanetlabOVSPort, self).__init__(ec, guid)
        self._home = "ovsport-%s" % self.guid
        self._port_number = None

    @property
    def node(self):
        """ Node that run the switch and the ports
        """
        return self.ovsswitch.node

    @property
    def ovsswitch(self):
        """ Switch where the port is created
        """
        ovsswitch = self.get_connected(PlanetlabOVSSwitch.get_rtype())
        if ovsswitch: return ovsswitch[0]
        return None
        
    @property
    def port_number(self):
        return self._port_number

    def valid_connection(self, guid):
        """ Check if the connection is available.

        :param guid: Guid of the current RM
        :type guid: int
        :rtype:  Boolean

        """
        rm = self.ec.get_resource(guid)
        if rm.get_rtype() not in self._authorized_connections:
            return False

        return True

    def create_port(self):
        """ Create the desired port
        """
        msg = "Creating the port %s" % self.get('port_name')
        self.debug(msg)

        if not self.get('port_name'):
            msg = "The port name is not assigned"
            self.error(msg)
            raise AttributeError, msg

        if not self.ovsswitch:
            msg = "The OVSwitch RM is not running"
            self.error(msg)
            raise AttributeError, msg

        command = "sliver-ovs create-port %s %s" % (
                self.ovsswitch.get('bridge_name'),
                self.get('port_name'))   
        
        shfile = os.path.join(self.app_home, "create_port.sh")
        try:
            self.node.run_and_wait(command, self.run_home,
                    shfile=shfile,
                    sudo = True,
                    stderr="port_stdout", 
                    stdout="port_stderr",
                    pidfile="port_pidfile",
                    ecodefile="port_exitcode")
        except RuntimeError:
            msg = "Could not create ovs-port"    	 
            self.debug(msg)
            raise RuntimeError, msg

        self.info("Created port %s on switch %s" % (
            self.get('port_name'),
            self.ovsswitch.get('bridge_name')))     
	    
    def initiate_udp_connection(self, remote_endpoint, connection_app_home, 
            connection_run_home, cipher, cipher_key, bwlimit, txqueuelen):
        """ Get the local_endpoint of the port
        """
        msg = "Discovering the port number for %s" % self.get('port_name')
        self.info(msg)

        command = "sliver-ovs get-local-endpoint %s" % self.get('port_name')

        shfile = os.path.join(connection_app_home, "get_port.sh")
        (out, err), proc = self.node.run_and_wait(command, connection_run_home,
                shfile=shfile,
                sudo=True, 
                overwrite = True,
                pidfile="get_port_pidfile",
                ecodefile="get_port_exitcode", 
                stdout="get_port_stdout",    
                stderr="get_port_stderr")

        if err != "":
            msg = "Error retrieving the local endpoint of the port"
            self.error(msg)
            raise RuntimeError, msg

        if out:
            self._port_number = out.strip()

        self.info("The number of the %s is %s" % (self.get('port_name'), 
           self.port_number))

        # Must set a routing rule in the ovs client nodes so they know
        # that the LAN can be found through the switch
        if remote_endpoint.is_rm_instance("planetlab::Tap"):
            self._vroute = self.ec.register_resource("planetlab::Vroute")
            self.ec.set(self._vroute, "action", "add")
            self.ec.set(self._vroute, "prefix", remote_endpoint.get("prefix"))
            self.ec.set(self._vroute, "nexthop", remote_endpoint.get("pointopoint"))
            self.ec.set(self._vroute, "network", self.get("network"))

            self.ec.register_connection(self._vroute, remote_endpoint.guid)
            self.ec.deploy(guids=[self._vroute], group = self.deployment_group)

            # For debugging
            msg = "Route for the tap configured"
            self.debug(msg)

        return self.port_number

    def establish_udp_connection(self, remote_endpoint,
            connection_app_home,
            connection_run_home, 
            port):
        remote_ip = remote_endpoint.node.get("ip")
        command = self._establish_connection_command(port, remote_ip)

        shfile = os.path.join(connection_app_home, "connect_port.sh")
        (out, err), proc = self.node.run_and_wait(command, connection_run_home,
                shfile=shfile,
                sudo=True, 
                overwrite = True,
                pidfile="connect_port_pidfile",
                ecodefile="connect_port_exitcode", 
                stdout="connect_port_stdout",    
                stderr="connect_port_stderr")

        # For debugging
        msg = "Connection on port configured"
        self.debug(msg)

    def _establish_connection_command(self, port, remote_ip):
        """ Script to create the connection from a switch to a 
             remote endpoint
        """
        local_port_name = self.get('port_name')

        command = ["sliver-ovs"]
        command.append("set-remote-endpoint")
        command.append(local_port_name)
        command.append(remote_ip)
        command.append(port)
        command = " ".join(command)
        command = self.replace_paths(command)
        return command
       
    def verify_connection(self, remote_endpoint, connection_app_home, 
                connection_run_home):
        self.ovsswitch.ovs_status()

    def terminate_connection(self, endpoint, connection_app_home, 
                connection_run_home):
        return True

    def check_status(self):
        return self.node.status(self._pid, self._ppid)

    def do_provision(self):
        self.node.mkdir(self.run_home)

        self.create_port()
        end_ip = self.ovsswitch.get('virtual_ip_pref').split('/')
        self.set("ip", end_ip[0])

        #Check the status of the OVS Switch
        self.ovsswitch.ovs_status()
    
        self.set_provisioned()
		
    def do_deploy(self):
        """ Deploy the OVS port after the OVS Switch
        """
        if not self.ovsswitch or self.ovsswitch.state < ResourceState.READY:       
            self.debug("---- RESCHEDULING DEPLOY ---- OVSwitch state %s " % self.ovsswitch.state )  
            self.ec.schedule(self.reschedule_delay, self.deploy)
        else:
            self.do_discover()
            self.do_provision()

            self.set_ready()

    def do_release(self):
        """ Delete the port on the OVSwitch. It needs to wait for the tunnel
        to be released.
        """
        from nepi.resources.linux.udptunnel import LinuxUdpTunnel
        rm = self.get_connected(LinuxUdpTunnel.get_rtype())

        if rm and rm[0].state < ResourceState.STOPPED:
            self.ec.schedule(self.reschedule_delay, self.release)
            return 
            
        msg = "Deleting the port %s" % self.get('port_name')
        self.info(msg)

        command = "sliver-ovs del_port %s" % self.get('port_name')

        shfile = os.path.join(self.app_home, "stop.sh")
        self.node.run_and_wait(command, self.run_home,
                shfile=shfile,
                sudo=True, 
                pidfile="stop_pidfile",
                ecodefile="stop_exitcode", 
                stdout="stop_stdout", 
                stderr="stop_stderr")

        super(PlanetlabOVSPort, self).do_release()

