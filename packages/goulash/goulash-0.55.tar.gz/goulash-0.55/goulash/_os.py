""" goulash._os
"""
import os

from goulash.python import get_env, ope

def home():
    return get_env('HOME')
get_home = home

def touch_file(_file):
    """ create _file if it does not exist  """
    if not ope(_file):
        with open(_file, 'w'):
            pass

def which(name):
    return os.popen('which '+name).readlines()[0].strip()

def get_mounts_by_type(mtype):
    tmp = os.popen('mount -l -t {0}'.format(mtype))
    tmp = tmp.readlines()
    tmp = [x.strip() for x in tmp if x.strip()]
    tmp2 = []
    for line in tmp:
        mdata = dict(line=line)
        line = line.split(' on ')
        name = line.pop(0)
        line = ''.join(line)
        line = line.split(' type ')
        mount_point = line.pop(0)
        mdata.update(name=name, mount_point=mount_point)
        tmp2.append(mdata)
    return tmp2
