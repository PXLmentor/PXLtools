"""
Render Layer Creator v1.3.0-stable

Purpose:    Production tool for creating legacy Maya render layers with advanced naming options.
Author:     Cristian Spagnuolo
Date:       2026-06-15
Stack:      Maya 2025
Python:     3.11
Depends:    PySide6, shiboken6, maya.cmds, pxl_ui (shared kit)

Description:
    Production tool for creating legacy Maya render layers with advanced naming
    options. Migrated to the shared PXLtools pxl_ui UI/UX standard (one shared
    stylesheet + AppHeader + shared collapsible sections); 100% of the
    render-layer logic is unchanged from v1.2.4 — only the UI chrome was
    migrated.

Changelog:
    1.3.0 - Migrated the UI to the shared PXLtools pxl_ui kit, EXACTLY mirroring
            the gold-standard PXLtools PBR Material v1.1.0 / Batch Renamer v1.1.0:
              - imports pxl_ui (theme/widgets/icons + pxl_update) with the same
                bootstrap + reload + _PXLUI availability flag pattern;
              - removed bespoke `class _C` and the inline MAIN_QSS; MAIN_QSS is
                now pxlt.tool_qss() with the icon tokens (__CHECK__, __SPINUP__,
                __SPINDOWN__, __SPINUPH__, __SPINDOWNH__, __SLH__, __SLHH__)
                substituted with generated PNG paths;
              - bespoke CollapsibleSection / _make_section replaced with the
                shared pxlw.CollapsibleSection (grey header bar, accent, number
                badge, chevron) + a thin _make_section_frame wrapper using the
                same look;
              - _build_header replaced with pxlw.AppHeader(...), graceful
                fallback;
              - combos rely on tool_qss only (single native arrow) — no
                per-widget QComboBox styling;
              - inline action buttons + paired fields share height (32) and are
                vertically centred;
              - _FlatTextStyle proxy applied on the dialog;
              - auto-update wired on launch via pxl_update.check
                (deferred, once/day).
            File renamed PXLmentor_Legacy_Render_Layer_Creator_v1_2_4.py ->
            PXLtools_Render_Layer_Creator_v1_3_0.py;
            window title -> "Render Layer Creator".
    1.2.4 - PXLtools branding pass: in-tool header logo swapped
                 from PixelMentor_Logo_Long.png to PXLtools_logo.png.
                 Fallback text label changed to "PXLtools".
    1.2.3 - Full PySide6 QDialog migration — same dark theme as TurnTable Builder v1.0.5.
            Replaced cmds.window + all cmds widgets with QDialog + Qt equivalents.
            Singleton pattern added. CollapsibleSection used for Instructions.
            Non-collapsible section frames for Objects, Lights, Camera, Naming Options.
            QScrollArea wraps content. MAIN_QSS applied globally.
    1.2.2 - UI standardization and code quality pass.
    1.2.1 - UI standardization. Unified header, icon, branding, instructions tab.
    1.2.0 - Previous stable release.

Usage:
    Paste this script into the Maya Script Editor (Python tab) and press Ctrl+Enter,
    or launch it from the PXLtools shelf.
"""

import logging
import os
import sys

import maya.cmds as cmds
import maya.mel as mel

logger = logging.getLogger(__name__)

TOOL_NAME = "Render Layer Creator"
VERSION = "1.3.0"
WINDOW_OBJECT_NAME = "PXLtoolsRenderLayerCreator_v130"
ICON_NAME = "icon_render_layers.png"

# ---------------------------------------------------------------------------
# pxl_ui shared kit bootstrap (Maya 2025 PySide6 / Nuke 15 PySide2 compatible)
# ---------------------------------------------------------------------------
try:
    _here = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _here = ""
for _c in (
    _here,
    os.path.abspath(os.path.join(_here, "..", "..", "shared")) if _here else "",
    r"J:\ClaudeCode\projects\PXLtools\shared",
):
    if _c and os.path.isdir(os.path.join(_c, "pxl_ui")) and _c not in sys.path:
        sys.path.insert(0, _c)
try:
    import importlib as _il
    for _m in ("pxl_ui.compat", "pxl_ui.theme", "pxl_ui.icons", "pxl_ui.widgets"):
        if _m in sys.modules:
            _il.reload(sys.modules[_m])
    from pxl_ui import widgets as pxlw, icons as pxli, theme as pxlt
    _PXLUI = True
except Exception:
    _PXLUI = False


# ---------------------------------------------------------------------------
# Global QSS -- shared single-source stylesheet (icon tokens substituted at build)
# ---------------------------------------------------------------------------

MAIN_QSS = pxlt.tool_qss() if _PXLUI else ""


# ---------------------------------------------------------------------------
# Flat-text proxy style -- kills the host's etched/drop-shadow disabled-text
# ---------------------------------------------------------------------------

try:
    from PySide6 import QtWidgets as _QtW, QtGui as _QtG
except ImportError:
    from PySide2 import QtWidgets as _QtW, QtGui as _QtG


