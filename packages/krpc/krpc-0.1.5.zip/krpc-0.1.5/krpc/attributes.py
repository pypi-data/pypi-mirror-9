import re


class _Attributes(object):
    """ Methods for extracting information from procedure attributes """

    @classmethod
    def is_a_procedure(cls, attrs):
        """ Return true if the attributes are for a plain procedure,
            i.e. not a property accessor, class method etc. """
        return not cls.is_a_property_accessor(attrs) and \
               not cls.is_a_class_method(attrs) and \
               not cls.is_a_class_property_accessor(attrs)

    @classmethod
    def is_a_property_accessor(cls, attrs):
        """ Return true if the attributes are for a property getter or setter. """
        return any(attr.startswith('Property.') for attr in attrs)

    @classmethod
    def is_a_property_getter(cls, attrs):
        """ Return true if the attributes are for a property getter. """
        return any(attr.startswith('Property.Get(') for attr in attrs)

    @classmethod
    def is_a_property_setter(cls, attrs):
        """ Return true if the attributes are for a property setter. """
        return any(attr.startswith('Property.Set(') for attr in attrs)

    @classmethod
    def is_a_class_method(cls, attrs):
        """ Return true if the attributes are for a class method. """
        return any(attr.startswith('Class.Method(') for attr in attrs)

    @classmethod
    def is_a_class_property_accessor(cls, attrs):
        """ Return true if the attributes are for a class property getter or setter. """
        return any(attr.startswith('Class.Property.') for attr in attrs)

    @classmethod
    def is_a_class_property_getter(cls, attrs):
        """ Return true if the attributes are for a class property getter. """
        return any(attr.startswith('Class.Property.Get(') for attr in attrs)

    @classmethod
    def is_a_class_property_setter(cls, attrs):
        """ Return true if the attributes are for a class property setter. """
        return any(attr.startswith('Class.Property.Set(') for attr in attrs)

    @classmethod
    def get_property_name(cls, attrs):
        """ Return the name of the property handled by a property getter or setter. """
        if cls.is_a_property_accessor(attrs):
            for attr in attrs:
                match = re.match(r'^Property\.(Get|Set)\((.+)\)$', attr)
                if match:
                    return match.group(2)
        raise ValueError('Procedure attributes are not a property accessor')

    @classmethod
    def get_service_name(cls, attrs):
        """ Return the name of the services that a class method or property accessor is part of. """
        if cls.is_a_class_method(attrs):
            for attr in attrs:
                match = re.match(r'^Class\.Method\(([^,\.]+)\.[^,]+,[^,]+\)$', attr)
                if match:
                    return match.group(1)
        if cls.is_a_class_property_accessor(attrs):
            for attr in attrs:
                match = re.match(r'^Class\.Property.(Get|Set)\(([^,\.]+)\.[^,]+,[^,]+\)$', attr)
                if match:
                    return match.group(2)
        raise ValueError('Procedure attributes are not a class method or class property accessor')

    @classmethod
    def get_class_name(cls, attrs):
        """ Return the name of the class that a method or property accessor is part of. """
        if cls.is_a_class_method(attrs):
            for attr in attrs:
                match = re.match(r'^Class\.Method\([^,\.]+\.([^,\.]+),[^,]+\)$', attr)
                if match:
                    return match.group(1)
        if cls.is_a_class_property_accessor(attrs):
            for attr in attrs:
                match = re.match(r'^Class\.Property.(Get|Set)\([^,\.]+\.([^,]+),[^,]+\)$', attr)
                if match:
                    return match.group(2)
        raise ValueError('Procedure attributes are not a class method or class property accessor')

    @classmethod
    def get_class_method_name(cls, attrs):
        """ Return the name of a class mathod. """
        if cls.is_a_class_method(attrs):
            for attr in attrs:
                match = re.match(r'^Class\.Method\([^,]+,([^,]+)\)$', attr)
                if match:
                    return match.group(1)
        raise ValueError('Procedure attributes are not a class method accessor')

    @classmethod
    def get_class_property_name(cls, attrs):
        """ Return the name of a class property (for a getter or setter procedure). """
        if cls.is_a_class_property_accessor(attrs):
            for attr in attrs:
                match = re.match(r'^Class\.Property\.(Get|Set)\([^,]+,([^,]+)\)$', attr)
                if match:
                    return match.group(2)
        raise ValueError('Procedure attributes are not a class property accessor')

    @classmethod
    def get_return_type_attrs(cls, attrs):
        """ Return the attributes for the return type of a procedure. """
        return_type_attrs = []
        for attr in attrs:
            match = re.match(r'^ReturnType.(.+)$', attr)
            if match:
                return_type_attrs.append(match.group(1))
        return return_type_attrs

    @classmethod
    def get_parameter_type_attrs(cls, pos, attrs):
        """ Return the attributes for a specific parameter of a procedure. """
        parameter_type_attrs = []
        for attr in attrs:
            match = re.match(r'^ParameterType\(' + str(pos) + '\).(.+)$', attr)
            if match:
                parameter_type_attrs.append(match.group(1))
        return parameter_type_attrs
