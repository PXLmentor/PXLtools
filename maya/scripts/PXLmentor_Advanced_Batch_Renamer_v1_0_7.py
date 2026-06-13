"""
Tool Name   : PXLmentor Advanced Batch Renamer
Version     : 1.0.7
Stage       : Stable
Author      : PXLmentor AI Pipeline TD
Description : Comprehensive Maya renaming utility with search/replace, prefix/suffix, and sequential numbering.

Changelog:
    1.0.7 - PXLtools branding pass: in-tool header logo swapped
                 from PixelMentor_Logo_Long.png to PXLtools_logo.png.
                 Fallback text label changed to "PXLtools".
    1.0.6 - Fixed QtWidgets.Qt.AlignCenter → QtCore.Qt.AlignCenter (PySide6 compatibility).
    1.0.5 - Full PySide6 QDialog migration — same dark theme as TurnTable Builder v1.0.5.
            Replaced cmds.window + all cmds widgets with QDialog + Qt equivalents.
            Singleton pattern added (topLevelWidgets search). CollapsibleSection used for
            Rename, Search & Replace, and Instructions sections. MAIN_QSS applied globally.
    1.0.4 - UI polish: primary action buttons use brand orange (#E8820C).
            Reset button neutral dark grey. boldLabelFont labels. spacing rhythm.
            status bar prefixed with ✓ / ✕ / — . frameLayout labels uppercased.
    1.0.3 - Fix: number now appended AFTER suffix (correct VFX order).
            Fix: numbering index shallowest-first. Fix: padding field layout.
            Fix: rename_with_options() validates and sanitizes names.
    1.0.2 - UI reorganized to accordion layout (two collapsible frameLayouts).
    1.0.1 - UI standardization. Unified header, icon, branding, instructions tab.
    1.0.0 - Initial stable release.
"""

import re
import os
import maya.cmds as cmds


# ── Colour tokens ─────────────────────────────────────────────────────────────

class _C:
    BG_DARK         = "#333333"
    BG_WINDOW       = "#464646"
    BG_SECTION_HDR  = "#393939"
    BG_SECTION_BOD  = "#4a4a4a"
    BG_INPUT        = "#3a3a3a"
    BG_HEADER       = "#0D1F24"
    BORDER          = "#2b2b2b"
    ORANGE          = "#E8820C"
    TEXT_PRIMARY    = "#dcdcdc"
    TEXT_MUTED      = "#b0b0b0"
    STATUS_OK_BG    = "#2a402a"
    STATUS_OK_TEXT  = "#7acc7a"
    STATUS_ERR_BG   = "#4a3030"
    STATUS_ERR_TEXT = "#e07070"
    HEADER_BG   = (0.051, 0.122, 0.141)
    BTN_PRIMARY = (0.910, 0.510, 0.047)
    BTN_RESET   = (0.320, 0.320, 0.320)
    STATUS_OK   = (0.220, 0.420, 0.220)
    STATUS_ERR  = (0.500, 0.220, 0.220)
    STATUS_IDLE = (0.220, 0.220, 0.220)


# ── Global QSS ────────────────────────────────────────────────────────────────

