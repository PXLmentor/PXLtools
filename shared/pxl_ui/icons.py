"""
pxl_ui.icons - monochrome SVG icon loader with theme tinting.

Same trick Zoo Tools Pro uses: one set of white/neutral line icons, recoloured
on the fly to match the theme. SVG is rendered through QtSvg (present in both
PySide6 and PySide2) then tinted with a SourceIn composite, so a single icon
file serves every colour state (idle / accent / muted).
"""

import os

from .compat import QtCore, QtGui, QtSvg

ICON_DIR = os.path.join(os.path.dirname(__file__), "icons")

# friendly name -> svg filename (decouples call sites from Lucide naming)
ALIASES = {
    "folder":     "folder-open",
    "scene":      "clapperboard",
    "model":      "box",
    "hdri":       "sun",
    "lighting":   "lightbulb",
    "camera":     "camera",
    "layers":     "layers",
    "render":     "film",
    "utilities":  "sliders-horizontal",
    "image":      "image",
    "info":       "info",
    "aces":       "settings-2",
    "grid":       "grid-3x3",
    "visibility": "eye",
    "expanded":   "chevron-down",
    "collapsed":  "chevron-right",
    "check":      "check",
    "delete":     "trash-2",
    "play":       "play",
    "rotate":     "rotate-cw",
    "install":    "download",
    "resolution": "monitor",
    "magic":      "sparkles",
    "ruler":      "ruler",
    "aperture":   "aperture",
    "refresh":    "refresh-cw",
    "move":       "move",
}


def _svg_path(name):
    fname = ALIASES.get(name, name)
    return os.path.join(ICON_DIR, fname + ".svg")


def _dpr():
    app = QtGui.QGuiApplication.instance()
    try:
        return float(app.devicePixelRatio()) if app else 1.0
    except Exception:
        return 1.0


def pixmap(name, size=18, color="#E6E6E6"):
    """Return a QPixmap of the icon, tinted to `color`, crisp under hi-dpi."""
    path = _svg_path(name)
    dpr = _dpr()
    px = max(1, int(round(size * dpr)))

    pm = QtGui.QPixmap(px, px)
    pm.fill(QtCore.Qt.transparent)

    if os.path.isfile(path):
        renderer = QtSvg.QSvgRenderer(path)
        p = QtGui.QPainter(pm)
        p.setRenderHint(QtGui.QPainter.Antialiasing, True)
        renderer.render(p)
        # recolour: keep alpha, replace RGB with `color`
        p.setCompositionMode(QtGui.QPainter.CompositionMode_SourceIn)
        p.fillRect(pm.rect(), QtGui.QColor(color))
        p.end()

    pm.setDevicePixelRatio(dpr)
    return pm


def icon(name, size=18, color="#E6E6E6"):
    return QtGui.QIcon(pixmap(name, size, color))


def save_png(name, size, color, out_path):
    """Render a tinted icon to a real PNG file (for QSS `image: url(...)`)."""
    app_dpr = _dpr()
    px = max(1, int(round(size * app_dpr)))
    pm = QtGui.QPixmap(px, px)
    pm.fill(QtCore.Qt.transparent)
    path = _svg_path(name)
    if os.path.isfile(path):
        renderer = QtSvg.QSvgRenderer(path)
        p = QtGui.QPainter(pm)
        p.setRenderHint(QtGui.QPainter.Antialiasing, True)
        renderer.render(p)
        p.setCompositionMode(QtGui.QPainter.CompositionMode_SourceIn)
        p.fillRect(pm.rect(), QtGui.QColor(color))
        p.end()
    pm.save(out_path, "PNG")
    return out_path
