"""
Batch Renamer v1.1.0-stable

Purpose:    Comprehensive Maya renaming utility with search/replace, prefix/suffix, and sequential numbering.
Author:     Cristian Spagnuolo
Date:       2026-06-15
Stack:      Maya 2025
Python:     3.11
Depends:    PySide6, shiboken6, maya.cmds, pxl_ui (shared kit)

Description:
    Comprehensive Maya renaming utility with search/replace, prefix/suffix,
    and sequential numbering. Migrated to the shared PXLtools pxl_ui UI/UX
    standard (one shared stylesheet + AppHeader + shared collapsible sections);
    100% of the rename logic is unchanged from v1.0.7 — only the UI chrome
    was migrated.

Changelog:
    1.1.0 - Migrated the UI to the shared PXLtools pxl_ui kit, EXACTLY mirroring
            the gold-standard PXLtools PBR Material v1.1.0:
              - imports pxl_ui (theme/widgets/icons + pxl_update) with the same
                bootstrap + reload + _PXLUI availability flag pattern;
              - removed bespoke `class _C` and the inline MAIN_QSS; MAIN_QSS is
                now pxlt.tool_qss() with the icon tokens (__CHECK__, __SPINUP__,
                __SPINDOWN__, __SPINUPH__, __SPINDOWNH__, __SLH__, __SLHH__)
                substituted with generated PNG paths;
              - bespoke CollapsibleSection replaced with the shared
                pxlw.CollapsibleSection (grey header bar, accent, chevron);
              - _build_header replaced with pxlw.AppHeader(...), graceful fallback;
              - combos rely on tool_qss only (single native arrow) — no per-widget
                QComboBox styling;
              - inline action buttons + paired fields share height (32) and are
                vertically centred;
              - _FlatTextStyle proxy applied on the dialog;
              - auto-update wired on launch via pxl_update.check (deferred, once/day).
            File renamed PXLmentor_Advanced_Batch_Renamer_v1_0_7.py ->
            PXLtools_Batch_Renamer_v1_1_0.py; window title -> "Batch Renamer".
    1.0.7 - PXLtools branding pass: in-tool header logo swapped
                 from PixelMentor_Logo_Long.png to PXLtools_logo.png.
                 Fallback text label changed to "PXLtools".
    1.0.6 - Fixed QtWidgets.Qt.AlignCenter -> QtCore.Qt.AlignCenter (PySide6 compatibility).
    1.0.5 - Full PySide6 QDialog migration -- same dark theme as TurnTable Builder v1.0.5.
            Replaced cmds.window + all cmds widgets with QDialog + Qt equivalents.
            Singleton pattern added (topLevelWidgets search). CollapsibleSection used for
            Rename, Search & Replace, and Instructions sections. MAIN_QSS applied globally.
    1.0.4 - UI polish: primary action buttons use brand orange (#E8820C).
            Reset button neutral dark grey. boldLabelFont labels. spacing rhythm.
            status bar prefixed with checkmark / X / dash. frameLayout labels uppercased.
    1.0.3 - Fix: number now appended AFTER suffix (correct VFX order).
            Fix: numbering index shallowest-first. Fix: padding field layout.
            Fix: rename_with_options() validates and sanitizes names.
    1.0.2 - UI reorganized to accordion layout (two collapsible frameLayouts).
    1.0.1 - UI standardization. Unified header, icon, branding, instructions tab.
    1.0.0 - Initial stable release.

Usage:
    Paste this script into the Maya Script Editor (Python tab) and press Ctrl+Enter,
    or launch it from the PXLtools shelf.
"""

import re
import os
import sys

import maya.cmds as cmds

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
# Tool constants
# ---------------------------------------------------------------------------

TOOL_NAME = "Batch Renamer"
VERSION = "1.1.0"
WINDOW_OBJECT_NAME = "PXLtoolsBatchRenamer_v110"
ICON_NAME = "icon_batch_renamer.png"


# ---------------------------------------------------------------------------
# Main tool class
# ---------------------------------------------------------------------------

