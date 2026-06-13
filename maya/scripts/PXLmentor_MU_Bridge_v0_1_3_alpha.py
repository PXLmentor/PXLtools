# Tool Name: PXLmentor MU Bridge
# Version: 0.1.3-alpha
# Author: PXLmentor AI Pipeline TD
# Description: Maya 2025 -> Unreal Engine 5.6 shader-preserving asset bridge.
#              Walks the selected aiStandardSurface networks, exports FBX +
#              .pxlbridge.json sidecar (texture color spaces tagged for ACEScg,
#              normal-map convention noted for UE DirectX flip on import).
#              V0.1: Maya -> Unreal only. Master Material + MaterialInstance
#              workflow. Utility-node translation arrives in V0.2.
# Changelog:
#   0.1.3-alpha - PXLtools branding pass: in-tool header logo swapped
#                 from PixelMentor_Logo_Long.png to PXLtools_logo.png.
#                 Fallback text label changed to "PXLtools".
#   0.1.2-alpha - CP003: Conform to PXLMENTOR_TOOL_STANDARD v1.1.0 - dropped
#                 the 96x96 right spacer from _build_header. Logo now centers
#                 in the visible content area (right of tool icon, to dialog
#                 right margin) rather than on the dialog geometric midline.
#                 Reads as visually centered; the previous symmetric layout
#                 looked off-balance because the spacer carried no visual weight.
#   0.1.1-alpha - CP002: PXLMENTOR_TOOL_STANDARD compliance pass. Rebuilt
#                 _build_header to canonical 106px layout (tool-icon-LEFT
#                 96x96 + center vbox with PixelMentor logo 262x48 + tool
#                 name + version + 96x96 spacer-RIGHT). Added CollapsibleSection
#                 class and _make_section_frame helper verbatim from Arnold
#                 v1.0.4 reference. Added Instructions CollapsibleSection as
#                 the first content section (starts collapsed). Expanded _C
#                 palette to canonical 16 entries. Expanded MAIN_QSS to include
#                 every reserved object name (#collapsibleBody, #sectionFrame,
#                 #ctrlLabel, #hint, #divider, full checkbox indicator block,
#                 QListWidget, scrollbar). Singleton refactored to __new__
#                 guard pattern with Maya main-window parenting. Status helper
#                 renamed _update_status -> _set_status with (msg, state)
#                 signature. Entry point renamed run -> show. Root layout uses
#                 setSizeConstraint(SetFixedSize) for dynamic-height collapse.
#   0.1.0-alpha - CP001: Initial scaffold (singleton PySide6 UI + export pipeline).

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Optional

import maya.cmds as cmds

from PySide6 import QtCore, QtGui, QtWidgets

# ---------------------------------------------------------------------------
# Path setup - the logic package and shared schema must be importable.
# When this file is pasted into Maya's Script Editor, __file__ is not defined;
# fall back to the Maya user scripts directory in that case.
# ---------------------------------------------------------------------------

try:
    _SCRIPTS_DIR = Path(__file__).resolve().parent
except NameError:
    _SCRIPTS_DIR = Path(cmds.internalVar(userScriptDir=True))

if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from pxl_mu_bridge import exporter as _exporter  # noqa: E402
from pxl_mu_bridge.report import ExportReportDialog  # noqa: E402
from pxl_mu_bridge_schema import ExportReport  # noqa: E402

logger = logging.getLogger(__name__)

WINDOW_OBJECT_NAME = "PXLmentorMUBridge_v013"
TOOL_TITLE = "MU Bridge"
TOOL_NAME_IN_HEADER = "Maya -> Unreal Bridge"


# ---------------------------------------------------------------------------
# Color tokens (canonical 16 entries per PXLMENTOR_TOOL_STANDARD § 3)
# ---------------------------------------------------------------------------

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
    HEADER_BG       = (0.051, 0.122, 0.141)
    BTN_PRIMARY     = (0.910, 0.510, 0.047)


