"""
Tool Name   : PXLmentor OBJ Batch Exporter
Version     : 1.0.5
Stage       : Stable
Author      : PXLmentor AI Pipeline TD
Description : Batch export Maya objects from a group to individual OBJ files with configurable options.

Changelog:
    1.0.5 - PXLtools branding pass: in-tool header logo swapped
                 from PixelMentor_Logo_Long.png to PXLtools_logo.png.
                 Fallback text label changed to "PXLtools".
    1.0.4 - Fixed QtWidgets.Qt.AlignCenter → QtCore.Qt.AlignCenter (PySide6 compatibility).
    1.0.3 - Full PySide6 QDialog migration — same dark theme as TurnTable Builder v1.0.5.
            Replaced cmds.window + all cmds widgets with QDialog + Qt equivalents.
            Singleton pattern added (topLevelWidgets search). CollapsibleSection used for
            Instructions. MAIN_QSS applied globally.
    1.0.2 - UI polish + code cleanup pass: _C color token class; brand-orange primary button;
            status bar prefixes; UPPERCASE section labels; spacing rhythm; _recalc_height().
    1.0.1 - UI standardization. Unified header, icon, branding.
    1.0.0 - Initial stable release. Batch OBJ export, progress bar, ETA, collapsible instructions.
"""

import logging
import os
import time

import maya.cmds as cmds