class BatchRenamer:
    """Batch Renamer -- production rename utility for Maya 2025 (pxl_ui)."""

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

        self._prefix_field      = None
        self._base_name_field   = None
        self._suffix_field      = None
        self._add_numbers_check = None
        self._start_number_spin = None
        self._padding_spin      = None
        self._find_field        = None
        self._replace_field     = None
        self._status_lbl        = None
        self._window            = None

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
            "1. Select objects in the scene to rename",
            "2. Use the Rename section for prefix / base name / suffix / numbering",
            "   Output order: prefix + base + suffix + number",
            "3. Use Search & Replace for targeted find-and-replace on existing names",
            "4. Click the action button in the relevant section",
            "5. All operations can be undone with Ctrl+Z",
        ]:
            lbl = QtWidgets.QLabel(line)
            lbl.setObjectName("hint")
            lbl.setWordWrap(True)
            instr_sec.add_widget(lbl)
        content_layout.addWidget(instr_sec)

        # ── RENAME section (expanded by default) ─────────────────────────────
        rename_sec = pxlw.CollapsibleSection(
            "RENAME", icon_name="rename", accent="#E8820C",
            collapsed=False, parent=content_widget,
        )

        prefix_lbl = QtWidgets.QLabel("Prefix  (optional):")
        prefix_lbl.setObjectName("ctrlLabel")
        rename_sec.add_widget(prefix_lbl)
        self._prefix_field = QtWidgets.QLineEdit()
        self._prefix_field.setMinimumHeight(32)
        rename_sec.add_widget(self._prefix_field)

        rename_sec.add_spacing(4)
        base_lbl = QtWidgets.QLabel("Base Name  (leave empty to keep original):")
        base_lbl.setObjectName("ctrlLabel")
        rename_sec.add_widget(base_lbl)
        self._base_name_field = QtWidgets.QLineEdit()
        self._base_name_field.setMinimumHeight(32)
        self._base_name_field.setPlaceholderText("Leave empty to keep original names")
        rename_sec.add_widget(self._base_name_field)

        rename_sec.add_spacing(4)
        suffix_lbl = QtWidgets.QLabel("Suffix  (optional):")
        suffix_lbl.setObjectName("ctrlLabel")
        rename_sec.add_widget(suffix_lbl)
        self._suffix_field = QtWidgets.QLineEdit()
        self._suffix_field.setMinimumHeight(32)
        rename_sec.add_widget(self._suffix_field)

        # Divider
        try:
            div = pxlw.Divider()
        except Exception:
            div = QtWidgets.QFrame()
            div.setObjectName("divider")
            div.setFrameShape(QtWidgets.QFrame.HLine)
        rename_sec.add_widget(div)

        # Sequential numbering
        num_lbl = QtWidgets.QLabel("Sequential Numbering:")
        num_lbl.setObjectName("ctrlLabel")
        rename_sec.add_widget(num_lbl)
        num_row = QtWidgets.QHBoxLayout()
        num_row.setSpacing(8)
        self._add_numbers_check = QtWidgets.QCheckBox("Add Sequential Numbers")
        num_row.addWidget(self._add_numbers_check)
        num_row.addStretch()
        start_lbl = QtWidgets.QLabel("Start:")
        start_lbl.setObjectName("hint")
        num_row.addWidget(start_lbl)
        self._start_number_spin = QtWidgets.QSpinBox()
        self._start_number_spin.setMinimum(0)
        self._start_number_spin.setMaximum(99999)
        self._start_number_spin.setValue(1)
        self._start_number_spin.setMinimumHeight(32)
        num_row.addWidget(self._start_number_spin)
        pad_lbl = QtWidgets.QLabel("Padding:")
        pad_lbl.setObjectName("hint")
        num_row.addWidget(pad_lbl)
        self._padding_spin = QtWidgets.QSpinBox()
        self._padding_spin.setMinimum(1)
        self._padding_spin.setMaximum(10)
        self._padding_spin.setValue(3)
        self._padding_spin.setMinimumHeight(32)
        num_row.addWidget(self._padding_spin)
        rename_sec.add_layout(num_row)

        rename_sec.add_spacing(4)
        rename_btn = QtWidgets.QPushButton("Rename Selected Hierarchy")
        rename_btn.setObjectName("btnPrimary")
        rename_btn.setMinimumHeight(42)
        rename_btn.clicked.connect(self.rename_with_options)
        rename_sec.add_widget(rename_btn)

        content_layout.addWidget(rename_sec)

        # ── SEARCH & REPLACE section (collapsed by default) ──────────────────
        search_sec = pxlw.CollapsibleSection(
            "SEARCH & REPLACE", icon_name="search", accent="#4F9DE0",
            collapsed=True, parent=content_widget,
        )

        find_lbl = QtWidgets.QLabel("Find:")
        find_lbl.setObjectName("ctrlLabel")
        search_sec.add_widget(find_lbl)
        self._find_field = QtWidgets.QLineEdit()
        self._find_field.setMinimumHeight(32)
        search_sec.add_widget(self._find_field)

        search_sec.add_spacing(4)
        replace_lbl = QtWidgets.QLabel("Replace With:")
        replace_lbl.setObjectName("ctrlLabel")
        search_sec.add_widget(replace_lbl)
        self._replace_field = QtWidgets.QLineEdit()
        self._replace_field.setMinimumHeight(32)
        search_sec.add_widget(self._replace_field)

        search_sec.add_spacing(4)
        search_btn = QtWidgets.QPushButton("Search and Replace")
        search_btn.setObjectName("btnPrimary")
        search_btn.setMinimumHeight(42)
        search_btn.clicked.connect(self.search_replace_only)
        search_sec.add_widget(search_btn)

        content_layout.addWidget(search_sec)

        # ── Footer ────────────────────────────────────────────────────────────
        footer_layout = QtWidgets.QVBoxLayout()
        footer_layout.setSpacing(4)
        reset_btn = QtWidgets.QPushButton("Reset All Fields")
        reset_btn.setFixedHeight(32)
        reset_btn.clicked.connect(self.reset_fields)
        footer_layout.addWidget(reset_btn)

        self._status_lbl = QtWidgets.QLabel("--  Ready to rename")
        self._status_lbl.setObjectName("statusIdle")
        self._status_lbl.setAlignment(QtCore.Qt.AlignCenter)
        footer_layout.addWidget(self._status_lbl)

        content_layout.addLayout(footer_layout)

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

    # ── Shared utilities ───────────────────────────────────────────────────────

    def get_hierarchy(self):
        """Return selected objects and all transform descendants, deepest-first."""
        selection = cmds.ls(selection=True, long=True)
        if not selection:
            cmds.warning("No objects selected.")
            return []
        all_objects = []
        for sel in selection:
            all_objects.append(sel)
            descendants = cmds.listRelatives(
                sel, allDescendents=True, fullPath=True, type='transform'
            ) or []
            all_objects.extend(descendants)
        all_objects = sorted(set(all_objects), key=lambda x: x.count('|'), reverse=True)
        return all_objects

    @staticmethod
    def _sanitize_name(name):
        """Replace characters Maya disallows in node names with underscores."""
        sanitized = re.sub(r'[^A-Za-z0-9_]', '_', name)
        sanitized = sanitized.strip('_')
        return sanitized if sanitized else 'node'

    # ── Rename logic ───────────────────────────────────────────────────────────

    def search_replace_only(self):
        """Perform find-and-replace on existing names in the selected hierarchy."""
        old_str = self._find_field.text()
        new_str = self._replace_field.text()

        if not old_str:
            self._set_status("Please enter a search string!", "err")
            cmds.warning("Please enter a search string")
            return

        all_objects = self.get_hierarchy()
        if not all_objects:
            return

        cmds.undoInfo(openChunk=True)
        renamed_count = 0
        invalid_names = []

        try:
            for obj in all_objects:
                if not cmds.objExists(obj):
                    continue
                short_name = obj.split('|')[-1]
                if old_str not in short_name:
                    continue

                new_name = short_name.replace(old_str, new_str)

                if ':' in short_name:
                    if ':' in new_name:
                        new_parts = new_name.rsplit(':', 1)
                        rename_target = new_parts[1] if new_parts[1] else new_parts[0].replace(':', '_')
                    else:
                        rename_target = new_name
                    old_base = short_name.rsplit(':', 1)[1]
                else:
                    old_base      = short_name
                    rename_target = new_name

                rename_target = self._sanitize_name(rename_target)

                if not rename_target:
                    cmds.warning("Could not rename {}: new name has no legal characters.".format(short_name))
                    continue

                if rename_target[0].isdigit():
                    invalid_names.append("{} -> {} (starts with number)".format(short_name, rename_target))

                if rename_target == old_base:
                    continue

                try:
                    cmds.rename(obj, rename_target)
                    renamed_count += 1
                except Exception as e:
                    cmds.warning("Could not rename {}: {}".format(short_name, e))

        finally:
            cmds.undoInfo(closeChunk=True)

        self._finish(renamed_count, invalid_names, context="search")

    def rename_with_options(self):
        """Rename with prefix, base name, suffix, and optional sequential numbering."""
        prefix      = self._prefix_field.text()
        base_name   = self._base_name_field.text()
        suffix      = self._suffix_field.text()
        add_numbers = self._add_numbers_check.isChecked()
        start_num   = self._start_number_spin.value()
        padding     = self._padding_spin.value()

        if not prefix and not base_name and not suffix and not add_numbers:
            self._set_status("Enter a prefix, base name, suffix, or enable numbering.", "err")
            cmds.warning("Please enter at least a prefix, base name, suffix, or enable numbering.")
            return

        all_objects = self.get_hierarchy()
        if not all_objects:
            return

        shallowest_first = sorted(all_objects, key=lambda x: x.count('|'))
        number_index     = {obj: i for i, obj in enumerate(shallowest_first)}

        cmds.undoInfo(openChunk=True)
        renamed_count = 0
        invalid_names = []

        try:
            for obj in all_objects:
                if not cmds.objExists(obj):
                    continue
                short_name = obj.split('|')[-1]

                new_name = base_name if base_name else short_name
                if prefix:
                    new_name = prefix + new_name
                if suffix:
                    new_name = new_name + suffix
                if add_numbers:
                    new_name = new_name + str(start_num + number_index[obj]).zfill(padding)

                sanitized = self._sanitize_name(new_name)
                if sanitized != new_name:
                    invalid_names.append("{} -> {} (chars sanitized)".format(short_name, sanitized))
                    new_name = sanitized

                if new_name and new_name[0].isdigit():
                    invalid_names.append("{} -> {} (starts with number)".format(short_name, new_name))

                if new_name == short_name:
                    continue

                try:
                    cmds.rename(obj, new_name)
                    renamed_count += 1
                except Exception as e:
                    cmds.warning("Could not rename {}: {}".format(short_name, e))

        finally:
            cmds.undoInfo(closeChunk=True)

        self._finish(renamed_count, invalid_names, context="rename")

    def reset_fields(self):
        """Reset all input fields to defaults."""
        self._find_field.setText("")
        self._replace_field.setText("")
        self._prefix_field.setText("")
        self._base_name_field.setText("")
        self._suffix_field.setText("")
        self._add_numbers_check.setChecked(False)
        self._start_number_spin.setValue(1)
        self._padding_spin.setValue(3)
        self._set_status("Ready to rename", "idle")

    def _finish(self, renamed_count, invalid_names, context="rename"):
        """Show result dialog and update status bar."""
        if invalid_names:
            invalid_list = '\n'.join(['* ' + n for n in invalid_names[:10]])
            if len(invalid_names) > 10:
                invalid_list += '\n... and {} more'.format(len(invalid_names) - 10)
            self._set_status(
                "Renamed {} object(s) -- {} name issue(s) detected.".format(
                    renamed_count, len(invalid_names)
                ),
                "err"
            )
            cmds.confirmDialog(
                title='Warning: Name Issues Detected',
                message=(
                    'Renamed {} object(s), but some names had issues.\n'
                    'Names cannot start with numbers or contain special characters.\n\n{}'
                ).format(renamed_count, invalid_list),
                button=['OK'], defaultButton='OK', icon='warning'
            )
        elif renamed_count > 0:
            self._set_status("Renamed {} object(s) successfully.".format(renamed_count), "ok")
            cmds.confirmDialog(
                title='Success',
                message='Renamed {} object(s).'.format(renamed_count),
                button=['OK']
            )
        else:
            msg = "No objects matched the search string." if context == "search" else "No objects were renamed."
            self._set_status(msg, "err")
            cmds.warning(msg)


# ---------------------------------------------------------------------------
# Run / entry point
# ---------------------------------------------------------------------------

def run():
    """Launch the PXLtools Batch Renamer."""
    BatchRenamer()
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
