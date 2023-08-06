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
from nepi.execution.resource import (ResourceManager, clsinit_copy, 
                                     ResourceState)
from nepi.resources.linux import rpmfuncs, debfuncs 
from nepi.util import sshfuncs, execfuncs
from nepi.util.sshfuncs import ProcStatus

import collections
import os
import random
import re
import tempfile
import time
import threading
import traceback

# TODO: Unify delays!!
# TODO: Validate outcome of uploads!! 

class ExitCode:
    """
    Error codes that the rexitcode function can return if unable to
    check the exit code of a spawned process
    """
    FILENOTFOUND = -1
    CORRUPTFILE = -2
    ERROR = -3
    OK = 0

class OSType:
    """
    Supported flavors of Linux OS
    """
    DEBIAN = 1 
    UBUNTU = 1 << 1 
    FEDORA = 1 << 2
    FEDORA_8 = 1 << 3 | FEDORA 
    FEDORA_12 = 1 << 4 | FEDORA 
    FEDORA_14 = 1 << 5 | FEDORA 

@clsinit_copy
class LinuxNode(ResourceManager):
    """
    .. class:: Class Args :
      
        :param ec: The Experiment controller
        :type ec: ExperimentController
        :param guid: guid of the RM
        :type guid: int

    .. note::

        There are different ways in which commands can be executed using the
        LinuxNode interface (i.e. 'execute' - blocking and non blocking, 'run',
        'run_and_wait'). 
        
        Brief explanation:

            * 'execute' (blocking mode) :  

                     HOW IT WORKS: 'execute', forks a process and run the
                     command, synchronously, attached to the terminal, in
                     foreground.
                     The execute method will block until the command returns
                     the result on 'out', 'err' (so until it finishes executing).
  
                     USAGE: short-lived commands that must be executed attached
                     to a terminal and in foreground, for which it IS necessary
                     to block until the command has finished (e.g. if you want
                     to run 'ls' or 'cat').

            * 'execute' (NON blocking mode - blocking = False) :

                    HOW IT WORKS: Same as before, except that execute method
                    will return immediately (even if command still running).

                    USAGE: long-lived commands that must be executed attached
                    to a terminal and in foreground, but for which it is not
                    necessary to block until the command has finished. (e.g.
                    start an application using X11 forwarding)

             * 'run' :

                   HOW IT WORKS: Connects to the host ( using SSH if remote)
                   and launches the command in background, detached from any
                   terminal (daemonized), and returns. The command continues to
                   run remotely, but since it is detached from the terminal,
                   its pipes (stdin, stdout, stderr) can't be redirected to the
                   console (as normal non detached processes would), and so they
                   are explicitly redirected to files. The pidfile is created as
                   part of the process of launching the command. The pidfile
                   holds the pid and ppid of the process forked in background,
                   so later on it is possible to check whether the command is still
                   running.

                    USAGE: long-lived commands that can run detached in background,
                    for which it is NOT necessary to block (wait) until the command
                    has finished. (e.g. start an application that is not using X11
                    forwarding. It can run detached and remotely in background)

             * 'run_and_wait' :

                    HOW IT WORKS: Similar to 'run' except that it 'blocks' until
                    the command has finished execution. It also checks whether
                    errors occurred during runtime by reading the exitcode file,
                    which contains the exit code of the command that was run
                    (checking stderr only is not always reliable since many
                    commands throw debugging info to stderr and the only way to
                    automatically know whether an error really happened is to
                    check the process exit code).

                    Another difference with respect to 'run', is that instead
                    of directly executing the command as a bash command line,
                    it uploads the command to a bash script and runs the script.
                    This allows to use the bash script to debug errors, since
                    it remains at the remote host and can be run manually to
                    reproduce the error.
                  
                    USAGE: medium-lived commands that can run detached in
                    background, for which it IS necessary to block (wait) until
                    the command has finished. (e.g. Package installation,
                    source compilation, file download, etc)

    """
    _rtype = "linux::Node"
    _help = "Controls Linux host machines ( either localhost or a host " \
            "that can be accessed using a SSH key)"
    _platform = "linux"

    @classmethod
    def _register_attributes(cls):
        cls._register_attribute(Attribute(
            "hostname", "Hostname of the machine",
            flags = Flags.Design))

        cls._register_attribute(Attribute(
            "username", "Local account username", 
            flags = Flags.Credential))

        cls._register_attribute(Attribute(
            "port", "SSH port",
            flags = Flags.Design))
        
        cls._register_attribute(Attribute(
            "home",
            "Experiment home directory to store all experiment related files",
            flags = Flags.Design))
        
        cls._register_attribute(Attribute(
            "identity", "SSH identity file",
            flags = Flags.Credential))
        
        cls._register_attribute(Attribute(
            "serverKey", "Server public key", 
            flags = Flags.Design))
        
        cls._register_attribute(Attribute(
            "cleanHome",
            "Remove all nepi files and directories "
            " from node home folder before starting experiment", 
            type = Types.Bool,
            default = False,
            flags = Flags.Design))

        cls._register_attribute(Attribute(
            "cleanExperiment", "Remove all files and directories " 
            " from a previous same experiment, before the new experiment starts", 
            type = Types.Bool,
            default = False,
            flags = Flags.Design))
        
        cls._register_attribute(Attribute(
            "cleanProcesses", 
            "Kill all running processes before starting experiment",
            type = Types.Bool,
            default = False,
            flags = Flags.Design))
        
        cls._register_attribute(Attribute(
            "cleanProcessesAfter", 
            """Kill all running processes after starting experiment
            This might be dangerous when using user root""",
            type = Types.Bool,
            default = True,
            flags = Flags.Design))
        
        cls._register_attribute(Attribute(
            "tearDown",
            "Bash script to be executed before releasing the resource",
            flags = Flags.Design))

        cls._register_attribute(Attribute(
            "gatewayUser",
            "Gateway account username",
            flags = Flags.Design))

        cls._register_attribute(Attribute(
            "gateway",
            "Hostname of the gateway machine",
            flags = Flags.Design))

        cls._register_attribute(Attribute(
            "ip",
            "Linux host public IP address. "
            "Must not be modified by the user unless hostname is 'localhost'",
            flags = Flags.Design))

    def __init__(self, ec, guid):
        super(LinuxNode, self).__init__(ec, guid)
        self._os = None
        # home directory at Linux host
        self._home_dir = ""

        # lock to prevent concurrent applications on the same node,
        # to execute commands at the same time. There are potential
        # concurrency issues when using SSH to a same host from 
        # multiple threads. There are also possible operational 
        # issues, e.g. an application querying the existence 
        # of a file or folder prior to its creation, and another 
        # application creating the same file or folder in between.
        self._node_lock = threading.Lock()
        
    def log_message(self, msg):
        return " guid {} - host {} - {} "\
            .format(self.guid, self.get("hostname"), msg)

    @property
    def home_dir(self):
        home = self.get("home") or ""
        if not home.startswith("/"):
            home = os.path.join(self._home_dir, home) 
            return home

    @property
    def nepi_home(self):
        return os.path.join(self.home_dir, ".nepi")

    @property
    def usr_dir(self):
        return os.path.join(self.nepi_home, "nepi-usr")

    @property
    def lib_dir(self):
        return os.path.join(self.usr_dir, "lib")

    @property
    def bin_dir(self):
        return os.path.join(self.usr_dir, "bin")

    @property
    def src_dir(self):
        return os.path.join(self.usr_dir, "src")

    @property
    def share_dir(self):
        return os.path.join(self.usr_dir, "share")

    @property
    def exp_dir(self):
        return os.path.join(self.nepi_home, "nepi-exp")

    @property
    def exp_home(self):
        return os.path.join(self.exp_dir, self.ec.exp_id)

    @property
    def node_home(self):
        return os.path.join(self.exp_home, "node-{}".format(self.guid))

    @property
    def run_home(self):
        return os.path.join(self.node_home, self.ec.run_id)

    @property
    def os(self):
        if self._os:
            return self._os

        if not self.localhost and not self.get("username"):
            msg = "Can't resolve OS, insufficient data "
            self.error(msg)
            raise RuntimeError, msg

        out = self.get_os()

        if out.find("Debian") == 0: 
            self._os = OSType.DEBIAN
        elif out.find("Ubuntu") ==0:
            self._os = OSType.UBUNTU
        elif out.find("Fedora release") == 0:
            self._os = OSType.FEDORA
            if out.find("Fedora release 8") == 0:
                self._os = OSType.FEDORA_8
            elif out.find("Fedora release 12") == 0:
                self._os = OSType.FEDORA_12
            elif out.find("Fedora release 14") == 0:
                self._os = OSType.FEDORA_14
        else:
            msg = "Unsupported OS"
            self.error(msg, out)
            raise RuntimeError("{} - {} ".format(msg, out))

        return self._os

    def get_os(self):
        # The underlying SSH layer will sometimes return an empty
        # output (even if the command was executed without errors).
        # To work arround this, repeat the operation N times or
        # until the result is not empty string
        out = ""
        try:
            (out, err), proc = self.execute("cat /etc/issue", 
                                            with_lock = True,
                                            blocking = True)
        except:
            trace = traceback.format_exc()
            msg = "Error detecting OS: {} ".format(trace)
            self.error(msg, out, err)
    
        return out

    @property
    def use_deb(self):
        return (self.os & (OSType.DEBIAN|OSType.UBUNTU))

    @property
    def use_rpm(self):
        return (self.os & OSType.FEDORA)

    @property
    def localhost(self):
        return self.get("hostname") in ['localhost', '127.0.0.1', '::1']

    def do_provision(self):
        # check if host is alive
        if not self.is_alive():
            msg = "Deploy failed. Unresponsive node {}".format(self.get("hostname"))
            self.error(msg)
            raise RuntimeError, msg

        self.find_home()

        if self.get("cleanProcesses"):
            self.clean_processes()

        if self.get("cleanHome"):
            self.clean_home()
            
        if self.get("cleanExperiment"):
            self.clean_experiment()
            
        # Create shared directory structure and node home directory
        paths = [self.lib_dir, 
                 self.bin_dir, 
                 self.src_dir, 
                 self.share_dir, 
                 self.node_home]

        self.mkdir(paths)

        # Get Public IP address if possible
        if not self.get("ip"):
            try:
                ip = sshfuncs.gethostbyname(self.get("hostname"))
                self.set("ip", ip)
            except:
                if self.get("gateway") is None:
                    msg = "Local DNS can not resolve hostname {}".format(self.get("hostname"))
                    self.error(msg)

        super(LinuxNode, self).do_provision()

    def do_deploy(self):
        if self.state == ResourceState.NEW:
            self.info("Deploying node")
            self.do_discover()
            self.do_provision()

        # Node needs to wait until all associated interfaces are 
        # ready before it can finalize deployment
        from nepi.resources.linux.interface import LinuxInterface
        ifaces = self.get_connected(LinuxInterface.get_rtype())
        for iface in ifaces:
            if iface.state < ResourceState.READY:
                self.ec.schedule(self.reschedule_delay, self.deploy)
                return 

        super(LinuxNode, self).do_deploy()

    def do_release(self):
        rms = self.get_connected()
        for rm in rms:
            # Node needs to wait until all associated RMs are released
            # before it can be released
            if rm.state != ResourceState.RELEASED:
                self.ec.schedule(self.reschedule_delay, self.release)
                return 

        tear_down = self.get("tearDown")
        if tear_down:
            self.execute(tear_down)

        if self.get("cleanProcessesAfter"):
            self.clean_processes()

        super(LinuxNode, self).do_release()

    def valid_connection(self, guid):
        # TODO: Validate!
        return True

    def clean_processes(self):
        self.info("Cleaning up processes")

        if self.localhost:
            return 
        
        if self.get("username") != 'root':
            cmd = ("sudo -S killall tcpdump || /bin/true ; " +
                   "sudo -S kill -9 $(ps aux | grep '[.]nepi' | awk '{print $2}') || /bin/true ; " +
                   "sudo -S killall -u {} || /bin/true ; ".format(self.get("username")))
        else:
            if self.state >= ResourceState.READY:
                import pickle
                pids = pickle.load(open("/tmp/save.proc", "rb"))
                pids_temp = dict()
                ps_aux = "ps aux |awk '{print $2,$11}'"
                (out, err), proc = self.execute(ps_aux)
                if len(out) != 0:
                    for line in out.strip().split("\n"):
                        parts = line.strip().split(" ")
                        pids_temp[parts[0]] = parts[1]
                    kill_pids = set(pids_temp.items()) - set(pids.items())
                    kill_pids = ' '.join(dict(kill_pids).keys())

                    cmd = ("killall tcpdump || /bin/true ; " +
                           "kill $(ps aux | grep '[.]nepi' | awk '{print $2}') || /bin/true ; " +
                           "kill {} || /bin/true ; ".format(kill_pids))
                else:
                    cmd = ("killall tcpdump || /bin/true ; " +
                           "kill $(ps aux | grep '[.]nepi' | awk '{print $2}') || /bin/true ; ")
            else:
                cmd = ("killall tcpdump || /bin/true ; " +
                       "kill $(ps aux | grep '[.]nepi' | awk '{print $2}') || /bin/true ; ")

        (out, err), proc = self.execute(cmd, retry = 1, with_lock = True)

    def clean_home(self):
        """ Cleans all NEPI related folders in the Linux host
        """
        self.info("Cleaning up home")
        
        cmd = "cd {} ; find . -maxdepth 1 -name \.nepi -execdir rm -rf {} + "\
              .format(self.home_dir)

        return self.execute(cmd, with_lock = True)

    def clean_experiment(self):
        """ Cleans all experiment related files in the Linux host.
        It preserves NEPI files and folders that have a multi experiment
        scope.
        """
        self.info("Cleaning up experiment files")
        
        cmd = "cd {} ; find . -maxdepth 1 -name '{}' -execdir rm -rf {} + "\
              .format(self.exp_dir, self.ec.exp_id)
        
        return self.execute(cmd, with_lock = True)

    def execute(self, command,
                sudo = False,
                env = None,
                tty = False,
                forward_x11 = False,
                retry = 3,
                connect_timeout = 30,
                strict_host_checking = False,
                persistent = True,
                blocking = True,
                with_lock = False
    ):
        """ Notice that this invocation will block until the
        execution finishes. If this is not the desired behavior,
        use 'run' instead."""

        if self.localhost:
            (out, err), proc = execfuncs.lexec(
                command, 
                user = self.get("username"), # still problem with localhost
                sudo = sudo,
                env = env)
        else:
            if with_lock:
                # If the execute command is blocking, we don't want to keep
                # the node lock. This lock is used to avoid race conditions
                # when creating the ControlMaster sockets. A more elegant
                # solution is needed.
                with self._node_lock:
                    (out, err), proc = sshfuncs.rexec(
                        command, 
                        host = self.get("hostname"),
                        user = self.get("username"),
                        port = self.get("port"),
                        gwuser = self.get("gatewayUser"),
                        gw = self.get("gateway"),
                        agent = True,
                        sudo = sudo,
                        identity = self.get("identity"),
                        server_key = self.get("serverKey"),
                        env = env,
                        tty = tty,
                        forward_x11 = forward_x11,
                        retry = retry,
                        connect_timeout = connect_timeout,
                        persistent = persistent,
                        blocking = blocking, 
                        strict_host_checking = strict_host_checking
                    )
            else:
                (out, err), proc = sshfuncs.rexec(
                    command, 
                    host = self.get("hostname"),
                    user = self.get("username"),
                    port = self.get("port"),
                    gwuser = self.get("gatewayUser"),
                    gw = self.get("gateway"),
                    agent = True,
                    sudo = sudo,
                    identity = self.get("identity"),
                    server_key = self.get("serverKey"),
                    env = env,
                    tty = tty,
                    forward_x11 = forward_x11,
                    retry = retry,
                    connect_timeout = connect_timeout,
                    persistent = persistent,
                    blocking = blocking, 
                    strict_host_checking = strict_host_checking
                )

        return (out, err), proc

    def run(self, command, home,
            create_home = False,
            pidfile = 'pidfile',
            stdin = None, 
            stdout = 'stdout', 
            stderr = 'stderr', 
            sudo = False,
            tty = False,
            strict_host_checking = False):
        
        self.debug("Running command '{}'".format(command))
        
        if self.localhost:
            (out, err), proc = execfuncs.lspawn(
                command, pidfile,
                home = home, 
                create_home = create_home, 
                stdin = stdin or '/dev/null',
                stdout = stdout or '/dev/null',
                stderr = stderr or '/dev/null',
                sudo = sudo) 
        else:
            with self._node_lock:
                (out, err), proc = sshfuncs.rspawn(
                    command,
                    pidfile = pidfile,
                    home = home,
                    create_home = create_home,
                    stdin = stdin or '/dev/null',
                    stdout = stdout or '/dev/null',
                    stderr = stderr or '/dev/null',
                    sudo = sudo,
                    host = self.get("hostname"),
                    user = self.get("username"),
                    port = self.get("port"),
                    gwuser = self.get("gatewayUser"),
                    gw = self.get("gateway"),
                    agent = True,
                    identity = self.get("identity"),
                    server_key = self.get("serverKey"),
                    tty = tty,
                    strict_host_checking = strict_host_checking
                )

        return (out, err), proc

    def getpid(self, home, pidfile = "pidfile"):
        if self.localhost:
            pidtuple =  execfuncs.lgetpid(os.path.join(home, pidfile))
        else:
            with self._node_lock:
                pidtuple = sshfuncs.rgetpid(
                    os.path.join(home, pidfile),
                    host = self.get("hostname"),
                    user = self.get("username"),
                    port = self.get("port"),
                    gwuser = self.get("gatewayUser"),
                    gw = self.get("gateway"),
                    agent = True,
                    identity = self.get("identity"),
                    server_key = self.get("serverKey"),
                    strict_host_checking = False
                )
        
        return pidtuple

    def status(self, pid, ppid):
        if self.localhost:
            status = execfuncs.lstatus(pid, ppid)
        else:
            with self._node_lock:
                status = sshfuncs.rstatus(
                    pid, ppid,
                    host = self.get("hostname"),
                    user = self.get("username"),
                    port = self.get("port"),
                    gwuser = self.get("gatewayUser"),
                    gw = self.get("gateway"),
                    agent = True,
                    identity = self.get("identity"),
                    server_key = self.get("serverKey"),
                    strict_host_checking = False
                )
           
        return status
    
    def kill(self, pid, ppid, sudo = False):
        out = err = ""
        proc = None
        status = self.status(pid, ppid)

        if status == sshfuncs.ProcStatus.RUNNING:
            if self.localhost:
                (out, err), proc = execfuncs.lkill(pid, ppid, sudo)
            else:
                with self._node_lock:
                    (out, err), proc = sshfuncs.rkill(
                        pid, ppid,
                        host = self.get("hostname"),
                        user = self.get("username"),
                        port = self.get("port"),
                        gwuser = self.get("gatewayUser"),
                        gw = self.get("gateway"),
                        agent = True,
                        sudo = sudo,
                        identity = self.get("identity"),
                        server_key = self.get("serverKey"),
                        strict_host_checking = False
                    )

        return (out, err), proc

    def copy(self, src, dst):
        if self.localhost:
            (out, err), proc = execfuncs.lcopy(
                src, dst, 
                recursive = True)
        else:
            with self._node_lock:
                (out, err), proc = sshfuncs.rcopy(
                    src, dst, 
                    port = self.get("port"),
                    gwuser = self.get("gatewayUser"),
                    gw = self.get("gateway"),
                    identity = self.get("identity"),
                    server_key = self.get("serverKey"),
                    recursive = True,
                    strict_host_checking = False)

        return (out, err), proc

    def upload(self, src, dst, text = False, overwrite = True,
               raise_on_error = True):
        """ Copy content to destination

        src  string with the content to copy. Can be:
            - plain text
            - a string with the path to a local file
            - a string with a semi-colon separeted list of local files
            - a string with a local directory

        dst  string with destination path on the remote host (remote is 
            always self.host)

        text src is text input, it must be stored into a temp file before 
        uploading
        """
        # If source is a string input 
        f = None
        if text and not os.path.isfile(src):
            # src is text input that should be uploaded as file
            # create a temporal file with the content to upload
            f = tempfile.NamedTemporaryFile(delete=False)
            f.write(src)
            f.close()
            src = f.name

        # If dst files should not be overwritten, check that the files do not
        # exits already
        if isinstance(src, str):
            src = map(str.strip, src.split(";"))
    
        if overwrite == False:
            src = self.filter_existing_files(src, dst)
            if not src:
                return ("", ""), None

        if not self.localhost:
            # Build destination as <user>@<server>:<path>
            dst = "{}@{}:{}".format(self.get("username"), self.get("hostname"), dst)

        ((out, err), proc) = self.copy(src, dst)

        # clean up temp file
        if f:
            os.remove(f.name)

        if err:
            msg = " Failed to upload files - src: {} dst: {}".format(";".join(src), dst)
            self.error(msg, out, err)
            
            msg = "{} out: {} err: {}".format(msg, out, err)
            if raise_on_error:
                raise RuntimeError, msg

        return ((out, err), proc)

    def download(self, src, dst, raise_on_error = True):
        if not self.localhost:
            # Build destination as <user>@<server>:<path>
            src = "{}@{}:{}".format(self.get("username"), self.get("hostname"), src)

        ((out, err), proc) = self.copy(src, dst)

        if err:
            msg = " Failed to download files - src: {} dst: {}".format(";".join(src), dst) 
            self.error(msg, out, err)

            if raise_on_error:
                raise RuntimeError, msg

        return ((out, err), proc)

    def install_packages_command(self, packages):
        command = ""
        if self.use_rpm:
            command = rpmfuncs.install_packages_command(self.os, packages)
        elif self.use_deb:
            command = debfuncs.install_packages_command(self.os, packages)
        else:
            msg = "Error installing packages ( OS not known ) "
            self.error(msg, self.os)
            raise RuntimeError, msg

        return command

    def install_packages(self, packages, home,
                         run_home = None,
                         raise_on_error = True):
        """ Install packages in the Linux host.

        'home' is the directory to upload the package installation script.
        'run_home' is the directory from where to execute the script.
        """
        command = self.install_packages_command(packages)

        run_home = run_home or home

        (out, err), proc = self.run_and_wait(command, run_home, 
                                             shfile = os.path.join(home, "instpkg.sh"),
                                             pidfile = "instpkg_pidfile",
                                             ecodefile = "instpkg_exitcode",
                                             stdout = "instpkg_stdout", 
                                             stderr = "instpkg_stderr",
                                             overwrite = False,
                                             raise_on_error = raise_on_error)

        return (out, err), proc 

    def remove_packages(self, packages, home, run_home = None,
                        raise_on_error = True):
        """ Uninstall packages from the Linux host.

        'home' is the directory to upload the package un-installation script.
        'run_home' is the directory from where to execute the script.
        """
        if self.use_rpm:
            command = rpmfuncs.remove_packages_command(self.os, packages)
        elif self.use_deb:
            command = debfuncs.remove_packages_command(self.os, packages)
        else:
            msg = "Error removing packages ( OS not known ) "
            self.error(msg)
            raise RuntimeError, msg

        run_home = run_home or home

        (out, err), proc = self.run_and_wait(command, run_home, 
                                             shfile = os.path.join(home, "rmpkg.sh"),
                                             pidfile = "rmpkg_pidfile",
                                             ecodefile = "rmpkg_exitcode",
                                             stdout = "rmpkg_stdout", 
                                             stderr = "rmpkg_stderr",
                                             overwrite = False,
                                             raise_on_error = raise_on_error)
        
        return (out, err), proc 

    def mkdir(self, paths, clean = False):
        """ Paths is either a single remote directory path to create,
        or a list of directories to create.
        """
        if clean:
            self.rmdir(paths)

        if isinstance(paths, str):
            paths = [paths]

        cmd = " ; ".join(["mkdir -p {}".format(path) for path in paths])

        return self.execute(cmd, with_lock = True)

    def rmdir(self, paths):
        """ Paths is either a single remote directory path to delete,
        or a list of directories to delete.
        """

        if isinstance(paths, str):
            paths = [paths]

        cmd = " ; ".join(map(lambda path: "rm -rf {}".format(path), paths))

        return self.execute(cmd, with_lock = True)
    
    def run_and_wait(self, command, home, 
                     shfile="cmd.sh",
                     env=None,
                     overwrite=True,
                     wait_run=True,
                     pidfile="pidfile", 
                     ecodefile="exitcode", 
                     stdin=None, 
                     stdout="stdout", 
                     stderr="stderr", 
                     sudo=False,
                     tty=False,
                     raise_on_error=True):
        """
        Uploads the 'command' to a bash script in the host.
        Then runs the script detached in background in the host, and
        busy-waites until the script finishes executing.
        """

        if not shfile.startswith("/"):
            shfile = os.path.join(home, shfile)

        self.upload_command(command, 
                            shfile = shfile, 
                            ecodefile = ecodefile, 
                            env = env,
                            overwrite = overwrite)

        command = "bash {}".format(shfile)
        # run command in background in remote host
        (out, err), proc = self.run(command, home, 
                                    pidfile = pidfile,
                                    stdin = stdin, 
                                    stdout = stdout, 
                                    stderr = stderr, 
                                    sudo = sudo,
                                    tty = tty)

        # check no errors occurred
        if proc.poll():
            msg = " Failed to run command '{}' ".format(command)
            self.error(msg, out, err)
            if raise_on_error:
                raise RuntimeError, msg

        # Wait for pid file to be generated
        pid, ppid = self.wait_pid(
            home = home, 
            pidfile = pidfile, 
            raise_on_error = raise_on_error)

        if wait_run:
            # wait until command finishes to execute
            self.wait_run(pid, ppid)
            
            (eout, err), proc = self.check_errors(home,
                                                  ecodefile = ecodefile,
                                                  stderr = stderr)

            # Out is what was written in the stderr file
            if err:
                msg = " Failed to run command '{}' ".format(command)
                self.error(msg, eout, err)

                if raise_on_error:
                    raise RuntimeError, msg

        (out, oerr), proc = self.check_output(home, stdout)
        
        return (out, err), proc
        
    def exitcode(self, home, ecodefile = "exitcode"):
        """
        Get the exit code of an application.
        Returns an integer value with the exit code 
        """
        (out, err), proc = self.check_output(home, ecodefile)

        # Succeeded to open file, return exit code in the file
        if proc.wait() == 0:
            try:
                return int(out.strip())
            except:
                # Error in the content of the file!
                return ExitCode.CORRUPTFILE

        # No such file or directory
        if proc.returncode == 1:
            return ExitCode.FILENOTFOUND
        
        # Other error from 'cat'
        return ExitCode.ERROR

    def upload_command(self, command, 
                       shfile="cmd.sh",
                       ecodefile="exitcode",
                       overwrite=True,
                       env=None):
        """ Saves the command as a bash script file in the remote host, and
        forces to save the exit code of the command execution to the ecodefile
        """

        if not (command.strip().endswith(";") or command.strip().endswith("&")):
            command += ";"
            
        # The exit code of the command will be stored in ecodefile
        command = " {{ {command} }} ; echo $? > {ecodefile} ;"\
                  .format(command=command, ecodefile=ecodefile)

        # Export environment
        environ = self.format_environment(env)

        # Add environ to command
        command = environ + command

        return self.upload(command, shfile, text=True, overwrite=overwrite)

    def format_environment(self, env, inline=False):
        """ Formats the environment variables for a command to be executed
        either as an inline command
        (i.e. export PYTHONPATH=src/..; export LALAL= ..;python script.py) or 
        as a bash script (i.e. export PYTHONPATH=src/.. \n export LALA=.. \n)
        """
        if not env: return ""

        # Remove extra white spaces
        env = re.sub(r'\s+', ' ', env.strip())

        sep = ";" if inline else "\n"
        return sep.join([" export {}".format(e) for e in env.split(" ")]) + sep 

    def check_errors(self, home, 
                     ecodefile = "exitcode", 
                     stderr = "stderr"):
        """ Checks whether errors occurred while running a command.
        It first checks the exit code for the command, and only if the
        exit code is an error one it returns the error output.

        """
        proc = None
        err = ""

        # get exit code saved in the 'exitcode' file
        ecode = self.exitcode(home, ecodefile)

        if ecode in [ ExitCode.CORRUPTFILE, ExitCode.ERROR ]:
            err = "Error retrieving exit code status from file {}/{}".format(home, ecodefile)
        elif ecode > 0 or ecode == ExitCode.FILENOTFOUND:
            # The process returned an error code or didn't exist. 
            # Check standard error.
            (err, eerr), proc = self.check_output(home, stderr)

            # If the stderr file was not found, assume nothing bad happened,
            # and just ignore the error.
            # (cat returns 1 for error "No such file or directory")
            if ecode == ExitCode.FILENOTFOUND and proc.poll() == 1: 
                err = "" 
                
        return ("", err), proc
    
    def wait_pid(self, home, pidfile = "pidfile", raise_on_error = False):
        """ Waits until the pid file for the command is generated, 
            and returns the pid and ppid of the process """
        pid = ppid = None
        delay = 1.0

        for i in xrange(2):
            pidtuple = self.getpid(home = home, pidfile = pidfile)
            
            if pidtuple:
                pid, ppid = pidtuple
                break
            else:
                time.sleep(delay)
                delay = delay * 1.5
        else:
            msg = " Failed to get pid for pidfile {}/{} ".format(home, pidfile )
            self.error(msg)
    
            if raise_on_error:
                raise RuntimeError, msg

        return pid, ppid

    def wait_run(self, pid, ppid, trial = 0):
        """ wait for a remote process to finish execution """
        delay = 1.0

        while True:
            status = self.status(pid, ppid)
            
            if status is ProcStatus.FINISHED:
                break
            elif status is not ProcStatus.RUNNING:
                delay = delay * 1.5
                time.sleep(delay)
                # If it takes more than 20 seconds to start, then
                # asume something went wrong
                if delay > 20:
                    break
            else:
                # The app is running, just wait...
                time.sleep(0.5)

    def check_output(self, home, filename):
        """ Retrives content of file """
        (out, err), proc = self.execute(
            "cat {}".format(os.path.join(home, filename)), retry = 1, with_lock = True)
        return (out, err), proc

    def is_alive(self):
        """ Checks if host is responsive
        """
        if self.localhost:
            return True

        out = err = ""
        msg = "Unresponsive host. Wrong answer. "

        # The underlying SSH layer will sometimes return an empty
        # output (even if the command was executed without errors).
        # To work arround this, repeat the operation N times or
        # until the result is not empty string
        try:
            (out, err), proc = self.execute("echo 'ALIVE'",
                                            blocking = True,
                                            with_lock = True)
            
            if out.find("ALIVE") > -1:
                return True
        except:
            trace = traceback.format_exc()
            msg = "Unresponsive host. Error reaching host: {} ".format(trace)

        self.error(msg, out, err)
        return False

    def find_home(self):
        """ 
        Retrieves host home directory
        """
        # The underlying SSH layer will sometimes return an empty
        # output (even if the command was executed without errors).
        # To work arround this, repeat the operation N times or
        # until the result is not empty string
        msg = "Impossible to retrieve HOME directory"
        try:
            (out, err), proc = self.execute("echo ${HOME}",
                                            blocking = True,
                                            with_lock = True)
            
            if out.strip() != "":
                self._home_dir =  out.strip()
        except:
            trace = traceback.format_exc()
            msg = "Impossible to retrieve HOME directory {}".format(trace)

        if not self._home_dir:
            self.error(msg)
            raise RuntimeError, msg

    def filter_existing_files(self, src, dst):
        """ Removes files that already exist in the Linux host from src list
        """
        # construct a dictionary with { dst: src }
        dests = { os.path.join(dst, os.path.basename(s)) : s for s in src } \
                if len(src) > 1 else {dst: src[0]}

        command = []
        for d in dests.keys():
            command.append(" [ -f {dst} ] && echo '{dst}' ".format(dst=d) )

        command = ";".join(command)

        (out, err), proc = self.execute(command, retry = 1, with_lock = True)
        
        for d in dests.keys():
            if out.find(d) > -1:
                del dests[d]

        if not dests:
            return []

        return dests.values()

