# -*- coding: utf-8 -*-

import os
import sys
import tempfile
import pdb
from npconf import ConfigValue


tempdir = tempfile.gettempdir()
banner = 'ATKit Activated Site-Wide (tempdir=%s)' % tempdir
user_config_dir = os.path.join(os.path.expanduser('~'), '.atkit')

root =  ConfigValue(name='atkit', strict=True)

debugger = ConfigValue(name='debugger', data={
    'enabled': True,
    'module': pdb,
})

excepthook = ConfigValue(name='excepthook', data={
    'enabled': True,
    'debugger_module': debugger.config.module,
})

omnilog = ConfigValue(name='omnilog', data={
    'enabled': True,
    'pager': 'less',
    'grep': 'grep',
    'tail': 'tail',
    'cat': 'cat',
    'log_path': os.path.join(tempdir, 'omnilog.log'),
    'loggername': 'omnilog',
    'log_template': '%(asctime)s:%(levelname)-4s %(message)s',
})


omnimodule = ConfigValue(name='omnimodule', data={
    'enabled': True,
    'path': os.path.join(user_config_dir, 'omodule.py'),
})

lib_dir = [p for p in sys.path if p.endswith('site-packages')][0]
lib_dir = os.path.dirname(lib_dir)
root.update({
    'enabled': True,
    'banner': banner,
    'log_path': os.path.join(tempdir, 'atkit.log'),
    'lib_dir': lib_dir,
    'sandbox': os.path.join(user_config_dir, 'sandbox'),
    'omnilog': omnilog,
    'excepthook': excepthook,
    'omnimodule': omnimodule,
    'debugger': debugger,
})


conf_file = os.path.join(user_config_dir, 'config.py')
root.configure(paths=conf_file)

config = root.config
