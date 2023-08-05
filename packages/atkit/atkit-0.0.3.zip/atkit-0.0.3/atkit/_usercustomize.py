# -*- coding: utf-8 -*-
"""
This module is symlinked somewhere in your sys.path (any original is safely preserved and restored when this module is
disabled.
"""

import os
from atkit.config import config

ENABLED = os.getenv('ATKIT_DISABLED', None) is None
if ENABLED and config.enabled:
    from atkit.util import atprint
    if config.banner:
        atprint(config.banner)
    import __builtin__
    if config.omnilog.enabled:
        from atkit.omnilog import OmniLogger
        ol = OmniLogger(name=config.omnilog.loggername, path=config.omnilog.log_path,
                        template=config.omnilog.log_template)
        for nickname, callable in (
            ('ol', ol),
            ('ql', ol.quick_log),
            ('lv', ol.log_var),
        ):
            setattr(__builtin__, nickname, callable)
    if config.excepthook.enabled:
        import sys
        from atkit.excepthook import exception_hook
        sys.excepthook = exception_hook