class _FlatTextStyle(_QtW.QProxyStyle):
    """Kills any text drop-shadow / etch the host style draws (matches the
    reference tool)."""
    def styleHint(self, hint, option=None, widget=None, returnData=None):
        if hint in (_QtW.QStyle.SH_EtchDisabledText,
                    _QtW.QStyle.SH_DitherDisabledText):
            return 0
        return super().styleHint(hint, option, widget, returnData)

    def drawItemText(self, painter, rect, flags, pal, enabled, text,
                     textRole=_QtG.QPalette.NoRole):
        if not text:
            return
        painter.save()
        if textRole != _QtG.QPalette.NoRole:
            painter.setPen(pal.color(textRole))
        painter.drawText(rect, int(flags), text)
        painter.restore()


# ---------------------------------------------------------------------------
# Section-frame helper -- non-collapsible section using the shared look.
# Mirrors the shared CollapsibleSection header (3px accent bar + icon + title)
# but stays always-open. Body uses objectName "sectionFrame" so tool_qss
# styles it. Returns (container, body_layout, header_hbox).
# ---------------------------------------------------------------------------

def _make_section_frame(title, icon_name=None, accent=None, parent=None):
    try:
        from PySide6 import QtWidgets, QtCore, QtGui
    except ImportError:
        from PySide2 import QtWidgets, QtCore, QtGui

    accent = accent or (pxlt.c("accent") if _PXLUI else "#E8820C")

    container = QtWidgets.QWidget(parent)
    outer = QtWidgets.QVBoxLayout(container)
    outer.setContentsMargins(0, 0, 0, 0)
    outer.setSpacing(0)

    header = QtWidgets.QFrame()
    header.setObjectName("PxlSectionHeader")
    header.setFixedHeight(pxlt.m("section_h") if _PXLUI else 30)
    header.setStyleSheet(
        "QFrame#PxlSectionHeader {{ background: {}; border: none; "
        "border-top-left-radius: {r}px; border-top-right-radius: {r}px; }}".format(
            pxlt.c("section_head") if _PXLUI else "#454545",
            r=(pxlt.m("r_section") if _PXLUI else 6),
        )
    )
    hbox = QtWidgets.QHBoxLayout(header)
    hbox.setContentsMargins(0, 0, 8, 0)
    hbox.setSpacing(8)

    bar = QtWidgets.QFrame()
    bar.setFixedWidth(3)
    bar.setStyleSheet("background: {}; border: none;".format(accent))
    hbox.addWidget(bar)

    if icon_name and _PXLUI:
        try:
            icl = QtWidgets.QLabel()
            icl.setFixedWidth(pxlt.m("icon"))
            icl.setStyleSheet("background: transparent;")
            icl.setPixmap(pxli.pixmap(icon_name, pxlt.m("icon"), accent))
            hbox.addWidget(icl)
        except Exception:
            pass

    title_lbl = QtWidgets.QLabel(title)
    title_lbl.setStyleSheet(
        "color: {}; font-weight: bold; font-size: {}px; background: transparent;".format(
            pxlt.c("text") if _PXLUI else "#E6E6E6",
            pxlt.m("fs_section") if _PXLUI else 12,
        )
    )
    hbox.addWidget(title_lbl)
    hbox.addStretch(1)
    outer.addWidget(header)

    body = QtWidgets.QFrame()
    body.setObjectName("sectionFrame")
    body_layout = QtWidgets.QVBoxLayout(body)
    body_layout.setContentsMargins(11, 8, 8, 8)
    body_layout.setSpacing(6)
    outer.addWidget(body)

    return container, body_layout, hbox


# ---------------------------------------------------------------------------
# Main tool class
# ---------------------------------------------------------------------------

