# -*- coding: utf-8 -*-

import sys
import os
import re
import traceback
import site
from atkit.config import config


def exception_hook(type, value, tb):
    debugger = config.excepthook.debugger
    bail_conditions = [
        not sys.stderr.isatty(),
        not sys.stdin.isatty(),
        type is KeyboardInterrupt,
    ]
    for index, condition in enumerate(bail_conditions):
        if condition:
            print >>sys.stderr, 'BECAUSE OF', index
            sys.__excepthook__(type, value, tb)
            break
    else:
        try:
            ol  # is "omnilogger" in the namespace/__builtin__?
            estring = []
            for line in traceback.format_exception(type, value, tb):
                if isinstance(line, basestring):
                    estring.extend(line.splitlines())
                else:
                    estring.extend(line)
            estring = [l for l in estring if l.strip()]
            estring = ['   EXCEPTION:  ' + l for l in estring]
            estring.insert(0, 'An exception occured:\n')
            estring = '\n'.join(estring)
            estring = re.sub('[\n\r]+', os.linesep, estring)
            ol.error(estring)
        except NameError:
            pass
        debugger.pm()
