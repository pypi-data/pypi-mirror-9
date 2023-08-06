import sys
import __builtin__
import copy
__all__ = ['ImportModule','RollbackImporter']
BLACKLIST = ["unittest", "logging", "warnings"]


def _resolve_name(name, package, level):
    """Return the absolute name of the module to be imported."""
    if not hasattr(package, 'rindex'):
        raise ValueError("'package' not set to a string")
    dot = len(package)
    for x in range(level, 1, -1):
        try:
            dot = package.rindex('.', 0, dot)
        except ValueError:
            raise ValueError("attempted relative import beyond top-level "
                             "package")
    return "{0}.{1}".format(package[:dot], name)


def ImportModule(name, package=None):
    """Import a module.

    The 'package' argument is required when performing a relative import. It
    specifies the package to use as the anchor point from which to resolve the
    relative import to an absolute import.

    """
    if name.startswith('.'):
        if not package:
            raise TypeError("relative imports require the 'package' argument")
        level = 0
        for character in name:
            if character != '.':
                break
            level += 1
        name = _resolve_name(name[level:], package, level)
    __import__(name)
    return sys.modules[name]


class RollbackImporter(object):
    '''RollbackImporter installs itself as a proxy for the built-in __import__ function
    that lies behind the 'import' statement. Once installed,
    they note all imported modules, and when uninstalled or restarted,
    they delete those modules from the system module list;
    this ensures that the modules will be freshly loaded from their source code when next imported.
    '''
    _instance = None

    @classmethod
    def instance(cls):
        if not cls._instance:
            print "Making new RollbackImporter Instance"
            cls._instance = cls()
        return cls._instance   

    def __init__(self):
        "Creates and installs as the global importer"
        self.install()

    def _import(self, name, globals=None, locals=None, fromlist=[], level = -1):
        result = apply(self.realImport, (name, globals, locals, fromlist, level))
        if len(name) <= len(result.__name__):
            name = copy.copy(result.__name__)
        for b in BLACKLIST:
            if b in name.lower():
                return result        
        # Remember import in the right order
        if name not in self.previousModules:
            # Only remember once
            if name not in self.newModules:                            
                self.newModules += [name]
        return result

    def install(self):
        self.previousModules = sys.modules.copy()
        self.realImport = __builtin__.__import__
        __builtin__.__import__ = self._import
        self.newModules = []

    def uninstall(self):
        for modname in self.newModules:
            if not self.previousModules.has_key(modname):
                # Force reload when modname next imported
                del(sys.modules[modname])
        __builtin__.__import__ = self.realImport

    @classmethod
    def restart(cls):
        cls.instance().uninstall()
        cls.instance().install()
