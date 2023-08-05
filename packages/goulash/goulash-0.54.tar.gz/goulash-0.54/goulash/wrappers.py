""" goulash.wrappers
"""

class JSONWrapper(object):
    # convenience wrapper that makes __getattr__
    # work via __getitem__
    def __init__(self, data):
        self._data = data

    def __getattr__(self, name):
        try:
            return self._data[name]
        except KeyError:
            return getattr(self._data, name)
    __getitem__ = __getattr__

class DumbWrapper(object):
    # Simplest wrapper pattern
    def __init__(self, wrapped_obj):
        self._wrapped = wrapped_obj

    def __getattr__(self, name):
        if hasattr(self, name):
            print 'self acc'
            return object.__getattribute__(self, name)
        else:
            tmp = object.__getattribute__(self, '_wrapped')
            print 'wrap acc', name, tmp
            return getattr(tmp,name)

    def __iter__(self):
        return iter(self._wrapped)


class Dictionaryish(DumbWrapper):
    def __contains__(self, other):
        """ dictionary compatability """
        return other in self._wrapped

    def __getitem__(self,k):
        """ dictionary compatability """
        return self._wrapped[k]

    def keys(self):
        return self._wrapped.keys()

    def update(self, *args, **kargs):
        return self._wrapped.update(*args, **kargs)

    def __setitem__(self, *args, **kargs):
        return self._wrapped.__setitem__(*args, **kargs)