# ---------------------------------------------------------------------------
# MAIN_QSS (canonical blocks per PXLMENTOR_TOOL_STANDARD § 4)
# ---------------------------------------------------------------------------

MAIN_QSS = """
QDialog, QWidget {
    background: #464646;
    color: #dcdcdc;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 12px;
}

QFrame#collapsibleBody {
    background: #4a4a4a; border: 1px solid #2b2b2b;
    border-top: 1px solid #3a3a3a; border-radius: 0 0 3px 3px;
}
QFrame#sectionFrame {
    background: #4a4a4a; border: 1px solid #2b2b2b;
    border-top: 1px solid #3a3a3a; border-radius: 0 0 3px 3px;
}

QPushButton {
    background: #555555; color: #dcdcdc;
    border: 1px solid #2b2b2b; border-radius: 3px;
    font-size: 12px; font-weight: bold; letter-spacing: 0.8px;
    padding: 0 14px; min-height: 34px;
}
QPushButton:hover    { background: #606060; color: #f0f0f0; }
QPushButton:pressed  { background: #404040; }
QPushButton:disabled { background: #404040; color: #686868; border-color: #333333; }

QPushButton#btnPrimary {
    background: #E8820C; color: white; border: none;
    font-size: 13px; letter-spacing: 1.2px; min-height: 42px;
}
QPushButton#btnPrimary:hover    { background: #f09020; }
QPushButton#btnPrimary:pressed  { background: #c06008; }
QPushButton#btnPrimary:disabled { background: #5a4000; color: #9a7020; }

QPushButton#btnSmall {
    background: #505050; color: #c0c0c0;
    border: 1px solid #3a3a3a; border-radius: 2px;
    font-size: 11px; font-weight: bold; letter-spacing: 0.5px;
    padding: 0 10px; min-height: 24px; max-height: 24px;
}
QPushButton#btnSmall:hover   { background: #606060; color: #f0f0f0; }
QPushButton#btnSmall:pressed { background: #3a3a3a; }

QLabel#statusOk   { background: #2a402a; color: #7acc7a; border: 1px solid #3a5a3a; border-radius: 2px; padding: 5px 10px; font-size: 11px; }
QLabel#statusIdle { background: #404040; color: #888888; border: 1px solid #333333; border-radius: 2px; padding: 5px 10px; font-size: 11px; }
QLabel#statusErr  { background: #4a3030; color: #e07070; border: 1px solid #6a3a3a; border-radius: 2px; padding: 5px 10px; font-size: 11px; }
QLabel#ctrlLabel  { color: #aaaaaa; font-size: 11px; font-weight: bold; letter-spacing: 1.5px; }
QLabel#hint       { color: #888888; font-size: 11px; }

QLineEdit, QDoubleSpinBox, QSpinBox {
    background: #3a3a3a; color: #dcdcdc;
    border: 1px solid #2b2b2b; border-radius: 2px;
    padding: 4px 8px; font-size: 12px;
}
QListWidget {
    background: #3a3a3a; color: #dcdcdc;
    border: 1px solid #2b2b2b; border-radius: 2px; font-size: 12px;
}
QListWidget::item:selected { background: #E8820C; color: white; }

QCheckBox { color: #dcdcdc; font-size: 12px; spacing: 8px; }
QCheckBox:hover { color: #ffffff; }
QCheckBox::indicator {
    width: 16px; height: 16px;
    border-radius: 2px; background: #3a3a3a; border: 1px solid #2b2b2b;
}
QCheckBox::indicator:hover           { background: #484848; border-color: #888888; }
QCheckBox::indicator:checked         { background: #E8820C; border: 1px solid #c06000; }
QCheckBox::indicator:checked:hover   { background: #f09020; border-color: #E8820C; }
QCheckBox:disabled                   { color: #686868; }
QCheckBox::indicator:disabled        { background: #404040; border-color: #333333; }

QFrame#divider { background: #2b2b2b; border: none; max-height: 1px; min-height: 1px; }

QScrollBar:vertical { background: #3a3a3a; width: 8px; }
QScrollBar::handle:vertical { background: #606060; border-radius: 4px; }
"""


