""" goulash.metaclasses

    random experiments with metaclasses.

    you probably don't want to use this stuff :)
"""
import new, copy

from collections import defaultdict

from goulash.util import uniq

subclass_registry = defaultdict(lambda:[])

def metaclass_hook(func):
    func.metaclass_hook = True
    return staticmethod(func)

def dynamic_name(): return 'DynMix({U})'.format(U=uniq())

class META(type):
    """ the most generic metaclass.

        all this does is provide support for hooks.  by default the
        class-registration-hook is turned on, but if you want that
        turned off just subclass this and set `metaclass_hooks=[]`

        NB: to avoid MRO issues, this should be the main metaclass
            that's used, and everything else should subclass it.

        metaclass_registration_hook::
          this tracks class-hierarchy information for every class
          that uses this metaclass.  it keeps a dictionary of this
          form updated:

             subclass_registry[<__bases__ list>] = [<subclass1>, ..]
    """

    @staticmethod
    def enumerate_metaclass_hooks(mcls):
        """ returns a dictionary of metaclass hooks
            that will be run along with __new___
        """
        # TODO: use Namespace()
        matches = [ x for x in dir(mcls) if \
                    getattr(getattr(mcls, x, None),
                            'metaclass_hook', False) ]
        return dict( [ [match, getattr(mcls, match)] for match in matches ] )

    @metaclass_hook
    def metaclass_class_registration_hook(mcls, name, bases, dct, class_obj):
        """ called when initializing (configuring) class,
            this method records data about hierarchy structure
        """
        subclass_registry[bases].append(class_obj)

    def __new__(mcls, name, bases, dct):
        """ simply reproduce the usual behaviour of type.__new__
            run any hooks (hooks are defined by subclassers)
        """
        try:
            class_obj = type.__new__(mcls, name, bases, dct)
        except TypeError,e:
            # probably the cannot create consistent MRO error
            print dict( [ [b.__name__,
                           getattr(b,'__metaclass__',None)] for b in bases])
            raise e
        hooks = mcls.metaclass_hooks if hasattr(mcls, 'metaclass_hooks') else \
                mcls.enumerate_metaclass_hooks(mcls)
        for hook in hooks.values():
            hook(mcls, name, bases, dct, class_obj)
        return class_obj


class ClassAlgebra(META):
    """ a metaclass that tracks it's subclasses. """

    def __lshift__(kls, my_mixin):
        """ algebra for left-mixin

             The following are equivalent:
              >>>  my_class = my_class << my_mixin
              >>>  class my_class(my_mixin, my_class): pass
        """
        name  = dynamic_name()
        bases = (my_mixin, kls)
        return kls.__metaclass__(name, bases, {})

    def __rshift__(kls, my_mixin):
        """ algebra for right-mixin:

             The following are equivalent:
              >>> my_class = my_class >> my_mixin
              >>> class my_class(my_class,my_mixin): pass
        """
        name  = dynamic_name()
        bases = (kls, my_mixin)
        return kls.__metaclass__(name, bases, {})

    def subclass(kls, name=None, dct={}, **kargs):
        """ dynamically generate a subclass of this class """
        dct = copy.copy(dct)
        dct.update(kargs)
        if hasattr(kls, '_subclass_hooks'):
            # TODO: shouldnt be here, abstract this
            name, dct = kls._subclass_hooks(name=name, **dct)
        name = name or "DynamicSubclassOf{K}_{U}".format(K=kls.__name__,
                                         U=uniq())
        # why does this behave differently than type() ?
        return new.classobj(name, (kls,), dct)

META1 = ClassAlgebra

def supports_class_algebra(kls):
    """ for use as a decorator
    """
    if hasattr(kls,'__metaclass__'):
        if kls.__metaclass__!=ClassAlgebra:
            raise TypeError("{0} already has a metaclass: '{1}'".
                            format(kls,kls.__metaclass__))
        else:
            return kls
    else:
        class Temp(kls):
            __metaclass__  = ClassAlgebra
        Temp.__name__ = kls.__name__
        return Temp

def subclass_tracker(*bases, **kargs):
    """ dynamically generates the subclass tracking class that extends ``bases``.

        often the name doesn't matter and will never be seen,
        but you might as well be verbose in case it's stumbled across.

        usually an empty dictionary is fine for the namespace.. after all you're
        specifying the bases already, right?

        Example usage follows:

          SomeService(classtracker(Service, Mixin1, Mixin2)):
               ''' function body '''

    """
    if kargs:
        assert kargs.keys() == ['namespace'],'only the namespace kw arg is defined'
        namespace = kargs.pop('namespace')
    else:
        namespace = {}
    name = 'DynamicallyGeneratedClassTracker'
    return META(name, bases, namespace)
