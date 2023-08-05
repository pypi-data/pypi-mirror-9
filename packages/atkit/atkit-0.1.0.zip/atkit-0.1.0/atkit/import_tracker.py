# -*- coding: utf-8 -*-

import sys

from collections import namedtuple
ImportMap = namedtuple('ImportMap', ['requesting', 'fullname', 'path'])

class ImportTracker(object):

    instance = None
    history = []

    def __new__(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = super(ImportTracker, cls).__new__(cls, *args, **kwargs)
        return cls.instance

    def find_module(self, fullname, path=None):
        f = sys._getframe()
        f = f.f_back
        calling_module = f.f_code.co_filename
        self.history.append(ImportMap(
            requesting=calling_module,
            fullname=fullname,
            path=path,
        ))
        return None

ImportTracker()
history = ImportTracker.instance.history
