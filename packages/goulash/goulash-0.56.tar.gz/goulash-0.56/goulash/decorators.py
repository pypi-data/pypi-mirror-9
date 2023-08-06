""" goulash.decorators
"""
import inspect

class arg_types(object):
    """ A decorator which enforces the rule that all arguments must be
        of type .  All keyword arguments are ignored. Throws ArgTypeError
        when expectations are violated.

        Example usage follows:

          @arg_types(int, float)
          def sum(*args): pass
    """

    class ArgTypeError(TypeError): pass

    def __init__(self, *args):
        err = 'all arguments to arg_types() should be types, got {0}'
        assert all([inspect.isclass(a) for a in args]), err.format(args)
        self.types = args

    def __call__(self, fxn):
        self.fxn = fxn
        def wrapped(*args, **kargs):
            for a in args:
                if not isinstance(a, self.types):
                    raise self.ArgTypeError("{0} (type={1}) is not in {2}".format(
                        a, type(a), self.types))
            return self.fxn(*args, **kargs)
        return wrapped

class memoized_property(object):
    """
    A read-only @property that is only evaluated once.

    From: http://www.reddit.com/r/Python/comments/ejp25/cached_property_decorator_that_is_memory_friendly/
    """
    def __init__(self, fget, doc=None):
        self.fget = fget
        self.__doc__ = doc or fget.__doc__
        self.__name__ = fget.__name__

    def __get__(self, obj, cls):
        if obj is None:
            return self
        obj.__dict__[self.__name__] = result = self.fget(obj)
        return result
