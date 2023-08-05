""" goulash.namespaces
"""
from copy import copy

from inspect import isfunction, isclass, ismethod

class ValueNotFound(Exception): pass

def classname(thing):
    """ Return the fully-qualified class
        name of the specified class or object
    """
    try:
        return thing.__module__ + '.' + thing.__name__
    except:
        pass
    try:
        return thing.__module__ + '.' + thing.__class__.__name__
    except:
        _ty = str(type(thing))
        raise AssertionError('Must pass class or instance object, got'+_ty)

class NamespaceTests:
    """ Various boolean tests over objects, packaged thus to be resuable
        TODO: NamespaceTests(StaticMethodsOnly)
    """

    @staticmethod
    def is_property(obj):
        return isinstance(obj, property)

    @staticmethod
    def name_startswith(obj, pattern):
        """ """
        return hasattr(obj, '__name__') and obj.__name__.startswith(pattern)

    @staticmethod
    def dictionaryish(obj):
        """ """
        return isinstance(obj, dict) and \
               all([isinstance(k, basestring) for k in obj.keys()])
#type#hasattr(obj, 'keys') and hasattr(obj.keys,'__call__')

    @staticmethod
    def is_unittest_testcase_class(obj):
        """ """
        import unittest
        return isclass(obj) and issubclass(obj, unittest.TestCase)

def grab(obj, k):
    return getattr(obj, k)

