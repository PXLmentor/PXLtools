"""
OBJ Exporter v1.1.0-stable

Purpose:    Batch export Maya objects from a group to individual OBJ files with configurable options.
Author:     Cristian Spagnuolo
Date:       2026-06-15
Stack:      Maya 2025
Python:     3.11
Depends:    PySide6, shiboken6, maya.cmds, pxl_ui (shared kit)

Description:
    Batch export Maya objects from a group to individual OBJ files with
    configurable options. Migrated to the shared PXLtools pxl_ui UI/UX
    standard (one shared stylesheet + AppHeader + shared collapsible sections);
    100% of the export logic is unchanged from v1.0.5 — only the UI chrome
    was migrated.

Changelog:
    1.1.0 - Migrated the UI to the shared PXLtools pxl_ui kit, EXACTLY mirroring
            the gold-standard PXLtools Batch Renamer v1.1.0 and PBR Material v1.1.0:
              - imports pxl_ui (theme/widgets/icons + pxl_update) with the same
                bootstrap + reload + _PXLUI availability flag pattern;
              - removed bespoke `class _C` and the inline MAIN_QSS; MAIN_QSS is
                now pxlt.tool_qss() with the icon tokens (__CHECK__, __SPINUP__,
                __SPINDOWN__, __SPINUPH__, __SPINDOWNH__, __SLH__, __SLHH__)
                substituted with generated PNG paths;
              - bespoke CollapsibleSection replaced with the shared
                pxlw.CollapsibleSection (grey header bar, accent, chevron);
              - _build_header replaced with pxlw.AppHeader(...), graceful fallback;
              - non-collapsible sections use shared _make_section_frame helper;
              - combos rely on tool_qss only (single native arrow) — no per-widget
                QComboBox styling;
              - inline action buttons + paired fields share height (32; primary
                buttons 42) and are vertically centred;
              - _FlatTextStyle proxy applied on the dialog;
              - auto-update wired on launch via pxl_update.check (deferred, once/day).
            File renamed PXLmentor_OBJ_Batch_Exporter_v1_0_5.py ->
            PXLtools_OBJ_Exporter_v1_1_0.py; window title -> "OBJ Exporter".
    1.0.5 - PXLtools branding pass: in-tool header logo swapped
                 from PixelMentor_Logo_Long.png to PXLtools_logo.png.
                 Fallback text label changed to "PXLtools".
    1.0.4 - Fixed QtWidgets.Qt.AlignCenter -> QtCore.Qt.AlignCenter (PySide6 compatibility).
    1.0.3 - Full PySide6 QDialog migration -- same dark theme as TurnTable Builder v1.0.5.
            Replaced cmds.window + all cmds widgets with QDialog + Qt equivalents.
            Singleton pattern added (topLevelWidgets search). CollapsibleSection used for
            Instructions. MAIN_QSS applied globally.
    1.0.2 - UI polish + code cleanup pass: _C color token class; brand-orange primary button;
            status bar prefixes; UPPERCASE section labels; spacing rhythm; _recalc_height().
    1.0.1 - UI standardization. Unified header, icon, branding.
    1.0.0 - Initial stable release. Batch OBJ export, progress bar, ETA, collapsible instructions.

Usage:
    Paste this script into the Maya Script Editor (Python tab) and press Ctrl+Enter,
    or launch it from the PXLtools shelf.
"""

import logging
import os
import sys
import time

import maya.cmds as cmds

log = logging.getLogger(__name__)

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
# Tool constants
# ---------------------------------------------------------------------------

TOOL_NAME = "OBJ Exporter"
VERSION = "1.1.0"
WINDOW_OBJECT_NAME = "PXLtoolsOBJExporter_v110"
ICON_NAME = "icon_obj_exporter.png"


# ---------------------------------------------------------------------------
# Main tool class
# ---------------------------------------------------------------------------