class RenderLayerCreator:
    """Render Layer Creator -- production tool for Maya 2025 (pxl_ui)."""

    TOOL_NAME = TOOL_NAME
    VERSION = VERSION
    WINDOW_OBJECT_NAME = WINDOW_OBJECT_NAME
    ICON_NAME = ICON_NAME
    _instance = None

    def __new__(cls):
        if cls._instance is not None:
            try:
                if cls._instance._window.isVisible():
                    cls._instance._window.raise_()
                    cls._instance._window.activateWindow()
                    return cls._instance
            except Exception:
                pass
        instance = super().__new__(cls)
        cls._instance = instance
        return instance

    def __init__(self):
        if hasattr(self, "_window") and self._window is not None:
            try:
                if self._window.isVisible():
                    return
            except Exception:
                pass

        self.objects_list = []
        self.lights_list  = []
        self.camera       = None

        self._objects_list_widget      = None
        self._lights_list_widget       = None
        self._camera_field             = None
        self._prefix_field             = None
        self._suffix_field             = None
        self._use_object_name_check    = None
        self._use_camera_name_check    = None
        self._layer_per_light_check    = None
        self._light_as_prefix_check    = None
        self._light_as_suffix_check    = None
        self._naming_preview           = None
        self._window                   = None

        self._build_window()

    # ── QSS icon-token substitution (mirrors the reference tool exactly) ──────

    def _resolved_qss(self):
        """Return MAIN_QSS with the icon tokens substituted by generated PNG
        paths (check / spin arrows / slider handle), written to a space-free
        temp dir. Identical helper to the PBR Material / Batch Renamer
        references."""
        try:
            from PySide6 import QtCore, QtGui
        except ImportError:
            from PySide2 import QtCore, QtGui

        _qss = MAIN_QSS
        try:
            if _PXLUI:
                _icd = cmds.internalVar(userPrefDir=True) + "icons/"
                _ic = _icd + "_pxlui_check.png"
                pxli.save_png("check", 11, pxlt.c("on_accent"), _ic)
                _qss = _qss.replace("__CHECK__", _ic.replace("\\", "/"))
                # Spin-box / combo arrows -- real PNG chevrons (PySide6 does NOT
                # render CSS border-triangles). Grey default + white on hover.
                _up  = _icd + "_pxlui_arrow_up.png"
                _dn  = _icd + "_pxlui_arrow_down.png"
                _uph = _icd + "_pxlui_arrow_up_h.png"
                _dnh = _icd + "_pxlui_arrow_down_h.png"
                pxli.save_png("chevron-up",   9, "#B8B8B8", _up)
                pxli.save_png("chevron-down", 9, "#B8B8B8", _dn)
                pxli.save_png("chevron-up",   9, "#ffffff", _uph)
                pxli.save_png("chevron-down", 9, "#ffffff", _dnh)
                _qss = (_qss.replace("__SPINUP__",   _up.replace("\\", "/"))
                            .replace("__SPINDOWN__", _dn.replace("\\", "/"))
                            .replace("__SPINUPH__",  _uph.replace("\\", "/"))
                            .replace("__SPINDOWNH__", _dnh.replace("\\", "/")))
                # Slider handle: white dot (normal) + white dot with an orange
                # RING on hover -- drawn to PNG so it stays perfectly round.
                def _mk_handle(out_path, ring):
                    _D = 20
                    _pm = QtGui.QPixmap(_D, _D); _pm.fill(QtCore.Qt.transparent)
                    _pn = QtGui.QPainter(_pm)
                    _pn.setRenderHint(QtGui.QPainter.Antialiasing, True)
                    _cc = _D / 2.0
                    _pn.setPen(QtCore.Qt.NoPen)
                    _pn.setBrush(QtGui.QColor("#ffffff"))
                    _pn.drawEllipse(QtCore.QPointF(_cc, _cc), 6.5, 6.5)
                    if ring:
                        _pen = QtGui.QPen(QtGui.QColor("#E8820C")); _pen.setWidthF(2.0)
                        _pn.setPen(_pen); _pn.setBrush(QtCore.Qt.NoBrush)
                        _pn.drawEllipse(QtCore.QPointF(_cc, _cc), 8.0, 8.0)
                    _pn.end(); _pm.save(out_path, "PNG")
                _slh  = _icd + "_pxlui_slh.png"
                _slhh = _icd + "_pxlui_slh_h.png"
                _mk_handle(_slh, False)
                _mk_handle(_slhh, True)
                _qss = (_qss.replace("__SLH__",  _slh.replace("\\", "/"))
                            .replace("__SLHH__", _slhh.replace("\\", "/")))
            else:
                for _ph in ("__CHECK__", "__SPINUP__", "__SPINDOWN__",
                            "__SPINUPH__", "__SPINDOWNH__", "__SLH__", "__SLHH__"):
                    _qss = _qss.replace(_ph, "")
        except Exception:
            for _ph in ("__CHECK__", "__SPINUP__", "__SPINDOWN__",
                        "__SPINUPH__", "__SPINDOWNH__", "__SLH__", "__SLHH__"):
                _qss = _qss.replace(_ph, "")
        return _qss

    # ── UI Construction ───────────────────────────────────────────────────────

    def _build_window(self):
        try:
            from PySide6 import QtWidgets, QtCore
        except ImportError:
            from PySide2 import QtWidgets, QtCore
        from maya import OpenMayaUI as omui
        import shiboken6

        maya_ptr = omui.MQtUtil.mainWindow()
        maya_win = shiboken6.wrapInstance(int(maya_ptr), QtWidgets.QWidget)

        self._window = QtWidgets.QDialog(maya_win)
        self._window.setObjectName(self.WINDOW_OBJECT_NAME)
        self._window.setWindowTitle("{} v{}".format(self.TOOL_NAME, self.VERSION))
        self._window.setMinimumWidth(550)
        self._window.setMinimumHeight(600)
        self._window.setAttribute(QtCore.Qt.WA_DeleteOnClose, False)
        self._window.setStyleSheet(self._resolved_qss())
        # Remove Qt's etched disabled-text emboss (matches the reference tool).
        try:
            self._window.setStyle(_FlatTextStyle(self._window.style()))
        except Exception:
            pass

        root = QtWidgets.QVBoxLayout(self._window)
        root.setContentsMargins(0, 0, 0, 10)
        root.setSpacing(0)

        # ── HEADER ────────────────────────────────────────────────────────────
        self._build_header(root)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        content = QtWidgets.QWidget()
        cl = QtWidgets.QVBoxLayout(content)
        cl.setContentsMargins(10, 8, 10, 8)
        cl.setSpacing(8)
        scroll.setWidget(content)
        root.addWidget(scroll)

        # ── INSTRUCTIONS (collapsible, starts collapsed) ──────────────────────
        instr_sec = pxlw.CollapsibleSection(
            "INSTRUCTIONS", icon_name="info", accent="#46C2D6",
            collapsed=True, parent=content,
        ) if _PXLUI else None

        if instr_sec:
            for line in [
                "1. Select object(s)/group(s) in viewport -> Add Selected (Objects section)",
                "2. Select light(s)/light group(s) in viewport -> Add Selected (Lights section)",
                "3. Select a camera in viewport -> Set Camera",
                "4. Configure naming options",
                "5. Click Create Render Layers",
            ]:
                lbl = QtWidgets.QLabel(line)
                lbl.setObjectName("hint")
                lbl.setWordWrap(True)
                instr_sec.add_widget(lbl)
            cl.addWidget(instr_sec)
        else:
            # Fallback: simple collapsible using shared look
            try:
                from PySide6 import QtWidgets as _QW, QtGui as _QG
            except ImportError:
                from PySide2 import QtWidgets as _QW, QtGui as _QG
            instr_frame, instr_layout, _ = _make_section_frame(
                "INSTRUCTIONS", accent="#46C2D6", parent=content
            )
            for line in [
                "1. Select object(s)/group(s) in viewport -> Add Selected (Objects section)",
                "2. Select light(s)/light group(s) in viewport -> Add Selected (Lights section)",
                "3. Select a camera in viewport -> Set Camera",
                "4. Configure naming options",
                "5. Click Create Render Layers",
            ]:
                lbl = _QW.QLabel(line)
                lbl.setWordWrap(True)
                instr_layout.addWidget(lbl)
            cl.addWidget(instr_frame)

        # ── OBJECTS section ───────────────────────────────────────────────────
        obj_frame, obj_layout, _ = _make_section_frame(
            "OBJECTS / GROUPS TO RENDER", icon_name="mesh", accent="#E8820C",
            parent=content,
        )
        obj_lbl = QtWidgets.QLabel("Objects / Groups:")
        obj_lbl.setObjectName("ctrlLabel")
        obj_layout.addWidget(obj_lbl)
        obj_row = QtWidgets.QHBoxLayout()
        self._objects_list_widget = QtWidgets.QListWidget()
        self._objects_list_widget.setFixedHeight(80)
        self._objects_list_widget.setSelectionMode(
            QtWidgets.QAbstractItemView.MultiSelection)
        obj_row.addWidget(self._objects_list_widget)
        obj_btns = QtWidgets.QVBoxLayout()
        obj_btns.setSpacing(4)
        add_obj_btn = QtWidgets.QPushButton("Add Selected")
        add_obj_btn.setObjectName("btnPrimary")
        add_obj_btn.setMinimumHeight(32)
        add_obj_btn.clicked.connect(self.add_objects)
        obj_btns.addWidget(add_obj_btn)
        clr_obj_btn = QtWidgets.QPushButton("Clear")
        clr_obj_btn.setMinimumHeight(32)
        clr_obj_btn.clicked.connect(self.clear_objects)
        obj_btns.addWidget(clr_obj_btn)
        obj_btns.addStretch()
        obj_row.addLayout(obj_btns)
        obj_layout.addLayout(obj_row)
        cl.addWidget(obj_frame)

        # ── LIGHTS section ────────────────────────────────────────────────────
        lgt_frame, lgt_layout, _ = _make_section_frame(
            "LIGHTS / LIGHT GROUPS", icon_name="light", accent="#F5D547",
            parent=content,
        )
        lgt_lbl = QtWidgets.QLabel("Lights / Light Groups:")
        lgt_lbl.setObjectName("ctrlLabel")
        lgt_layout.addWidget(lgt_lbl)
        lgt_row = QtWidgets.QHBoxLayout()
        self._lights_list_widget = QtWidgets.QListWidget()
        self._lights_list_widget.setFixedHeight(60)
        self._lights_list_widget.setSelectionMode(
            QtWidgets.QAbstractItemView.MultiSelection)
        lgt_row.addWidget(self._lights_list_widget)
        lgt_btns = QtWidgets.QVBoxLayout()
        lgt_btns.setSpacing(4)
        add_lgt_btn = QtWidgets.QPushButton("Add Selected")
        add_lgt_btn.setObjectName("btnPrimary")
        add_lgt_btn.setMinimumHeight(32)
        add_lgt_btn.clicked.connect(self.add_lights)
        lgt_btns.addWidget(add_lgt_btn)
        clr_lgt_btn = QtWidgets.QPushButton("Clear")
        clr_lgt_btn.setMinimumHeight(32)
        clr_lgt_btn.clicked.connect(self.clear_lights)
        lgt_btns.addWidget(clr_lgt_btn)
        lgt_btns.addStretch()
        lgt_row.addLayout(lgt_btns)
        lgt_layout.addLayout(lgt_row)
        cl.addWidget(lgt_frame)

        # ── CAMERA section ────────────────────────────────────────────────────
        cam_frame, cam_layout, _ = _make_section_frame(
            "CAMERA", icon_name="camera", accent="#4F9DE0",
            parent=content,
        )
        cam_lbl = QtWidgets.QLabel("Render Camera:")
        cam_lbl.setObjectName("ctrlLabel")
        cam_layout.addWidget(cam_lbl)
        cam_row = QtWidgets.QHBoxLayout()
        cam_row.setSpacing(6)
        self._camera_field = QtWidgets.QLineEdit()
        self._camera_field.setReadOnly(True)
        self._camera_field.setPlaceholderText("No camera set...")
        self._camera_field.setMinimumHeight(32)
        set_cam_btn = QtWidgets.QPushButton("Set Camera")
        set_cam_btn.setObjectName("btnPrimary")
        set_cam_btn.setMinimumHeight(32)
        set_cam_btn.setMinimumWidth(100)
        set_cam_btn.clicked.connect(self.set_camera)
        cam_row.addWidget(self._camera_field, 1)
        cam_row.addWidget(set_cam_btn)
        cam_layout.addLayout(cam_row)
        cl.addWidget(cam_frame)

        # ── NAMING OPTIONS section ────────────────────────────────────────────
        nam_frame, nam_layout, _ = _make_section_frame(
            "NAMING OPTIONS", icon_name="rename", accent="#34B3A0",
            parent=content,
        )

        prefix_suffix_row = QtWidgets.QHBoxLayout()
        prefix_suffix_row.setSpacing(10)
        left_col = QtWidgets.QVBoxLayout()
        left_col.setSpacing(4)
        pfx_lbl = QtWidgets.QLabel("Prefix:")
        pfx_lbl.setObjectName("ctrlLabel")
        left_col.addWidget(pfx_lbl)
        self._prefix_field = QtWidgets.QLineEdit()
        self._prefix_field.setMinimumHeight(32)
        self._prefix_field.textChanged.connect(self.update_naming_preview)
        left_col.addWidget(self._prefix_field)
        right_col = QtWidgets.QVBoxLayout()
        right_col.setSpacing(4)
        sfx_lbl = QtWidgets.QLabel("Suffix:")
        sfx_lbl.setObjectName("ctrlLabel")
        right_col.addWidget(sfx_lbl)
        self._suffix_field = QtWidgets.QLineEdit()
        self._suffix_field.setMinimumHeight(32)
        self._suffix_field.textChanged.connect(self.update_naming_preview)
        right_col.addWidget(self._suffix_field)
        prefix_suffix_row.addLayout(left_col)
        prefix_suffix_row.addLayout(right_col)
        nam_layout.addLayout(prefix_suffix_row)

        nam_layout.addSpacing(4)
        self._use_object_name_check = QtWidgets.QCheckBox("Use object name in layer name")
        self._use_object_name_check.setChecked(True)
        self._use_object_name_check.stateChanged.connect(self.update_naming_preview)
        nam_layout.addWidget(self._use_object_name_check)

        self._use_camera_name_check = QtWidgets.QCheckBox("Use camera name in layer name")
        self._use_camera_name_check.setChecked(False)
        self._use_camera_name_check.stateChanged.connect(self.update_naming_preview)
        nam_layout.addWidget(self._use_camera_name_check)

        div = QtWidgets.QFrame()
        div.setObjectName("divider")
        div.setFrameShape(QtWidgets.QFrame.HLine)
        nam_layout.addWidget(div)

        multi_lbl = QtWidgets.QLabel("Multi-Light Options:")
        multi_lbl.setObjectName("ctrlLabel")
        nam_layout.addWidget(multi_lbl)

        self._layer_per_light_check = QtWidgets.QCheckBox("Create separate render layer per light")
        self._layer_per_light_check.setChecked(False)
        self._layer_per_light_check.stateChanged.connect(self.toggle_light_naming)
        nam_layout.addWidget(self._layer_per_light_check)

        light_pos_row = QtWidgets.QHBoxLayout()
        light_pos_row.setSpacing(20)
        lpos_lbl = QtWidgets.QLabel("Light name position:")
        lpos_lbl.setObjectName("ctrlLabel")
        light_pos_row.addWidget(lpos_lbl)
        self._light_as_prefix_check = QtWidgets.QCheckBox("Light name as Prefix")
        self._light_as_prefix_check.setChecked(False)
        self._light_as_prefix_check.setEnabled(False)
        self._light_as_prefix_check.stateChanged.connect(self.on_light_prefix_changed)
        light_pos_row.addWidget(self._light_as_prefix_check)
        self._light_as_suffix_check = QtWidgets.QCheckBox("Light name as Suffix")
        self._light_as_suffix_check.setChecked(True)
        self._light_as_suffix_check.setEnabled(False)
        self._light_as_suffix_check.stateChanged.connect(self.on_light_suffix_changed)
        light_pos_row.addWidget(self._light_as_suffix_check)
        light_pos_row.addStretch()
        nam_layout.addLayout(light_pos_row)

        div2 = QtWidgets.QFrame()
        div2.setObjectName("divider")
        div2.setFrameShape(QtWidgets.QFrame.HLine)
        nam_layout.addWidget(div2)

        self._naming_preview = QtWidgets.QLabel("— Layer name preview: [object]")
        self._naming_preview.setObjectName("statusIdle")
        self._naming_preview.setWordWrap(True)
        nam_layout.addWidget(self._naming_preview)

        cl.addWidget(nam_frame)

        # ── ACTION BUTTONS ────────────────────────────────────────────────────
        action_row = QtWidgets.QHBoxLayout()
        action_row.setSpacing(8)
        create_btn = QtWidgets.QPushButton("Create Render Layers")
        create_btn.setObjectName("btnPrimary")
        create_btn.setMinimumHeight(42)
        create_btn.clicked.connect(self.create_render_layers)
        action_row.addWidget(create_btn)
        delete_btn = QtWidgets.QPushButton("Delete All Render Layers")
        delete_btn.setObjectName("btnDestruct")
        delete_btn.setMinimumHeight(42)
        delete_btn.clicked.connect(self.delete_all_layers)
        action_row.addWidget(delete_btn)
        cl.addLayout(action_row)

        cl.addStretch()

        self._window.show()
        self._window.adjustSize()

    # ── Header builder -- shared AppHeader (fallback to a simple header) ──────

    def _build_header(self, layout):
        try:
            from PySide6 import QtWidgets, QtGui, QtCore
        except ImportError:
            from PySide2 import QtWidgets, QtGui, QtCore

        if _PXLUI:
            try:
                _ip = cmds.internalVar(userPrefDir=True) + "icons/" + self.ICON_NAME
                layout.addWidget(pxlw.AppHeader(
                    self.TOOL_NAME, "v" + self.VERSION, icon_path=_ip))
                return
            except Exception:
                pass

        # ── Fallback header (pxl_ui unavailable) ─────────────────────────────
        icon_path = cmds.internalVar(userPrefDir=True) + "icons/"

        header_widget = QtWidgets.QWidget()
        header_widget.setFixedHeight(106)
        header_widget.setStyleSheet("background-color: #333333;")

        root_hbox = QtWidgets.QHBoxLayout(header_widget)
        root_hbox.setContentsMargins(10, 5, 10, 5)
        root_hbox.setSpacing(0)

        left_label = QtWidgets.QLabel()
        left_label.setFixedSize(96, 96)
        left_label.setAlignment(QtCore.Qt.AlignCenter)
        tool_icon = icon_path + self.ICON_NAME
        if os.path.exists(tool_icon):
            pixmap = QtGui.QPixmap(tool_icon).scaled(
                96, 96, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
            )
            left_label.setPixmap(pixmap)
        else:
            left_label.setText("[Icon]")
            left_label.setStyleSheet("background-color: rgb(51,51,51); color: white;")
        root_hbox.addWidget(left_label)

        center_vbox = QtWidgets.QVBoxLayout()
        center_vbox.setContentsMargins(0, 0, 0, 0)
        center_vbox.setSpacing(2)
        center_vbox.setAlignment(QtCore.Qt.AlignVCenter)

        logo_label = QtWidgets.QLabel()
        logo_label.setFixedSize(262, 48)
        logo_label.setAlignment(QtCore.Qt.AlignCenter)
        logo_path = icon_path + "PXLtools_logo.png"
        if os.path.exists(logo_path):
            logo_pixmap = QtGui.QPixmap(logo_path).scaled(
                262, 48, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
            )
            logo_label.setPixmap(logo_pixmap)
        else:
            logo_label.setText("PXLtools")
            logo_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")

        logo_hbox = QtWidgets.QHBoxLayout()
        logo_hbox.setContentsMargins(0, 0, 0, 0)
        logo_hbox.addStretch()
        logo_hbox.addWidget(logo_label)
        logo_hbox.addStretch()

        name_label = QtWidgets.QLabel(self.TOOL_NAME)
        name_label.setAlignment(QtCore.Qt.AlignCenter)
        name_label.setStyleSheet("color: white; font-weight: bold; font-size: 11px;")

        version_label = QtWidgets.QLabel("v{}".format(self.VERSION))
        version_label.setAlignment(QtCore.Qt.AlignCenter)
        version_label.setStyleSheet("color: #aaaaaa; font-size: 9px;")

        center_vbox.addLayout(logo_hbox)
        center_vbox.addWidget(name_label)
        center_vbox.addWidget(version_label)
        root_hbox.addLayout(center_vbox, 1)

        layout.addWidget(header_widget)

    # ── Logic (unchanged from v1.2.4) ─────────────────────────────────────────

    def add_objects(self, *args):
        selected = cmds.ls(selection=True, long=True)
        if not selected:
            cmds.warning("No objects selected")
            return
        for obj in selected:
            if obj not in self.objects_list:
                self.objects_list.append(obj)
                self._objects_list_widget.addItem(obj.split('|')[-1])

    def clear_objects(self, *args):
        self.objects_list = []
        self._objects_list_widget.clear()

    def add_lights(self, *args):
        selected = cmds.ls(selection=True, long=True)
        if not selected:
            cmds.warning("No lights selected")
            return
        for light in selected:
            if light not in self.lights_list:
                self.lights_list.append(light)
                self._lights_list_widget.addItem(light.split('|')[-1])

    def clear_lights(self, *args):
        self.lights_list = []
        self._lights_list_widget.clear()

    def set_camera(self, *args):
        selected = cmds.ls(selection=True, long=True)
        if not selected:
            cmds.warning("No camera selected")
            return
        cam = None
        for sel in selected:
            if cmds.nodeType(sel) == 'camera':
                cam = sel
                break
            shapes = cmds.listRelatives(sel, shapes=True, type='camera')
            if shapes:
                cam = sel
                break
        if cam:
            self.camera = cam
            self._camera_field.setText(cam.split('|')[-1])
        else:
            cmds.warning("Selected object is not a camera")

    def toggle_light_naming(self, *args):
        layer_per_light = self._layer_per_light_check.isChecked()
        self._light_as_prefix_check.setEnabled(layer_per_light)
        self._light_as_suffix_check.setEnabled(layer_per_light)
        self.update_naming_preview()

    def on_light_prefix_changed(self, *args):
        if self._light_as_prefix_check.isChecked():
            self._light_as_suffix_check.setChecked(False)
        self.update_naming_preview()

    def on_light_suffix_changed(self, *args):
        if self._light_as_suffix_check.isChecked():
            self._light_as_prefix_check.setChecked(False)
        self.update_naming_preview()

    def update_naming_preview(self, *args):
        prefix       = self._prefix_field.text()
        suffix       = self._suffix_field.text()
        use_obj      = self._use_object_name_check.isChecked()
        use_cam      = self._use_camera_name_check.isChecked()
        layer_per_lt = self._layer_per_light_check.isChecked()
        lt_as_prefix = self._light_as_prefix_check.isChecked()
        lt_as_suffix = self._light_as_suffix_check.isChecked()

        parts = []
        if prefix:                           parts.append(prefix)
        if layer_per_lt and lt_as_prefix:    parts.append("[light]")
        if use_obj:                          parts.append("[object]")
        if use_cam:                          parts.append("[camera]")
        if layer_per_lt and lt_as_suffix:    parts.append("[light]")
        if suffix:                           parts.append(suffix)
        if not parts:                        parts.append("[unnamed]")

        self._naming_preview.setText("— Layer name preview: " + "_".join(parts))

    def get_all_descendants(self, node):
        descendants = []
        for child in (cmds.listRelatives(node, children=True, fullPath=True) or []):
            descendants.append(child)
            descendants.extend(self.get_all_descendants(child))
        return descendants

    def create_render_layers(self, *args):
        if not self.objects_list:
            cmds.warning("No objects in list -- please add objects before creating layers")
            return
        if not self.lights_list:
            cmds.warning("No lights in list -- please add lights before creating layers")
            return
        if not self.camera:
            cmds.warning("No camera set -- please set a camera before creating layers")
            return

        try:
            if cmds.mayaHasRenderSetup():
                cmds.optionVar(intValue=('renderSetupEnable', 0))
                cmds.warning("Switched to legacy render layers. Restart Maya for full effect.")
        except Exception as e:
            logger.debug("mayaHasRenderSetup check skipped: %s", e)

        prefix       = self._prefix_field.text()
        suffix       = self._suffix_field.text()
        use_obj      = self._use_object_name_check.isChecked()
        use_cam      = self._use_camera_name_check.isChecked()
        layer_per_lt = self._layer_per_light_check.isChecked()
        lt_as_prefix = self._light_as_prefix_check.isChecked()
        lt_as_suffix = self._light_as_suffix_check.isChecked()

        all_lights, light_groups = [], []
        for light in self.lights_list:
            descendants = [light] + self.get_all_descendants(light)
            group_lights = []
            for item in descendants:
                for shape in (cmds.listRelatives(item, shapes=True, fullPath=True) or []):
                    if cmds.nodeType(shape) in [
                        'spotLight', 'pointLight', 'directionalLight',
                        'areaLight', 'volumeLight', 'aiAreaLight', 'aiSkyDomeLight'
                    ]:
                        tfm = cmds.listRelatives(shape, parent=True, fullPath=True)[0]
                        if tfm not in all_lights:
                            all_lights.append(tfm)
                            group_lights.append(tfm)
                        break
            if group_lights:
                light_groups.append({
                    'name': light.split('|')[-1].replace(':', '_'),
                    'lights': group_lights
                })

        cam_name = self.camera.split('|')[-1].replace(':', '_')
        created_layers = []

        if layer_per_lt:
            for lg in light_groups:
                for obj in self.objects_list:
                    parts = []
                    if prefix:       parts.append(prefix)
                    if lt_as_prefix: parts.append(lg['name'])
                    if use_obj:      parts.append(obj.split('|')[-1].replace(':', '_'))
                    if use_cam:      parts.append(cam_name)
                    if lt_as_suffix: parts.append(lg['name'])
                    if suffix:       parts.append(suffix)
                    created_layers.append(
                        self.create_single_layer("_".join(parts) or "layer", obj, lg['lights'])
                    )
        else:
            for obj in self.objects_list:
                parts = []
                if prefix:   parts.append(prefix)
                if use_obj:  parts.append(obj.split('|')[-1].replace(':', '_'))
                if use_cam:  parts.append(cam_name)
                if suffix:   parts.append(suffix)
                created_layers.append(
                    self.create_single_layer("_".join(parts) or "layer", obj, all_lights)
                )

        cmds.editRenderLayerGlobals(currentRenderLayer='defaultRenderLayer')

        listed = ['- ' + l for l in created_layers[:10]]
        if len(created_layers) > 10:
            listed.append('... and {} more'.format(len(created_layers) - 10))
        cmds.confirmDialog(
            title='Success',
            message='Created {} render layer(s):\n{}'.format(
                len(created_layers), '\n'.join(listed)
            ),
            button=['OK']
        )

    def create_single_layer(self, layer_name, obj, lights_to_add):
        layer = cmds.createRenderLayer(name=layer_name, empty=True)
        objects_to_add = [obj] + self.get_all_descendants(obj)

        all_nodes = []
        for o in objects_to_add:
            all_nodes.append(o)
            all_nodes.extend(cmds.listRelatives(o, shapes=True, fullPath=True) or [])

        if all_nodes:
            cmds.editRenderLayerMembers(layer, all_nodes)
        cmds.editRenderLayerMembers(layer, lights_to_add)
        cmds.editRenderLayerMembers(layer, self.camera)

        cam_shape = self.camera if cmds.nodeType(self.camera) == 'camera' else None
        if not cam_shape:
            shapes = cmds.listRelatives(self.camera, shapes=True, type='camera')
            if shapes:
                cam_shape = shapes[0]

        if cam_shape:
            cmds.editRenderLayerGlobals(currentRenderLayer=layer)
            if cmds.objExists('persp'):
                ps = cmds.listRelatives('persp', shapes=True, type='camera')
                if ps:
                    cmds.editRenderLayerAdjustment(ps[0] + '.renderable')
                    cmds.setAttr(ps[0] + '.renderable', 0)
            for cam in cmds.ls(type='camera'):
                if cam != cam_shape and cam not in ['frontShape', 'topShape', 'sideShape']:
                    try:
                        cmds.editRenderLayerAdjustment(cam + '.renderable')
                        cmds.setAttr(cam + '.renderable', 0)
                    except Exception as e:
                        logger.debug("Could not set renderable override on %s: %s", cam, e)
            cmds.editRenderLayerAdjustment(cam_shape + '.renderable')
            cmds.setAttr(cam_shape + '.renderable', 1)

        return layer

    def delete_all_layers(self, *args):
        layers_to_delete = [
            l for l in cmds.ls(type='renderLayer') if l != 'defaultRenderLayer'
        ]
        if not layers_to_delete:
            cmds.confirmDialog(title='Info', message='No render layers to delete.', button=['OK'])
            return
        result = cmds.confirmDialog(
            title='Confirm Deletion',
            message='Delete {} render layer(s)?'.format(len(layers_to_delete)),
            button=['Yes', 'No'], defaultButton='No', cancelButton='No', dismissString='No'
        )
        if result == 'Yes':
            cmds.editRenderLayerGlobals(currentRenderLayer='defaultRenderLayer')
            deleted = 0
            for layer in layers_to_delete:
                try:
                    cmds.delete(layer)
                    deleted += 1
                except Exception as e:
                    cmds.warning("Could not delete layer: {} -- {}".format(layer, e))
            cmds.confirmDialog(
                title='Success',
                message='Deleted {} render layer(s).'.format(deleted),
                button=['OK']
            )


# ---------------------------------------------------------------------------
# Run / entry point
# ---------------------------------------------------------------------------

def run():
    """Launch the PXLtools Render Layer Creator."""
    RenderLayerCreator()
    # Auto-update: check GitHub for a newer STABLE release (throttled once/day),
    # deferred so it never slows the tool open and can't break launch.
    try:
        from pxl_ui import pxl_update
        cmds.evalDeferred(lambda: pxl_update.check(channel="stable", dcc="maya"),
                          lowestPriority=True)
    except Exception:
        pass


def show():
    run()


run()
