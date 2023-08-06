""" goulash.venv
"""
import os
import fnmatch
from goulash.python import opj, ope, expanduser, abspath

get_path   = lambda: os.environ['PATH']
get_venv   = lambda: os.environ.get('VIRTUAL_ENV', None)
to_vbin    = lambda venv: opj(venv, 'bin')
to_vlib    = lambda venv: opj(venv, 'lib')
venv_bin   = lambda cmd: opj(to_vbin(get_venv()), cmd)

def is_venv(dir):
    """ naive.. but seems to work
        TODO: find a canonical version of this function or refine it
    """
    if ope( opj(dir, 'bin', 'activate_this.py')):
        return dir


def contains_venv(_dir, **kargs):
    """ ascertain whether _dir is, or if it contains, a venv.
        returns the first matching path according to the heuritic:

            1) if the directoy is a venv, return it
            2) if the directory has subdir(s) that are venvs, return the first
            3) no venv found?  return None
    """
    kargs.update(max_venvs=1)
    venvs = find_venvs(_dir, **kargs)
    return venvs and venvs[0]

def find_venvs(_dir, report=None, max_venvs=None, ignore_dirs=[]):
    _dir = abspath(expanduser(_dir))
    venvs = []
    if is_venv(_dir):
        return venvs.append(_dir)

    count = 1
    for dirpath, dirnames, filenames in os.walk(_dir):
        if len(venvs) == max_venvs:
            break
        # trick to make sure we dont process .git/.tox first, etc
        dirnames = [x for x in reversed(sorted(dirnames))]
        for subdir in dirnames:
            count += 1
            subdir = opj(dirpath, subdir)
            if is_venv(subdir):
                if not any([
                    fnmatch.fnmatch(
                        subdir, os.path.join('*',d,'*')) for d in ignore_dirs]):
                    venvs.append(subdir)

    if report is not None and not venvs:
        assert callable(report)
        msg = "contains_venv({0}):"
        report(msg.format(_dir))
        msg = "  searched {0} subdirectories: found no python venv's"
        msg = msg.format(count)
        report(msg)

    return venvs