class OBJExporter:
    """OBJ Exporter -- batch export group children as individual OBJ files (pxl_ui)."""

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

        self.export_folder = ""
        self.start_time    = 0

        # Qt widget handles
        self._groups_check    = None
        self._ptgroups_check  = None
        self._materials_check = None
        self._smoothing_check = None
        self._normals_check   = None
        self._folder_field    = None
        self._progress_bar    = None
        self._current_obj_lbl = None
        self._eta_lbl         = None
        self._export_btn      = None
        self._status_lbl      = None
        self._window          = None

        self._build_window()

    # ── QSS icon-token substitution (mirrors the reference tool exactly) ──────

    def _resolved_qss(self):
        """Return MAIN_QSS with the icon tokens substituted by generated PNG
        paths (check / spin arrows / slider handle), written to a space-free
        temp dir. Identical helper to the PBR Material reference."""
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

    # ── Window construction ────────────────────────────────────────────────────

    def _build_window(self):
        from PySide6 import QtWidgets, QtCore
        from maya import OpenMayaUI as omui
        import shiboken6

        maya_ptr = omui.MQtUtil.mainWindow()
        maya_win = shiboken6.wrapInstance(int(maya_ptr), QtWidgets.QWidget)

        dlg = QtWidgets.QDialog(maya_win)
        dlg.setObjectName(self.WINDOW_OBJECT_NAME)
        dlg.setWindowTitle("{} v{}".format(self.TOOL_NAME, self.VERSION))
        dlg.setMinimumWidth(550)
        dlg.setAttribute(QtCore.Qt.WA_DeleteOnClose, False)
        dlg.setStyleSheet(self._resolved_qss())
        # Remove Qt's etched disabled-text emboss (matches the reference tool).
        try:
            dlg.setStyle(_FlatTextStyle(dlg.style()))
        except Exception:
            pass
        self._window = dlg

        root = QtWidgets.QVBoxLayout(dlg)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)

        # ── HEADER ──────────────────────────────────────────────────────────
        self._build_header(root)

        # ── CONTENT ─────────────────────────────────────────────────────────
        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 10, 15, 10)
        content_layout.setSpacing(10)

        # ── INSTRUCTIONS (collapsible, starts collapsed) ─────────────────────
        instr_sec = pxlw.CollapsibleSection(
            "INSTRUCTIONS", icon_name="info", accent="#46C2D6",
            collapsed=True, parent=content_widget,
        )
        for line in [
            "1. Select a group containing the objects to export",
            "2. Configure export options (fewer options = smaller files)",
            "3. Choose destination folder",
            "4. Click Export -- process cannot be stopped once started",
        ]:
            lbl = QtWidgets.QLabel(line)
            lbl.setObjectName("hint")
            lbl.setWordWrap(True)
            instr_sec.add_widget(lbl)
        content_layout.addWidget(instr_sec)

        # ── EXPORT OPTIONS section ────────────────────────────────────────────
        opts_frame, opts_layout, _opts_hbox = _make_section_frame(
            "EXPORT OPTIONS", icon_name="settings-2", accent="#E8820C",
            parent=content_widget,
        )

        row = QtWidgets.QHBoxLayout()
        row.setSpacing(20)
        left_col = QtWidgets.QVBoxLayout()
        left_col.setSpacing(4)
        self._groups_check    = QtWidgets.QCheckBox("Groups")
        self._ptgroups_check  = QtWidgets.QCheckBox("Polygon Groups")
        self._materials_check = QtWidgets.QCheckBox("Materials")
        left_col.addWidget(self._groups_check)
        left_col.addWidget(self._ptgroups_check)
        left_col.addWidget(self._materials_check)
        right_col = QtWidgets.QVBoxLayout()
        right_col.setSpacing(4)
        self._smoothing_check = QtWidgets.QCheckBox("Smoothing")
        self._normals_check   = QtWidgets.QCheckBox("Normals")
        right_col.addWidget(self._smoothing_check)
        right_col.addWidget(self._normals_check)
        row.addLayout(left_col)
        row.addLayout(right_col)
        row.addStretch()
        opts_layout.addLayout(row)
        opts_layout.addSpacing(4)
        toggle_btn = QtWidgets.QPushButton("Select / Deselect All")
        toggle_btn.setMinimumHeight(32)
        toggle_btn.clicked.connect(self.toggle_all_options)
        opts_layout.addWidget(toggle_btn)

        content_layout.addWidget(opts_frame)

        # ── EXPORT FOLDER section ─────────────────────────────────────────────
        folder_frame, folder_layout, _folder_hbox = _make_section_frame(
            "EXPORT FOLDER", icon_name="folder-open", accent="#4F9DE0",
            parent=content_widget,
        )

        lbl = QtWidgets.QLabel("Destination Folder:")
        lbl.setObjectName("ctrlLabel")
        folder_layout.addWidget(lbl)
        folder_row = QtWidgets.QHBoxLayout()
        folder_row.setSpacing(6)
        self._folder_field = QtWidgets.QLineEdit()
        self._folder_field.setPlaceholderText("No folder selected")
        self._folder_field.setReadOnly(True)
        self._folder_field.setMinimumHeight(32)
        folder_row.addWidget(self._folder_field)
        browse_btn = QtWidgets.QPushButton("Browse...")
        browse_btn.setMinimumHeight(32)
        browse_btn.setMinimumWidth(90)
        browse_btn.clicked.connect(self.select_folder)
        folder_row.addWidget(browse_btn)
        folder_layout.addLayout(folder_row)

        content_layout.addWidget(folder_frame)

        # ── PROGRESS section ──────────────────────────────────────────────────
        prog_frame, prog_layout, _prog_hbox = _make_section_frame(
            "PROGRESS", icon_name="layers", accent="#34B3A0",
            parent=content_widget,
        )

        self._progress_bar = QtWidgets.QProgressBar()
        self._progress_bar.setVisible(False)
        prog_layout.addWidget(self._progress_bar)
        self._current_obj_lbl = QtWidgets.QLabel("")
        self._current_obj_lbl.setObjectName("hint")
        prog_layout.addWidget(self._current_obj_lbl)
        self._eta_lbl = QtWidgets.QLabel("")
        self._eta_lbl.setObjectName("hint")
        prog_layout.addWidget(self._eta_lbl)

        content_layout.addWidget(prog_frame)

        # ── Export button ─────────────────────────────────────────────────────
        self._export_btn = QtWidgets.QPushButton("Export")
        self._export_btn.setObjectName("btnPrimary")
        self._export_btn.setMinimumHeight(42)
        self._export_btn.clicked.connect(self.export_objects)
        content_layout.addWidget(self._export_btn)

        # ── Status label ──────────────────────────────────────────────────────
        self._status_lbl = QtWidgets.QLabel("--  Ready to export")
        self._status_lbl.setObjectName("statusIdle")
        self._status_lbl.setAlignment(QtCore.Qt.AlignCenter)
        content_layout.addWidget(self._status_lbl)

        root.addWidget(content_widget)
        dlg.show()

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

    # ── Status helper ──────────────────────────────────────────────────────────

    def _set_status(self, msg, state="idle"):
        name = {"ok": "statusOk", "err": "statusErr", "idle": "statusIdle"}.get(state, "statusIdle")
        self._status_lbl.setObjectName(name)
        self._status_lbl.setText(msg)
        self._status_lbl.setStyle(self._status_lbl.style())

    # ── UI actions ─────────────────────────────────────────────────────────────

    def select_folder(self):
        """Open folder browser and store the selected destination path."""
        folder = cmds.fileDialog2(fileMode=3, caption="Select Export Folder")
        if folder:
            self.export_folder = folder[0]
            self._folder_field.setText(self.export_folder)
            self._set_status("✓  Folder selected -- ready to export", "ok")

    def toggle_all_options(self):
        """Toggle all export checkboxes to the opposite of the current Groups state."""
        new_state = not self._groups_check.isChecked()
        for check in (
            self._groups_check,
            self._ptgroups_check,
            self._materials_check,
            self._smoothing_check,
            self._normals_check,
        ):
            check.setChecked(new_state)

    # ── Export helpers ─────────────────────────────────────────────────────────

    def get_export_options(self):
        """Build the OBJexport options string from current checkbox states."""
        def flag(check):
            return "1" if check.isChecked() else "0"

        return (
            "groups={};ptgroups={};materials={};smoothing={};normals={}".format(
                flag(self._groups_check),
                flag(self._ptgroups_check),
                flag(self._materials_check),
                flag(self._smoothing_check),
                flag(self._normals_check),
            )
        )

    def format_time(self, seconds):
        """Return a human-readable duration string."""
        if seconds < 60:
            return "{:.0f}s".format(seconds)
        elif seconds < 3600:
            return "{}m {}s".format(int(seconds / 60), int(seconds % 60))
        else:
            return "{}h {}m".format(int(seconds / 3600), int((seconds % 3600) / 60))

    # ── Core export ────────────────────────────────────────────────────────────

    def export_objects(self):
        """Main export routine -- iterates group children and writes individual OBJ files."""
        from PySide6 import QtWidgets

        if not self.export_folder:
            self._set_status("✕  Please select an export folder first", "err")
            cmds.warning("PXLtools OBJ Exporter: No export folder selected.")
            return

        selection = cmds.ls(selection=True, long=True)
        if not selection:
            self._set_status("✕  No group selected", "err")
            cmds.warning("PXLtools OBJ Exporter: No group selected.")
            return

        all_children = []
        for sel in selection:
            children = cmds.listRelatives(sel, children=True, fullPath=True, type="transform")
            if children:
                all_children.extend(children)

        if not all_children:
            self._set_status("✕  No objects found in the selected group", "err")
            cmds.warning("PXLtools OBJ Exporter: No child transforms found in selection.")
            return

        export_options = self.get_export_options()
        log.debug("OBJ Exporter -- options: %s", export_options)

        total_objects = len(all_children)
        self._progress_bar.setMaximum(total_objects)
        self._progress_bar.setValue(0)
        self._progress_bar.setVisible(True)
        self._export_btn.setEnabled(False)
        self._set_status("--  Exporting...", "idle")

        self.start_time = time.time()
        exported_count  = 0

        for i, obj in enumerate(all_children):
            obj_name  = obj.split("|")[-1]
            file_path = os.path.join(self.export_folder, obj_name + ".obj")

            progress_percent = int((float(i) / total_objects) * 100)
            self._current_obj_lbl.setText(
                "Exporting: {} ({}/{})".format(obj_name, i + 1, total_objects)
            )

            if i > 0:
                elapsed  = time.time() - self.start_time
                avg_time = elapsed / i
                eta      = avg_time * (total_objects - i)
                self._eta_lbl.setText(
                    "ETA: {} ({}% complete)".format(self.format_time(eta), progress_percent)
                )

            self._progress_bar.setValue(i + 1)
            QtWidgets.QApplication.processEvents()
            cmds.select(obj, replace=True)

            try:
                cmds.file(
                    file_path,
                    force=True,
                    options=export_options,
                    type="OBJexport",
                    exportSelected=True,
                )
                exported_count += 1
            except Exception as exc:
                cmds.warning(
                    "PXLtools OBJ Exporter: Failed to export '{}' -- {}".format(obj_name, exc)
                )

        # Completion
        total_time = time.time() - self.start_time
        self._current_obj_lbl.setText("")
        self._eta_lbl.setText("Completed in {}".format(self.format_time(total_time)))
        state = "ok" if exported_count == total_objects else "err"
        self._set_status(
            "✓  Exported {} of {} objects".format(exported_count, total_objects), state
        )
        self._progress_bar.setValue(total_objects)
        self._export_btn.setEnabled(True)

        try:
            cmds.select(selection, replace=True)
        except Exception:
            pass

        log.info(
            "OBJ Exporter: exported %d/%d files to '%s'",
            exported_count,
            total_objects,
            self.export_folder,
        )


# ---------------------------------------------------------------------------
# Run / entry point
# ---------------------------------------------------------------------------

def run():
    """Launch the PXLtools OBJ Exporter."""
    OBJExporter()
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
