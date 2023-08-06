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
# Author: Julien Tribino <julien.tribino@inria.fr>
#         Lucia Guevgeozian <lucia.guevgeozian_odizzio@inria.fr>

from nepi.execution.attribute import Attribute, Flags, Types
from nepi.execution.resource import ResourceManager, clsinit_copy, \
        ResourceState


class ResourceGateway:
    """
    Dictionary used to set OMF gateway depending on Testbed information.
    """
    #XXX: A.Q. COMMENT: This looks a bit hardcoded
    #       SHOULDN'T THIS BE IN A SEPARATED FILE RATHER THAN IN THE 
    #       BASE CLASS FOR ALL OMF RESOURCES?
    TestbedtoGateway = dict({
        "wilabt" : "ops.wilab2.ilabt.iminds.be",
        "nitos" : "nitlab.inf.uth.gr",
        "nicta" : "??.??.??",
    })

    AMtoGateway = dict({
        "am.wilab2.ilabt.iminds.be" : "ops.wilab2.ilabt.iminds.be",
        "nitlab.inf.uth.gr" : "nitlab.inf.uth.gr",
        "nicta" : "??.??.??",
    })

@clsinit_copy
class OMFResource(ResourceManager):
    """
    Generic resource gathering XMPP credential information and common methods
    for OMF nodes, channels, applications, etc.
    """
    _rtype = "abstract::omf::Resource"
    _platform = "omf"

    @classmethod
    def _register_attributes(cls):

        xmppServer = Attribute("xmppServer", "Xmpp Server",
            flags = Flags.Credential)
        xmppUser = Attribute("xmppUser","Name of the Xmpp User/Slice", 
            flags = Flags.Credential)
        xmppPort = Attribute("xmppPort", "Xmpp Port",
            flags = Flags.Credential)
        xmppPassword = Attribute("xmppPassword", "Xmpp Password",
                flags = Flags.Credential)
        version = Attribute("version", "Version of OMF : Either 5 or 6",
                default = "6", )

        cls._register_attribute(xmppUser)
        cls._register_attribute(xmppServer)
        cls._register_attribute(xmppPort)
        cls._register_attribute(xmppPassword)
        cls._register_attribute(version)

    def __init__(self, ec, guid):
        super(OMFResource, self).__init__(ec, guid)
        pass

