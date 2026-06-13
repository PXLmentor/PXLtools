"""
Standalone preview of the new TurnTable Builder UI shell (no functionality).

Runs outside Maya/Nuke on plain PySide6 so the look can be reviewed as the real
Qt window. The SAME widget code runs in Maya (PySide6) and Nuke (PySide2) via
pxl_ui.compat.

    python turntable_preview.py          # render PNG screenshots to ./_shots
    python turntable_preview.py --show    # open the live window
"""

import os
import sys

# make `pxl_ui` importable when run as a loose script
_HERE = os.path.dirname(os.path.abspath(__file__))
_SHARED = os.path.dirname(os.path.dirname(_HERE))   # .../PXLtools/shared
if _SHARED not in sys.path:
    sys.path.insert(0, _SHARED)

os.environ.setdefault("QT_SCALE_FACTOR", "2")        # crisp screenshots

from pxl_ui.compat import QtCore, QtGui, QtWidgets    # noqa: E402
from pxl_ui import theme, icons, widgets              # noqa: E402

Qt = QtCore.Qt
W = theme.m("toolset_w")


# --------------------------------------------------------------------------- #
#  small local helpers (preview-only)                                         #
# --------------------------------------------------------------------------- #
def _check_grid(labels, cols=2):
    w = QtWidgets.QWidget()
    g = QtWidgets.QGridLayout(w)
    g.setContentsMargins(0, 0, 0, 0)
    g.setHorizontalSpacing(16)
    g.setVerticalSpacing(6)
    for i, (text, on) in enumerate(labels):
        cb = QtWidgets.QCheckBox(text)
        cb.setChecked(on)
        g.addWidget(cb, i // cols, i % cols)
    return w


def _hdri_grid(n=6):
    w = QtWidgets.QWidget()
    g = QtWidgets.QGridLayout(w)
    g.setContentsMargins(0, 0, 0, 0)
    g.setSpacing(6)
    for i in range(n):
        cell = QtWidgets.QFrame()
        cell.setFixedSize(92, 58)
        active = (i == 0)
        hcol = theme.section_color("hdri")
        cell.setStyleSheet(
            "background: %s; border: 2px solid %s; border-radius: 5px;"
            % (theme.c("input"),
               hcol if active else theme.c("hairline")))
        cl = QtWidgets.QVBoxLayout(cell)
        cl.setContentsMargins(6, 4, 6, 4)
        ic = QtWidgets.QLabel()
        ic.setPixmap(icons.pixmap("hdri", 18,
                                  hcol if active else theme.c("text_dim")))
        lab = QtWidgets.QLabel("HDRI %02d" % (i + 1))
        lab.setStyleSheet("color: %s; font-size: 10px;" % (
            theme.c("text") if active else theme.c("text_muted")))
        cl.addWidget(ic)
        cl.addStretch(1)
        cl.addWidget(lab)
        g.addWidget(cell, i // 3, i % 3)
    return w


def _row(*ws):
    h = QtWidgets.QHBoxLayout()
    h.setContentsMargins(0, 0, 0, 0)
    h.setSpacing(theme.m("gap"))
    for x in ws:
        if isinstance(x, int):
            h.addStretch(x)
        else:
            h.addWidget(x)
    return h


# --------------------------------------------------------------------------- #
#  CONTENT: PREP tab                                                          #
# --------------------------------------------------------------------------- #
def build_prep():
    col = QtWidgets.QWidget()
    v = QtWidgets.QVBoxLayout(col)
    v.setContentsMargins(10, 10, 10, 10)
    v.setSpacing(8)

    # Instructions (collapsed)
    s0 = widgets.CollapsibleSection("INSTRUCTIONS", "info", collapsed=True, accent=theme.section_color("info"))
    s0.add_widget(widgets.Hint(
        "Set your root folder, load the turntable scene, attach a model, "
        "light it, then build render layers in the TURNTABLE tab."))
    v.addWidget(s0)

    # Folder setup
    s1 = widgets.CollapsibleSection("FOLDER SETUP", "folder", accent=theme.section_color("folder"))
    pr = widgets.PathRow("Turntable Root Folder", "Select TurnTable_ROOT…")
    pr.field.setText("J:/Shows/Demo/TurnTable_ROOT")
    s1.add_widget(pr)
    s1.add_widget(_wrap(_row(widgets.PrimaryButton("Set Root Folder"), 1,
                             widgets.StatusPill("Configured", "ok"))))
    s1.add_widget(widgets.Divider())
    s1.add_widget(widgets.FieldLabel("ACES 1.2 Colour Management"))
    s1.add_widget(_wrap(_row(widgets.StatusPill("ACES configured", "ok"), 1,
                             widgets.GhostButton("Setup Guide", "play"))))
    s1.add_widget(widgets.Divider())
    s1.add_widget(widgets.FieldLabel("OpenCV (preview thumbnails)"))
    s1.add_widget(_wrap(_row(widgets.StatusPill("Not installed", "warn"), 1,
                             widgets.GhostButton("Install OpenCV", "install"))))
    v.addWidget(s1)

    # Scene & frames
    s2 = widgets.CollapsibleSection("SCENE & FRAMES", "scene", accent=theme.section_color("scene"))
    s2.add_widget(widgets.PrimaryButton("Load Turntable Scene", "play"))
    fs = widgets.SliderRow("Frame Start", 1, 1000, 1)
    fe = widgets.SliderRow("Frame End", 1, 1000, 120)
    s2.add_widget(fs)
    s2.add_widget(fe)
    s2.add_widget(widgets.GhostButton("Apply Frame Range", "check"))
    v.addWidget(s2)

    # Model
    s3 = widgets.CollapsibleSection("MODEL", "model", accent=theme.section_color("model"))
    s3.add_widget(widgets.SegmentedRow(["SHADER BALL", "YOUR MODEL"]))
    s3.add_widget(_check_grid([("Shader Ball", True), ("Cloth", False),
                               ("Liquid", False)], cols=3))
    s3.add_widget(_wrap(_row(widgets.GhostButton("Capture Selected", "check"),
                             1, widgets.StatusPill("No model captured",
                                                   "muted"))))
    cb = QtWidgets.QCheckBox("Maintain Offset")
    s3.add_widget(cb)
    v.addWidget(s3)

    # Lighting & visibility
    s4 = widgets.CollapsibleSection("LIGHTING & VISIBILITY", "lighting", accent=theme.section_color("lighting"))
    s4.add_widget(widgets.FieldLabel("Visibility"))
    s4.add_widget(_check_grid([("Model", True), ("Shader Ball", True),
                               ("Charts", False), ("Floor Grid", True),
                               ("Ref Cubes", False)], cols=2))
    s4.add_widget(widgets.Divider())
    s4.add_widget(_wrap(_row(widgets.FieldLabel("Grid"), 1)))
    s4.add_widget(widgets.SegmentedRow(["10 cm", "1 mt"]))
    s4.add_widget(_wrap(_row(widgets.FieldLabel("Backdrop"), 1)))
    s4.add_widget(widgets.SegmentedRow(["HDRI", "LIMBO"]))
    s4.add_widget(widgets.Divider())
    s4.add_layout(_row(widgets.GhostButton("RenderView", "aperture"),
                       widgets.GhostButton("Render", "play")))
    v.addWidget(s4)

    # Utilities (collapsed)
    s5 = widgets.CollapsibleSection("UTILITIES", "utilities", collapsed=True, accent=theme.section_color("utilities"))
    s5.add_widget(widgets.SliderRow("Scale", 0, 500, 100, suffix=" %"))
    v.addWidget(s5)

    # HDRI environment
    s6 = widgets.CollapsibleSection("HDRI ENVIRONMENT", "hdri", accent=theme.section_color("hdri"))
    s6.add_widget(widgets.SliderRow("Rotation", 0, 360, 0, suffix=" deg"))
    s6.add_widget(_hdri_grid(6))
    s6.add_widget(widgets.GhostButton("Replace Active Slot", "image"))
    v.addWidget(s6)

    v.addSpacing(2)
    v.addWidget(widgets.DangerButton(
        "Clear Scene   (keeps your model)", "delete"))
    v.addStretch(1)
    return col


# --------------------------------------------------------------------------- #
#  CONTENT: TURNTABLE tab                                                     #
# --------------------------------------------------------------------------- #
def build_render():
    col = QtWidgets.QWidget()
    v = QtWidgets.QVBoxLayout(col)
    v.setContentsMargins(10, 10, 10, 10)
    v.setSpacing(8)

    s1 = widgets.CollapsibleSection("RENDER LAYERS", "layers", accent=theme.section_color("layers"))
    s1.add_widget(widgets.FieldLabel("Select HDRI Slots"))
    s1.add_widget(_check_grid(
        [("Slot 01  HDRI 1", True), ("Slot 02  HDRI 2", True),
         ("Slot 03  HDRI 3", False), ("Slot 04  HDRI 4", False),
         ("Slot 05  HDRI 5", False), ("Slot 06  HDRI 6", False)], cols=2))
    s1.add_layout(_row(widgets.GhostButton("Select All", "check"),
                       widgets.GhostButton("Deselect All")))
    cb = QtWidgets.QCheckBox("Include Charts Layers  (RL_charts_XX)")
    s1.add_widget(cb)
    s1.add_widget(widgets.Divider())
    s1.add_widget(widgets.PrimaryButton("Create Render Layers", "layers"))
    s1.add_widget(widgets.DangerButton("Delete TT Render Layers", "delete"))
    v.addWidget(s1)

    s2 = widgets.CollapsibleSection("RENDER TURNTABLE", "render", accent=theme.section_color("render"))
    s2.add_widget(widgets.Hint(
        "Render all turntable layers in sequence using the active renderer."))
    s2.add_widget(widgets.ComboRow("Resolution",
                                   ["HD 720  (1280x720)",
                                    "HD 1080  (1920x1080)",
                                    "4K  (3840x2160)"]))
    s2.add_widget(widgets.PrimaryButton("Render Turntable", "render"))
    v.addWidget(s2)
    v.addStretch(1)
    return col


def _wrap(layout):
    w = QtWidgets.QWidget()
    w.setLayout(layout)
    return w


# --------------------------------------------------------------------------- #
#  TAB STRIP (real-looking, for capture)                                      #
# --------------------------------------------------------------------------- #
def _tabstrip(active):
    w = QtWidgets.QFrame()
    w.setStyleSheet("background: %s;" % theme.c("header_bar"))
    w.setFixedHeight(36)
    h = QtWidgets.QHBoxLayout(w)
    h.setContentsMargins(10, 0, 10, 0)
    h.setSpacing(2)
    for i, name in enumerate(("PREP", "TURNTABLE")):
        t = QtWidgets.QLabel("   %s   " % name)
        t.setAlignment(Qt.AlignCenter)
        on = (i == active)
        t.setStyleSheet(
            "color: %s; background: %s; padding: 7px 4px;"
            "border-top-left-radius: 4px; border-top-right-radius: 4px;"
            "%s"
            % (theme.c("text") if on else theme.c("text_muted"),
               theme.c("window") if on else "transparent",
               ("border-bottom: 2px solid %s;" % theme.c("accent")) if on
               else ""))
        h.addWidget(t)
    h.addStretch(1)
    return w


# --------------------------------------------------------------------------- #
#  CAPTURE                                                                     #
# --------------------------------------------------------------------------- #
def _compose(content, active_tab):
    """header + tab strip + full content, sized to fit, returned as a widget."""
    frame = QtWidgets.QWidget()
    frame.setObjectName("PxlRoot")
    lay = QtWidgets.QVBoxLayout(frame)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(0)
    _tool_icon = os.path.join(os.path.dirname(_SHARED), "maya", "scripts",
                              "icons", "icon_turntable_builder.png")
    lay.addWidget(widgets.AppHeader("TurnTable Builder", "v1.2.0", "render",
                                    icon_path=_tool_icon))
    lay.addWidget(_tabstrip(active_tab))
    lay.addWidget(content)
    frame.setFixedWidth(W)
    frame.adjustSize()
    return frame


def _grab(frame, out_path):
    frame.setAttribute(Qt.WA_DontShowOnScreen, True)
    frame.show()
    QtWidgets.QApplication.processEvents()
    frame.adjustSize()
    QtWidgets.QApplication.processEvents()
    pm = frame.grab()
    pm.save(out_path, "PNG")
    frame.hide()
    return out_path


def _apply_theme(app):
    qss = theme.build_qss()
    shots = os.path.join(_HERE, "_shots")
    if not os.path.isdir(shots):
        os.makedirs(shots)
    check_png = icons.save_png("check", 11, theme.c("on_accent"),
                               os.path.join(shots, "_check.png"))
    qss = qss.replace("__CHECK__", check_png.replace("\\", "/"))
    app.setStyleSheet(qss)
    return shots


def main():
    show = "--show" in sys.argv
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    shots = _apply_theme(app)

    if show:
        win = QtWidgets.QTabWidget()
        win.setObjectName("PxlRoot")
        win.setStyleSheet("background: %s;" % theme.c("window"))
        win.addTab(build_prep(), "  PREP  ")
        win.addTab(build_render(), "  TURNTABLE  ")
        win.setFixedWidth(W)
        win.resize(W, 900)
        win.setWindowTitle("TurnTable Builder - UI preview")
        win.show()
        return app.exec() if hasattr(app, "exec") else app.exec_()

    p1 = _grab(_compose(build_prep(), 0),
               os.path.join(shots, "turntable_prep.png"))
    p2 = _grab(_compose(build_render(), 1),
               os.path.join(shots, "turntable_render.png"))
    print("WROTE", p1)
    print("WROTE", p2)


if __name__ == "__main__":
    main()
