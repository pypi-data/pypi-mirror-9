#
#    NEPI, a framework to manage network experiments
#    Copyright (C) 2014 INRIA
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
from nepi.execution.trace import Trace, TraceAttr
from nepi.execution.resource import ResourceManager, clsinit_copy, \
        ResourceState
from nepi.resources.linux.application import LinuxApplication
from nepi.util.timefuncs import tnow, tdiffsec
from nepi.resources.netns.netnsemulation import NetNSEmulation
from nepi.resources.linux.netns.netnsclient import LinuxNetNSClient

import os
import time
import threading

@clsinit_copy
class LinuxNetNSEmulation(LinuxApplication, NetNSEmulation):
    _rtype = "linux::netns::Emulation"

    @classmethod
    def _register_attributes(cls):
        verbose = Attribute("verbose",
            "True to output debugging info for the client-server communication",
            type = Types.Bool,
            flags = Flags.Design)

        enable_dump = Attribute("enableDump",
            "Enable dumping the remote executed commands to a script "
            "in order to later reproduce and debug the experiment",
            type = Types.Bool,
            default = False,
            flags = Flags.Design)

        version = Attribute("version",
            "Version of netns to install from nsam repo",
            default = "netns-dev", 
            flags = Flags.Design)

        cls._register_attribute(enable_dump)
        cls._register_attribute(verbose)
        cls._register_attribute(version)

    def __init__(self, ec, guid):
        LinuxApplication.__init__(self, ec, guid)
        NetNSEmulation.__init__(self)

        self._client = None
        self._home = "netns-emu-%s" % self.guid
        self._socket_name = "netns-%s.sock" % os.urandom(4).encode('hex')

    @property
    def socket_name(self):
        return self._socket_name

    @property
    def remote_socket(self):
        return os.path.join(self.run_home, self.socket_name)

    def upload_sources(self):
        self.node.mkdir(os.path.join(self.node.src_dir, "netnswrapper"))

        # upload wrapper python script
        wrapper = os.path.join(os.path.dirname(__file__), "..", "..", "netns", 
                "netnswrapper.py")

        self.node.upload(wrapper,
                os.path.join(self.node.src_dir, "netnswrapper", "netnswrapper.py"),
                overwrite = False)

        # upload wrapper debug python script
        wrapper_debug = os.path.join(os.path.dirname(__file__), "..", "..", "netns", 
                "netnswrapper_debug.py")

        self.node.upload(wrapper_debug,
                os.path.join(self.node.src_dir, "netnswrapper", "netnswrapper_debug.py"),
                overwrite = False)

        # upload server python script
        server = os.path.join(os.path.dirname(__file__), "..", "..", "netns",
                "netnsserver.py")

        self.node.upload(server,
                os.path.join(self.node.src_dir, "netnswrapper", "netnsserver.py"),
                overwrite = False)

        # Upload user defined sources
        self.node.mkdir(os.path.join(self.node.src_dir, "netns"))
        src_dir = os.path.join(self.node.src_dir, "netns")

        super(LinuxNetNSEmulation, self).upload_sources(src_dir = src_dir)
    
    def upload_extra_sources(self, sources = None, src_dir = None):
        return super(LinuxNetNSEmulation, self).upload_sources(
                sources = sources, 
                src_dir = src_dir)

    def upload_start_command(self):
        command = self.get("command")
        env = self.get("env")

        # We want to make sure the emulator is running
        # before the experiment starts.
        # Run the command as a bash script in background,
        # in the host ( but wait until the command has
        # finished to continue )
        env = self.replace_paths(env)
        command = self.replace_paths(command)

        shfile = os.path.join(self.app_home, "start.sh")
        self.node.upload_command(command, 
                    shfile = shfile,
                    env = env,
                    overwrite = True)

        # Run the wrapper 
        self._run_in_background()

        # Wait until the remote socket is created
        self.wait_remote_socket()

    def do_deploy(self):
        if not self.node or self.node.state < ResourceState.READY:
            self.debug("---- RESCHEDULING DEPLOY ---- node state %s " % self.node.state )
            
            # ccnd needs to wait until node is deployed and running
            self.ec.schedule(self.reschedule_delay, self.deploy)
        else:
            if not self.get("command"):
                self.set("command", self._start_command)
            
            if not self.get("depends"):
                self.set("depends", self._dependencies)

            if self.get("sources"):
                sources = self.get("sources")
                source = sources.split(" ")[0]
                basename = os.path.basename(source)
                version = ( basename.strip().replace(".tar.gz", "")
                    .replace(".tar","")
                    .replace(".gz","")
                    .replace(".zip","") )

                self.set("version", version)
                self.set("sources", source)

            if not self.get("build"):
                self.set("build", self._build)

            if not self.get("env"):
                self.set("env", self._environment)

            self.do_discover()
            self.do_provision()

            # Create client
            self._client = LinuxNetNSClient(self)

            self.set_ready()

    def do_start(self):
        """ Starts  execution execution

        """
        self.info("Starting")

        if self.state == ResourceState.READY:
            self.set_started()
        else:
            msg = " Failed to execute command '%s'" % command
            self.error(msg, out, err)
            raise RuntimeError, msg

    def do_stop(self):
        """ Stops simulation execution

        """
        if self.state == ResourceState.STARTED:
            self.set_stopped()

    def do_release(self):
        self.info("Releasing resource")

        tear_down = self.get("tearDown")
        if tear_down:
            self.node.execute(tear_down)

        self.do_stop()
        self._client.shutdown()
        LinuxApplication.do_stop(self)
        
        super(LinuxApplication, self).do_release()

    @property
    def _start_command(self):
        command = [] 

        #command.append("sudo")
        command.append("PYTHONPATH=$PYTHONPATH:${SRC}/netnswrapper/")
        command.append("python ${SRC}/netnswrapper/netnsserver.py -S %s" % \
                os.path.basename(self.remote_socket) )

        if self.get("enableDump"):
            command.append("-D")

        if self.get("verbose"):
            command.append("-v")

        command = " ".join(command)
        return command

    @property
    def _dependencies(self):
        if self.node.use_rpm:
            return (" python python-devel mercurial unzip bridge-utils iproute")
        elif self.node.use_deb:
            return (" python python-dev mercurial unzip bridge-utils iproute")
        return ""

    @property
    def netns_repo(self):
        return "http://nepi.inria.fr/code/netns"

    @property
    def netns_version(self):
        version = self.get("version")
        return version or "dev"

    @property
    def python_unshare_repo(self):
        return "http://nepi.inria.fr/code/python-unshare"

    @property
    def python_unshare_version(self):
        return "dev"

    @property
    def python_passfd_repo(self):
        return "http://nepi.inria.fr/code/python-passfd"

    @property
    def python_passfd_version(self):
        return "dev"

    @property
    def netns_src(self):
        location = "${SRC}/netns/%(version)s" \
                    % {
                        "version": self.netns_version,
                      }

        return location

    @property
    def python_unshare_src(self):
        location = "${SRC}/python_unshare/%(version)s" \
                    % {
                        "version": self.python_unshare_version,
                      }

        return location

    @property
    def python_passfd_src(self):
        location = "${SRC}/python_passfd/%(version)s" \
                    % {
                        "version": self.python_passfd_version,
                      }

        return location

    def clone_command(self, name, repo, src):
        clone_cmd = (
                # Test if alredy cloned
                " ( "
                "  ( "
                "    ( test -d %(src)s ) "
                "   && echo '%(name)s binaries found, nothing to do'"
                "  ) "
                " ) "
                "  || " 
                # clone source code
                " ( "
                "   mkdir -p %(src)s && "
                "   hg clone %(repo)s %(src)s"
                " ) "
             ) % {
                    "repo": repo,
                    "src": src,
                    "name": name,
                 }

        return clone_cmd

    @property
    def _build(self):
        netns_clone = self.clone_command("netns", self.netns_repo, 
                self.netns_src)
        python_unshare_clone = self.clone_command("python_unshare", 
                self.python_unshare_repo, self.python_unshare_src)
        python_passfd_clone = self.clone_command("python_passfd", 
                self.python_passfd_repo, self.python_passfd_src)

        build_cmd = (
                # Netns installation
                "( %(netns_clone)s )"
                "  && "
                "( %(python_unshare_clone)s )"
                "  && "
                "( %(python_passfd_clone)s )"
             ) % { 
                    "netns_clone": netns_clone,
                    "python_unshare_clone": python_unshare_clone,  
                    "python_passfd_clone": python_passfd_clone,  
                 }

        return build_cmd

    @property
    def _environment(self):
        env = []
        env.append("PYTHONPATH=$PYTHONPAH:%(netns_src)s/src/:%(python_unshare_src)s/src:%(python_passfd_src)s/src}" % { 
                    "netns_src": self.netns_src,
                    "python_unshare_src": self.python_unshare_src,
                    "python_passfd_src": self.python_passfd_src,
                 })

        return " ".join(env) 

    def replace_paths(self, command):
        """
        Replace all special path tags with shell-escaped actual paths.
        """
        return ( command
            .replace("${USR}", self.node.usr_dir)
            .replace("${LIB}", self.node.lib_dir)
            .replace("${BIN}", self.node.bin_dir)
            .replace("${SRC}", self.node.src_dir)
            .replace("${SHARE}", self.node.share_dir)
            .replace("${EXP}", self.node.exp_dir)
            .replace("${EXP_HOME}", self.node.exp_home)
            .replace("${APP_HOME}", self.app_home)
            .replace("${RUN_HOME}", self.run_home)
            .replace("${NODE_HOME}", self.node.node_home)
            .replace("${HOME}", self.node.home_dir)
            )

    def valid_connection(self, guid):
        # TODO: Validate!
        return True

    def wait_remote_socket(self):
        """ Waits until the remote socket is created
        """
        command = " [ -e %s ] && echo 'DONE' " % self.remote_socket

        for i in xrange(200):
            (out, err), proc = self.node.execute(command, retry = 1, 
                    with_lock = True)

            if out.find("DONE") > -1:
                break
        else:
            raise RuntimeError("Remote socket not found at %s" % \
                    self.remote_socket)
    

