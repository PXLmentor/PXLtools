"""
Animatic Builder v1.7.0-stable

Purpose:    Maya tool for automatically creating animatics from shot list JSON/CSV files.
Author:     Cristian Spagnuolo
Date:       2026-06-15
Stack:      Maya 2025
Python:     3.11
Depends:    PySide6, shiboken6, maya.cmds, pxl_ui (shared kit)

Description:
    Maya tool for automatically creating animatics from shot list JSON/CSV files.
    Migrated to the shared PXLtools pxl_ui UI/UX standard (one shared stylesheet +
    AppHeader + shared collapsible sections); 100% of the animatic logic is unchanged
    from v1.6.7 — only the UI chrome was migrated.

Changelog:
    1.7.0 - Migrated the UI to the shared PXLtools pxl_ui kit, EXACTLY mirroring
            the gold-standard siblings PXLtools PBR Material v1.1.0 and OBJ Exporter v1.1.0:
              - imports pxl_ui (theme/widgets/icons + pxl_update) with the same
                bootstrap + reload + _PXLUI availability flag pattern;
              - removed bespoke `class _C` and the inline MAIN_QSS; MAIN_QSS is
                now pxlt.tool_qss() with the icon tokens (__CHECK__, __SPINUP__,
                __SPINDOWN__, __SPINUPH__, __SPINDOWNH__, __SLH__, __SLHH__)
                substituted with generated PNG paths;
              - bespoke CollapsibleSection / _make_section_frame replaced with the
                shared pxlw.CollapsibleSection (grey header bar, accent, number
                badge, chevron) + a thin section-frame wrapper using the same look;
              - _build_header replaced with pxlw.AppHeader(...), graceful fallback;
              - combos rely on tool_qss only (single native arrow) — no per-widget
                QComboBox styling;
              - inline browse/action buttons and their paired fields share one
                height (32; primary 42) and are vertically centred;
              - _FlatTextStyle proxy applied on the dialog;
              - auto-update wired on launch via pxl_update.check (deferred, once/day).
            File renamed PXLmentor_Animatic_Builder_v1_6_7.py ->
            PXLtools_Animatic_Builder_v1_7_0.py; window title -> "Animatic Builder".
    1.6.7 - PXLtools branding pass: in-tool header logo swapped
                 from PixelMentor_Logo_Long.png to PXLtools_logo.png.
                 Fallback text label changed to "PXLtools".
    1.6.6 - Full PySide6 QDialog migration — same dark theme as TurnTable Builder v1.0.5.
        Replaced cmds.window + all cmds widgets with QDialog + Qt equivalents.
        Singleton pattern added. CollapsibleSection used for Instructions.
        QScrollArea wraps content. Non-collapsible section frames for all major sections.
        QComboBox replaces optionMenu. MAIN_QSS applied globally.
    1.6.5 - UI standardization and code quality pass.
    1.6.4 - UI standardization. Unified header, icon, branding, instructions tab.
    1.6.3 - Render settings: sequencer resolution matches project settings.
    1.6.2 - Keyframe improvement: placeholder keyframes key all transform channels.
    1.6.1 - Critical fixes: camera naming, placeholder keyframes.
    1.6.0 - UI/UX improvements, CSV default, static placeholder behaviour.
    1.5.2 - Timecode format fix: MM:SS:FR primary format.
    1.5.1 - HH:MM:SS:FR long-form timecode support.
    1.5.0 - Major CSV overhaul: metadata header, FPS conversion.
    1.4.x - CSV import, file type selector, bug fixes.
    1.3.0 - Clean Scene button.
    1.2.x - Start frame, resolution preset, FPS preset, sequencer fixes.
    1.1.x - Camera Sequencer, object placeholders, layout fixes.
    1.0.0 - Initial release.

Usage:
    Paste this script into the Maya Script Editor (Python tab) and press Ctrl+Enter,
    or launch it from the PXLtools shelf.
"""

import csv
import json
import logging
import os
import sys

import maya.cmds as cmds
import maya.mel as mel

logger = logging.getLogger(__name__)

TOOL_NAME = "Animatic Builder"
VERSION = "1.7.0"
WINDOW_OBJECT_NAME = "PXLtoolsAnimaticBuilder_v170"
ICON_NAME = "icon_animatic_builder.png"

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
# but stays always-open. Body uses objectName "sectionFrame" so tool_qss styles
# it. Returns (container, body_layout, header_hbox) so callers can add a
# right-aligned action button into the header bar.
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

