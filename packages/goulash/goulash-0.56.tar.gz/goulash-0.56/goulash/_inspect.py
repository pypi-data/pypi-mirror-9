""" goulash._inspect
"""
import inspect
from addict import Dict

def getcaller(level=2):
    """ """
    x = inspect.stack()[level]
    frame = x[0]
    file_name = x[1]
    flocals = frame.f_locals
    fglobals = frame.f_globals
    func_name = x[3]
    himself = flocals.get('self', None)
    try:
        kls  = himself and himself.__class__
    except AttributeError:
        # python uses self only by convention, so it's
        # possible there is a "himself" local but it's
        # not actually an object.
        kls = None
    kls_func = getattr(kls, func_name, None)
    if type(kls_func)==property:
        func = kls_func
    else:
        try:
            func = himself and getattr(himself, func_name)
        except AttributeError:
            func = func_name+'[nested]'
    out = dict(file=file_name,
               self=himself,
               locals=flocals,
               globals=fglobals,
               func=func,
               func_name=func_name)
    out.update({'class':kls})
    return Dict(out)
get_caller = getcaller
