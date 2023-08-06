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

import ipaddr
import networkx
import math
import random

class TopologyType:
    LINEAR = "linear"
    LADDER = "ladder"
    MESH = "mesh"
    TREE = "tree"
    STAR = "star"
    ADHOC = "adhoc"

## TODO: 
##      - AQ: Add support for hypergraphs (to be able to add hyper edges to 
##        model CSMA or wireless networks)

class NetGraph(object):
    """ NetGraph represents a network topology. 
    Network graphs are internally using the networkx library.

    """

    def __init__(self, **kwargs):
        """ A graph can be generated using a specified pattern 
        (LADDER, MESH, TREE, etc), or provided as an argument.

            :param topology: Undirected graph to use as internal representation 
            :type topology: networkx.Graph

            :param topo_type: One of TopologyType.{LINEAR,LADDER,MESH,TREE,STAR}
            used to automatically generate the topology graph. 
            :type topo_type: TopologyType

            :param node_count: Number of nodes in the topology to be generated. 
            :type node_count: int

            :param branches: Number of branches (arms) for the STAR topology. 
            :type branches: int


            :param assign_ips: Automatically assign IP addresses to each node. 
            :type assign_ips: bool

            :param network: Base network segment for IP address assignment.
            :type network: str

            :param prefix: Base network prefix for IP address assignment.
            :type prefix: int

            :param version: IP version for IP address assignment.
            :type version: int

            :param assign_st: Select source and target nodes on the graph.
            :type assign_st: bool

	    :param sources_targets: dictionary with the list of sources (key =
            "sources") and list of targets (key = "targets") if defined, ignore
            assign_st
	    :type sources_targets: dictionary of lists

	    :param leaf_source: if True, random sources will be selected only 
            from leaf nodes.
	    :type leaf_source: bool

        NOTE: Only point-to-point like network topologies are supported for now.
                (Wireless and Ethernet networks were several nodes share the same
                edge (hyperedge) can not be modeled for the moment).

        """
        self._topology = kwargs.get("topology")
        self._topo_type = kwargs.get("topo_type", TopologyType.ADHOC)

        if not self.topology:
            if kwargs.get("node_count"):
                node_count = kwargs["node_count"]
                branches = kwargs.get("branches")

                self._topology = self.generate_topology(self.topo_type, 
                        node_count, branches = branches)
            else:
                self._topology = networkx.Graph()

        if kwargs.get("assign_ips"):
            network = kwargs.get("network", "10.0.0.0")
            prefix = kwargs.get("prefix", 8)
            version = kwargs.get("version", 4)

            self.assign_p2p_ips(network = network, prefix = prefix, 
                    version = version)

    	sources_targets = kwargs.get("sources_targets")
	if sources_targets:
            [self.set_source(n) for n in sources_targets["sources"]]
	    [self.set_target(n) for n in sources_targets["targets"]]
	elif kwargs.get("assign_st"):
            self.select_target_zero()
            self.select_random_source(is_leaf = kwargs.get("leaf_source"))

    @property
    def topology(self):
        return self._topology

    @property
    def topo_type(self):
        return self._topo_type

    @property
    def order(self):
        return self.topology.order()

    def nodes(self):
        return self.topology.nodes()

    def edges(self):
        return self.topology.edges()

    def generate_topology(self, topo_type, node_count, branches = None):
        if topo_type == TopologyType.LADDER:
            total_nodes = node_count/2
            graph = networkx.ladder_graph(total_nodes)

        elif topo_type == TopologyType.LINEAR:
            graph = networkx.path_graph(node_count)

        elif topo_type == TopologyType.MESH:
            graph = networkx.complete_graph(node_count)

        elif topo_type == TopologyType.TREE:
            h = math.log(node_count + 1)/math.log(2) - 1
            graph = networkx.balanced_tree(2, h)

        elif topo_type == TopologyType.STAR:
            graph = networkx.Graph()
            graph.add_node(0)

            nodesinbranch = (node_count - 1)/ BRANCHES
            c = 1

            for i in xrange(BRANCHES):
                prev = 0
                for n in xrange(1, nodesinbranch + 1):
                    graph.add_node(c)
                    graph.add_edge(prev, c)
                    prev = c
                    c += 1

        return graph

    def add_node(self, nid):
        if nid not in self.topology: 
            self.topology.add_node(nid)

    def add_edge(self, nid1, nid2):
        self.add_node(nid1)
        self.add_node( nid2)

        if nid1 not in self.topology[nid2]:
            self.topology.add_edge(nid2, nid1)

    def annotate_node_ip(self, nid, ip):
        if "ips" not in self.topology.node[nid]:
            self.topology.node[nid]["ips"] = list()

        self.topology.node[nid]["ips"].append(ip)
 
    def node_ip_annotations(self, nid):
        return self.topology.node[nid].get("ips", [])
   
    def annotate_node(self, nid, name, value):
        if not isinstance(value, str) and not isinstance(value, int) and \
                not isinstance(value, float) and not isinstance(value, bool):
            raise RuntimeError, "Non-serializable annotation"

        self.topology.node[nid][name] = value
    
    def node_annotation(self, nid, name):
        return self.topology.node[nid].get(name)

    def node_annotations(self, nid):
        return self.topology.node[nid].keys()
    
    def del_node_annotation(self, nid, name):
        del self.topology.node[nid][name]

    def annotate_edge(self, nid1, nid2, name, value):
        if not isinstance(value, str) and not isinstance(value, int) and \
                not isinstance(value, float) and not isinstance(value, bool):
            raise RuntimeError, "Non-serializable annotation"

        self.topology.edge[nid1][nid2][name] = value
   
    def annotate_edge_net(self, nid1, nid2, ip1, ip2, mask, network, 
            prefixlen):
        self.topology.edge[nid1][nid2]["net"] = dict()
        self.topology.edge[nid1][nid2]["net"][nid1] = ip1
        self.topology.edge[nid1][nid2]["net"][nid2] = ip2
        self.topology.edge[nid1][nid2]["net"]["mask"] = mask
        self.topology.edge[nid1][nid2]["net"]["network"] = network
        self.topology.edge[nid1][nid2]["net"]["prefix"] = prefixlen

    def edge_net_annotation(self, nid1, nid2):
        return self.topology.edge[nid1][nid2].get("net", dict())
 
    def edge_annotation(self, nid1, nid2, name):
        return self.topology.edge[nid1][nid2].get(name)
 
    def edge_annotations(self, nid1, nid2):
        return self.topology.edge[nid1][nid2].keys()
    
    def del_edge_annotation(self, nid1, nid2, name):
        del self.topology.edge[nid1][nid2][name]

    def assign_p2p_ips(self, network = "10.0.0.0", prefix = 8, version = 4):
        """ Assign IP addresses to each end of each edge of the network graph,
        computing all the point to point subnets and addresses in the network
        representation.

            :param network: Base network address used for subnetting. 
            :type network: str

            :param prefix: Prefix for the base network address used for subnetting.
            :type prefixt: int

            :param version: IP version (either 4 or 6).
            :type version: int

        """
        if networkx.number_connected_components(self.topology) > 1:
            raise RuntimeError("Disconnected graph!!")

        # Assign IP addresses to host
        netblock = "%s/%d" % (network, prefix)
        if version == 4:
            net = ipaddr.IPv4Network(netblock)
            new_prefix = 30
        elif version == 6:
            net = ipaddr.IPv6Network(netblock)
            new_prefix = 30
        else:
            raise RuntimeError, "Invalid IP version %d" % version
        
        ## Clear all previusly assigned IPs
        for nid in self.topology.nodes():
            self.topology.node[nid]["ips"] = list()

        ## Generate and assign new IPs
        sub_itr = net.iter_subnets(new_prefix = new_prefix)
        
        for nid1, nid2 in self.topology.edges():
            #### Compute subnets for each link
            
            # get a subnet of base_add with prefix /30
            subnet = sub_itr.next()
            mask = subnet.netmask.exploded
            network = subnet.network.exploded
            prefixlen = subnet.prefixlen

            # get host addresses in that subnet
            i = subnet.iterhosts()
            addr1 = i.next()
            addr2 = i.next()

            ip1 = addr1.exploded
            ip2 = addr2.exploded
            self.annotate_edge_net(nid1, nid2, ip1, ip2, mask, network, 
                    prefixlen)

            self.annotate_node_ip(nid1, ip1)
            self.annotate_node_ip(nid2, ip2)

    def get_p2p_info(self, nid1, nid2):
        net = self.topology.edge[nid1][nid2]["net"]
        return ( net[nid1], net[nid2], net["mask"], net["network"], 
                net["prefixlen"] )

    def set_source(self, nid):
        self.topology.node[nid]["source"] = True

    def is_source(self, nid):
        return self.topology.node[nid].get("source")

    def set_target(self, nid):
        self.topology.node[nid]["target"] = True

    def is_target(self, nid):
        return self.topology.node[nid].get("target")

    def targets(self):
        """ Returns the nodes that are targets """
        return [nid for nid in self.topology.nodes() \
                if self.topology.node[nid].get("target")]

    def sources(self):
        """ Returns the nodes that are sources """
        return [nid for nid in self.topology.nodes() \
                if self.topology.node[nid].get("source")]

    def select_target_zero(self):
        """ Mark the node 0 as target
        """
        nid = 0 if 0 in self.topology.nodes() else "0"
        self.set_target(nid)

    def select_random_source(self, **kwargs):
        """  Mark a random node as source. 
        """

        # The ladder is a special case because is not symmetric.
        if self.topo_type == TopologyType.LADDER:
            total_nodes = self.order/2
            leaf1 = total_nodes
            leaf2 = total_nodes - 1
            leaves = [leaf1, leaf2]
            source = leaves.pop(random.randint(0, len(leaves) - 1))
        else:
            # options must not be already sources or targets
            options = [ k for k,v in self.topology.degree().iteritems() \
                    if (not kwargs.get("is_leaf") or v == 1)  \
                        and not self.topology.node[k].get("source") \
                        and not self.topology.node[k].get("target")]
            source = options.pop(random.randint(0, len(options) - 1))
        
        self.set_source(source)