# ---------------------------------------------------------------------------
# CollapsibleSection (verbatim per PXLMENTOR_TOOL_STANDARD § 6)
# ---------------------------------------------------------------------------

class CollapsibleSection(object):
    def __init__(self, title, number=None, parent=None, compact=False):
        self._collapsed = False
        self._compact = compact
        self._container = QtWidgets.QWidget(parent)
        self._container.setObjectName("collapsibleContainer")
        outer = QtWidgets.QVBoxLayout(self._container)
        outer.setContentsMargins(0, 0, 0, 2)
        outer.setSpacing(0)

        self._header = QtWidgets.QFrame()
        self._header.setFixedHeight(26 if compact else 38)
        self._header.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self._header.setStyleSheet(
            "QFrame { background: #393939; border: 1px solid #2b2b2b; "
            "border-bottom: none; border-radius: 3px 3px 0 0; }"
        )
        hbox = QtWidgets.QHBoxLayout(self._header)
        hbox.setContentsMargins(10, 0, 10, 0)
        hbox.setSpacing(6)

        _asiz = "11px" if compact else "16px"
        self._arrow = QtWidgets.QLabel("▾")
        self._arrow.setStyleSheet(
            "color: #E8820C; font-size: {}; background: transparent;".format(_asiz)
        )
        hbox.addWidget(self._arrow)

        if number:
            num_lbl = QtWidgets.QLabel(number)
            num_lbl.setStyleSheet(
                "color: #aaaaaa; font-size: 12px; font-family: 'Courier New'; background: transparent;"
            )
            hbox.addWidget(num_lbl)

        _tsiz = "9px" if compact else "12px"
        title_lbl = QtWidgets.QLabel(title.upper())
        title_lbl.setStyleSheet(
            "color: #dcdcdc; font-weight: bold; font-size: {}; "
            "letter-spacing: 1px; background: transparent;".format(_tsiz)
        )
        hbox.addWidget(title_lbl)
        hbox.addStretch()
        outer.addWidget(self._header)

        # Body - objectName drives QSS, NO inline setStyleSheet (cascade-breaker)
        self._body = QtWidgets.QFrame()
        self._body.setObjectName("collapsibleBody")
        self._body_layout = QtWidgets.QVBoxLayout(self._body)
        if compact:
            self._body_layout.setContentsMargins(6, 5, 6, 7)
            self._body_layout.setSpacing(3)
        else:
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
        _asiz = "11px" if self._compact else "16px"
        if collapsed:
            self._header.setStyleSheet(
                "QFrame { background: #3a3a3a; border: 1px solid #2b2b2b; border-radius: 3px; }"
            )
            self._arrow.setStyleSheet(
                "color: #888888; font-size: {}; background: transparent;".format(_asiz)
            )
        else:
            self._header.setStyleSheet(
                "QFrame { background: #393939; border: 1px solid #2b2b2b; "
                "border-bottom: none; border-radius: 3px 3px 0 0; }"
            )
            self._arrow.setStyleSheet(
                "color: #E8820C; font-size: {}; background: transparent;".format(_asiz)
            )
        self._container.updateGeometry()


# ---------------------------------------------------------------------------
# Non-collapsible section frame helper (verbatim per § 7)
# ---------------------------------------------------------------------------

