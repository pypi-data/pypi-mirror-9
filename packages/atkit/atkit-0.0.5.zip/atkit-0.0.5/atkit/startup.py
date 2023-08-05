# -*- coding: utf-8 -*-

import readline
import rlcompleter
import atexit
import os

try:
    import fancycompleter
    fancycompleter.interact()
except ImportError:
    pass

readline.parse_and_bind('tab: complete')
readline.parse_and_bind('"\e[1~": beginning-of-line')
readline.parse_and_bind('"\e[4~": end-of-line')
readline.parse_and_bind('"\e[5~": history-search-backward')
readline.parse_and_bind('"\e[6~": history-search-forward')
readline.parse_and_bind('"\e[5C": forward-word')
readline.parse_and_bind('"\e[5D": backward-word')
readline.parse_and_bind('"\e\e[C": forward-word')
readline.parse_and_bind('"\e\e[D": backward-word')
readline.parse_and_bind('tab: complete')
readline.parse_and_bind('"\e[3~": delete-char')

histfile = os.path.join(os.path.expanduser('~'), '.pythonhistory')
try:
    readline.read_history_file(histfile)
except IOError:
    pass

atexit.register(readline.write_history_file, histfile)

del os, histfile, readline, rlcompleter
