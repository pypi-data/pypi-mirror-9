""" goulash.util
"""
import os
import time, uuid

def summarize_fpath(fpath):
    """ truncates a filepath to be more suitable for display.
        every instance of $HOME is replaced with ~
    """
    home = os.environ.get('HOME', None)
    if home:
        return fpath.replace(home, '~')

def uniq(use_time=False):
    """ """
    result = str(uuid.uuid1())
    if use_time: result+=str(time.time())[:-3]
    return result
