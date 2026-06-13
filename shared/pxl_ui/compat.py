"""
pxl_ui.compat - PySide6 / PySide2 import shim.

Maya 2025 ships PySide6. Nuke 15 ships PySide2. Every widget in pxl_ui imports
Qt classes from this module so the same code runs in both DCCs without
conditional imports scattered through the package.

Usage:
    from pxl_ui.compat import QtCore, QtGui, QtWidgets, QtSvg, Signal, PYSIDE
"""

import sys

PYSIDE = None

# Bind to whichever Qt binding the HOST already loaded so we never mix two
# bindings in one process (Nuke 15 = PySide2, Maya 2025 = PySide6). Only fall
# back to import-probing when neither is loaded yet (e.g. standalone preview).
if "PySide2" in sys.modules and "PySide6" not in sys.modules:
    from PySide2 import QtCore, QtGui, QtWidgets, QtSvg  # noqa: F401
    from PySide2.QtCore import Signal, Slot, Property  # noqa: F401
    PYSIDE = 2
elif "PySide6" in sys.modules:
    from PySide6 import QtCore, QtGui, QtWidgets, QtSvg  # noqa: F401
    from PySide6.QtCore import Signal, Slot, Property  # noqa: F401
    PYSIDE = 6
else:
    try:
        from PySide6 import QtCore, QtGui, QtWidgets, QtSvg  # noqa: F401
        from PySide6.QtCore import Signal, Slot, Property  # noqa: F401
        PYSIDE = 6
    except ImportError:
        from PySide2 import QtCore, QtGui, QtWidgets, QtSvg  # noqa: F401
        from PySide2.QtCore import Signal, Slot, Property  # noqa: F401
        PYSIDE = 2


def is_pyside6():
    return PYSIDE == 6


def is_pyside2():
    return PYSIDE == 2


def exec_dialog(dialog):
    """Call exec() in a way that works on both PySide6 and PySide2.

    PySide2 used QDialog.exec_() (underscore - `exec` was a Python 2 keyword).
    PySide6 renamed it to .exec(). This wrapper picks whichever exists.
    """
    fn = getattr(dialog, "exec", None) or getattr(dialog, "exec_", None)
    return fn() if fn is not None else 0


def render_svg(renderer, painter):
    """QSvgRenderer.render() - identical signature on both bindings."""
    renderer.render(painter)