def _make_section_frame(title, parent=None):
    """Return (container_widget, body_layout, header_hbox) for a non-collapsible section."""
    container = QtWidgets.QWidget(parent)
    outer = QtWidgets.QVBoxLayout(container)
    outer.setContentsMargins(0, 0, 0, 2)
    outer.setSpacing(0)

    header = QtWidgets.QFrame()
    header.setFixedHeight(38)
    header.setStyleSheet(
        "QFrame { background: #393939; border: 1px solid #2b2b2b; "
        "border-bottom: none; border-radius: 3px 3px 0 0; }"
    )
    hbox = QtWidgets.QHBoxLayout(header)
    hbox.setContentsMargins(10, 0, 10, 0)
    hbox.setSpacing(6)
    title_lbl = QtWidgets.QLabel(title.upper())
    title_lbl.setStyleSheet(
        "color: #dcdcdc; font-weight: bold; font-size: 12px; "
        "letter-spacing: 1px; background: transparent;"
    )
    hbox.addWidget(title_lbl)
    hbox.addStretch()
    outer.addWidget(header)

    body = QtWidgets.QFrame()
    body.setObjectName("sectionFrame")
    body_layout = QtWidgets.QVBoxLayout(body)
    body_layout.setContentsMargins(10, 10, 10, 12)
    body_layout.setSpacing(6)
    outer.addWidget(body)

    return container, body_layout, hbox


# ---------------------------------------------------------------------------
# Tool
# ---------------------------------------------------------------------------