class AnimaticBuilder:
    """Animatic Builder -- create animatics from shot list JSON/CSV files (pxl_ui)."""

    TOOL_NAME = TOOL_NAME
    VERSION = VERSION
    WINDOW_OBJECT_NAME = WINDOW_OBJECT_NAME
    ICON_NAME = ICON_NAME
    _instance = None

    def __new__(cls):
        if cls._instance is not None:
            try:
                if cls._instance._dialog.isVisible():
                    cls._instance._dialog.raise_()
                    cls._instance._dialog.activateWindow()
                    return cls._instance
            except Exception:
                pass
        instance = super().__new__(cls)
        cls._instance = instance
        return instance

    def __init__(self):
        if hasattr(self, "_dialog") and self._dialog is not None:
            try:
                if self._dialog.isVisible():
                    return
            except Exception:
                pass

        self.version = self.VERSION
        self.json_data = None
        self.json_file_path = ""
        self._dialog = None
        self._build_ui()

    # ------------------------------------------------------------------
    # QSS icon-token substitution (mirrors the reference tool exactly)
    # ------------------------------------------------------------------

    def _resolved_qss(self):
        """Return MAIN_QSS with the icon tokens substituted by generated PNG
        paths (check / spin arrows / slider handle), written to a space-free
        temp dir. Identical helper to the TurnTable reference."""
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

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        try:
            from PySide6 import QtWidgets, QtCore
        except ImportError:
            from PySide2 import QtWidgets, QtCore
        from maya import OpenMayaUI as omui
        import shiboken6

        main_ptr = omui.MQtUtil.mainWindow()
        maya_main = shiboken6.wrapInstance(int(main_ptr), QtWidgets.QWidget)

        dlg = QtWidgets.QDialog(maya_main)
        dlg.setObjectName(self.WINDOW_OBJECT_NAME)
        dlg.setWindowTitle("{} v{}".format(self.TOOL_NAME, self.version))
        dlg.setMinimumWidth(550)
        dlg.setAttribute(QtCore.Qt.WA_DeleteOnClose, False)
        dlg.setStyleSheet(self._resolved_qss())
        # Remove Qt's etched disabled-text emboss (matches the reference tool).
        try:
            dlg.setStyle(_FlatTextStyle(dlg.style()))
        except Exception:
            pass
        self._dialog = dlg

        # Root layout
        root_vbox = QtWidgets.QVBoxLayout(dlg)
        root_vbox.setContentsMargins(0, 0, 0, 0)
        root_vbox.setSpacing(0)
        root_vbox.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)

        # ── HEADER ──────────────────────────────────────────────────────
        self._build_header(root_vbox)

        # ── CONTENT ─────────────────────────────────────────────────────
        content_widget = QtWidgets.QWidget()
        content_vbox = QtWidgets.QVBoxLayout(content_widget)
        content_vbox.setContentsMargins(15, 10, 15, 10)
        content_vbox.setSpacing(10)

        # ── INSTRUCTIONS (collapsible, starts collapsed) ──────────────────
        instr_sec = pxlw.CollapsibleSection(
            "INSTRUCTIONS", icon_name="info", accent="#46C2D6",
            collapsed=True, parent=content_widget,
        ) if _PXLUI else None

        if instr_sec is None:
            # fallback: skip collapsible if pxl_ui unavailable
            pass
        else:
            for line in [
                "1. Load a JSON or CSV shot list file using Browse...",
                "2. Click Analyze to preview shots and timing",
                "3. Configure render settings and camera options",
                "4. Click Create Animatic — cameras and timing are set automatically",
                "5. Use Clean Scene to remove generated cameras and restore the scene",
            ]:
                lbl = QtWidgets.QLabel(line)
                lbl.setObjectName("hint")
                lbl.setWordWrap(True)
                instr_sec.add_widget(lbl)
            content_vbox.addWidget(instr_sec)

        # ── SECTION 1: LOAD SHOT LIST ────────────────────────────────────────────
        sec1, lay1, _hbox1 = _make_section_frame(
            "LOAD SHOT LIST", icon_name="folder-open", accent="#E8820C",
            parent=content_widget,
        )
        content_vbox.addWidget(sec1)

        row_ft = QtWidgets.QHBoxLayout()
        row_ft.setSpacing(8)
        lbl_ft = QtWidgets.QLabel("File Type:")
        lbl_ft.setObjectName("ctrlLabel")
        row_ft.addWidget(lbl_ft)
        self.file_type_menu = QtWidgets.QComboBox()
        self.file_type_menu.addItem("CSV (Simple Placeholder)")
        self.file_type_menu.addItem("JSON (Full Animatic)")
        self.file_type_menu.setMinimumHeight(32)
        self.file_type_menu.currentTextChanged.connect(self.update_file_type_info)
        row_ft.addWidget(self.file_type_menu, 1)
        lay1.addLayout(row_ft)

        self.file_type_info = QtWidgets.QLabel(
            "CSV: Simple placeholder animatic with basic timing (no animation)"
        )
        self.file_type_info.setObjectName("hint")
        self.file_type_info.setWordWrap(True)
        lay1.addWidget(self.file_type_info)

        lay1.addSpacing(4)

        row_path = QtWidgets.QHBoxLayout()
        row_path.setSpacing(6)
        self.json_path_field = QtWidgets.QLineEdit()
        self.json_path_field.setPlaceholderText("No file loaded")
        self.json_path_field.setReadOnly(True)
        self.json_path_field.setMinimumHeight(32)
        row_path.addWidget(self.json_path_field, 1)
        btn_browse = QtWidgets.QPushButton("Browse...")
        btn_browse.setMinimumWidth(100)
        btn_browse.setMinimumHeight(32)
        btn_browse.clicked.connect(self.load_file)
        row_path.addWidget(btn_browse)
        lay1.addLayout(row_path)

        self._status_lbl = QtWidgets.QLabel("— No file loaded")
        self._status_lbl.setObjectName("statusIdle")
        lay1.addWidget(self._status_lbl)

        # ── SECTION 2: NAMING CONVENTIONS ───────────────────────────────────────
        sec2, lay2, _hbox2 = _make_section_frame(
            "NAMING CONVENTIONS", icon_name="tag", accent="#9B7EDE",
            parent=content_widget,
        )
        content_vbox.addWidget(sec2)

        grid2 = QtWidgets.QGridLayout()
        grid2.setColumnMinimumWidth(0, 150)
        grid2.setSpacing(6)

        lbl_cp = QtWidgets.QLabel("Camera Prefix:")
        lbl_cp.setObjectName("ctrlLabel")
        grid2.addWidget(lbl_cp, 0, 0)
        self.camera_prefix_field = QtWidgets.QLineEdit("CAM_")
        self.camera_prefix_field.setMinimumHeight(32)
        grid2.addWidget(self.camera_prefix_field, 0, 1)

        lbl_lp = QtWidgets.QLabel("Light Prefix:")
        lbl_lp.setObjectName("ctrlLabel")
        grid2.addWidget(lbl_lp, 1, 0)
        self.light_prefix_field = QtWidgets.QLineEdit("LGT_")
        self.light_prefix_field.setMinimumHeight(32)
        grid2.addWidget(self.light_prefix_field, 1, 1)

        lbl_sp = QtWidgets.QLabel("Shot Prefix:")
        lbl_sp.setObjectName("ctrlLabel")
        grid2.addWidget(lbl_sp, 2, 0)
        self.shot_prefix_field = QtWidgets.QLineEdit("GRP_")
        self.shot_prefix_field.setMinimumHeight(32)
        grid2.addWidget(self.shot_prefix_field, 2, 1)

        lay2.addLayout(grid2)

        hint2 = QtWidgets.QLabel("Example: CAM_Shot_001, LGT_Shot_001_Key, Shot_001")
        hint2.setObjectName("hint")
        lay2.addWidget(hint2)

        # ── SECTION 3: PROJECT SETTINGS ─────────────────────────────────────────
        sec3, lay3, _hbox3 = _make_section_frame(
            "PROJECT SETTINGS", icon_name="settings-2", accent="#34B3A0",
            parent=content_widget,
        )
        content_vbox.addWidget(sec3)

        grid3 = QtWidgets.QGridLayout()
        grid3.setColumnMinimumWidth(0, 150)
        grid3.setSpacing(6)

        lbl_sf = QtWidgets.QLabel("Start Frame:")
        lbl_sf.setObjectName("ctrlLabel")
        grid3.addWidget(lbl_sf, 0, 0)
        self.start_frame_field = QtWidgets.QSpinBox()
        self.start_frame_field.setRange(0, 99999)
        self.start_frame_field.setValue(1001)
        self.start_frame_field.setMinimumHeight(32)
        grid3.addWidget(self.start_frame_field, 0, 1)

        lbl_fps = QtWidgets.QLabel("Frame Rate (FPS):")
        lbl_fps.setObjectName("ctrlLabel")
        grid3.addWidget(lbl_fps, 1, 0)
        self.fps_preset_menu = QtWidgets.QComboBox()
        self.fps_preset_menu.addItem("24 FPS (Cinematic)")
        self.fps_preset_menu.addItem("30 FPS (Social)")
        self.fps_preset_menu.addItem("60 FPS (Fast Motion)")
        self.fps_preset_menu.addItem("120 FPS (Slow-Mo)")
        self.fps_preset_menu.addItem("Custom")
        self.fps_preset_menu.setMinimumHeight(32)
        self.fps_preset_menu.currentTextChanged.connect(self.update_fps_from_preset)
        grid3.addWidget(self.fps_preset_menu, 1, 1)

        lbl_fv = QtWidgets.QLabel("FPS Value:")
        lbl_fv.setObjectName("ctrlLabel")
        grid3.addWidget(lbl_fv, 2, 0)
        self.fps_field = QtWidgets.QSpinBox()
        self.fps_field.setRange(1, 240)
        self.fps_field.setValue(24)
        self.fps_field.setEnabled(False)
        self.fps_field.setMinimumHeight(32)
        grid3.addWidget(self.fps_field, 2, 1)

        lbl_rp = QtWidgets.QLabel("Resolution Preset:")
        lbl_rp.setObjectName("ctrlLabel")
        grid3.addWidget(lbl_rp, 3, 0)
        self.resolution_preset_menu = QtWidgets.QComboBox()
        self.resolution_preset_menu.addItem("16:9 - 1920x1080 (1080p)")
        self.resolution_preset_menu.addItem("16:9 - 7680x4320 (8K)")
        self.resolution_preset_menu.addItem("16:9 - 3840x2160 (4K)")
        self.resolution_preset_menu.addItem("16:9 - 1280x720 (720p)")
        self.resolution_preset_menu.addItem("1:1 - 4096x4096 (4K Square)")
        self.resolution_preset_menu.addItem("1:1 - 2048x2048 (2K Square)")
        self.resolution_preset_menu.addItem("1:1 - 1024x1024 (1K Square)")
        self.resolution_preset_menu.addItem("Custom")
        self.resolution_preset_menu.setMinimumHeight(32)
        self.resolution_preset_menu.currentTextChanged.connect(self.update_resolution_from_preset)
        grid3.addWidget(self.resolution_preset_menu, 3, 1)

        lbl_rw = QtWidgets.QLabel("Width:")
        lbl_rw.setObjectName("ctrlLabel")
        grid3.addWidget(lbl_rw, 4, 0)
        self.res_width_field = QtWidgets.QSpinBox()
        self.res_width_field.setRange(320, 99999)
        self.res_width_field.setValue(1920)
        self.res_width_field.setEnabled(False)
        self.res_width_field.setMinimumHeight(32)
        grid3.addWidget(self.res_width_field, 4, 1)

        lbl_rh = QtWidgets.QLabel("Height:")
        lbl_rh.setObjectName("ctrlLabel")
        grid3.addWidget(lbl_rh, 5, 0)
        self.res_height_field = QtWidgets.QSpinBox()
        self.res_height_field.setRange(240, 99999)
        self.res_height_field.setValue(1080)
        self.res_height_field.setEnabled(False)
        self.res_height_field.setMinimumHeight(32)
        grid3.addWidget(self.res_height_field, 5, 1)

        lbl_ar = QtWidgets.QLabel("Aspect Ratio:")
        lbl_ar.setObjectName("ctrlLabel")
        grid3.addWidget(lbl_ar, 6, 0)
        self.aspect_ratio_field = QtWidgets.QLineEdit("16:9")
        self.aspect_ratio_field.setReadOnly(True)
        self.aspect_ratio_field.setMinimumHeight(32)
        grid3.addWidget(self.aspect_ratio_field, 6, 1)

        lay3.addLayout(grid3)

        # ── SECTION 4: SCENE OBJECT SETUP ───────────────────────────────────────
        sec4, lay4, _hbox4 = _make_section_frame(
            "SCENE OBJECT SETUP", icon_name="layers", accent="#4F9DE0",
            parent=content_widget,
        )
        content_vbox.addWidget(sec4)

        self.use_placeholder_check = QtWidgets.QCheckBox("Create placeholder object")
        self.use_placeholder_check.setChecked(True)
        self.use_placeholder_check.stateChanged.connect(self.toggle_placeholder_options)
        lay4.addWidget(self.use_placeholder_check)

        row_pt = QtWidgets.QHBoxLayout()
        row_pt.setSpacing(8)
        lbl_ptype = QtWidgets.QLabel("Placeholder Type:")
        lbl_ptype.setObjectName("ctrlLabel")
        row_pt.addWidget(lbl_ptype)
        self.placeholder_type_menu = QtWidgets.QComboBox()
        self.placeholder_type_menu.addItem("Cube")
        self.placeholder_type_menu.addItem("Sphere")
        self.placeholder_type_menu.addItem("Cylinder")
        self.placeholder_type_menu.setMinimumHeight(32)
        row_pt.addWidget(self.placeholder_type_menu, 1)
        lay4.addLayout(row_pt)

        lay4.addSpacing(4)

        self.use_scene_object_check = QtWidgets.QCheckBox("Use existing scene object")
        self.use_scene_object_check.setChecked(False)
        self.use_scene_object_check.stateChanged.connect(self.toggle_scene_object_options)
        lay4.addWidget(self.use_scene_object_check)

        row_so = QtWidgets.QHBoxLayout()
        row_so.setSpacing(6)
        self.scene_object_field = QtWidgets.QLineEdit()
        self.scene_object_field.setPlaceholderText("Select object in scene")
        self.scene_object_field.setReadOnly(True)
        self.scene_object_field.setEnabled(False)
        self.scene_object_field.setMinimumHeight(32)
        row_so.addWidget(self.scene_object_field, 1)
        self._btn_get_selected = QtWidgets.QPushButton("Get Selected")
        self._btn_get_selected.setMinimumWidth(100)
        self._btn_get_selected.setMinimumHeight(32)
        self._btn_get_selected.setEnabled(False)
        self._btn_get_selected.clicked.connect(self.get_selected_object)
        row_so.addWidget(self._btn_get_selected)
        lay4.addLayout(row_so)

        # ── SECTION 5: ANALYZE ──────────────────────────────────────────────────
        sec5, lay5, _hbox5 = _make_section_frame(
            "ANALYZE SHOT LIST", icon_name="aces", accent="#46C2D6",
            parent=content_widget,
        )
        content_vbox.addWidget(sec5)

        btn_analyze = QtWidgets.QPushButton("Analyze Shot List")
        btn_analyze.setMinimumHeight(32)
        btn_analyze.clicked.connect(self.analyze_json)
        lay5.addWidget(btn_analyze)

        lay5.addSpacing(4)

        # Analysis results sub-frame
        try:
            from PySide6 import QtWidgets as _QW
        except ImportError:
            from PySide2 import QtWidgets as _QW
        results_frame = _QW.QFrame()
        results_frame.setObjectName("sectionFrame")
        results_layout = _QW.QVBoxLayout(results_frame)
        results_layout.setContentsMargins(10, 8, 10, 10)
        results_layout.setSpacing(4)

        results_hdr = _QW.QLabel("ANALYSIS RESULTS")
        results_hdr.setObjectName("hint")
        results_layout.addWidget(results_hdr)

        self.analysis_project_name  = _QW.QLabel("Project: Not analyzed")
        self.analysis_total_shots   = _QW.QLabel("Total Shots: —")
        self.analysis_duration      = _QW.QLabel("Duration: —")
        self.analysis_fps           = _QW.QLabel("Source FPS: —")
        self.analysis_camera_system = _QW.QLabel("Camera System: —")

        for lbl in (
            self.analysis_project_name,
            self.analysis_total_shots,
            self.analysis_duration,
            self.analysis_fps,
            self.analysis_camera_system,
        ):
            results_layout.addWidget(lbl)

        inner_div = _QW.QFrame()
        inner_div.setFrameShape(_QW.QFrame.HLine)
        results_layout.addWidget(inner_div)

        breakdown_lbl = _QW.QLabel("Shot Breakdown:")
        breakdown_lbl.setObjectName("ctrlLabel")
        results_layout.addWidget(breakdown_lbl)

        self.analysis_shot_list = _QW.QListWidget()
        self.analysis_shot_list.setFixedHeight(120)
        self.analysis_shot_list.setSelectionMode(_QW.QAbstractItemView.SingleSelection)
        results_layout.addWidget(self.analysis_shot_list)

        lay5.addWidget(results_frame)

        # ── SECTION 6: BUILD ────────────────────────────────────────────────────
        sec6, lay6, _hbox6 = _make_section_frame(
            "BUILD ANIMATIC", icon_name="render", accent="#E8820C",
            parent=content_widget,
        )
        content_vbox.addWidget(sec6)

        btn_build = QtWidgets.QPushButton("CREATE ANIMATIC")
        btn_build.setObjectName("btnPrimary")
        btn_build.setMinimumHeight(42)
        btn_build.clicked.connect(self.build_animatic)
        lay6.addWidget(btn_build)

        lay6.addSpacing(4)

        self._build_status_lbl = QtWidgets.QLabel("— Ready to build")
        self._build_status_lbl.setObjectName("statusIdle")
        try:
            from PySide6 import QtCore as _QC
        except ImportError:
            from PySide2 import QtCore as _QC
        self._build_status_lbl.setAlignment(_QC.Qt.AlignCenter)
        lay6.addWidget(self._build_status_lbl)

        lay6.addSpacing(6)

        btn_clean = QtWidgets.QPushButton("Clean Scene (Remove Animatic)")
        btn_clean.setObjectName("btnDestruct")
        btn_clean.setMinimumHeight(32)
        btn_clean.clicked.connect(self.clean_scene)
        lay6.addWidget(btn_clean)

        root_vbox.addWidget(content_widget)
        dlg.show()

    # ------------------------------------------------------------------
    # Header builder — shared AppHeader (fallback to a simple header)
    # ------------------------------------------------------------------

    def _build_header(self, layout):
        try:
            from PySide6 import QtWidgets, QtGui, QtCore
        except ImportError:
            from PySide2 import QtWidgets, QtGui, QtCore

        if _PXLUI:
            try:
                _ip = cmds.internalVar(userPrefDir=True) + "icons/" + self.ICON_NAME
                layout.addWidget(pxlw.AppHeader(
                    self.TOOL_NAME, "v" + self.version, icon_path=_ip))
                return
            except Exception:
                pass

        # ── Fallback header (pxl_ui unavailable) ─────────────────────────
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

        version_label = QtWidgets.QLabel("v{}".format(self.version))
        version_label.setAlignment(QtCore.Qt.AlignCenter)
        version_label.setStyleSheet("color: #aaaaaa; font-size: 9px;")

        center_vbox.addLayout(logo_hbox)
        center_vbox.addWidget(name_label)
        center_vbox.addWidget(version_label)
        root_hbox.addLayout(center_vbox, 1)

        layout.addWidget(header_widget)

    # ── STATUS HELPERS ───────────────────────────────────────────────────────────

    def _set_status(self, msg, state="idle"):
        """Update the file load status label."""
        name = {"ok": "statusOk", "err": "statusErr", "idle": "statusIdle"}.get(state, "statusIdle")
        self._status_lbl.setObjectName(name)
        self._status_lbl.setText(msg)
        self._status_lbl.setStyle(self._status_lbl.style())

    def _set_build_status(self, msg, state="idle"):
        """Update the build status label."""
        name = {"ok": "statusOk", "err": "statusErr", "idle": "statusIdle"}.get(state, "statusIdle")
        self._build_status_lbl.setObjectName(name)
        self._build_status_lbl.setText(msg)
        self._build_status_lbl.setStyle(self._build_status_lbl.style())

    # ── UI CALLBACKS ─────────────────────────────────────────────────────────────

    def toggle_placeholder_options(self, *args):
        """Toggle placeholder type menu based on checkbox state."""
        use_placeholder = self.use_placeholder_check.isChecked()
        self.placeholder_type_menu.setEnabled(use_placeholder)
        if use_placeholder:
            self.use_scene_object_check.setChecked(False)
            self.toggle_scene_object_options()

    def toggle_scene_object_options(self, *args):
        """Toggle scene object field and button based on checkbox state."""
        use_scene_object = self.use_scene_object_check.isChecked()
        self.scene_object_field.setEnabled(use_scene_object)
        self._btn_get_selected.setEnabled(use_scene_object)
        if use_scene_object:
            self.use_placeholder_check.setChecked(False)
            self.toggle_placeholder_options()

    def get_selected_object(self, *args):
        """Populate the scene object field from the current viewport selection."""
        selection = cmds.ls(selection=True, transforms=True)
        if not selection:
            cmds.warning("No object selected in scene")
            return
        self.scene_object_field.setText(selection[0])

    def update_fps_from_preset(self, *args):
        """Update FPS spinbox from the preset dropdown selection."""
        preset = self.fps_preset_menu.currentText()
        fps_presets = {
            "24 FPS (Cinematic)":  (24,  False),
            "30 FPS (Social)":     (30,  False),
            "60 FPS (Fast Motion)":(60,  False),
            "120 FPS (Slow-Mo)":   (120, False),
            "Custom":              (24,  True),
        }
        if preset in fps_presets:
            fps_value, editable = fps_presets[preset]
            self.fps_field.setValue(fps_value)
            self.fps_field.setEnabled(editable)

    def update_resolution_from_preset(self, *args):
        """Update resolution fields from the preset dropdown selection."""
        preset = self.resolution_preset_menu.currentText()
        resolution_presets = {
            "16:9 - 7680x4320 (8K)":      (7680, 4320, "16:9", False),
            "16:9 - 3840x2160 (4K)":      (3840, 2160, "16:9", False),
            "16:9 - 1920x1080 (1080p)":   (1920, 1080, "16:9", False),
            "16:9 - 1280x720 (720p)":     (1280,  720, "16:9", False),
            "1:1 - 4096x4096 (4K Square)":(4096, 4096, "1:1",  False),
            "1:1 - 2048x2048 (2K Square)":(2048, 2048, "1:1",  False),
            "1:1 - 1024x1024 (1K Square)":(1024, 1024, "1:1",  False),
            "Custom":                      (1920, 1080, "16:9", True),
        }
        if preset in resolution_presets:
            width, height, aspect, editable = resolution_presets[preset]
            self.res_width_field.setValue(width)
            self.res_height_field.setValue(height)
            self.res_width_field.setEnabled(editable)
            self.res_height_field.setEnabled(editable)
            self.aspect_ratio_field.setText(aspect)
            self.aspect_ratio_field.setReadOnly(not editable)

    def update_file_type_info(self, *args):
        """Update file type info label when dropdown changes."""
        file_type = self.file_type_menu.currentText()
        if "CSV" in file_type:
            info = "CSV: Simple placeholder animatic with basic timing (no animation)"
        else:
            info = "JSON: Full animatic with camera animation, lighting, and detailed settings"
        self.file_type_info.setText(info)

    # ── FILE LOADING ─────────────────────────────────────────────────────────────

    def load_file(self, *args):
        """Dispatch to JSON or CSV loader based on the file type dropdown."""
        file_type = self.file_type_menu.currentText()
        if "JSON" in file_type:
            self.load_json_file()
        else:
            self.load_csv_file()

    def load_json_file(self, *args):
        """Open a file browser and load a JSON shot list."""
        file_path = cmds.fileDialog2(
            fileMode=1,
            caption="Select Shot List JSON File",
            fileFilter="JSON Files (*.json);;All Files (*.*)"
        )
        if not file_path:
            return

        self.json_file_path = file_path[0]
        self.json_path_field.setText(self.json_file_path)

        try:
            with open(self.json_file_path, 'r') as f:
                self.json_data = json.load(f)
            self._set_status("✓ JSON file loaded successfully", "ok")
        except Exception as e:
            self._set_status("✕ Error loading JSON: {}".format(str(e)), "err")
            cmds.warning("Error loading JSON file: {}".format(str(e)))
            self.json_data = None

    def load_csv_file(self, *args):
        """Load a CSV file with metadata header and MM:SS:FR timecode format."""
        file_path = cmds.fileDialog2(
            fileMode=1,
            caption="Select Shot List CSV File",
            fileFilter="CSV Files (*.csv);;All Files (*.*)"
        )
        if not file_path:
            return

        self.json_file_path = file_path[0]
        self.json_path_field.setText(self.json_file_path)

        try:
            target_fps = self.fps_field.value()
            shots = []
            project_title = "CSV Import"
            source_fps = target_fps

            with open(self.json_file_path, 'r') as csvfile:
                lines = csvfile.readlines()

                for line in lines[:10]:
                    if line.startswith('Project Title:'):
                        parts = line.split(',')
                        if len(parts) > 1:
                            project_title = parts[1].strip()
                    elif line.startswith('FPS:'):
                        parts = line.split(',')
                        if len(parts) > 1:
                            try:
                                source_fps = int(parts[1].strip())
                            except Exception:
                                pass

                data_start_line = 0
                for i, line in enumerate(lines):
                    if 'Shot ID' in line or 'shot_id' in line.lower():
                        data_start_line = i
                        break

                csvfile.seek(0)
                reader = csv.reader(csvfile)
                for _ in range(data_start_line + 1):
                    next(reader, None)

                skipped_rows = []
                row_number = data_start_line + 1

                for row in reader:
                    row_number += 1
                    if not row or len(row) < 2:
                        continue

                    shot_id         = row[0].strip()
                    in_out_time     = row[1].strip() if len(row) > 1 else ""
                    shot_type       = row[2].strip() if len(row) > 2 else "Medium Shot"
                    lens_gear       = row[3].strip() if len(row) > 3 else "50mm"
                    camera_movement = row[4].strip() if len(row) > 4 else "Static"

                    if not shot_id or shot_id.startswith('#'):
                        continue

                    if ' - ' not in in_out_time:
                        skipped_rows.append(
                            "Row {}: Invalid In/Out format (expected MM:SS - MM:SS)".format(row_number)
                        )
                        continue

                    try:
                        in_time, out_time = in_out_time.split(' - ')
                        in_time  = in_time.strip()
                        out_time = out_time.strip()

                        in_frames_source  = self.mmss_to_frames(in_time, source_fps)
                        out_frames_source = self.mmss_to_frames(out_time, source_fps)
                        duration_frames_source = out_frames_source - in_frames_source

                        if duration_frames_source <= 0:
                            skipped_rows.append(
                                "Row {}: Invalid duration (In >= Out)".format(row_number)
                            )
                            continue

                        if source_fps != target_fps:
                            duration_seconds = duration_frames_source / float(source_fps)
                            duration_frames_target = int(duration_seconds * target_fps)
                        else:
                            duration_frames_target = duration_frames_source

                        shot_name = shot_type.replace('(', '').replace(')', '')

                        shot_data = {
                            "shot_id":          shot_id,
                            "shot_name":        shot_name,
                            "duration_frames":  duration_frames_target,
                            "duration_seconds": duration_frames_target / float(target_fps),
                            "shot_type":        shot_type,
                            "lens_gear":        lens_gear,
                            "camera_movement":  camera_movement,
                            "source_timecode_in":  in_time,
                            "source_timecode_out": out_time,
                            "animation": {
                                "has_animation":  False,
                                "animation_type": "Static",
                                "start_frame":    0,
                                "end_frame":      duration_frames_target,
                            },
                            "camera": {
                                "focal_length_mm": 50,
                                "movement_type":   "Static",
                                "camera_angle":    0,
                            },
                            "lighting": {
                                "type": "Default"
                            },
                        }
                        shots.append(shot_data)

                    except Exception as e:
                        skipped_rows.append(
                            "Row {}: Parse error — {}".format(row_number, str(e))
                        )
                        continue

            if not shots:
                error_msg = "No valid shots found in CSV file"
                if skipped_rows:
                    error_msg += "\n\nSkipped rows:\n" + "\n".join(skipped_rows)
                raise ValueError(error_msg)

            total_duration = sum(s['duration_frames'] for s in shots) / float(target_fps)

            self.json_data = {
                "project_metadata": {
                    "project_name":           project_title,
                    "total_duration_seconds": total_duration,
                    "total_shots":            len(shots),
                    "default_fps":            target_fps,
                    "source_fps":             source_fps,
                },
                "shots": shots,
                "export_settings": {
                    "frame_rate":       target_fps,
                    "resolution_width":  1920,
                    "resolution_height": 1080,
                },
            }

            fps_conversion_note = ""
            if source_fps != target_fps:
                fps_conversion_note = " → converted to {}fps".format(target_fps)

            success_msg = "✓ '{}' loaded: {} shots, {:.1f}s (Source: {}fps{})".format(
                project_title, len(shots), total_duration, source_fps, fps_conversion_note
            )
            if skipped_rows:
                success_msg += " — {} row(s) skipped".format(len(skipped_rows))
                for skip in skipped_rows:
                    cmds.warning("CSV: " + skip)

            self._set_status(success_msg, "ok")

        except Exception as e:
            self._set_status("✕ Error loading CSV: {}".format(str(e)), "err")
            cmds.warning("Error loading CSV file: {}".format(str(e)))
            self.json_data = None

    def mmss_to_frames(self, timecode, fps):
        """Convert a timecode string to an absolute frame number.

        Primary format: MM:SS:FR (minutes:seconds:frames)
        Also handles:   HH:MM:SS:FR and bare integer frame numbers.
        """
        timecode = timecode.strip()
        if ':' not in timecode:
            return int(timecode)

        parts = timecode.split(':')
        if len(parts) == 3:
            minutes = int(parts[0])
            seconds = int(parts[1])
            frames  = int(parts[2])
            return (minutes * 60 * fps) + (seconds * fps) + frames
        elif len(parts) == 4:
            hours   = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2])
            frames  = int(parts[3])
            return (hours * 3600 * fps) + (minutes * 60 * fps) + (seconds * fps) + frames
        elif len(parts) == 2:
            seconds = int(parts[0])
            frames  = int(parts[1])
            return (seconds * fps) + frames
        else:
            raise ValueError(
                "Invalid timecode format: {}. Expected MM:SS:FR or HH:MM:SS:FR".format(timecode)
            )

    # ── ANALYZE ──────────────────────────────────────────────────────────────────

    def analyze_json(self, *args):
        """Analyze the loaded shot list and display summary; optionally trigger build."""
        if not self.json_data:
            cmds.warning("Please load a JSON or CSV file first")
            cmds.confirmDialog(
                title='No File Loaded',
                message='Please load a shot list file before analyzing.',
                button=['OK']
            )
            return

        metadata   = self.json_data.get('project_metadata', {})
        shots      = self.json_data.get('shots', [])
        project_name    = metadata.get('project_name', 'Unknown Project')
        total_shots     = len(shots)
        total_duration  = metadata.get('total_duration_seconds', 0)
        source_fps      = metadata.get('default_fps', 24)
        camera_system   = metadata.get('camera_system', 'Not specified')

        self.analysis_project_name.setText("Project: {}".format(project_name))
        self.analysis_total_shots.setText("Total Shots: {}".format(total_shots))
        self.analysis_duration.setText(
            "Duration: {:.2f} seconds ({} frames @ {}fps)".format(
                total_duration, int(total_duration * source_fps), source_fps
            )
        )
        self.analysis_fps.setText("Source FPS: {}".format(source_fps))
        self.analysis_camera_system.setText("Camera System: {}".format(camera_system))

        self.analysis_shot_list.clear()
        for shot in shots:
            shot_info = "{} - {} ({:.2f}s, {} frames)".format(
                shot.get('shot_id', 'Unknown'),
                shot.get('shot_name', 'Unnamed'),
                shot.get('duration_seconds', 0),
                shot.get('duration_frames', 0)
            )
            self.analysis_shot_list.addItem(shot_info)

        target_fps = self.fps_field.value()
        message = "Analysis Complete!\n\n"
        message += "Project: {}\n".format(project_name)
        message += "Source FPS: {} fps\n".format(source_fps)
        if source_fps != target_fps:
            message += "Target FPS: {} fps (will be converted)\n".format(target_fps)
        else:
            message += "Target FPS: {} fps (matches source)\n".format(target_fps)
        message += "\nTotal Shots: {}\n".format(total_shots)
        message += "Overall Duration: {:.2f} seconds\n\n".format(total_duration)
        message += "All shots have been validated and are ready to build.\n\n"
        message += "Note: If you change FPS, reload the file for accurate conversion.\n\n"
        message += "Would you like to proceed with creating the animatic?"

        result = cmds.confirmDialog(
            title='Analysis Complete',
            message=message,
            button=['Yes, Build It!', 'Not Yet'],
            defaultButton='Yes, Build It!',
            cancelButton='Not Yet',
            dismissString='Not Yet'
        )
        if result == 'Yes, Build It!':
            self.build_animatic()

    # ── BUILD ────────────────────────────────────────────────────────────────────

    def build_animatic(self, *args):
        """Build the complete animatic in Maya using the camera sequencer."""
        if not self.json_data:
            cmds.warning("Please load and analyze a shot list file first")
            cmds.confirmDialog(
                title='No File Loaded',
                message='Please load a shot list file before building the animatic.',
                button=['OK']
            )
            return

        camera_prefix = self.camera_prefix_field.text()
        light_prefix  = self.light_prefix_field.text()
        shot_prefix   = self.shot_prefix_field.text()
        start_frame   = self.start_frame_field.value()
        fps           = self.fps_field.value()
        res_width     = self.res_width_field.value()
        res_height    = self.res_height_field.value()

        use_placeholder  = self.use_placeholder_check.isChecked()
        use_scene_object = self.use_scene_object_check.isChecked()

        self._set_build_status("— Building animatic...", "idle")
        cmds.refresh()

        try:
            cmds.currentUnit(time='{}fps'.format(fps))
            cmds.setAttr('defaultResolution.width',  res_width)
            cmds.setAttr('defaultResolution.height', res_height)

            shots    = self.json_data.get('shots', [])
            metadata = self.json_data.get('project_metadata', {})

            if cmds.objExists('ANIMATIC_MASTER'):
                cmds.delete('ANIMATIC_MASTER')
            master_group = cmds.group(empty=True, name='ANIMATIC_MASTER')

            scene_object = None
            if use_placeholder:
                placeholder_type = self.placeholder_type_menu.currentText()
                if placeholder_type == "Cube":
                    scene_object = cmds.polyCube(name="PRODUCT_Placeholder")[0]
                elif placeholder_type == "Sphere":
                    scene_object = cmds.polySphere(name="PRODUCT_Placeholder")[0]
                elif placeholder_type == "Cylinder":
                    scene_object = cmds.polyCylinder(name="PRODUCT_Placeholder")[0]
                cmds.setAttr('{}.translateX'.format(scene_object), 0)
                cmds.setAttr('{}.translateY'.format(scene_object), 0)
                cmds.setAttr('{}.translateZ'.format(scene_object), 0)
                cmds.parent(scene_object, master_group)
            elif use_scene_object:
                scene_object = self.scene_object_field.text()
                if not scene_object or not cmds.objExists(scene_object):
                    cmds.warning("Scene object not found or not specified")
                    scene_object = None

            created_cameras = []
            shot_data_for_sequencer = []
            timeline_start = start_frame

            for shot in shots:
                shot_id        = shot.get('shot_id', 'Unknown')
                shot_name      = shot.get('shot_name', 'Unnamed')
                duration_frames = shot.get('duration_frames', 0)

                local_start  = start_frame
                local_end    = start_frame + duration_frames
                timeline_end = timeline_start + duration_frames

                shot_group_name = "{}{}".format(shot_prefix, shot_id)
                shot_group = cmds.group(empty=True, name=shot_group_name)

                camera_name = "{}{}".format(camera_prefix, shot_id)
                if cmds.objExists(camera_name):
                    cmds.warning("Camera {} already exists — replacing".format(camera_name))
                    cmds.delete(camera_name)

                camera_transform, camera_shape = cmds.camera(name=camera_name)
                if camera_transform != camera_name:
                    camera_transform = cmds.rename(camera_transform, camera_name)

                created_cameras.append(camera_transform)

                camera_data  = shot.get('camera', {})
                focal_length = camera_data.get('focal_length_mm', 50)
                cmds.setAttr('{}.focalLength'.format(camera_shape), focal_length)
                cmds.setAttr('{}.filmFit'.format(camera_shape), 3)  # Fill

                self.position_camera_by_type(camera_transform, shot, scene_object)

                animation_data = shot.get('animation', {})
                if animation_data.get('has_animation', False):
                    self.animate_camera(
                        camera_transform, shot, local_start, local_end, scene_object
                    )
                else:
                    for attr in ['translateX', 'translateY', 'translateZ',
                                 'rotateX', 'rotateY', 'rotateZ']:
                        cmds.setKeyframe(camera_transform, attribute=attr, time=local_start)
                        cmds.setKeyframe(camera_transform, attribute=attr, time=local_end)

                cmds.parent(camera_transform, shot_group)
                cmds.parent(shot_group, master_group)

                shot_data_for_sequencer.append({
                    'camera':            camera_transform,
                    'shot_node_name':    shot_id,
                    'shot_display_name': shot_name,
                    'local_start':       local_start,
                    'local_end':         local_end,
                    'timeline_start':    timeline_start,
                    'timeline_end':      timeline_end,
                })

                timeline_start = timeline_end

            total_frames = timeline_start - start_frame
            cmds.playbackOptions(
                minTime=start_frame, maxTime=timeline_start,
                animationStartTime=start_frame, animationEndTime=timeline_start
            )

            self.create_camera_sequencer(shot_data_for_sequencer, start_frame, res_width, res_height)

            self._set_build_status(
                "✓ Animatic built successfully! {} shots created.".format(len(shots)), "ok"
            )

            object_info = ""
            if scene_object:
                object_info = "Scene Object: {}\n".format(scene_object)

            cmds.confirmDialog(
                title='✓ Success',
                message=(
                    'Animatic created successfully!\n\n'
                    'Shots: {}\n'.format(len(shots)) +
                    'Cameras: {}\n'.format(len(created_cameras)) +
                    object_info +
                    'Start Frame: {}\n'.format(start_frame) +
                    'Total Duration: {} frames\n\n'.format(total_frames) +
                    'Camera sequencer has been set up.\n'
                    'All elements are organized in the ANIMATIC_MASTER group.\n\n'
                    'Note: Each shot animates locally from frame {}.'.format(start_frame)
                ),
                button=['OK']
            )

        except Exception as e:
            self._set_build_status("✕ Error building animatic: {}".format(str(e)), "err")
            cmds.warning("Error building animatic: {}".format(str(e)))
            logger.exception("build_animatic failed")
            raise

    # ── CLEAN SCENE ──────────────────────────────────────────────────────────────

    def clean_scene(self, *args):
        """Remove all script-generated animatic elements from the scene."""
        items_to_clean = []
        if cmds.objExists('ANIMATIC_MASTER'):
            items_to_clean.append('ANIMATIC_MASTER group')
        if cmds.objExists('sequencer1'):
            items_to_clean.append('Sequencer')
        all_shots = cmds.ls(type='shot')
        if all_shots:
            items_to_clean.append('{} shot node(s)'.format(len(all_shots)))

        if not items_to_clean:
            cmds.confirmDialog(
                title='— Nothing to Clean',
                message='No animatic elements found in the scene.\n\nThe scene is already clean.',
                button=['OK']
            )
            return

        items_list = '\n• '.join(items_to_clean)
        result = cmds.confirmDialog(
            title='Clean Scene — Confirm Deletion',
            message=(
                'This will remove the following animatic elements:\n\n• {}\n\n'.format(items_list) +
                'User objects and scene content will NOT be deleted.\n\n'
                'Are you sure you want to continue?'
            ),
            button=['Yes, Clean Scene', 'Cancel'],
            defaultButton='Cancel',
            cancelButton='Cancel',
            dismissString='Cancel'
        )
        if result != 'Yes, Clean Scene':
            return

        try:
            deleted_items = []

            if cmds.objExists('ANIMATIC_MASTER'):
                children = cmds.listRelatives('ANIMATIC_MASTER', children=True, fullPath=True) or []
                camera_count = sum(
                    1 for child in children
                    if cmds.nodeType(child) == 'transform'
                    and cmds.listRelatives(child, shapes=True, type='camera')
                )
                cmds.delete('ANIMATIC_MASTER')
                deleted_items.append('ANIMATIC_MASTER group (with {} cameras)'.format(camera_count))

            all_shots = cmds.ls(type='shot')
            if all_shots:
                for shot in all_shots:
                    if cmds.objExists(shot):
                        cmds.delete(shot)
                deleted_items.append('{} shot node(s)'.format(len(all_shots)))

            if cmds.objExists('sequencer1'):
                connections = cmds.listConnections('sequencer1.shots', source=True) or []
                if not connections:
                    cmds.delete('sequencer1')
                    deleted_items.append('Sequencer')

            cmds.playbackOptions(minTime=1, maxTime=120, animationStartTime=1, animationEndTime=120)

            self._set_build_status("✓ Scene cleaned successfully", "ok")

            deleted_list = '\n• '.join(deleted_items)
            cmds.confirmDialog(
                title='✓ Scene Cleaned',
                message=(
                    'Successfully removed:\n\n• {}\n\n'.format(deleted_list) +
                    'Your scene objects remain untouched.\n'
                    'Timeline reset to default (1-120).'
                ),
                button=['OK']
            )

        except Exception as e:
            self._set_build_status("✕ Error cleaning scene: {}".format(str(e)), "err")
            cmds.warning("Error cleaning scene: {}".format(str(e)))
            cmds.confirmDialog(
                title='✕ Error',
                message='An error occurred while cleaning:\n\n{}'.format(str(e)),
                button=['OK']
            )

    # ── SEQUENCER ────────────────────────────────────────────────────────────────

    def create_camera_sequencer(self, shot_data_list, start_frame, res_width, res_height):
        """Create Maya camera sequencer with all shots using local animation."""
        if not shot_data_list:
            return []

        created_shots = []

        for shot_data in shot_data_list:
            camera           = shot_data['camera']
            shot_display_name = shot_data['shot_display_name']
            local_start      = int(shot_data['local_start'])
            local_end        = int(shot_data['local_end'])
            timeline_start   = int(shot_data['timeline_start'])
            timeline_end     = int(shot_data['timeline_end'])

            try:
                shot_node = cmds.shot(
                    shotName=shot_display_name,
                    startTime=local_start,
                    endTime=local_end,
                    sequenceStartTime=timeline_start,
                    sequenceEndTime=timeline_end
                )
                camera_shape = cmds.listRelatives(camera, shapes=True, type='camera')
                if camera_shape:
                    cmds.connectAttr(
                        camera_shape[0] + '.message',
                        shot_node + '.currentCamera',
                        force=True
                    )
                created_shots.append(shot_node)
            except Exception as e:
                cmds.warning("Failed to create shot {}: {}".format(shot_display_name, str(e)))

        if created_shots:
            try:
                if cmds.objExists('sequencer1'):
                    sequencer = 'sequencer1'
                else:
                    try:
                        mel.eval('sequenceManager -addSequencerAudio 1')
                        sequencer = 'sequencer1'
                    except Exception:
                        sequencer = cmds.createNode('sequencer', name='sequencer1')

                    if not cmds.objExists(sequencer):
                        cmds.warning("Failed to create sequencer")
                        return created_shots

                for shot_node in created_shots:
                    cmds.connectAttr(
                        shot_node + '.message', sequencer + '.shots', nextAvailable=True
                    )

                if cmds.objExists(sequencer):
                    cmds.setAttr(sequencer + '.currentShot', 0)

                try:
                    cmds.setAttr(sequencer + '.imageSizeX', res_width)
                    cmds.setAttr(sequencer + '.imageSizeY', res_height)
                except Exception as e:
                    cmds.warning("Could not set sequencer resolution: {}".format(str(e)))

                cmds.warning(
                    "Created {} shots in sequencer. Each shot animates locally from frame {}. "
                    "Open Windows > Sequencer to view.".format(len(created_shots), start_frame)
                )

            except Exception as e:
                cmds.warning("Sequencer creation had issues: {}".format(str(e)))

        return created_shots

    # ── CAMERA POSITIONING ───────────────────────────────────────────────────────

    def position_camera_by_type(self, camera_transform, shot, scene_object=None):
        """Position camera based on shot type and aim at the scene object."""
        shot_type   = shot.get('shot_type', '').lower()
        camera_data = shot.get('camera', {})

        if scene_object and cmds.objExists(scene_object):
            bbox = cmds.exactWorldBoundingBox(scene_object)
            center_x = (bbox[0] + bbox[3]) / 2.0
            center_y = (bbox[1] + bbox[4]) / 2.0
            center_z = (bbox[2] + bbox[5]) / 2.0
            max_size = max(bbox[3] - bbox[0], bbox[4] - bbox[1], bbox[5] - bbox[2])

            if 'close-up' in shot_type or 'macro' in shot_type or 'ecu' in shot_type:
                distance_multiplier = 1.5
            elif 'wide' in shot_type:
                distance_multiplier = 4.0
            elif 'hero' in shot_type:
                distance_multiplier = 3.0
            else:
                distance_multiplier = 2.5

            camera_distance = max_size * distance_multiplier
        else:
            center_x = center_y = center_z = 0
            camera_distance = 10

        if 'close-up' in shot_type or 'macro' in shot_type or 'ecu' in shot_type:
            cmds.setAttr('{}.translateX'.format(camera_transform), center_x)
            cmds.setAttr('{}.translateY'.format(camera_transform), center_y)
            cmds.setAttr('{}.translateZ'.format(camera_transform), center_z + camera_distance)
        elif 'wide' in shot_type:
            cmds.setAttr('{}.translateX'.format(camera_transform), center_x)
            cmds.setAttr('{}.translateY'.format(camera_transform), center_y + (camera_distance * 0.3))
            cmds.setAttr('{}.translateZ'.format(camera_transform), center_z + camera_distance)
        elif 'hero' in shot_type:
            cmds.setAttr('{}.translateX'.format(camera_transform), center_x + (camera_distance * 0.3))
            cmds.setAttr('{}.translateY'.format(camera_transform), center_y + (camera_distance * 0.25))
            cmds.setAttr('{}.translateZ'.format(camera_transform), center_z + camera_distance)
        else:
            cmds.setAttr('{}.translateX'.format(camera_transform), center_x)
            cmds.setAttr('{}.translateY'.format(camera_transform), center_y + (camera_distance * 0.2))
            cmds.setAttr('{}.translateZ'.format(camera_transform), center_z + camera_distance)

        camera_height = camera_data.get('camera_height', '').lower()
        if 'low' in camera_height and scene_object:
            current_y = cmds.getAttr('{}.translateY'.format(camera_transform))
            cmds.setAttr('{}.translateY'.format(camera_transform),
                         current_y - (camera_distance * 0.3))

        if scene_object and cmds.objExists(scene_object):
            aim_locator = cmds.spaceLocator(name='aim_target_temp')[0]
            cmds.setAttr('{}.translateX'.format(aim_locator), center_x)
            cmds.setAttr('{}.translateY'.format(aim_locator), center_y)
            cmds.setAttr('{}.translateZ'.format(aim_locator), center_z)
            constraint = cmds.aimConstraint(
                aim_locator, camera_transform, weight=1,
                aimVector=(0, 0, -1), upVector=(0, 1, 0),
                worldUpType="vector", worldUpVector=(0, 1, 0)
            )
            cmds.delete(constraint)
            cmds.delete(aim_locator)
        else:
            camera_angle = camera_data.get('camera_angle', 0)
            if camera_angle != 0:
                cmds.setAttr('{}.rotateX'.format(camera_transform), camera_angle)

    # ── CAMERA ANIMATION ─────────────────────────────────────────────────────────

    def animate_camera(self, camera_transform, shot, start_frame, end_frame, scene_object=None):
        """Create camera animation for a shot based on its animation_type."""
        animation_data = shot.get('animation', {})
        animation_type = animation_data.get('animation_type', '').lower()

        if 'orbital' in animation_type or '360' in animation_type:
            rotation_degrees = animation_data.get('rotation_degrees', 360)
            if scene_object and cmds.objExists(scene_object):
                bbox = cmds.exactWorldBoundingBox(scene_object)
                center_x = (bbox[0] + bbox[3]) / 2.0
                center_y = (bbox[1] + bbox[4]) / 2.0
                center_z = (bbox[2] + bbox[5]) / 2.0
                orbit_center = cmds.spaceLocator(name='orbit_center_temp')[0]
                cmds.xform(orbit_center, worldSpace=True,
                           translation=(center_x, center_y, center_z))
                original_parent = cmds.listRelatives(camera_transform, parent=True)
                cmds.parent(camera_transform, orbit_center)
                cmds.setKeyframe(orbit_center, attribute='rotateY', time=start_frame, value=0)
                cmds.setKeyframe(orbit_center, attribute='rotateY', time=end_frame,
                                 value=rotation_degrees)
                if original_parent:
                    cmds.parent(camera_transform, original_parent[0])
                else:
                    cmds.parent(camera_transform, world=True)
                cmds.delete(orbit_center)
                cmds.bakeResults(
                    camera_transform,
                    time=(start_frame, end_frame),
                    simulation=True, sampleBy=1,
                    attribute=['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
                )
            else:
                cmds.setKeyframe(camera_transform, attribute='rotateY',
                                 time=start_frame, value=0)
                cmds.setKeyframe(camera_transform, attribute='rotateY',
                                 time=end_frame, value=rotation_degrees)

        elif 'tracking' in animation_type or 'dolly' in animation_type:
            movement_dir = shot.get('camera', {}).get('movement_direction', '').lower()
            start_z = cmds.getAttr('{}.translateZ'.format(camera_transform))
            if 'forward' in movement_dir:
                cmds.setKeyframe(camera_transform, attribute='translateZ',
                                 time=start_frame, value=start_z)
                cmds.setKeyframe(camera_transform, attribute='translateZ',
                                 time=end_frame, value=start_z - 5)
            elif 'backward' in movement_dir:
                cmds.setKeyframe(camera_transform, attribute='translateZ',
                                 time=start_frame, value=start_z)
                cmds.setKeyframe(camera_transform, attribute='translateZ',
                                 time=end_frame, value=start_z + 5)

        elif 'pan' in animation_type or 'whip' in animation_type:
            movement_dir = shot.get('camera', {}).get('movement_direction', '').lower()
            if 'right to left' in movement_dir:
                cmds.setKeyframe(camera_transform, attribute='rotateY',
                                 time=start_frame, value=30)
                cmds.setKeyframe(camera_transform, attribute='rotateY',
                                 time=end_frame, value=-30)
            elif 'left to right' in movement_dir:
                cmds.setKeyframe(camera_transform, attribute='rotateY',
                                 time=start_frame, value=-30)
                cmds.setKeyframe(camera_transform, attribute='rotateY',
                                 time=end_frame, value=30)

        elif 'push' in animation_type or 'zoom' in animation_type:
            start_z = cmds.getAttr('{}.translateZ'.format(camera_transform))
            cmds.setKeyframe(camera_transform, attribute='translateZ',
                             time=start_frame, value=start_z)
            cmds.setKeyframe(camera_transform, attribute='translateZ',
                             time=end_frame, value=start_z - 3)

        if animation_data.get('ease_in', False) and animation_data.get('ease_out', False):
            cmds.keyTangent(camera_transform, inTangentType='auto', outTangentType='auto',
                            time=(start_frame, end_frame))
        elif animation_data.get('ease_in', False):
            cmds.keyTangent(camera_transform, inTangentType='auto', time=(start_frame,))
        elif animation_data.get('ease_out', False):
            cmds.keyTangent(camera_transform, outTangentType='auto', time=(end_frame,))


# ==============================================================================
# ENTRY POINT
# ==============================================================================

def run():
    """Launch the PXLtools Animatic Builder."""
    AnimaticBuilder()
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
