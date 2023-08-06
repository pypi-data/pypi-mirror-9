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

import logging
import os
import sys
import threading
import time
import uuid

SINGLETON = "singleton::"
SIMULATOR_UUID = "singleton::Simulator"
CONFIG_UUID = "singleton::Config"
GLOBAL_VALUE_UUID = "singleton::GlobalValue"
IPV4_GLOBAL_ROUTING_HELPER_UUID = "singleton::Ipv4GlobalRoutingHelper"

def load_ns3_libraries():
    import ctypes
    import re

    libdir = os.environ.get("NS3LIBRARIES")

    # Load the ns-3 modules shared libraries
    if libdir:
        files = os.listdir(libdir)
        regex = re.compile("(.*\.so)$")
        libs = [m.group(1) for filename in files for m in [regex.search(filename)] if m]

        initial_size = len(libs)
        # Try to load the libraries in the right order by trial and error.
        # Loop until all libraries are loaded.
        while len(libs) > 0:
            for lib in libs:
                libfile = os.path.join(libdir, lib)
                try:
                    ctypes.CDLL(libfile, ctypes.RTLD_GLOBAL)
                    libs.remove(lib)
                except:
                    #import traceback
                    #err = traceback.format_exc()
                    #print err
                    pass

            # if did not load any libraries in the last iteration break
            # to prevent infinit loop
            if initial_size == len(libs):
                raise RuntimeError("Imposible to load shared libraries %s" % str(libs))
            initial_size = len(libs)

def load_ns3_module():
    load_ns3_libraries()

    # import the python bindings for the ns-3 modules
    bindings = os.environ.get("NS3BINDINGS")
    if bindings:
        sys.path.append(bindings)

    import pkgutil
    import imp
    import ns

    # create a Python module to add all ns3 classes
    ns3mod = imp.new_module("ns3")
    sys.modules["ns3"] = ns3mod

    for importer, modname, ispkg in pkgutil.iter_modules(ns.__path__):
        if modname in [ "visualizer" ]:
            continue

        fullmodname = "ns.%s" % modname
        module = __import__(fullmodname, globals(), locals(), ['*'])

        for sattr in dir(module):
            if sattr.startswith("_"):
                continue

            attr = getattr(module, sattr)

            # netanim.Config and lte.Config singleton overrides ns3::Config
            if sattr == "Config" and modname in ['netanim', 'lte']:
                sattr = "%s.%s" % (modname, sattr)

            setattr(ns3mod, sattr, attr)

    return ns3mod

