import os
import re
import types
import string
from pyul.support import Path

__all__ = ['get_class_name','wildcard_to_re',
           'get_user_temp_dir','synthesize',
           'is_descriptor','is_dunder','is_sunder',
           'split_path','block_indent','safe_format']


def get_class_name(x):
    if not isinstance(x, basestring):
        if type(x) in [types.FunctionType, types.TypeType, types.ModuleType] :
            return x.__name__
        else:
            return x.__class__.__name__
    else:
        return x


def wildcard_to_re(pattern):
    """Translate a wildcard pattern to a regular expression"""
    i, n = 0, len(pattern)
    res = '(?i)' # case insensitive re
    while i < n:
        c = pattern[i]
        i = i+1
        if c == '*':
            res = res + r'[^\\]*'
        elif c == '/':
            res = res + re.escape('\\')
        else:
            res = res + re.escape(c)
    return res + "$"


def get_user_temp_dir(temp_dirname='.tmp'):
    """
    Returns a path to a temp directory within the user folder
    
    :param dirname: A string representing the temp folder's name
    
    """
    return Path(os.path.expanduser('~')).joinpath(temp_dirname)


def synthesize(inst, name, value, readonly=False):
    """
    Convenience method to create getters, setters and a property for the instance.
    Should the instance already have the getters or setters defined this won't add them
    and the property will reference the already defined getters and setters
    Should be called from within __init__. Creates [name], get[Name], set[Name], 
    _[name] on inst.

    :param inst: An instance of the class to add the methods to.
    :param name: The base name to build the function names, and storage variable.
    :param value: The initial state of the created variable.

    """
    cls = type(inst)
    storageName = '_{0}'.format(name)
    getterName = 'get{0}{1}'.format(name[0].capitalize(), name[1:])
    setterName = 'set{0}{1}'.format(name[0].capitalize(), name[1:])
    deleterName = 'del{0}{1}'.format(name[0].capitalize(), name[1:])

    setattr(inst, storageName, value)

    # We always define the getter
    def customGetter(self):
        return getattr(self, storageName)

    # Add the Getter
    if not hasattr(inst, getterName):
        setattr(cls, getterName, customGetter)

    # Handle Read Only
    if readonly :
        if not hasattr(inst, name):
            setattr(cls, name, property(fget=getattr(cls, getterName, None) or customGetter, fdel=getattr(cls, getterName, None)))
    else:
        # We only define the setter if we arn't read only
        def customSetter(self, state):
            setattr(self, storageName, state)        
        if not hasattr(inst, setterName):
            setattr(cls, setterName, customSetter)
        member = None
        if hasattr(cls, name):
            # we need to try to update the property fget, fset, fdel incase the class has defined its own custom functions
            member = getattr(cls, name)
            if not isinstance(member, property):
                raise ValueError('Member "{0}" for class "{1}" exists and is not a property.'.format(name, cls.__name__))
        # Reguardless if the class has the property or not we still try to set it with
        setattr(cls, name, property(fget=getattr(member, 'fget', None) or getattr(cls, getterName, None) or customGetter,
                                    fset=getattr(member, 'fset', None) or getattr(cls, setterName, None) or customSetter,
                                    fdel=getattr(member, 'fdel', None) or getattr(cls, getterName, None)))


def is_descriptor(obj):
    """Returns True if obj is a descriptor, False otherwise."""
    return (
            hasattr(obj, '__get__') or
            hasattr(obj, '__set__') or
            hasattr(obj, '__delete__'))


def is_dunder(name):
    """Returns True if a __dunder__ name, False otherwise."""
    return (name[:2] == name[-2:] == '__' and
            name[2:3] != '_' and
            name[-3:-2] != '_' and
            len(name) > 4)


def is_sunder(name):
    """Returns True if a _sunder_ name, False otherwise."""
    return (name[0] == name[-1] == '_' and
            name[1:2] != '_' and
            name[-2:-1] != '_' and
            len(name) > 2)


def split_path(filepath):
    """Returns (drive, parts) of the given filepath"""
    parts = []
    drive, _ = os.path.splitdrive(filepath)
    while True:
        newpath, tail = os.path.split(filepath)
        if newpath == filepath:
            assert not tail
            if filepath: parts.append(filepath)
            break
        parts.append(tail)
        filepath = newpath
    parts.reverse()
    return drive, parts


def block_indent(string, spaces=4):
    """Returns the given multiline string indented by the number of spaces given"""
    return "\n".join((spaces * " ") + i for i in string.splitlines())


class SafeDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'


FORMATTER = string.Formatter()
def safe_format(string, *args, **kwargs):
    return FORMATTER.vformat(string, args, SafeDict(**kwargs))