log = logging.getLogger(__name__)


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
    STATUS_OK_BDR   = "#3a5a3a"
    STATUS_ERR_BG   = "#4a3030"
    STATUS_ERR_TEXT = "#e07070"
    STATUS_ERR_BDR  = "#6a3a3a"
    # Tuples kept for any remaining cmds calls
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
QLabel#sectionLabel {
    color: #aaaaaa; font-size: 11px; font-weight: bold; letter-spacing: 1px;
}
QLineEdit {
    background: #3a3a3a; color: #dcdcdc;
    border: 1px solid #2b2b2b; border-radius: 2px;
    padding: 4px 8px; font-size: 12px;
}
QCheckBox { color: #dcdcdc; font-size: 12px; spacing: 8px; }
QCheckBox::indicator {
    width: 16px; height: 16px;
    border-radius: 2px; background: #3a3a3a; border: 1px solid #2b2b2b;
}
QCheckBox::indicator:checked { background: #E8820C; border: 1px solid #c06000; }
QCheckBox:disabled { color: #686868; }
QProgressBar {
    background: #3a3a3a; border: 1px solid #2b2b2b; border-radius: 2px;
    color: #dcdcdc; text-align: center; min-height: 14px; max-height: 14px;
}
QProgressBar::chunk { background: #E8820C; border-radius: 2px; }
QFrame#divider {
    background: #2b2b2b; border: none; max-height: 1px; min-height: 1px;
}
"""


# ── Helper: CollapsibleSection ────────────────────────────────────────────────

class CollapsibleSection(object):
    """Collapsible section — header bar + body frame."""

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


# ── Helper: non-collapsible section frame ─────────────────────────────────────

def _make_section(title, parent_layout):
    """Build a non-collapsible section header + body, add to parent_layout.
    Returns the body QVBoxLayout."""
    from PySide6 import QtWidgets

    hdr = QtWidgets.QFrame()
    hdr.setFixedHeight(38)
    hdr.setStyleSheet(
        "QFrame { background: #393939; border: 1px solid #2b2b2b; "
        "border-bottom: none; border-radius: 3px 3px 0 0; }"
    )
    hbox = QtWidgets.QHBoxLayout(hdr)
    hbox.setContentsMargins(10, 0, 10, 0)
    lbl = QtWidgets.QLabel(title.upper())
    lbl.setStyleSheet(
        "color: #dcdcdc; font-weight: bold; font-size: 12px; "
        "letter-spacing: 1px; background: transparent;"
    )
    hbox.addWidget(lbl)
    hbox.addStretch()
    parent_layout.addWidget(hdr)

    body = QtWidgets.QFrame()
    body.setStyleSheet(
        "QFrame { background: #4a4a4a; border: 1px solid #2b2b2b; "
        "border-top: 1px solid #3a3a3a; border-radius: 0 0 3px 3px; }"
    )
    body_layout = QtWidgets.QVBoxLayout(body)
    body_layout.setContentsMargins(10, 10, 10, 12)
    body_layout.setSpacing(6)
    parent_layout.addWidget(body)
    return body_layout


# ── Main tool class ────────────────────────────────────────────────────────────

class OBJBatchExporter:
    """PXLmentor OBJ Batch Exporter — export group children as individual OBJ files."""

    VERSION            = "1.0.3"
    TOOL_NAME          = "OBJ Batch Exporter"
    ICON_NAME          = "icon_obj_exporter.png"
    WINDOW_OBJECT_NAME = "PXLmentorOBJBatchExporter_v103"

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

        # Header
        root.addWidget(self._build_header())

        # Scrollable content
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        content = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content)
        content_layout.setContentsMargins(10, 6, 10, 6)
        content_layout.setSpacing(6)
        scroll.setWidget(content)
        root.addWidget(scroll)

        # Instructions (collapsible, collapsed by default)
        instr = CollapsibleSection("Instructions")
        instr.set_collapsed(True)
        for line in [
            "1. Select a group containing the objects to export",
            "2. Configure export options (fewer options = smaller files)",
            "3. Choose destination folder",
            "4. Click Export — process cannot be stopped once started",
        ]:
            lbl = QtWidgets.QLabel(line)
            lbl.setStyleSheet("color: #b0b0b0; font-size: 11px;")
            instr.add_widget(lbl)
        content_layout.addWidget(instr.widget)

        # Export Options section
        opts_layout = _make_section("Export Options", content_layout)
        row = QtWidgets.QHBoxLayout()
        row.setSpacing(20)
        left_col = QtWidgets.QVBoxLayout()
        left_col.setSpacing(4)
        self._groups_check   = QtWidgets.QCheckBox("Groups")
        self._ptgroups_check = QtWidgets.QCheckBox("Polygon Groups")
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
        toggle_btn.setFixedHeight(30)
        toggle_btn.clicked.connect(self.toggle_all_options)
        opts_layout.addWidget(toggle_btn)

        # Export Folder section
        folder_layout = _make_section("Export Folder", content_layout)
        lbl = QtWidgets.QLabel("Destination Folder:")
        lbl.setStyleSheet("color: #b0b0b0; font-size: 11px; font-weight: bold;")
        folder_layout.addWidget(lbl)
        folder_row = QtWidgets.QHBoxLayout()
        folder_row.setSpacing(6)
        self._folder_field = QtWidgets.QLineEdit()
        self._folder_field.setPlaceholderText("No folder selected")
        self._folder_field.setReadOnly(True)
        folder_row.addWidget(self._folder_field)
        browse_btn = QtWidgets.QPushButton("Browse...")
        browse_btn.setFixedSize(90, 30)
        browse_btn.clicked.connect(self.select_folder)
        folder_row.addWidget(browse_btn)
        folder_layout.addLayout(folder_row)

        # Progress section
        prog_layout = _make_section("Progress", content_layout)
        self._progress_bar = QtWidgets.QProgressBar()
        self._progress_bar.setVisible(False)
        prog_layout.addWidget(self._progress_bar)
        self._current_obj_lbl = QtWidgets.QLabel("")
        self._current_obj_lbl.setStyleSheet("color: #b0b0b0; font-size: 11px;")
        prog_layout.addWidget(self._current_obj_lbl)
        self._eta_lbl = QtWidgets.QLabel("")
        self._eta_lbl.setStyleSheet("color: #b0b0b0; font-size: 11px;")
        prog_layout.addWidget(self._eta_lbl)

        # Export button
        self._export_btn = QtWidgets.QPushButton("Export")
        self._export_btn.setObjectName("btnPrimary")
        self._export_btn.setMinimumHeight(42)
        self._export_btn.clicked.connect(self.export_objects)
        content_layout.addWidget(self._export_btn)

        # Status label
        self._status_lbl = QtWidgets.QLabel("—  Ready to export")
        self._status_lbl.setObjectName("statusIdle")
        self._status_lbl.setAlignment(QtCore.Qt.AlignCenter)
        content_layout.addWidget(self._status_lbl)

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

        # Left — tool icon
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

        # Center — logo + name + version
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

        # Right — balance spacer
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

    # ── UI actions ─────────────────────────────────────────────────────────────

    def select_folder(self):
        """Open folder browser and store the selected destination path."""
        folder = cmds.fileDialog2(fileMode=3, caption="Select Export Folder")
        if folder:
            self.export_folder = folder[0]
            self._folder_field.setText(self.export_folder)
            self._set_status("✓  Folder selected — ready to export", "ok")

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
        """Main export routine — iterates group children and writes individual OBJ files."""
        from PySide6 import QtWidgets

        if not self.export_folder:
            self._set_status("✕  Please select an export folder first", "err")
            cmds.warning("PXLmentor OBJ Exporter: No export folder selected.")
            return

        selection = cmds.ls(selection=True, long=True)
        if not selection:
            self._set_status("✕  No group selected", "err")
            cmds.warning("PXLmentor OBJ Exporter: No group selected.")
            return

        all_children = []
        for sel in selection:
            children = cmds.listRelatives(sel, children=True, fullPath=True, type="transform")
            if children:
                all_children.extend(children)

        if not all_children:
            self._set_status("✕  No objects found in the selected group", "err")
            cmds.warning("PXLmentor OBJ Exporter: No child transforms found in selection.")
            return

        export_options = self.get_export_options()
        log.debug("OBJ Batch Exporter — options: %s", export_options)

        total_objects = len(all_children)
        self._progress_bar.setMaximum(total_objects)
        self._progress_bar.setValue(0)
        self._progress_bar.setVisible(True)
        self._export_btn.setEnabled(False)
        self._set_status("—  Exporting…", "idle")

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
                    "PXLmentor OBJ Exporter: Failed to export '{}' — {}".format(obj_name, exc)
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
            "OBJ Batch Exporter: exported %d/%d files to '%s'",
            exported_count,
            total_objects,
            self.export_folder,
        )


# ── Entry point ───────────────────────────────────────────────────────────────

def show():
    OBJBatchExporter()


show()
