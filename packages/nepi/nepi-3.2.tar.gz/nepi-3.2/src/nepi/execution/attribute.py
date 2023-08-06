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

### Attribute Types
class Types:
    """ Allowed types for the Attribute value
    """
    String  = "STRING"
    Bool    = "BOOL"
    Enumerate    = "ENUM"
    Double  = "DOUBLE"
    Integer = "INTEGER"

### Attribute Flags
class Flags:
    """ Flags to characterize the scope of an Attribute
    """
    # Attribute value can not be read (it is hidden to the user) 
    NoRead    = 1 # 1
    
    # Attribute value can not be modified (it is not editable by the user)
    NoWrite   = 1 << 1 # 2
    
    # Attribute value can be modified only before deployment
    Design  = 1 << 2 # 4

    # Attribute value will be used at deployment time for initial configuration
    Construct    = 1 << 3 #  8

    # Attribute provides credentials to access resources
    Credential  = 1 << 4  | Design # 16 + 4

    # Attribute is a filter used to discover resources
    Filter  = 1 << 5 | Design # 32 + 4

    # Attribute Flag is reserved for internal RM usage (i.e. should be 
    # transparent to the user)
    Reserved  = 1 << 6 # 64

    # Attribute global is set to all resources of rtype
    Global  = 1 << 7 # 128


class Attribute(object):
    """ An Attribute exposes a configuration parameter of a resource
    """

    def __init__(self, name, help, type = Types.String,
            flags = None, default = None, allowed = None,
            range = None, set_hook = None):
        """
        :param name: Name of the Attribute
        :type name: str

        :param help: Description of the Attribute
        :type help: str
        
        :param type: The type expected for the Attribute value.
                     Should be one of Attribute.Types
        :type type: str

        :param flags: Defines Attribute behavior (i.e. whether it is read-only,
                read and write, etc). This parameter must take its values from
                Attribute.Flags. Flags values can be bitwised
        :type flags: hex

        :param default: Default value for the Attribute
        :type default: Depends on the type of Attribute
        
        :param allowed: List of values that the Attribute can take. 
                This parameter is only meaningful for Enumerate type Attributes
        :type allowed: list
        
        :param range: (max, min) tuple with range of possible values for
                Attributes.
                This parameter is only meaningful for Integer or Double type
                Attributes
        :type range: (int, int) or (float, float)
        
        :param set_hook: Function that will be executed whenever a new 
                value is set for the Attribute.
        :type set_hook: function

    """
        self._name = name
        self._help = help
        self._type = type
        self._flags = flags or 0
        self._allowed = allowed
        self._range = range
        self._default = self._value = default
        # callback to be invoked upon changing the 
        # attribute value
        self.set_hook = set_hook

    @property
    def name(self):
        """ Returns the name of the Attribute """
        return self._name

    @property
    def default(self):
        """ Returns the default value of the Attribute """
        return self._default

    @property
    def type(self):
        """ Returns the type of the Attribute """
        return self._type

    @property
    def help(self):
        """ Returns the description of the Attribute """
        return self._help

    @property
    def flags(self):
        """ Returns the flags of the Attribute """
        return self._flags

    @property
    def allowed(self):
        """ Returns the set of allowed values for the Attribute """
        return self._allowed

    @property
    def range(self):
        """ Returns the range of allowed numerical values for the Attribute """
        return self._range

    def has_flag(self, flag):
        """ Returns True if the Attribute has the flag 'flag'

        :param flag: Flag to be checked
        :type flag: Flags
        """
        return (self._flags & flag) == flag

    def get_value(self):
        """ Returns the value of the Attribute """
        return self._value

    def set_value(self, value):
        """ Configure a new value for the Attribute """
        valid = True

        if self.type == Types.Enumerate:
            valid = value in self._allowed

        if self.type in [Types.Double, Types.Integer] and self.range:
            (min, max) = self.range

            value = float(value)

            valid = (value >= min and value <= max) 
        
        valid = valid and self.is_valid_value(value)

        if valid: 
            if self.set_hook:
                # Hook receives old value, new value
                value = self.set_hook(self._value, value)

            self._value = value
        else:
            raise ValueError("Invalid value %s for attribute %s" %
                    (str(value), self.name))

    value = property(get_value, set_value)

    def is_valid_value(self, value):
        """ Attribute subclasses will override this method to add 
        adequate validation"""
        return True

    @property
    def has_changed(self):
        """ Returns True if the value has changed from the default """
        return self.value != self.default

