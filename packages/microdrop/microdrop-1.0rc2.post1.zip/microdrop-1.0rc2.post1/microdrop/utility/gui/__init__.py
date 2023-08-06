from logger import logger

import gtk

from .. import is_float, is_int
from pygtkhelpers.ui.extra_dialogs import *


def register_shortcuts(window, shortcuts, enabled_widgets=None,
                        disabled_widgets=None):
    logger.debug('register_shortcuts()...')
    if enabled_widgets and disabled_widgets:
        raise ValueError, '''Only an enabled list OR a disabled list of'''\
                            ''' widgets is permitted.'''
    accelgroup = gtk.AccelGroup()

    def action_wrapper(action, enabled, disabled, *args, **kwargs):
        active = window.get_focus()
        if (enabled and active in enabled) or \
            (enabled is None and (disabled is None or active not in disabled)):
            # Perform associated action and stop propagation of key event
            action(*args, **kwargs)
            return True
        else:
            # Ignore shortcut and pass control to default handlers
            return False

    for shortcut, action in shortcuts.iteritems():
        key, modifier = gtk.accelerator_parse(shortcut)
        accelgroup.connect_group(key, modifier, gtk.ACCEL_VISIBLE,
            lambda a, b, c, d, action=action: \
                action_wrapper(action, enabled_widgets, disabled_widgets))
    window.add_accel_group(accelgroup)
    logger.debug('DONE')
    return accelgroup


def textentry_validate(textentry, prev_value, type_):
    val = textentry.get_text()
    if val and type_ is float:
        if is_float(val):
            return float(val)
    elif val and type_ is int:
        if is_int(val):
            return int(val)
    textentry.set_text(str(prev_value))
    return prev_value


def contains_pointer(widget, coords=None):
    if coords is None:
        (x,y) = widget.get_pointer()
    else:
        (x,y) = coords
    return 0<=x<=widget.allocation.width and 0<=y<=widget.allocation.height
