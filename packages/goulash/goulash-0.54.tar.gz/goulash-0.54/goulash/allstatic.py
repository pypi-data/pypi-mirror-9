""" goulash
"""
from types import FunctionType

from goulash.namespaces import Namespace

is_property           = lambda obj: type(obj).__name__=='property'
is_function           = lambda obj: type(obj)==FunctionType
is_nonprivatefunction = lambda name, obj: (not name.startswith('_')) and is_function(obj)
is_staticmethod       = lambda obj: type(obj).__name__=='staticmethod'


class AllStaticMethods(type):
    """ AllStaticMethods:
         set this class as your metaclass in order to build a
         module-like class.. all methods inside the class will
         be turned into static methods.
    """
    def __init__(*args, **kargs):
        return type.__init__(*args, **kargs)

    def __new__(mcs, name, bases, dct, finished=True):
        """
            NOTE: the 'finished' flag is used for chaining..
                  make sure you know what you're doing if you use it.
        """
        for x, func in Namespace(dct).functions.items():
                dct[x] = staticmethod(func)
        if finished:
            return type.__new__(mcs, name, bases, dct)
        else:
            return (mcs, name, bases, dct)
