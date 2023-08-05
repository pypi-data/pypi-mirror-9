"""The class and functions of this file form the interface for the Epicenter
variable API GET and PATCH calls. It allows custom setters and 
"""
import types
import sys
import ast
from operator import setitem
import re

version = sys.version_info
if version[0] >= 3:
    PYTHON3 = True
else:
    PYTHON3 = False
del version


class SetterError(Exception):
    def __init__(self, message):
        self.message = message


class VariableSetter(object):
    Model_Module = None

    default_updaters = {}
    custom_updaters = {}
    setattr_types = {}
    atomic_types = set()

    @classmethod
    def register_direct_setters(cls):
        """Register the values that can be used directly
        """
        cls.setattr_types[dict] = cls.direct_dict_setter
        cls.setattr_types[object] = cls.direct_object_setter
        cls.setattr_types['__slots__'] = cls.direct_slots_setter

    @classmethod
    def register_atomic_types(cls):
        """Types that can be directly set without recursing
        """
        cls.atomic_types.add(int)
        cls.atomic_types.add(float)
        cls.atomic_types.add(bool)
        if not PYTHON3:
            cls.atomic_types.add(unicode)
        cls.atomic_types.add(str)
        cls.atomic_types.add(list)


    @classmethod
    def register_default_updaters(cls):
        """Register the default variable setters
        """
        cls.default_updaters[int] = cls.int_setter
        cls.default_updaters[float] = cls.float_setter
        cls.default_updaters[bool] = cls.bool_setter
        if not PYTHON3:
            cls.default_updaters[unicode] = cls.unicode_setter
        cls.default_updaters[str] = cls.string_setter
        cls.default_updaters[dict] = cls.dict_setter
        cls.default_updaters[list] = cls.list_setter
        cls.default_updaters[set] = cls.set_setter
        cls.default_updaters[object] = cls.object_setter
        cls.default_updaters['__slots__'] = cls.slots_setter

    @classmethod
    def register_custom_updater(cls, custom_type, setter, prefix=True):
        """Register a custom variable setter
        """
        setattr(cls, setter.__name__, types.MethodType(setter, cls))
        cls.custom_updaters[custom_type] = getattr(cls, setter.__name__)

    @classmethod
    def set_module(cls, model):
        """Set the model that will be used as the base namespace
        """
        cls.Model_Module = model

    @classmethod
    def update_variable(cls, name, value, base_object=None):
        """
        """
        if base_object is None:
            base_object = cls.Model_Module
        try:
            variable = eval("cls.Model_Module.{name}".format(name=name))
            setter = cls.choose_updater(variable)
            setter(base_object, name, value)
        # Make AttributeError, into name errors
        except AttributeError as ae:
            raise NameError(ae.args[0])
        return eval("cls.Model_Module.{name}".format(name=name))

    @classmethod
    def choose_updater(cls, variable):
        """Choose the setter used for the variable.
        """
        variable_type = type(variable)
        if variable_type in cls.custom_updaters:
            return cls.custom_updaters[variable_type]

        if variable_type not in cls.default_updaters:
            if hasattr(variable, '__dict__'):
                variable_type = '__dict__'
            elif hasattr(variable, '__slots__'):
                variable_type = '__slots__'

        if variable_type in cls.default_updaters:
            return cls.default_updaters[variable_type]
        elif variable_type == "__dict__":
            return cls.default_updaters[object]
        else:  # default is to just try to make a dict of it.
            return cls.default_updaters[dict]

    @classmethod
    def get_direct_setter(cls, variable):
        """
        """
        variable_type = type(variable)
        if variable_type not in cls.setattr_types:
            if hasattr(variable, '__slots__'):
                variable_type = '__slots__'
            elif hasattr(variable, '__dict__'):
                variable_type = '__dict__'

        if variable_type in cls.setattr_types:
            return cls.setattr_types[variable_type]
        elif variable_type == "__dict__":
            return cls.setattr_types[object]
        else:  # default is to just try to make a dict of it.
            return cls.setattr_types[dict]

    # Checks if an atomic setter should use setitem or setattr
    brackets = re.compile('(?P<base>.*)\[(?P<key>.*)\]')            

    @classmethod
    def int_setter(cls, base_object, name, value):
        """Set an integer
        """
        match = cls.brackets.match(name)
        if match is not None:
            parent = eval('cls.Model_Module.{name}'.
                          format(name=match.group('base')))
            setitem(parent, eval(match.group('key')), int(value))
        else:
            parent_name, attribute_name = \
                cls._split_parent_attribute_name(name)
            parent = eval(parent_name)
            setattr(parent, attribute_name, int(value))

    @classmethod
    def float_setter(cls, base_object, name, value):
        """Set a float
        """
        match = cls.brackets.match(name)
        if match is not None:
            parent = eval('cls.Model_Module.{name}'.
                          format(name=match.group('base')))
            setitem(parent, eval(match.group('key')), float(value))
        else:
            parent_name, attribute_name = \
                cls._split_parent_attribute_name(name)
            parent = eval(parent_name)
            setattr(parent, attribute_name, float(value))

    @classmethod
    def _split_parent_attribute_name(cls, name):
        """Get the name of the parent object and the attribute.
        e.g., if the name is `model.data.x`, then the parent object is
        `model.name`
        """
        full_name = 'cls.Model_Module.{name}'.format(name=name)
        split_name = full_name.rsplit('.', 1)
        parent_name = split_name[0]
        attribute_name = split_name[-1]
        return parent_name, attribute_name

    @classmethod
    def string_setter(cls, base_object, name, value):
        """Set a string in Python 3
        """
        match = cls.brackets.match(name)
        if match is not None:
            parent = eval('cls.Model_Module.{name}'.
                          format(name=match.group('base')))
            setitem(parent, eval(match.group('key')), value)
        else:
            parent_name, attribute_name = \
                cls._split_parent_attribute_name(name)
            parent = eval(parent_name)
            setattr(parent, attribute_name, value)

    @classmethod
    def unicode_setter(cls, base_object, name, value):
        """Set a unicode string
        """
        match = cls.brackets.match(name)
        if match is not None:
            parent = eval('cls.Model_Module.{name}'.
                          format(name=match.group('base')))
            setitem(parent, eval(match.group('key')), value)
        else:
            parent_name, attribute_name = \
                cls._split_parent_attribute_name(name)
            parent = eval(parent_name)
            setattr(parent, attribute_name, value)

    @classmethod
    def format_bool(cls, value):
        """Format a boolean. Silly javascript.
        """
        if str(value) == "false" or str(value) == "False":
            value = False
        elif str(value) == "true" or str(value) == "True":
            value = True
        else:
            raise SetterError("Cannot figure out what boolean value to use")
        return value

    @classmethod
    def format_value(cls, variable_type, value):
        """Format an atomic type
        """
        if variable_type is bool:
            return cls.format_bool(value)
        elif variable_type is list:
            return ast.literal_eval(str(value))
        else:
            return variable_type(value)

    @classmethod
    def bool_setter(cls, base_object, name, value):
        """Set a boolean
        """
        value = cls.format_bool(value)
        match = cls.brackets.match(name)
        if match is not None:
            parent = eval('cls.Model_Module.{name}'.
                          format(name=match.group('base')))
            setitem(parent, eval(match.group('key')), value)
        else:
            parent_name, attribute_name = \
                cls._split_parent_attribute_name(name)
            parent = eval(parent_name)
            setattr(parent, attribute_name, value)

    @classmethod
    def list_setter(cls, base_object, name, value):
        """Set a list
        """
        new_list = ast.literal_eval(str(value))
        if not isinstance(new_list, list):
            raise SetterError("Cannot set a list with a non-list value")

        match = cls.brackets.match(name)
        if match is not None:
            parent = eval('cls.Model_Module.{name}'.
                          format(name=match.group('base')))
            setitem(parent, eval(match.group('key')), value)
        else:
            parent_name, attribute_name = \
                cls._split_parent_attribute_name(name)
            parent = eval(parent_name)
            setattr(parent, attribute_name, value)

    @classmethod
    def dict_setter(cls, base_object, name, value):
        """Set a dictionary
        """
        new_dict = ast.literal_eval(str(value))
        if not isinstance(new_dict, dict):
            raise SetterError("Cannot update dict with non-dict value")

        old_dict = eval("cls.Model_Module.{name}".format(name=name))
        cls.direct_dict_setter(old_dict, new_dict)

    @classmethod
    def direct_dict_setter(cls, old_dict, new_dict):
        """Set a dictionary directly without needing the variable name
        """
        for new_key in new_dict:
            formatted_key = cls.format_key(new_key)
            if formatted_key not in old_dict:
                old_dict.__setitem__(formatted_key, new_dict[new_key])
            else:
                variable_type = type(old_dict[formatted_key])
                if variable_type in cls.atomic_types:
                    value = cls.format_value(variable_type, new_dict[new_key])
                    old_dict.__setitem__(formatted_key, value)
                else:
                    setter = cls.get_direct_setter(old_dict[formatted_key])
                    setter(old_dict[formatted_key], new_dict[new_key])

    @classmethod
    def object_setter(cls, base_object, name, value):
        """Set an object
        """
        new_dict = ast.literal_eval(str(value))
        if not isinstance(new_dict, dict):
            raise SetterError("Cannot update an object with a non-dict value")

        old_object = eval("cls.Model_Module.{name}".format(name=name))
        cls.direct_object_setter(old_object, new_dict)

    @classmethod
    def direct_object_setter(cls, old_object, new_dict):
        """Set an object directly without needing the variable name
        """
        for new_key in new_dict:
            if not hasattr(old_object, new_key):
                setattr(old_object, new_key, new_dict[new_key])
            else:
                variable_type = type(getattr(old_object, new_key))
                if variable_type in cls.atomic_types:
                    value = cls.format_value(variable_type, new_dict[new_key])
                    setattr(old_object, new_key, value)
                else:
                    variable = getattr(old_object, new_key)
                    setter = cls.get_direct_setter(variable)
                    setter(variable, new_dict[new_key])

    @classmethod
    def slots_setter(cls, base_object, name, value):
        """Set an object with slots
        """
        new_dict = eval(str(value))
        if not isinstance(new_dict, dict):
            raise SetterError("Cannot update an object with a non-dict value")

        old_object = eval("cls.Model_Module.{name}".format(name=name))
        cls.direct_slots_setter(old_object, new_dict)

    @classmethod
    def direct_slots_setter(cls, old_object, new_dict):
        """Set an object directly without needing the variable name
        """
        for new_key in new_dict:
            if not hasattr(old_object, new_key):
                continue
            else:
                variable_type = type(getattr(old_object, new_key))
                if variable_type in cls.atomic_types:
                    value = cls.format_value(variable_type, new_dict[new_key])
                    setattr(old_object, new_key, value)
                else:
                    variable = getattr(old_object, new_key)
                    setter = cls.get_direct_setter(variable)
                    setter(variable, new_dict[new_key])

    @classmethod
    def set_setter(cls, base_object, name, value):
        """Symmetric difference a set object
        """
        new_set = set(value)
        exec("cls.Model_Module.{name} = cls.Model_Module.{name} ^ new_set".
             format(name=name))

    @classmethod
    def format_key(cls, key):
        """Try to guess the proper type of the given key
        """
        converted = False
        if not converted:
            try:
                new_key = float(key)
                if str(new_key) == key:
                    key = new_key
                    converted = True
            except ValueError:
                pass

        if not converted:
            try:
                new_key = int(key)
                if str(new_key) == key:
                    key = new_key
                    converted = True
            except ValueError:
                pass

        if not converted:
            key = key.encode("unicode_escape").decode('utf-8')

        return key


def custom_class_setter(cls, base_object, complex_name, complex_value):
    """Implement complex types as a custom setter. Complex value
    should be a dictionary with two fields: "real" and "imaginary".
    """
    exec("cls.Model_Module.{name} = complex(complex_value['real'],"
         "complex_value['imaginary'])".
         format(name=complex_name))

VariableSetter.register_custom_updater(complex, custom_class_setter, False)
VariableSetter.register_default_updaters()
VariableSetter.register_direct_setters()
VariableSetter.register_atomic_types()