class NS3Wrapper(object):
    def __init__(self, loglevel = logging.INFO, enable_dump = False):
        super(NS3Wrapper, self).__init__()
        # Thread used to run the simulation
        self._simulation_thread = None
        self._condition = None

        # True if Simulator::Run was invoked
        self._started = False

        # holds reference to all C++ objects and variables in the simulation
        self._objects = dict()

        # Logging
        self._logger = logging.getLogger("ns3wrapper")
        self._logger.setLevel(loglevel)

        ## NOTE that the reason to create a handler to the ns3 module,
        # that is re-loaded each time a ns-3 wrapper is instantiated,
        # is that else each unit test for the ns3wrapper class would need
        # a separate file. Several ns3wrappers would be created in the 
        # same unit test (single process), leading to inchorences in the 
        # state of ns-3 global objects
        #
        # Handler to ns3 classes
        self._ns3 = None

        # Collection of allowed ns3 classes
        self._allowed_types = None

        # Object to dump instructions to reproduce and debug experiment
        from ns3wrapper_debug import NS3WrapperDebuger
        self._debuger = NS3WrapperDebuger(enabled = enable_dump)

    @property
    def debuger(self):
        return self._debuger

    @property
    def ns3(self):
        if not self._ns3:
            # load ns-3 libraries and bindings
            self._ns3 = load_ns3_module()

        return self._ns3

    @property
    def allowed_types(self):
        if not self._allowed_types:
            self._allowed_types = set()
            type_id = self.ns3.TypeId()
            
            tid_count = type_id.GetRegisteredN()
            base = type_id.LookupByName("ns3::Object")

            for i in xrange(tid_count):
                tid = type_id.GetRegistered(i)
                
                if tid.MustHideFromDocumentation() or \
                        not tid.HasConstructor() or \
                        not tid.IsChildOf(base): 
                    continue

                type_name = tid.GetName()
                self._allowed_types.add(type_name)
        
        return self._allowed_types

    @property
    def logger(self):
        return self._logger

    @property
    def is_running(self):
        return self.is_started and not self.ns3.Simulator.IsFinished()

    @property
    def is_started(self):
        if not self._started:
            now = self.ns3.Simulator.Now()
            if not now.IsZero():
                self._started = True

        return self._started

    @property
    def is_finished(self):
        return self.ns3.Simulator.IsFinished()

    def make_uuid(self):
        return "uuid%s" % uuid.uuid4()

    def get_object(self, uuid):
        return self._objects.get(uuid)

    def factory(self, type_name, **kwargs):
        """ This method should be used to construct ns-3 objects
        that have a TypeId and related introspection information """

        if type_name not in self.allowed_types:
            msg = "Type %s not supported" % (type_name) 
            self.logger.error(msg)

        uuid = self.make_uuid()
        
        ### DEBUG
        self.logger.debug("FACTORY %s( %s )" % (type_name, str(kwargs)))
        
        ### DUMP
        self.debuger.dump_factory(uuid, type_name, kwargs)

        factory = self.ns3.ObjectFactory()
        factory.SetTypeId(type_name)

        for name, value in kwargs.iteritems():
            ns3_value = self._attr_from_string_to_ns3_value(type_name, name, value)
            factory.Set(name, ns3_value)

        obj = factory.Create()

        self._objects[uuid] = obj

        ### DEBUG
        self.logger.debug("RET FACTORY ( uuid %s ) %s = %s( %s )" % (
            str(uuid), str(obj), type_name, str(kwargs)))
 
        return uuid

    def create(self, clazzname, *args):
        """ This method should be used to construct ns-3 objects that
        do not have a TypeId (e.g. Values) """

        if not hasattr(self.ns3, clazzname):
            msg = "Type %s not supported" % (clazzname) 
            self.logger.error(msg)

        uuid = self.make_uuid()
        
        ### DEBUG
        self.logger.debug("CREATE %s( %s )" % (clazzname, str(args)))
    
        ### DUMP
        self.debuger.dump_create(uuid, clazzname, args)

        clazz = getattr(self.ns3, clazzname)
 
        # arguments starting with 'uuid' identify ns-3 C++
        # objects and must be replaced by the actual object
        realargs = self.replace_args(args)
       
        obj = clazz(*realargs)
        
        self._objects[uuid] = obj

        ### DEBUG
        self.logger.debug("RET CREATE ( uuid %s ) %s = %s( %s )" % (str(uuid), 
            str(obj), clazzname, str(args)))

        return uuid

    def invoke(self, uuid, operation, *args, **kwargs):
        ### DEBUG
        self.logger.debug("INVOKE %s -> %s( %s, %s ) " % (
            uuid, operation, str(args), str(kwargs)))
        ########

        result = None
        newuuid = None

        if operation == "isRunning":
            result = self.is_running

        elif operation == "isStarted":
            result = self.is_started

        elif operation == "isFinished":
            result = self.is_finished

        elif operation == "isAppRunning":
            result = self._is_app_running(uuid)

        elif operation == "isAppStarted":
            result = self._is_app_started(uuid)

        elif operation == "recvFD":
            ### passFD operation binds to a different random socket 
            ### en every execution, so the socket name that could be
            ### dumped to the debug script using dump_invoke is
            ### not be valid accross debug executions.
            result = self._recv_fd(uuid, *args, **kwargs)

        elif operation == "addStaticRoute":
            result = self._add_static_route(uuid, *args)
            
            ### DUMP - result is static, so will be dumped as plain text
            self.debuger.dump_invoke(result, uuid, operation, args, kwargs)

        elif operation == "retrieveObject":
            result = self._retrieve_object(uuid, *args, **kwargs)
       
            ### DUMP - result is static, so will be dumped as plain text
            self.debuger.dump_invoke(result, uuid, operation, args, kwargs)
       
        else:
            newuuid = self.make_uuid()

            ### DUMP - result is a uuid that encoded an dynamically generated 
            ### object
            self.debuger.dump_invoke(newuuid, uuid, operation, args, kwargs)

            if uuid.startswith(SINGLETON):
                obj = self._singleton(uuid)
            else:
                obj = self.get_object(uuid)
            
            method = getattr(obj, operation)

            # arguments starting with 'uuid' identify ns-3 C++
            # objects and must be replaced by the actual object
            realargs = self.replace_args(args)
            realkwargs = self.replace_kwargs(kwargs)

            result = method(*realargs, **realkwargs)

            # If the result is an object (not a base value),
            # then keep track of the object a return the object
            # reference (newuuid)
            if not (result is None or type(result) in [
                    bool, float, long, str, int]):
                self._objects[newuuid] = result
                result = newuuid

        ### DEBUG
        self.logger.debug("RET INVOKE %s%s = %s -> %s(%s, %s) " % (
            "(uuid %s) " % str(newuuid) if newuuid else "", str(result), uuid, 
            operation, str(args), str(kwargs)))
        ########

        return result

    def _set_attr(self, obj, name, ns3_value):
        obj.SetAttribute(name, ns3_value)

    def set(self, uuid, name, value):
        ### DEBUG
        self.logger.debug("SET %s %s %s" % (uuid, name, str(value)))
    
        ### DUMP
        self.debuger.dump_set(uuid, name, value)

        obj = self.get_object(uuid)
        type_name = obj.GetInstanceTypeId().GetName()
        ns3_value = self._attr_from_string_to_ns3_value(type_name, name, value)

        # If the Simulation thread is not running,
        # then there will be no thread-safety problems
        # in changing the value of an attribute directly.
        # However, if the simulation is running we need
        # to set the value by scheduling an event, else
        # we risk to corrupt the state of the
        # simulation.
        
        event_executed = [False]

        if self.is_running:
            # schedule the event in the Simulator
            self._schedule_event(self._condition, event_executed, 
                    self._set_attr, obj, name, ns3_value)

        if not event_executed[0]:
            self._set_attr(obj, name, ns3_value)

        ### DEBUG
        self.logger.debug("RET SET %s = %s -> set(%s, %s)" % (str(value), uuid, name, 
            str(value)))

        return value

    def _get_attr(self, obj, name, ns3_value):
        obj.GetAttribute(name, ns3_value)

    def get(self, uuid, name):
        ### DEBUG
        self.logger.debug("GET %s %s" % (uuid, name))
        
        ### DUMP
        self.debuger.dump_get(uuid, name)

        obj = self.get_object(uuid)
        type_name = obj.GetInstanceTypeId().GetName()
        ns3_value = self._create_attr_ns3_value(type_name, name)

        event_executed = [False]

        if self.is_running:
            # schedule the event in the Simulator
            self._schedule_event(self._condition, event_executed,
                    self._get_attr, obj, name, ns3_value)

        if not event_executed[0]:
            self._get_attr(obj, name, ns3_value)

        result = self._attr_from_ns3_value_to_string(type_name, name, ns3_value)

        ### DEBUG
        self.logger.debug("RET GET %s = %s -> get(%s)" % (str(result), uuid, name))

        return result

    def start(self):
        ### DUMP
        self.debuger.dump_start()

        # Launch the simulator thread and Start the
        # simulator in that thread
        self._condition = threading.Condition()
        self._simulator_thread = threading.Thread(
                target = self._simulator_run,
                args = [self._condition])
        self._simulator_thread.setDaemon(True)
        self._simulator_thread.start()
        
        ### DEBUG
        self.logger.debug("START")

    def stop(self, time = None):
        ### DUMP
        self.debuger.dump_stop(time=time)
        
        if time is None:
            self.ns3.Simulator.Stop()
        else:
            self.ns3.Simulator.Stop(self.ns3.Time(time))

        ### DEBUG
        self.logger.debug("STOP time=%s" % str(time))

    def shutdown(self):
        ### DUMP
        self.debuger.dump_shutdown()

        while not self.ns3.Simulator.IsFinished():
            #self.logger.debug("Waiting for simulation to finish")
            time.sleep(0.5)
        
        if self._simulator_thread:
            self._simulator_thread.join()
       
        self.ns3.Simulator.Destroy()
        
        # Remove all references to ns-3 objects
        self._objects.clear()
        
        sys.stdout.flush()
        sys.stderr.flush()

        ### DEBUG
        self.logger.debug("SHUTDOWN")

    def _simulator_run(self, condition):
        # Run simulation
        self.ns3.Simulator.Run()
        # Signal condition to indicate simulation ended and
        # notify waiting threads
        condition.acquire()
        condition.notifyAll()
        condition.release()

    def _schedule_event(self, condition, event_executed, func, *args):
        """ Schedules event on running simulation, and wait until
            event is executed"""

        def execute_event(contextId, condition, event_executed, func, *args):
            try:
                func(*args)
                event_executed[0] = True
            finally:
                # notify condition indicating event was executed
                condition.acquire()
                condition.notifyAll()
                condition.release()

        # contextId is defined as general context
        contextId = long(0xffffffff)

        # delay 0 means that the event is expected to execute inmediately
        delay = self.ns3.Seconds(0)
    
        # Mark event as not executed
        event_executed[0] = False

        condition.acquire()
        try:
            self.ns3.Simulator.ScheduleWithContext(contextId, delay, execute_event, 
                    condition, event_executed, func, *args)
            if not self.ns3.Simulator.IsFinished():
                condition.wait()
        finally:
            condition.release()

    def _create_attr_ns3_value(self, type_name, name):
        TypeId = self.ns3.TypeId()
        tid = TypeId.LookupByName(type_name)
        info = TypeId.AttributeInformation()
        if not tid.LookupAttributeByName(name, info):
            msg = "TypeId %s has no attribute %s" % (type_name, name) 
            self.logger.error(msg)

        checker = info.checker
        ns3_value = checker.Create() 
        return ns3_value

    def _attr_from_ns3_value_to_string(self, type_name, name, ns3_value):
        TypeId = self.ns3.TypeId()
        tid = TypeId.LookupByName(type_name)
        info = TypeId.AttributeInformation()
        if not tid.LookupAttributeByName(name, info):
            msg = "TypeId %s has no attribute %s" % (type_name, name) 
            self.logger.error(msg)

        checker = info.checker
        value = ns3_value.SerializeToString(checker)

        type_name = checker.GetValueTypeName()
        if type_name in ["ns3::UintegerValue", "ns3::IntegerValue"]:
            return int(value)
        if type_name == "ns3::DoubleValue":
            return float(value)
        if type_name == "ns3::BooleanValue":
            return value == "true"

        return value

    def _attr_from_string_to_ns3_value(self, type_name, name, value):
        TypeId = self.ns3.TypeId()
        tid = TypeId.LookupByName(type_name)
        info = TypeId.AttributeInformation()
        if not tid.LookupAttributeByName(name, info):
            msg = "TypeId %s has no attribute %s" % (type_name, name) 
            self.logger.error(msg)

        str_value = str(value)
        if isinstance(value, bool):
            str_value = str_value.lower()

        checker = info.checker
        ns3_value = checker.Create()
        ns3_value.DeserializeFromString(str_value, checker)
        return ns3_value

    # singletons are identified as "ns3::ClassName"
    def _singleton(self, ident):
        if not ident.startswith(SINGLETON):
            return None

        clazzname = ident[ident.find("::")+2:]
        if not hasattr(self.ns3, clazzname):
            msg = "Type %s not supported" % (clazzname)
            self.logger.error(msg)

        return getattr(self.ns3, clazzname)

    # replace uuids and singleton references for the real objects
    def replace_args(self, args):
        realargs = [self.get_object(arg) if \
                str(arg).startswith("uuid") else arg for arg in args]
 
        realargs = [self._singleton(arg) if \
                str(arg).startswith(SINGLETON) else arg for arg in realargs]

        return realargs

    # replace uuids and singleton references for the real objects
    def replace_kwargs(self, kwargs):
        realkwargs = dict([(k, self.get_object(v) \
                if str(v).startswith("uuid") else v) \
                for k,v in kwargs.iteritems()])
 
        realkwargs = dict([(k, self._singleton(v) \
                if str(v).startswith(SINGLETON) else v )\
                for k, v in realkwargs.iteritems()])

        return realkwargs

    def _is_app_running(self, uuid):
        now = self.ns3.Simulator.Now()
        if now.IsZero():
            return False

        if self.ns3.Simulator.IsFinished():
            return False

        app = self.get_object(uuid)
        stop_time_value = self.ns3.TimeValue()
        app.GetAttribute("StopTime", stop_time_value)
        stop_time = stop_time_value.Get()

        start_time_value = self.ns3.TimeValue()
        app.GetAttribute("StartTime", start_time_value)
        start_time = start_time_value.Get()
        
        if now.Compare(start_time) >= 0:
            if stop_time.IsZero() or now.Compare(stop_time) < 0:
                return True

        return False
    
    def _is_app_started(self, uuid):
        return self._is_app_running(uuid) or self.is_finished

    def _add_static_route(self, ipv4_uuid, network, prefix, nexthop):
        ipv4 = self.get_object(ipv4_uuid)

        list_routing = ipv4.GetRoutingProtocol()
        (static_routing, priority) = list_routing.GetRoutingProtocol(0)

        ifindex = self._find_ifindex(ipv4, nexthop)
        if ifindex == -1:
            return False
        
        nexthop = self.ns3.Ipv4Address(nexthop)

        if network in ["0.0.0.0", "0", None]:
            # Default route: 0.0.0.0/0
            static_routing.SetDefaultRoute(nexthop, ifindex)
        else:
            mask = self.ns3.Ipv4Mask("/%s" % prefix) 
            network = self.ns3.Ipv4Address(network)

            if prefix == 32:
                # Host route: x.y.z.w/32
                static_routing.AddHostRouteTo(network, nexthop, ifindex)
            else:
                # Network route: x.y.z.w/n
                static_routing.AddNetworkRouteTo(network, mask, nexthop, 
                        ifindex) 
        return True

    def _find_ifindex(self, ipv4, nexthop):
        ifindex = -1

        nexthop = self.ns3.Ipv4Address(nexthop)

        # For all the interfaces registered with the ipv4 object, find
        # the one that matches the network of the nexthop
        nifaces = ipv4.GetNInterfaces()
        for ifidx in xrange(nifaces):
            iface = ipv4.GetInterface(ifidx)
            naddress = iface.GetNAddresses()
            for addridx in xrange(naddress):
                ifaddr = iface.GetAddress(addridx)
                ifmask = ifaddr.GetMask()
                
                ifindex = ipv4.GetInterfaceForPrefix(nexthop, ifmask)

                if ifindex == ifidx:
                    return ifindex
        return ifindex

    def _retrieve_object(self, uuid, typeid, search = False):
        obj = self.get_object(uuid)

        type_id = self.ns3.TypeId()
        tid = type_id.LookupByName(typeid)
        nobj = obj.GetObject(tid)

        newuuid = None
        if search:
            # search object
            for ouuid, oobj in self._objects.iteritems():
                if nobj == oobj:
                    newuuid = ouuid
                    break
        else: 
            newuuid = self.make_uuid()
            self._objects[newuuid] = nobj

        return newuuid

    def _recv_fd(self, uuid):
        """ Waits on a local address to receive a file descriptor
        from a local process. The file descriptor is associated
        to a FdNetDevice to stablish communication between the
        simulation and what ever process writes on that file descriptor
        """

        def recvfd(sock, fdnd):
            (fd, msg) = passfd.recvfd(sock)
            # Store a reference to the endpoint to keep the socket alive
            fdnd.SetFileDescriptor(fd)
        
        import passfd
        import socket
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        sock.bind("")
        address = sock.getsockname()
        
        fdnd = self.get_object(uuid)
        t = threading.Thread(target=recvfd, args=(sock,fdnd))
        t.start()

        return address


