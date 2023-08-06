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


from nepi.execution.resource import ResourceManager, clsinit_copy, \
        ResourceState
from nepi.execution.attribute import Attribute, Flags
from nepi.resources.planetlab.node import PlanetlabNode        
from nepi.resources.linux.application import LinuxApplication
import os

@clsinit_copy                    
class PlanetlabOVSSwitch(LinuxApplication):
    """
    .. class:: Class Args :
      
        :param ec: The Experiment controller
        :type ec: ExperimentController
        :param guid: guid of the RM
        :type guid: int

    """

    _rtype = "planetlab::OVSSwitch"
    _help = "Runs an OpenVSwitch on a PlanetLab host"
    _platform = "planetlab"

    _authorized_connections = ["planetlab::Node", "planetla::OVSPort", "linux::Node"]       

    @classmethod
    def _register_attributes(cls):
        """ Register the attributes of OVSSwitch RM 

        """
        bridge_name = Attribute("bridge_name", 
                "Name of the switch/bridge",
                flags = Flags.Design)	
        virtual_ip_pref = Attribute("virtual_ip_pref", 
                "Virtual IP/PREFIX of the switch",
                flags = Flags.Design)	
        controller_ip = Attribute("controller_ip", 
                "IP of the controller",
                flags = Flags.Design)	
        controller_port = Attribute("controller_port", 
                "Port of the controller",
                flags = Flags.Design)	

        cls._register_attribute(bridge_name)
        cls._register_attribute(virtual_ip_pref)
        cls._register_attribute(controller_ip)
        cls._register_attribute(controller_port)

    def __init__(self, ec, guid):
        """
        :param ec: The Experiment controller
        :type ec: ExperimentController
        :param guid: guid of the RM
        :type guid: int
    
        """
        super(PlanetlabOVSSwitch, self).__init__(ec, guid)
        self._home = "ovsswitch-%s" % self.guid
        self._node = None

    @property
    def node(self):
        """ Node wthat run the switch
        """
        if not self._node:
            nodes = self.get_connected(PlanetlabNode.get_rtype())
            if not nodes or len(nodes) != 1: 
                msg = "PlanetlabOVSSwitch must be connected to exactly one PlanetlabNode"
                #self.error(msg)
                raise RuntimeError, msg

            self._node = nodes[0]

        return self._node

    def valid_connection(self, guid):
        """ Check if the connection with the guid in parameter is possible. Only meaningful connections are allowed.

        :param guid: Guid of the current RM
        :type guid: int
        :rtype:  Boolean

        """
        rm = self.ec.get_resource(guid)
        if rm.get_rtype() not in self._authorized_connections:
            return False
        return True

    def do_provision(self):
        self.node.mkdir(self.run_home)

        self.check_sliver_ovs()
        self.servers_on()
        self.create_bridge()
        self.assign_controller()
        self.ovs_status()
        
        self.set_provisioned()
				
    def do_deploy(self):
        """ Deploy the OVS Switch : Turn on the server, create the bridges
            and assign the controller
        """

        if not self.node or self.node.state < ResourceState.READY:
            self.debug("---- RESCHEDULING DEPLOY ---- node state %s " % self.node.state)
            self.ec.schedule(self.reschedule_delay, self.deploy)
        else:
            self.do_discover()
            self.do_provision()
               
            self.set_ready()

    def check_sliver_ovs(self):  
        """ Check if sliver-ovs exists. If it does not exist, the execution is stopped
        """
        command = "compgen -c | grep sliver-ovs"			
        shfile = os.path.join(self.app_home, "check_ovs_cmd.sh")
        try:
            self.node.run_and_wait(command, self.run_home,
                    shfile=shfile,
                    sudo = True, 
                    pidfile="check_ovs_cmd_pidfile",
                    ecodefile="check_ovs_cmd_exitcode", 
                    stdout="check_ovs_cmd_stdout", 
                    stderr="check_ovs_cmd_stderr")
        except RuntimeError:
            msg = "Command sliver-ovs does not exist on the VM"    	 
            self.debug(msg)
            raise RuntimeError, msg

    def servers_on(self):
        """ Start the openvswitch servers and check it
        """
        # Make sure the server is not running        
        command = "sliver-ovs del-bridge %s; sliver-ovs stop" % self.get('bridge_name')
        shfile = os.path.join(self.app_home, "clean.sh")
        self.node.run_and_wait(command, self.run_home,
                shfile=shfile,
                sudo=True,
                raise_on_error=False,
                pidfile="clean_pidfile",
                ecodefile="clean_exitcode", 
                stdout="clean_stdout", 
                stderr="clean_stderr")

        # start the server        
        command = "sliver-ovs start"   		
        shfile = os.path.join(self.app_home, "start.sh")
        try:
            self.node.run_and_wait(command, self.run_home,
                    shfile=shfile,
                    sudo=True, 
                    pidfile="start_pidfile",
                    ecodefile="start_exitcode", 
                    stdout="start_stdout", 
                    stderr="start_stderr")
        except RuntimeError:
            msg = "Failed to start ovs-server on VM"    	 
            self.debug(msg)
            raise RuntimeError, msg

        command = "ps -A | grep ovsdb-server"
        shfile = os.path.join(self.app_home, "ovsdb_status.sh")
        try:
            self.node.run_and_wait(command, self.run_home,
                    shfile=shfile,
                    sudo=True, 
                    pidfile="ovsdb_status_pidfile",
                    ecodefile="ovsdb_status_exitcode", 
                    stdout="ovsdb_status_stdout", 
                    stderr="ovsdb_status_stderr")
        except RuntimeError:
            msg = "ovsdb-server not running on VM"    	 
            self.debug(msg)
            raise RuntimeError, msg
        
        self.info("Server OVS Started...")  

    def create_bridge(self):
        """ Create the bridge/switch and check error during SSH connection
        """
        # TODO: Check if previous bridge exist and delete them. Use ovs-vsctl list-br
        # TODO: Add check for virtual_ip belonging to vsys_tag
        if not (self.get("bridge_name") and self.get("virtual_ip_pref")):
            msg = "No assignment in one or both attributes"
            self.error(msg)
            raise AttributeError, msg

        command = "sliver-ovs create-bridge '%s' '%s'" % (
                          self.get("bridge_name"), 
                          self.get("virtual_ip_pref")) 
        
        shfile = os.path.join(self.app_home, "bridge_create.sh")
        try:
            self.node.run_and_wait(command, self.run_home,
                    shfile=shfile,
                    sudo=True, 
                    pidfile="bridge_create_pidfile",
                    ecodefile="bridge_create_exitcode", 
                    stdout="bridge_create_stdout", 
                    stderr="bridge_create_stderr")
        except RuntimeError:
            msg = "No such pltap netdev\novs-appctl: ovs-vswitchd: server returned an error"
            self.debug(msg)
            raise RuntimeError, msg

        self.info(" Bridge %s Created and Assigned to %s" %\
            (self.get("bridge_name"), self.get("virtual_ip_pref")) )

    def assign_controller(self):
        """ Set the controller IP
        """

        if not (self.get("controller_ip") and self.get("controller_port")):
            return 

        """
        if not (self.get("controller_ip") and self.get("controller_port")):
            msg = "No assignment in one or both attributes"
            self.error(msg)
            raise AttributeError, msg
        """
        command = "ovs-vsctl set-controller %s tcp:%s:%s" % \
                (self.get("bridge_name"), 
                        self.get("controller_ip"), 
                        self.get("controller_port"))
        
        shfile = os.path.join(self.app_home, "set_controller.sh")
        try:
            self.node.run_and_wait(command, self.run_home,
                    shfile=shfile,
                    sudo=True, 
                    pidfile="set_controller_pidfile",
                    ecodefile="set_controller_exitcode", 
                    stdout="set_controller_stdout", 
                    stderr="set_controller_stderr")
        except RuntimeError:
            msg = "SSH connection in the method assign_controller"
            self.debug(msg)
            raise RuntimeError, msg

        self.info("Controller assigned to the bridge %s" % self.get("bridge_name"))
	    
    def ovs_status(self):
        """ Print the status of the bridge				
        """
        command = "sliver-ovs show | tail -n +2"
        shfile = os.path.join(self.app_home, "ovs_status.sh")
        try:
            self.node.run_and_wait(command, self.run_home,
                    shfile=shfile,
                    sudo=True, 
                    pidfile="ovs_status_pidfile",
                    ecodefile="ovs_status_exitcode", 
                    stdout="ovs_status_stdout", 
                    stderr="ovs_status_stderr")
        except RuntimeError:
            msg = "Error when checking the status of the OpenVswitch"
            self.debug(msg)
            raise RuntimeError, msg

    def do_release(self):
        """ Delete the bridge and close the server.  

          .. note : It need to wait for the others RM (OVSPort and OVSTunnel)
        to be released before releasing itself

        """

        from nepi.resources.planetlab.openvswitch.ovsport import PlanetlabOVSPort
        rms = self.get_connected(PlanetlabOVSPort.get_rtype())

        for rm in rms:
            if rm.state < ResourceState.RELEASED:
                self.ec.schedule(self.reschedule_delay, self.release)
                return 
            
        msg = "Deleting the bridge %s" % self.get('bridge_name')
        self.info(msg)
        
        command = "sliver-ovs del-bridge %s; sliver-ovs stop" % self.get('bridge_name')
        shfile = os.path.join(self.app_home, "stop.sh")

        self.node.run_and_wait(command, self.run_home,
                shfile=shfile,
                sudo=True, 
                pidfile="stop_pidfile",
                ecodefile="stop_exitcode", 
                stdout="stop_stdout", 
                stderr="stop_stderr")

        super(PlanetlabOVSSwitch, self).do_release()

