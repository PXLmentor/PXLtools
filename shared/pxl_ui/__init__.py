"""
pxl_ui - shared PySide UI kit for PXLtools (Maya 2025 / Nuke 15).

One look, one set of widgets, one theme file - used by every PXL tool so the
whole suite is visually consistent and ports between PySide6 (Maya) and
PySide2 (Nuke) unchanged.

    from pxl_ui import theme, icons, widgets
    from pxl_ui.compat import QtWidgets
"""

from . import compat   # noqa: F401
from . import theme     # noqa: F401
from . import icons     # noqa: F401
from . import widgets   # noqa: F401

__version__ = "0.1.0"