MAIN_QSS = """
QDialog, QWidget {
    background: #464646;
    color: #dcdcdc;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 12px;
}
QPushButton {
    background: #555555; color: #dcdcdc;
    border: 1px solid #2b2b2b; border-radius: 3px;
    font-size: 12px; font-weight: bold; letter-spacing: 0.8px;
    padding: 0 14px; min-height: 34px;
}
QPushButton:hover { background: #606060; color: #f0f0f0; }
QPushButton:pressed { background: #404040; }
QPushButton:disabled { background: #404040; color: #686868; border-color: #333333; }
QPushButton#btnPrimary {
    background: #E8820C; color: white; border: none;
    font-size: 13px; letter-spacing: 1.2px; min-height: 42px;
}
QPushButton#btnPrimary:hover { background: #f09020; }
QPushButton#btnPrimary:pressed { background: #c06008; }
QPushButton#btnPrimary:disabled { background: #5a4000; color: #9a7020; }
QLabel#statusOk {
    background: #2a402a; color: #7acc7a;
    border: 1px solid #3a5a3a; border-radius: 2px;
    padding: 5px 10px; font-size: 11px;
}
QLabel#statusIdle {
    background: #404040; color: #888888;
    border: 1px solid #333333; border-radius: 2px;
    padding: 5px 10px; font-size: 11px;
}
QLabel#statusErr {
    background: #4a3030; color: #e07070;
    border: 1px solid #6a3a3a; border-radius: 2px;
    padding: 5px 10px; font-size: 11px;
}
QLineEdit {
    background: #3a3a3a; color: #dcdcdc;
    border: 1px solid #2b2b2b; border-radius: 2px;
    padding: 4px 8px; font-size: 12px;
}
QSpinBox {
    background: #3a3a3a; color: #dcdcdc;
    border: 1px solid #2b2b2b; border-radius: 2px;
    padding: 2px 6px; font-size: 12px;
    min-width: 60px;
}
QCheckBox { color: #dcdcdc; font-size: 12px; spacing: 8px; }
QCheckBox::indicator {
    width: 16px; height: 16px;
    border-radius: 2px; background: #3a3a3a; border: 1px solid #2b2b2b;
}
QCheckBox::indicator:checked { background: #E8820C; border: 1px solid #c06000; }
QCheckBox:disabled { color: #686868; }
QFrame#divider {
    background: #2b2b2b; border: none; max-height: 1px; min-height: 1px;
}
"""


# ── Helper: CollapsibleSection ────────────────────────────────────────────────

class CollapsibleSection(object):
    def __init__(self, title, number=None, parent=None):
        from PySide6 import QtWidgets, QtCore, QtGui

        self._collapsed = False
        self._container = QtWidgets.QWidget(parent)
        outer = QtWidgets.QVBoxLayout(self._container)
        outer.setContentsMargins(0, 0, 0, 2)
        outer.setSpacing(0)

        self._header = QtWidgets.QFrame()
        self._header.setFixedHeight(38)
        self._header.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self._header.setStyleSheet(
            "QFrame { background: #393939; border: 1px solid #2b2b2b; "
            "border-bottom: none; border-radius: 3px 3px 0 0; }"
        )
        hbox = QtWidgets.QHBoxLayout(self._header)
        hbox.setContentsMargins(10, 0, 10, 0)
        hbox.setSpacing(6)

        self._arrow = QtWidgets.QLabel("▾")
        self._arrow.setStyleSheet("color: #E8820C; font-size: 16px; background: transparent;")
        hbox.addWidget(self._arrow)

        if number:
            num_lbl = QtWidgets.QLabel(number)
            num_lbl.setStyleSheet(
                "color: #aaaaaa; font-size: 12px; font-family: 'Courier New'; background: transparent;"
            )
            hbox.addWidget(num_lbl)

        title_lbl = QtWidgets.QLabel(title.upper())
        title_lbl.setStyleSheet(
            "color: #dcdcdc; font-weight: bold; font-size: 12px; "
            "letter-spacing: 1px; background: transparent;"
        )
        hbox.addWidget(title_lbl)
        hbox.addStretch()
        outer.addWidget(self._header)

        self._body = QtWidgets.QFrame()
        self._body.setStyleSheet(
            "QFrame { background: #4a4a4a; border: 1px solid #2b2b2b; "
            "border-top: 1px solid #3a3a3a; border-radius: 0 0 3px 3px; }"
        )
        self._body_layout = QtWidgets.QVBoxLayout(self._body)
        self._body_layout.setContentsMargins(10, 10, 10, 12)
        self._body_layout.setSpacing(6)
        outer.addWidget(self._body)

        self._header.mousePressEvent = lambda _e: self.set_collapsed(not self._collapsed)

    @property
    def widget(self):
        return self._container

    @property
    def body_layout(self):
        return self._body_layout

    def add_widget(self, w):
        self._body_layout.addWidget(w)

    def add_layout(self, lay):
        self._body_layout.addLayout(lay)

    def add_spacing(self, n):
        self._body_layout.addSpacing(n)

    def set_collapsed(self, collapsed):
        self._collapsed = collapsed
        self._body.setVisible(not collapsed)
        self._arrow.setText("▸" if collapsed else "▾")
        if collapsed:
            self._header.setStyleSheet(
                "QFrame { background: #3a3a3a; border: 1px solid #2b2b2b; border-radius: 3px; }"
            )
            self._arrow.setStyleSheet("color: #888888; font-size: 16px; background: transparent;")
        else:
            self._header.setStyleSheet(
                "QFrame { background: #393939; border: 1px solid #2b2b2b; "
                "border-bottom: none; border-radius: 3px 3px 0 0; }"
            )
            self._arrow.setStyleSheet("color: #E8820C; font-size: 16px; background: transparent;")
        self._container.updateGeometry()