class Namespace(object):
    """ NamespacePartion: introspective operations over dictionary-like objects

        NOTE: By default, all operations return dictionaries. Set
            dictionaries to False and you can get back another
            partion object.

        NOTE: This does not work in-place. (see the copy import up there?)
    """


    def __repr__(self):
        return "Namespace({0})".format(str(self.obj))

    ## dictionary compatability
    ############################################################################
    def items(self): return self.namespace.items()
    def values(self): return self.namespace.values()
    def keys(self): return reversed(sorted(self.namespace.keys()))
    def __iter__(self): return iter(self.namespace)
    def __getitem__(self,name): return self.namespace[name]
    def copy(self):
        """ This can fail for a variety of reasons involving
            thread safety, etc.. hopefully this approach is
            somewhat reasonable for the average case though
        """
        try:
            return copy(self.namespace)
        except TypeError:
            return dict([[name, self.namespace[name]] for name in self.namespace])

    def intersection(self, other):
        if isinstance(other, (dict, NSPart)):
            other = getattr(other, 'namespace', other)
            result = [ [k,self[k]] for k in self.namespace if k in other]
        else:
            raise RuntimeError('niy')
        result = dict(result)
        return result if self.dictionaries \
               else self.__class__(result, original=self)

    def __add__(self, other):
        """ Update this namespace with another.

            works for all combinations of dict+namespace,
            namespace+dict, namespace+namespace.  if any of the
            constituents are or want to return dictionaries,
            return type will be dictionaries.
        """
        out = copy(self.namespace)
        if isinstance(other, Namespace):
            out.update(other.namespace)
        elif isinstance(other, dict):
            out.update(other)
            return out
        if self.dictionaries or other.dictionaries:
            return out
        else:
            return Namespace(out, dictionaries=False)

    def __init__(self, obj, dictionaries=True, original=None):
        """ """
        self.dictionaries = dictionaries

        if original is not None and isinstance(obj, dict):
            assert isinstance(original, Namespace)
            self.namespace = obj
            self.obj = original.obj
            self.dictionaries = original.dictionaries

        elif not NamespaceTests.dictionaryish(obj):
            if isinstance(obj,dict):
                err = ("You gave a dictionary, but "
                       "maybe the keys aren't strings?")
                #warning.warn(err)
                self.obj=obj
                self.namespace={}
                return
            if not hasattr(obj, '__dict__'):
                err = ("Namespace Partitioner really expects something "
                       "like a dictionary, got {0}".format(type(obj).__name__))
                raise TypeError(err)
            namespace = {}
            if not isinstance(obj, dict):
                namespace.update(**dict([[k, grab(obj,k)] for k in dir(obj)]))
            else:
                namespace = obj
            self.namespace=namespace
            self.obj=obj
        else:
            self.namespace = obj
            self.obj = obj

    ## core introspection stuff
    ############################################################################
    @property
    def nonprivate(self):
        return self._clean()

    @property
    def properties(self):
        this = self if isclass(self.obj) else \
               self.__class__(self.obj.__class__)
        return this.generic(NamespaceTests.is_property)

    @property
    def unittest_testcases(self):
        """ Filter unittest test cases """
        return self.generic(NamespaceTests.is_unittest_testcase_class)

    @property
    def django_testcases(self):
        """ Filter django test cases """
        return self.generic(NamespaceTests.is_django_testcase_class)

    @property
    def functions(self):
        """ Filter functions """
        return self.generic(isfunction)

    @property
    def methods(self):
        """ Filter methods """
        return self.generic(ismethod)

    @property
    def private(self):
        return self.startswith('_')

    @property
    def data(self):
        """ no methods, no private stuff
            TODO: no "complex" stuff e.g. classobj
        """
        tmp = NSPart(self.copy())
        tmp.dictionaries = False
        tmp = tmp.nonprivate
        result = [ [x, self.namespace[x]] for x in tmp if x not in tmp.methods ]
        result = [ [x[0],x[1]] for x in result if not isclass(x[1]) ]
        result = dict(result)
        return result if self.dictionaries else NSPart(result)

    ## generic methods
    ############################################################################
    @property
    def subobjects(self):
        """ just sugar. """
        return self

    def with_attr(self,name):
        result=[]
        for k, v in self.items():
            if hasattr(v,name):
                result.append([k,v])
        result = dict(result)
        return result if self.dictionaries else self.__class__(result, original=self)

    def _clean(self, pattern='_'):
        """ For dictionary-like objects we'll clean out names that start with
            pattern.. for generic objects, we'll turn them into namespace
            dictionaries and proceed.
        """
        namespace = copy(self.namespace)
        bad_names = [x for x in namespace.keys() if x.startswith(pattern)]
        [ namespace.pop(name) for name in bad_names ]
        return namespace if self.dictionaries else self.__class__(namespace, original=self)

    def startswith(self, string):
        return self.generic_key(lambda k: k.startswith(string))


    def generic(self, test, value_test=True):
        """ Partitions the namespace with respect to a test function.

                TODO: refactor this around inspect.getmemebers()
        """
        namespace = self.copy()
        for key, val in namespace.items():
            if value_test:
                if not test(val):
                    namespace.pop(key)
            else: #keytest
                if not test(key):
                    namespace.pop(key)
        return namespace if self.dictionaries else \
               self.__class__(namespace, original=self)

    def generic_key(self, test):
        return self.generic(test, value_test=False)

    def type_equal(self, thing):
        """ filter by type """
        _ty = ( type(thing).__name__=='type' and thing) or type(thing)
        return self.generic(lambda obj: type(obj)==_ty)

    def subclasses_of(self, thing, strict=True):
        """ filter by subclass """
        kls = thing
        if not isclass(thing):
            kls = thing.__class__
        test = lambda obj: issubclass(obj,kls)
        return self.generic(test)

    @property
    def class_variables(self):
        if not isclass(self.obj):
            return Namespace(self.obj.__class__).class_variables
        keys = set(self.namespace.keys())
        keys -= set(self.methods.keys())
        keys -= set(self.functions.keys())
        result = dict([[key,self.namespace[key]] for key in keys])
        return result if self.dictionaries else self.__class__(result, original=self)

    @property
    def locals(self):
        """ only things that are defined by this object or this object's
            class.. i.e. nothing from superclasses
        """
        keys = set(self.keys())
        kls = self.obj if isclass(self.obj) else self.obj.__class__
        bases = kls.__bases__
        # because some (misbehaving) __gettr__ hacks
        # could possibly return noniterable __bases__
        #try:
        base_ns = [dir(b) for b in bases]
        #except TypeError: result = {}
        #else:
        base_ns = set(reduce(lambda x,y: x+y, base_ns))
        keys = keys - base_ns
        result = dict([[k, self.namespace[k]] for k in keys])
        [result.pop(x,None) for x in ('__dict__','__module__','__weakref__')]
        return result if self.dictionaries else self.__class__(result, original=self)



# Begin aliases, shortcuts
################################################################################
NSPart = Namespace
clean_namespace = lambda namespace: Namespace(namespace).cleaned
Tests = NamespaceTests
