# -*- coding: utf-8 -*-

import sys

def atprint(string, fd=sys.stdout):
    lines = string.splitlines()
    lines.insert(0, '\n')
    fd.write(('\nATK=> '.join(lines)).strip() + '\n')
    fd.flush()