# ── Main tool class ────────────────────────────────────────────────────────────

class BatchRenamer:
    VERSION            = "1.0.5"
    TOOL_NAME          = "Advanced Batch Renamer"
    ICON_NAME          = "icon_batch_renamer.png"
    WINDOW_OBJECT_NAME = "PXLmentorAdvancedBatchRenamer_v105"

    def __init__(self):
        from PySide6 import QtWidgets

        # Singleton check
        app = QtWidgets.QApplication.instance()
        if app:
            for w in app.topLevelWidgets():
                if w.objectName() == self.WINDOW_OBJECT_NAME:
                    w.show()
                    w.raise_()
                    w.activateWindow()
                    return

        self._prefix_field      = None
        self._base_name_field   = None
        self._suffix_field      = None
        self._add_numbers_check = None
        self._start_number_spin = None
        self._padding_spin      = None
        self._find_field        = None
        self._replace_field     = None
        self._status_lbl        = None

        self._build_window()

    # ── Window construction ────────────────────────────────────────────────────

    def _build_window(self):
        from PySide6 import QtWidgets, QtCore
        from maya import OpenMayaUI as omui
        import shiboken6

        maya_ptr = omui.MQtUtil.mainWindow()
        maya_win = shiboken6.wrapInstance(int(maya_ptr), QtWidgets.QWidget)

        self._window = QtWidgets.QDialog(maya_win)
        self._window.setObjectName(self.WINDOW_OBJECT_NAME)
        self._window.setWindowTitle("{} v{}".format(self.TOOL_NAME, self.VERSION))
        self._window.setMinimumWidth(550)
        self._window.setAttribute(QtCore.Qt.WA_DeleteOnClose, False)
        self._window.setStyleSheet(MAIN_QSS)

        root = QtWidgets.QVBoxLayout(self._window)
        root.setContentsMargins(0, 0, 0, 10)
        root.setSpacing(6)

        root.addWidget(self._build_header())

        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 6, 10, 6)
        content_layout.setSpacing(6)
        root.addWidget(content_widget)

        # Instructions (collapsible, collapsed by default)
        instr = CollapsibleSection("Instructions")
        instr.set_collapsed(True)
        for line in [
            "1. Select objects in the scene to rename",
            "2. Use the Rename section for prefix / base name / suffix / numbering",
            "   Output order: prefix + base + suffix + number",
            "3. Use Search & Replace for targeted find-and-replace on existing names",
            "4. Click the action button in the relevant section",
            "5. All operations can be undone with Ctrl+Z",
        ]:
            lbl = QtWidgets.QLabel(line)
            lbl.setStyleSheet("color: #b0b0b0; font-size: 11px;")
            instr.add_widget(lbl)
        content_layout.addWidget(instr.widget)

        # Rename section (expanded by default)
        rename_sec = CollapsibleSection("Rename")
        rename_sec.set_collapsed(False)

        prefix_lbl = QtWidgets.QLabel("Prefix  (optional):")
        prefix_lbl.setStyleSheet("color: #b0b0b0; font-size: 11px; font-weight: bold;")
        rename_sec.add_widget(prefix_lbl)
        self._prefix_field = QtWidgets.QLineEdit()
        rename_sec.add_widget(self._prefix_field)

        rename_sec.add_spacing(4)
        base_lbl = QtWidgets.QLabel("Base Name  (leave empty to keep original):")
        base_lbl.setStyleSheet("color: #b0b0b0; font-size: 11px; font-weight: bold;")
        rename_sec.add_widget(base_lbl)
        self._base_name_field = QtWidgets.QLineEdit()
        self._base_name_field.setPlaceholderText("Leave empty to keep original names")
        rename_sec.add_widget(self._base_name_field)

        rename_sec.add_spacing(4)
        suffix_lbl = QtWidgets.QLabel("Suffix  (optional):")
        suffix_lbl.setStyleSheet("color: #b0b0b0; font-size: 11px; font-weight: bold;")
        rename_sec.add_widget(suffix_lbl)
        self._suffix_field = QtWidgets.QLineEdit()
        rename_sec.add_widget(self._suffix_field)

        # Divider
        div = QtWidgets.QFrame()
        div.setObjectName("divider")
        div.setFrameShape(QtWidgets.QFrame.HLine)
        rename_sec.add_widget(div)

        # Sequential numbering
        num_lbl = QtWidgets.QLabel("Sequential Numbering:")
        num_lbl.setStyleSheet("color: #b0b0b0; font-size: 11px; font-weight: bold;")
        rename_sec.add_widget(num_lbl)
        num_row = QtWidgets.QHBoxLayout()
        num_row.setSpacing(8)
        self._add_numbers_check = QtWidgets.QCheckBox("Add Sequential Numbers")
        num_row.addWidget(self._add_numbers_check)
        num_row.addStretch()
        start_lbl = QtWidgets.QLabel("Start:")
        start_lbl.setStyleSheet("color: #b0b0b0; font-size: 11px;")
        num_row.addWidget(start_lbl)
        self._start_number_spin = QtWidgets.QSpinBox()
        self._start_number_spin.setMinimum(0)
        self._start_number_spin.setMaximum(99999)
        self._start_number_spin.setValue(1)
        num_row.addWidget(self._start_number_spin)
        pad_lbl = QtWidgets.QLabel("Padding:")
        pad_lbl.setStyleSheet("color: #b0b0b0; font-size: 11px;")
        num_row.addWidget(pad_lbl)
        self._padding_spin = QtWidgets.QSpinBox()
        self._padding_spin.setMinimum(1)
        self._padding_spin.setMaximum(10)
        self._padding_spin.setValue(3)
        num_row.addWidget(self._padding_spin)
        rename_sec.add_layout(num_row)

        rename_sec.add_spacing(4)
        rename_btn = QtWidgets.QPushButton("Rename Selected Hierarchy")
        rename_btn.setObjectName("btnPrimary")
        rename_btn.clicked.connect(self.rename_with_options)
        rename_sec.add_widget(rename_btn)

        content_layout.addWidget(rename_sec.widget)

        # Search & Replace section (collapsed by default)
        search_sec = CollapsibleSection("Search & Replace")
        search_sec.set_collapsed(True)

        find_lbl = QtWidgets.QLabel("Find:")
        find_lbl.setStyleSheet("color: #b0b0b0; font-size: 11px; font-weight: bold;")
        search_sec.add_widget(find_lbl)
        self._find_field = QtWidgets.QLineEdit()
        search_sec.add_widget(self._find_field)

        search_sec.add_spacing(4)
        replace_lbl = QtWidgets.QLabel("Replace With:")
        replace_lbl.setStyleSheet("color: #b0b0b0; font-size: 11px; font-weight: bold;")
        search_sec.add_widget(replace_lbl)
        self._replace_field = QtWidgets.QLineEdit()
        search_sec.add_widget(self._replace_field)

        search_sec.add_spacing(4)
        search_btn = QtWidgets.QPushButton("Search and Replace")
        search_btn.setObjectName("btnPrimary")
        search_btn.clicked.connect(self.search_replace_only)
        search_sec.add_widget(search_btn)

        content_layout.addWidget(search_sec.widget)

        # Footer
        footer_layout = QtWidgets.QVBoxLayout()
        footer_layout.setSpacing(4)
        reset_btn = QtWidgets.QPushButton("Reset All Fields")
        reset_btn.setFixedHeight(30)
        reset_btn.clicked.connect(self.reset_fields)
        footer_layout.addWidget(reset_btn)

        self._status_lbl = QtWidgets.QLabel("—  Ready to rename")
        self._status_lbl.setObjectName("statusIdle")
        self._status_lbl.setAlignment(QtCore.Qt.AlignCenter)
        footer_layout.addWidget(self._status_lbl)

        content_layout.addLayout(footer_layout)
        content_layout.addStretch()

        self._window.show()
        self._window.adjustSize()

    def _build_header(self):
        from PySide6 import QtWidgets, QtCore, QtGui

        icon_path = cmds.internalVar(userPrefDir=True) + "icons/"

        header = QtWidgets.QWidget()
        header.setFixedHeight(106)
        header.setStyleSheet("background-color: #0D1F24;")

        hbox = QtWidgets.QHBoxLayout(header)
        hbox.setContentsMargins(10, 5, 10, 5)
        hbox.setSpacing(0)

        left_lbl = QtWidgets.QLabel()
        left_lbl.setFixedSize(96, 96)
        left_lbl.setAlignment(QtCore.Qt.AlignCenter)
        icon_file = icon_path + self.ICON_NAME
        if os.path.exists(icon_file):
            left_lbl.setPixmap(
                QtGui.QPixmap(icon_file).scaled(96, 96, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            )
        else:
            left_lbl.setStyleSheet("background: #333333; color: white;")
            left_lbl.setText("[icon]")
        hbox.addWidget(left_lbl)

        center = QtWidgets.QVBoxLayout()
        center.setContentsMargins(0, 0, 0, 0)
        center.setSpacing(2)
        center.setAlignment(QtCore.Qt.AlignVCenter)

        logo_lbl = QtWidgets.QLabel()
        logo_lbl.setFixedSize(262, 48)
        logo_lbl.setAlignment(QtCore.Qt.AlignCenter)
        logo_file = icon_path + "PXLtools_logo.png"
        if os.path.exists(logo_file):
            logo_lbl.setPixmap(
                QtGui.QPixmap(logo_file).scaled(262, 48, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            )
        else:
            logo_lbl.setText("PXLtools")
            logo_lbl.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        logo_row = QtWidgets.QHBoxLayout()
        logo_row.setContentsMargins(0, 0, 0, 0)
        logo_row.addStretch()
        logo_row.addWidget(logo_lbl)
        logo_row.addStretch()
        center.addLayout(logo_row)

        name_lbl = QtWidgets.QLabel(self.TOOL_NAME)
        name_lbl.setAlignment(QtCore.Qt.AlignCenter)
        name_lbl.setStyleSheet("color: white; font-weight: bold; font-size: 11px;")
        center.addWidget(name_lbl)

        ver_lbl = QtWidgets.QLabel("v{}".format(self.VERSION))
        ver_lbl.setAlignment(QtCore.Qt.AlignCenter)
        ver_lbl.setStyleSheet("color: #aaaaaa; font-size: 9px;")
        center.addWidget(ver_lbl)

        hbox.addLayout(center, 1)

        right_spacer = QtWidgets.QLabel()
        right_spacer.setFixedSize(96, 96)
        hbox.addWidget(right_spacer)

        return header

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
                    invalid_names.append("{} → {} (starts with number)".format(short_name, rename_target))

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
                    invalid_names.append("{} → {} (chars sanitized)".format(short_name, sanitized))
                    new_name = sanitized

                if new_name and new_name[0].isdigit():
                    invalid_names.append("{} → {} (starts with number)".format(short_name, new_name))

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
            invalid_list = '\n'.join(['• ' + n for n in invalid_names[:10]])
            if len(invalid_names) > 10:
                invalid_list += '\n... and {} more'.format(len(invalid_names) - 10)
            self._set_status(
                "Renamed {} object(s) — {} name issue(s) detected.".format(
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


# ── Entry point ───────────────────────────────────────────────────────────────

def show():
    BatchRenamer()


show()
