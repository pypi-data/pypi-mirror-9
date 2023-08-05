# -*- coding: utf-8 -*-

import sys
from atkit.config import config
import logging
import types
from time import time

class OmniLogger(object):

    levels = {
        'd': logging.DEBUG,
        'i': logging.INFO,
        'w': logging.WARN,
        'e': logging.ERROR,
        'c': logging.CRITICAL,
    }

    formatters = {
        str: None,
        unicode: None,
        int: str,
    }

    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(OmniLogger, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, name, path, template):
        self.real_logger = logging.getLogger(name)
        fh = logging.FileHandler(path)
        file_formatter = logging.Formatter(template)
        file_formatter.formatTime = lambda record, datefmt=None: str(int(time()))
        fh.setFormatter(file_formatter)
        fh.setLevel(logging.DEBUG)
        self.real_logger.addHandler(fh)

        for name in dir(self.real_logger):
            if name.startswith('_'):
                continue
            value = getattr(self.real_logger, name)
            setattr(self, name, value)

        self.setLevel(logging.INFO)
        self.sep = ' '
        self.grab_frame_depth = 2

    def sl(self, level):
        l = self.levels.get(level)
        if l is not None:
            level = l
        self.setLevel(level)

    def get_calling_frame(self):
        try:
            raise Exception('')
        except Exception:
            frame = sys.exc_info()[2].tb_frame
        return frame.f_back.f_back.f_back

    def prepend_outer_objects(self, frame):
        # TODO: try to do actual arbitrary depth
        for name, value in frame.f_locals.iteritems():
            if isinstance(value, types.InstanceType) and hasattr(value, frame.f_code.co_name):
                co_name = '%s.%s' % (value.__class__.__name__, frame.f_code.co_name)
                break
        else:
            co_name = frame.f_code.co_name
        if co_name == '<module>':
            co_name = None
        return co_name

    def add_context_info(self, msg):
        calling_frame = self.get_calling_frame()
        co_filename = calling_frame.f_code.co_filename
        f_lineno = calling_frame.f_lineno
        co_name = self.prepend_outer_objects(frame=calling_frame)
        if co_name is None:
            co_name = ''
        else:
            co_name = ' ' + co_name + '()'
        return ' %s[%d]%s: %s' % (
            co_filename,
            f_lineno,
            co_name,
            msg)

    def join(self, args, formatter):
        return self.sep.join([formatter(a) for a in args])

    def format_args(self, *args, **kwargs):
        if len(args) < 1:
            return ''
        elif len(args) == 1:
            arg, = args
            formatter = self.formatters.get(type(arg))
            if formatter is None:
                return repr(arg)
            else:
                return formatter(arg)
        else:
            return self.join(args, formatter=self.format_args)

    def format_namevalue(self, *args):
        calling_frame = self.get_calling_frame()
        if len(args) < 1:
            raise ValueError('Requires at least one argument.')
        elif len(args) == 1:
            arg, = args
            if isinstance(arg, basestring):
                name = arg
                gl = calling_frame.f_globals
                value = gl[name]
            elif isinstance(arg, tuple):
                name, value = arg
                if isinstance(value, basestring):
                    if not isinstance(name, basestring):  # we have an (obj, attr) kind of situation
                        attr_name = value
                        value_repr = getattr(name, value)
                        name, value = attr_name, value_repr
            else:
                value = arg
                name = value.__name__
            return '%s: %s' % (name, self.format_args(value))
        else:
            return self.join(args, formatter=self.format_namevalue)

    def quick_log(self, *args):
        msg = self.format_args(*args)
        msg = self.add_context_info(msg)
        self.info(msg)

    def log_var(self, *args):
        msg = self.format_namevalue(*args)
        msg = self.add_context_info(msg)
        self.info(msg)
