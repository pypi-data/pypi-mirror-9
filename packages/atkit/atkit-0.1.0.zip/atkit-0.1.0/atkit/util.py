# -*- coding: utf-8 -*-

import sys

class ObjectWrapper(object):

    def __init__(self, obj, **kwargs):
        self.obj = obj
        self.__dict__.update(kwargs)
        desc = getattr(self, 'desc')
        if not desc:
            self.desc = getattr(self.obj, '__doc__', '') or ''

def atprint(string, fd=sys.stdout):
    lines = string.splitlines()
    lines.insert(0, '\n')
    fd.write(('\nATK=> '.join(lines)).strip() + '\n')
    fd.flush()

def add_to_builtin(name, obj, desc=''):
    import __builtin__
    try:
        __builtin__.atcust[name] = ObjectWrapper(obj, desc=desc)
    except AttributeError:
        __builtin__.atcust = {name: obj}
    setattr(__builtin__, name, obj)
