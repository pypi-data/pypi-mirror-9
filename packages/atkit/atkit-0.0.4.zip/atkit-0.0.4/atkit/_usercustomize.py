# -*- coding: utf-8 -*-
"""
This module is symlinked somewhere in your sys.path (any original is safely preserved and restored when this module is
disabled.
"""

def env_var_enabled(default=False):
    import os
    env_var = os.getenv('ATKIT', None)
    if env_var is None:
        return True  # if unset, enabled!
    neg = [
        'disabled',
        'no',
        'off',
        'stop',
        'false',
    ]
    pos = [
        'enabled',
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

try:
    from atkit.config import config
    missing = False
except ImportError:
    missing = True

if not missing and env_var_enabled() and config.enabled:
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