class MUBridge:
    """MU Bridge - production tool for Maya 2025.

    Maya -> Unreal shader-preserving asset bridge. V0.1 export-only.
    """

    VERSION = "0.1.3-alpha"
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
        self._dialog: Optional[QtWidgets.QDialog] = None
        self._last_manifest_path: Optional[Path] = None
        self._last_report: Optional[ExportReport] = None
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        from maya import OpenMayaUI as omui
        import shiboken6

        main_ptr = omui.MQtUtil.mainWindow()
        maya_main = shiboken6.wrapInstance(int(main_ptr), QtWidgets.QWidget)

        dlg = QtWidgets.QDialog(maya_main)
        dlg.setObjectName(WINDOW_OBJECT_NAME)
        dlg.setWindowTitle("{} v{}".format(TOOL_TITLE, self.version))
        dlg.setMinimumWidth(620)
        dlg.setStyleSheet(MAIN_QSS)
        dlg.setAttribute(QtCore.Qt.WA_DeleteOnClose, False)
        self._dialog = dlg

        # Root layout - SetFixedSize makes dialog auto-resize on collapse/expand
        root_vbox = QtWidgets.QVBoxLayout(dlg)
        root_vbox.setContentsMargins(0, 0, 0, 0)
        root_vbox.setSpacing(0)
        root_vbox.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)

        # ── HEADER ──────────────────────────────────────────────────────
        root_vbox.addWidget(self._build_header())

        # ── CONTENT ─────────────────────────────────────────────────────
        content_widget = QtWidgets.QWidget()
        content_vbox = QtWidgets.QVBoxLayout(content_widget)
        content_vbox.setContentsMargins(15, 10, 15, 10)
        content_vbox.setSpacing(10)

        # Instructions (collapsible, starts collapsed) - first section
        instr_sec = CollapsibleSection("Instructions", parent=content_widget)
        instr_sec.set_collapsed(True)
        instr_sec.add_widget(QtWidgets.QLabel(
            "1. Select one or more transforms whose meshes carry aiStandardSurface materials."
        ))
        instr_sec.add_widget(QtWidgets.QLabel(
            "2. Choose an output folder for the FBX + .pxlbridge.json sidecar."
        ))
        instr_sec.add_widget(QtWidgets.QLabel(
            "3. Set an asset name (becomes <name>.fbx and <name>.pxlbridge.json)."
        ))
        instr_sec.add_widget(QtWidgets.QLabel(
            "4. Click EXPORT SELECTED. Texture color spaces are tagged for the ACEScg pipeline."
        ))
        instr_sec.add_widget(QtWidgets.QLabel(
            "5. Review the export report dialog for warnings or dropped Arnold attributes "
            "(subsurface, coat, transmission, sheen are not mapped in V0.1)."
        ))
        content_vbox.addWidget(instr_sec.widget)

        # Output folder section
        out_frame, out_layout, _out_hbox = _make_section_frame(
            "Output Folder", parent=content_widget,
        )
        lbl_out = QtWidgets.QLabel("Folder for the .fbx + .pxlbridge.json:")
        lbl_out.setObjectName("ctrlLabel")
        out_layout.addWidget(lbl_out)
        out_row = QtWidgets.QHBoxLayout()
        out_row.setSpacing(6)
        self._out_field = QtWidgets.QLineEdit()
        self._out_field.setPlaceholderText("Pick a folder...")
        btn_browse = QtWidgets.QPushButton("Select Folder")
        btn_browse.setMinimumWidth(120)
        btn_browse.clicked.connect(self._pick_output_folder)
        out_row.addWidget(self._out_field)
        out_row.addWidget(btn_browse)
        out_layout.addLayout(out_row)
        content_vbox.addWidget(out_frame)

        # Asset name section
        name_frame, name_layout, _name_hbox = _make_section_frame(
            "Asset Name", parent=content_widget,
        )
        lbl_name = QtWidgets.QLabel("Asset name (no extension):")
        lbl_name.setObjectName("ctrlLabel")
        name_layout.addWidget(lbl_name)
        self._name_field = QtWidgets.QLineEdit()
        self._name_field.setPlaceholderText("e.g. hero_prop_A  (becomes hero_prop_A.fbx)")
        name_layout.addWidget(self._name_field)
        hint_lbl = QtWidgets.QLabel(
            "Invalid characters in filenames (< > : \" / \\ | ? *) are rejected at export time."
        )
        hint_lbl.setObjectName("hint")
        hint_lbl.setWordWrap(True)
        name_layout.addWidget(hint_lbl)
        content_vbox.addWidget(name_frame)

        # Action row + status
        btn_row = QtWidgets.QHBoxLayout()
        btn_row.setSpacing(8)
        self._btn_show_report = QtWidgets.QPushButton("Show Last Report")
        self._btn_show_report.setObjectName("btnSmall")
        self._btn_show_report.setMinimumWidth(140)
        self._btn_show_report.clicked.connect(self._show_last_report)
        self._btn_show_report.setEnabled(False)
        self._btn_primary = QtWidgets.QPushButton("EXPORT SELECTED")
        self._btn_primary.setObjectName("btnPrimary")
        self._btn_primary.clicked.connect(self._on_export_clicked)
        btn_row.addWidget(self._btn_show_report)
        btn_row.addStretch(1)
        btn_row.addWidget(self._btn_primary, 2)
        content_vbox.addLayout(btn_row)

        self._status_lbl = QtWidgets.QLabel(
            "Ready. Select transform(s), choose output folder, set asset name, then EXPORT SELECTED."
        )
        self._status_lbl.setObjectName("statusIdle")
        self._status_lbl.setWordWrap(True)
        content_vbox.addWidget(self._status_lbl)

        root_vbox.addWidget(content_widget)
        dlg.show()

    # ------------------------------------------------------------------
    # Header bar (per § 5 - verbatim from Arnold v1.0.4)
    # ------------------------------------------------------------------

    def _build_header(self):
        icon_path = cmds.internalVar(userPrefDir=True) + "icons/"
        bg = tuple(int(v * 255) for v in _C.HEADER_BG)

        header_widget = QtWidgets.QWidget()
        header_widget.setFixedHeight(106)
        header_widget.setStyleSheet(
            "background-color: rgb({},{},{});".format(*bg)
        )

        root_hbox = QtWidgets.QHBoxLayout(header_widget)
        root_hbox.setContentsMargins(10, 5, 10, 5)
        root_hbox.setSpacing(0)

        # LEFT: tool icon 96x96 (same image as the shelf button)
        left_label = QtWidgets.QLabel()
        left_label.setFixedSize(96, 96)
        left_label.setAlignment(QtCore.Qt.AlignCenter)
        tool_icon = icon_path + "icon_mu_bridge.png"
        if os.path.exists(tool_icon):
            pixmap = QtGui.QPixmap(tool_icon).scaled(
                96, 96, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation,
            )
            left_label.setPixmap(pixmap)
        else:
            left_label.setText("[Icon]")
            left_label.setStyleSheet("background-color: rgb(51,51,51); color: white;")
        root_hbox.addWidget(left_label)

        # CENTER: logo + tool name + version, vertically stacked
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
                262, 48, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation,
            )
            logo_label.setPixmap(logo_pixmap)
        else:
            logo_label.setText("PXLmentor")
            logo_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")

        logo_hbox = QtWidgets.QHBoxLayout()
        logo_hbox.setContentsMargins(0, 0, 0, 0)
        logo_hbox.addStretch()
        logo_hbox.addWidget(logo_label)
        logo_hbox.addStretch()

        name_label = QtWidgets.QLabel(TOOL_NAME_IN_HEADER)
        name_label.setAlignment(QtCore.Qt.AlignCenter)
        name_label.setStyleSheet("color: white; font-weight: bold; font-size: 11px;")

        version_label = QtWidgets.QLabel("v{}".format(self.version))
        version_label.setAlignment(QtCore.Qt.AlignCenter)
        version_label.setStyleSheet("color: #aaaaaa; font-size: 9px;")

        center_vbox.addLayout(logo_hbox)
        center_vbox.addWidget(name_label)
        center_vbox.addWidget(version_label)
        root_hbox.addLayout(center_vbox, 1)

        # NO right spacer per PXLMENTOR_TOOL_STANDARD v1.1.0 - the center_vbox
        # stretches all the way to the right margin so the logo centers in the
        # visible content area (visually balanced against the left icon).

        return header_widget

    # ------------------------------------------------------------------
    # Status helper (per § 11)
    # ------------------------------------------------------------------

    def _set_status(self, msg, state="idle"):
        name = {"ok": "statusOk", "err": "statusErr", "idle": "statusIdle"}.get(
            state, "statusIdle",
        )
        self._status_lbl.setObjectName(name)
        self._status_lbl.setText(msg)
        self._status_lbl.setStyle(self._status_lbl.style())

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _pick_output_folder(self):
        start = self._out_field.text().strip() or os.path.expanduser("~")
        chosen = QtWidgets.QFileDialog.getExistingDirectory(
            self._dialog, "Choose Output Folder", start,
        )
        if chosen:
            self._out_field.setText(chosen.replace("\\", "/"))
            self._set_status("- Output folder set.", "idle")

    def _on_export_clicked(self):
        out_dir = self._out_field.text().strip()
        asset_name = self._name_field.text().strip()

        if not out_dir:
            self._set_status("X Pick an output folder first.", "err")
            return
        if not asset_name:
            self._set_status("X Enter an asset name.", "err")
            return
        if any(c in asset_name for c in r'<>:"/\|?*'):
            self._set_status("X Asset name contains invalid characters.", "err")
            return

        self._btn_primary.setEnabled(False)
        self._set_status("Exporting...", "idle")
        QtWidgets.QApplication.processEvents()

        try:
            manifest_path, report = _exporter.export_selection(
                Path(out_dir), asset_name,
            )
        except ValueError as exc:
            self._set_status("X Export failed: {}".format(exc), "err")
            self._btn_primary.setEnabled(True)
            return
        except Exception as exc:
            logger.exception("Unexpected export failure")
            self._set_status("X Unexpected error: {}".format(exc), "err")
            self._btn_primary.setEnabled(True)
            return

        self._last_manifest_path = manifest_path
        self._last_report = report
        self._btn_show_report.setEnabled(True)
        self._btn_primary.setEnabled(True)

        msg = "- Exported {}  ({} warning(s), {} dropped param(s))".format(
            manifest_path.name, len(report.warnings), len(report.dropped_params),
        )
        self._set_status(msg, "err" if report.validation_errors else "ok")
        self._show_last_report()

    def _show_last_report(self):
        if not self._last_report or not self._last_manifest_path:
            return
        dlg = ExportReportDialog(
            self._last_report, self._last_manifest_path, parent=self._dialog,
        )
        dlg.exec()


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

def show():
    MUBridge()


show()
