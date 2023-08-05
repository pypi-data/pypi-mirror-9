# -*- coding: utf-8 -*-
"""
This module is symlinked somewhere in your sys.path (any original is safely preserved and restored when this module is
disabled.
"""

from atkit.util import add_to_builtin

ATKIT_DISABLE_ATTR = '_atkit_disabled'

def env_var_enabled(default=False):
    import os
    env_var = os.getenv('ATKIT', None)
    if env_var is None:
        return True  # if unset, enabled!
    neg = [
        'disabled',
        'disable',
        'no',
        'off',
        'stop',
        'false',
    ]
    pos = [
        'enabled',
        'enable',
        'yes',
        'on',
        'start',
        'true',
    ]
    env_var = env_var.strip().lower()
    if env_var in neg:
        return False
    if env_var in pos:
        return True
    return default

def atkit_disable_temporaraly():
    # FIXME: undo some more things
    import __builtin__
    for name in __builtin__.atcust.keys():
        delattr(__builtin__, name)
    delattr(__builtin__, 'atcust')
    setattr(__builtin__, ATKIT_DISABLE_ATTR, True)
add_to_builtin('atkit_disable_temporaraly', atkit_disable_temporaraly)

def temporary_disable():
    import __builtin__
    return getattr(__builtin__, ATKIT_DISABLE_ATTR, False)

try:
    from atkit.config import config
    missing = False
except ImportError:
    missing = True

if (not temporary_disable() and
    not missing and
    env_var_enabled() and
    config.enabled):

    from atkit.util import add_to_builtin
    if config.banner:
        from atkit.util import atprint
        atprint(config.banner)
    if config.omnilog.enabled:
        from atkit.omnilog import OmniLogger
        ol = OmniLogger(name=config.omnilog.loggername, path=config.omnilog.log_path,
                        template=config.omnilog.log_template)
        for nickname, callable in (
            ('ol', ol),
            ('ql', ol.quick_log),
            ('lv', ol.log_var),
        ):
            add_to_builtin(nickname, callable)
    if config.excepthook.enabled:
        import sys
        from atkit.excepthook import exception_hook
        sys.excepthook = exception_hook
    if config.omnimodule.enabled:
        import os
        if os.path.exists(config.omnimodule.path):
            import imp
            omodule = imp.load_source('omodule', config.omnimodule.path)
            add_to_builtin('om', omodule, desc='A module usable for just about anything.')
    if config.debugger.enabled:
        debugger = config.debugger.module
        add_to_builtin('bp', debugger.set_trace, desc='bp = Break Point')
    if config.patch_builtin.enabled:
        for name, value in config.patch_builtin.data.iteritems():
            add_to_builtin(name, value)
    if config.import_tracker.enabled:
        import sys
        from atkit.import_tracker import ImportTracker
        sys.meta_path.insert(0, ImportTracker())
    if config.enhanced_shell.enabled:
        import atkit
        _file, startup_path, _type = imp.find_module('startup', atkit.__path__)  # we don't want to actually import
        os.environ['PYTHONSTARTUP'] = startup_path  # this is a hack, and it works.
