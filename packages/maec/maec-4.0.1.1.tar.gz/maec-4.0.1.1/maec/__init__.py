__version__ = "4.0.1.1"

import collections
import json
from StringIO import StringIO
import bindings.maec_bundle as bundle_binding
import bindings.maec_package as package_binding

class Entity(object):
    """Base class for all classes in the MAEC SimpleAPI."""

    def __eq__(self, other):
        # This fixes some strange behavior where an object isn't equal to
        # itself
        if other is self:
            return True

        # I'm not sure about this, if we want to compare exact classes or if
        # various subclasses will also do (I think not), but for now I'm going
        # to assume they must be equal. - GTB
        if self.__class__ != other.__class__:
            return False

    def to_xml(self):
        """Export an object as an XML String"""

        s = StringIO()
        self.to_obj().export(s, 0)
        return s.getvalue()
        
    def to_xml_file(self, filename):
        """Export an object to an XML file. Only supports Package or Bundle objects at the moment."""
  
        from maec.utils import MAECNamespaceParser
        out_file  = open(filename, 'w')
        out_file.write("<?xml version='1.0' encoding='UTF-8'?>\n")
        out_file.write("<!DOCTYPE doc [<!ENTITY comma '&#44;'>]>\n")
        self.to_obj().export(out_file, 0, namespacedef_=MAECNamespaceParser(self.to_obj()).get_namespace_schemalocation_str())
        out_file.close()

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def istypeof(cls, obj):
        """Check if `cls` is the type of `obj`

        In the normal case, as implemented here, a simple isinstance check is
        used. However, there are more complex checks possible.
        """
        return isinstance(obj, cls)


class EntityList(collections.MutableSequence, Entity):
    _contained_type = object

    def __init__(self):
        self._inner = []

    def __getitem__(self, key):
        return self._inner.__getitem__(key)

    def __setitem__(self, key, value):
        if not self._is_valid(value):
            value = self._try_fix_value(value)
        self._inner.__setitem__(key, value)

    def __delitem__(self, key):
        self._inner.__delitem__(key)

    def __len__(self):
        return len(self._inner)

    def insert(self, idx, value):
        if not self._is_valid(value):
            value = self._try_fix_value(value)
        self._inner.insert(idx, value)

    def _is_valid(self, value):
        """Check if this is a valid object to add to the list.

        If the function is not overridden, only objects of type
        _contained_type can be added.
        """
        return isinstance(value, self._contained_type)

    def _try_fix_value(self, value):
        new_value = self._fix_value(value)
        if not new_value:
            raise ValueError("Can't put '%s' (%s) into a %s" %
                (value, type(value), self.__class__))
        return new_value

    def _fix_value(self, value):
        """Attempt to coerce value into the correct type.

        Subclasses should define this function.
        """
        pass

    # The next four functions can be overridden, but otherwise define the
    # default behavior for EntityList subclasses which define the following
    # class-level members:
    # - _binding_class
    # - _binding_var
    # - _contained_type

    def to_obj(self, object_type=None):
        tmp_list = [x.to_obj() for x in self]

        if not object_type:
            list_obj = self._binding_class()
        else:
            list_obj = object_type

        setattr(list_obj, self._binding_var, tmp_list)

        return list_obj

    def to_list(self):
        return [h.to_dict() for h in self]

    @classmethod
    def from_obj(cls, list_obj, list_class=None):
        if not list_obj:
            return None

        if not list_class:
            list_ = cls()
        else:
            list_ = list_class

        for item in getattr(list_obj, cls._binding_var):
            list_.append(cls._contained_type.from_obj(item))

        return list_

    @classmethod
    def from_list(cls, list_list, list_class=None):
        if not isinstance(list_list, list):
            return None

        if not list_class:
            list_ = cls()
        else:
            return None

        for item in list_list:
            list_.append(cls._contained_type.from_dict(item))

        return list_

# Parse a MAEC instance and return the correct Binding object
# Returns a tuple where pos 0 = Package, and pos 1 = Bundle, or None 
def parse_xml_instance(filename):
    package_obj = package_binding.parse(filename)
    bundle_obj = bundle_binding.parse(filename)
    
    if not bundle_obj.hasContent_():
        return (package_obj, None)
    elif package_obj.hasContent_():
        return (None, bundle_obj)