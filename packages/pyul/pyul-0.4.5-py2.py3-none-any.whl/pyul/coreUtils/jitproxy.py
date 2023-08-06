from .event import Event

__all__ = ['JITProxy']


class JITProxy(object):
    """
    A 'just-in-time' proxying wrapper class.  Aids in instanciating classes who's init
    takes far longer then you would like for the init of your app to take and offloads
    that time to directly when the class if first used
    """
    __slots__ = ["_obj", "_klass", "_args", "_kwds", "__weakref__"]

    @staticmethod
    def initObj(obj):
        oga = object.__getattribute__
        if oga(obj, "_obj") is None:
            object.__setattr__(obj,"_obj",
                               oga(obj, "_klass")(*oga(obj, "_args"),
                                                  **oga(obj, "_kwds")))
            oga(obj, "_on_init")(oga(obj, "_obj"))

    def __init__(self, klass, *args, **kwds):
        """
        :param klass: Class of objet to be instantiated just in time
        :param *args: arguments to be used when instantiating object
        :param **kw: keywords to be used when instantiating object
        """
        object.__setattr__(self, "_klass", klass)
        object.__setattr__(self, "_args", args)
        object.__setattr__(self, "_kwds", kwds)
        object.__setattr__(self, "_obj", None)
        object.__setattr__(self, "_on_init", Event())

    #
    # proxying (special cases)
    #
    def __getattribute__(self, name):
        if name == '_on_init' and object.__getattribute__(self, "_obj") is None:
            return object.__getattribute__(self, "_on_init")
        else:
            JITProxy.initObj(self)
            return getattr(object.__getattribute__(self, "_obj"), name)

    def __getattr__(self, name):
        JITProxy.initObj(self)
        return getattr(object.__getattribute__(self, "_obj"), name)

    def __delattr__(self, name):
        delattr(object.__getattribute__(self, "_obj"), name)

    def __setattr__(self, name, value):
        if name == '_on_init' and object.__getattribute__(self, "_obj") is None:
            return setattr(object.__getattribute__(self, "_on_init"), name, value)
        else:        
            JITProxy.initObj(self)
            setattr(object.__getattribute__(self, "_obj"), name, value)

    def __nonzero__(self):
        JITProxy.initObj(self)
        return bool(object.__getattribute__(self, "_obj"))

    def __str__(self):
        JITProxy.initObj(self)
        return str(object.__getattribute__(self, "_obj"))

    def __repr__(self):
        JITProxy.initObj(self)
        return repr(object.__getattribute__(self, "_obj"))

    #
    # factories
    #
    _special_names = [
        '__abs__', '__add__', '__and__', '__call__', '__cmp__', '__coerce__', 
        '__contains__', '__delitem__', '__delslice__', '__div__', '__divmod__', 
        '__eq__', '__float__', '__floordiv__', '__ge__', '__getitem__', 
        '__getslice__', '__gt__', '__hash__', '__hex__', '__iadd__', '__iand__',
        '__idiv__', '__idivmod__', '__ifloordiv__', '__ilshift__', '__imod__', 
        '__imul__', '__int__', '__invert__', '__ior__', '__ipow__', '__irshift__', 
        '__isub__', '__iter__', '__itruediv__', '__ixor__', '__le__', '__len__', 
        '__long__', '__lshift__', '__lt__', '__mod__', '__mul__', '__ne__', 
        '__neg__', '__oct__', '__or__', '__pos__', '__pow__', '__radd__', 
        '__rand__', '__rdiv__', '__rdivmod__', '__reduce__', '__reduce_ex__', 
        '__repr__', '__reversed__', '__rfloorfiv__', '__rlshift__', '__rmod__', 
        '__rmul__', '__ror__', '__rpow__', '__rrshift__', '__rshift__', '__rsub__', 
        '__rtruediv__', '__rxor__', '__setitem__', '__setslice__', '__sub__', 
        '__truediv__', '__xor__', 'next',
    ]

    @classmethod
    def _create_class_proxy(cls, theclass):
        """creates a proxy for the given class"""

        def make_method(name):
            def method(self, *args, **kw):
                return getattr(object.__getattribute__(self, "_obj"), name)(*args, **kw)
            return method

        namespace = {}
        for name in cls._special_names:
            if hasattr(theclass, name):
                namespace[name] = make_method(name)
        return type("%s(%s)" % (cls.__name__, theclass.__name__), (cls,), namespace)

    def __new__(cls, obj, *args, **kwargs):
        """
        creates an proxy instance referencing `obj`. (obj, *args, **kwargs) are
        passed to this class' __init__, so deriving classes can define an 
        __init__ method of their own.
        note: _class_proxy_cache is unique per deriving class (each deriving
        class must hold its own cache)
        """
        try:
            cache = cls.__dict__["_class_proxy_cache"]
        except KeyError:
            cls._class_proxy_cache = cache = {}
        try:
            theclass = cache[obj.__class__]
        except KeyError:
            cache[obj.__class__] = theclass = cls._create_class_proxy(obj.__class__)
        ins = object.__new__(theclass)
        theclass.__init__(ins, obj, *args, **kwargs)
        return ins
