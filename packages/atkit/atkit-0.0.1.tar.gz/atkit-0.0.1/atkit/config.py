# -*- coding: utf-8 -*-

import os
import sys
import tempfile
import pdb
from npconf import ConfigValue


tempdir = tempfile.gettempdir()
def get_lib_dir():
    return os.path.join(sys.prefix, 'lib', 'python%d.%d' % (sys.version_info.major, sys.version_info.minor))

banner = 'ATKit Activated Site-Wide (tempdir=%s)' % tempdir
user_config_dir = os.path.join(os.path.expanduser('~'), '.atkit')

root =  ConfigValue(name='atkit', strict=True)

excepthook = ConfigValue(name='excepthook', data={
    'enabled': True,
    'debugger': pdb,
})

omnilog = ConfigValue(name='omnilog', data={
    'enabled': True,
    'log_path': os.path.join(tempdir, 'omnilog.log'),
    'loggername': 'omnilog',
    'log_template': '%(asctime)s:%(levelname)-4s %(message)s',
})

root.update({
    'enabled': True,
    'banner': banner,
    'log_path': os.path.join(tempdir, 'atkit.log'),
    'lib_dir': get_lib_dir,  # tested with "callable()", otherwise assumed to be a string.
    'sandbox': os.path.join(user_config_dir, 'sandbox'),
    'omnilog': omnilog,
    'excepthook': excepthook,
})


conf_file = os.path.join(user_config_dir, 'config.py')
root.configure(paths=conf_file)

config = root.config
