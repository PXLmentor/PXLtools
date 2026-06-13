# Tool Name: PXLmentor Arnold PBR Material Creator
# Version: 1.0.6
# Author: PXLmentor AI Pipeline TD
# Description: Create Arnold aiStandardSurface PBR materials from Substance Painter texture sets.
#              Supports UDIM, ACES 1.2, custom texture identifiers, shared place2dTexture,
#              and bump-from-diffuse fallback.
# Changelog:
#   1.0.6 - PXLtools branding pass: in-tool header logo swapped
#                 from PixelMentor_Logo_Long.png to PXLtools_logo.png.
#                 Fallback text label changed to "PXLtools".
#   1.0.5 - Conform to PXLMENTOR_TOOL_STANDARD v1.1.0 - removed the 96x96
#           right-spacer from _build_header so the PXLmentor logo centers in
#           the visible content area (right of the tool icon) rather than on
#           the dialog geometric midline. The previous symmetric layout looked
#           off-balance because the spacer carried no visual weight.
#   1.0.4 - Section reorder: Texture Location first, then Texture Identifiers.
#           Renamed "Texture Folder" → "Texture Location".
#           Auto-detect identifier logic: scans folder on selection, matches known aliases
#           (BaseColor/Diff/Diffuse/Albedo, Roughness/Rough/Rgh, Metalness/Metallic/Met/Mtl,
#           Normal/Norm/Nrm) case-insensitively, populates fields automatically.
#           Detection result shown in hint label; Re-detect button available.
#           Window expansion fix: removed QScrollArea, content layout directly in dialog root.
#           root_vbox.setSizeConstraint(SetFixedSize) — dialog auto-resizes on section toggle.
#           QSS cascade fix: CollapsibleSection body uses setObjectName("collapsibleBody")
#           instead of inline setStyleSheet (was breaking child-widget cascade).
#           _make_section_frame body uses setObjectName("sectionFrame") — same fix.
#           Full TurnTable v1.0.17 QSS parity: added #collapsibleBody, #sectionFrame,
#           checkbox hover states, ctrlLabel, hint label styles.
#           Button text visibility: setMinimumWidth(120) on all sidebar/browse buttons.
#   1.0.3 - Full PySide6 QDialog migration — same dark theme as TurnTable Builder v1.0.5.
#           Replaced cmds.window + all cmds widgets with QDialog + Qt equivalents.
#           Singleton pattern added. CollapsibleSection used for Instructions.
#           Non-collapsible section frames for Texture Identifiers, Texture Folder,
#           Select Diffuse Textures, Options. QScrollArea wraps content.
#           MAIN_QSS applied globally.
#   1.0.2 - UI polish + code cleanup pass
#   1.0.1 - UI standardization. Unified header, icon, branding, instructions tab.
#   1.0.0 - Initial stable release

import logging
import os
import re

import maya.cmds as cmds

logger = logging.getLogger(__name__)

WINDOW_OBJECT_NAME = "PXLmentorArnoldPBRMaterialCreator_v106"

# ---------------------------------------------------------------------------
# Texture alias dictionary — auto-detect order is priority order
# ---------------------------------------------------------------------------

_TEXTURE_ALIASES = {
    'diffuse':   ['BaseColor', 'Base_Color', 'Albedo', 'Diffuse', 'Diff', 'Dif'],
    'roughness': ['Roughness', 'Rough', 'Rgh'],
    'metalness': ['Metalness', 'Metallic', 'Metal', 'Met', 'Mtl'],
    'normal':    ['Normal', 'Norm', 'Nrm'],
}

_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.tif', '.tiff', '.exr', '.tga', '.bmp'}


# ---------------------------------------------------------------------------
# Color Tokens
# ---------------------------------------------------------------------------

class _C:
    BG_DARK        = "#333333"
    BG_WINDOW      = "#464646"
    BG_SECTION_HDR = "#393939"
    BG_SECTION_BOD = "#4a4a4a"
    BG_INPUT       = "#3a3a3a"
    BG_HEADER      = "#0D1F24"
    BORDER         = "#2b2b2b"
    ORANGE         = "#E8820C"
    TEXT_PRIMARY   = "#dcdcdc"
    TEXT_MUTED     = "#b0b0b0"
    STATUS_OK_BG   = "#2a402a"
    STATUS_OK_TEXT = "#7acc7a"
    STATUS_ERR_BG  = "#4a3030"
    STATUS_ERR_TEXT = "#e07070"
    INFO_BG        = "#2a2a3a"
    INFO_TEXT      = "#9090c0"
    HEADER_BG      = (0.051, 0.122, 0.141)
    BTN_PRIMARY    = (0.910, 0.510, 0.047)


MAIN_QSS = """
QDialog, QWidget {
    background: #464646;
    color: #dcdcdc;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 12px;
}

/* ── Collapsible section body ── */
QFrame#collapsibleBody {
    background: #4a4a4a; border: 1px solid #2b2b2b;
    border-top: 1px solid #3a3a3a; border-radius: 0 0 3px 3px;
}

/* ── Non-collapsible section body ── */
QFrame#sectionFrame {
    background: #4a4a4a; border: 1px solid #2b2b2b;
    border-top: 1px solid #3a3a3a; border-radius: 0 0 3px 3px;
}

/* ── Scrollbar ── */
QScrollBar:vertical { background: #3a3a3a; width: 8px; }
QScrollBar::handle:vertical { background: #606060; border-radius: 4px; }

/* ── Buttons ── */
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
QPushButton#btnSmall {
    background: #505050; color: #c0c0c0;
    border: 1px solid #3a3a3a; border-radius: 2px;
    font-size: 11px; font-weight: bold; letter-spacing: 0.5px;
    padding: 0 10px; min-height: 24px; max-height: 24px;
}
QPushButton#btnSmall:hover { background: #606060; color: #f0f0f0; }
QPushButton#btnSmall:pressed { background: #3a3a3a; }

/* ── Status labels ── */
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
QLabel#infoLabel {
    background: #2a2a3a; color: #9090c0;
    border: 1px solid #3a3a5a; border-radius: 2px;
    padding: 5px 10px; font-size: 11px;
}
QLabel#ctrlLabel {
    color: #aaaaaa; font-size: 11px; font-weight: bold; letter-spacing: 1.5px;
}
QLabel#hint {
    color: #888888; font-size: 11px;
}

/* ── Inputs ── */
QLineEdit {
    background: #3a3a3a; color: #dcdcdc;
    border: 1px solid #2b2b2b; border-radius: 2px;
    padding: 4px 8px; font-size: 12px;
}
QDoubleSpinBox {
    background: #3a3a3a; color: #dcdcdc;
    border: 1px solid #2b2b2b; border-radius: 2px;
    padding: 2px 6px; font-size: 12px;
}
QListWidget {
    background: #3a3a3a; color: #dcdcdc;
    border: 1px solid #2b2b2b; border-radius: 2px;
    font-size: 12px;
}
QListWidget::item:selected { background: #E8820C; color: white; }

/* ── Checkboxes ── */
QCheckBox { color: #dcdcdc; font-size: 12px; spacing: 8px; }
QCheckBox:hover { color: #ffffff; }
QCheckBox::indicator {
    width: 16px; height: 16px;
    border-radius: 2px; background: #3a3a3a; border: 1px solid #2b2b2b;
}
QCheckBox::indicator:hover { background: #484848; border-color: #888888; }
QCheckBox::indicator:checked { background: #E8820C; border: 1px solid #c06000; }
QCheckBox::indicator:checked:hover { background: #f09020; border-color: #E8820C; }
QCheckBox:disabled { color: #686868; }
QCheckBox::indicator:disabled { background: #404040; border-color: #333333; }

/* ── Divider ── */
QFrame#divider {
    background: #2b2b2b; border: none; max-height: 1px; min-height: 1px;
}
"""


# ---------------------------------------------------------------------------
# CollapsibleSection helper
# ---------------------------------------------------------------------------

class CollapsibleSection(object):
    def __init__(self, title, number=None, parent=None, compact=False):
        from PySide6 import QtWidgets, QtCore, QtGui
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
        self._arrow = QtWidgets.QLabel("\u25be")
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

        # Body — objectName drives QSS, NO inline setStyleSheet (cascade-breaker)
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
    def widget(self): return self._container
    @property
    def body_layout(self): return self._body_layout
    def add_widget(self, w): self._body_layout.addWidget(w)
    def add_layout(self, lay): self._body_layout.addLayout(lay)
    def add_spacing(self, n): self._body_layout.addSpacing(n)

    def set_collapsed(self, collapsed):
        self._collapsed = collapsed
        self._body.setVisible(not collapsed)
        self._arrow.setText("\u25b8" if collapsed else "\u25be")
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
# Non-collapsible section frame helper
# ---------------------------------------------------------------------------

def _make_section_frame(title, parent=None):
    """Return (container_widget, body_layout) for a non-collapsible section."""
    from PySide6 import QtWidgets
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
    # objectName drives QSS — NO inline setStyleSheet (cascade-breaker)
    body.setObjectName("sectionFrame")
    body_layout = QtWidgets.QVBoxLayout(body)
    body_layout.setContentsMargins(10, 10, 10, 12)
    body_layout.setSpacing(6)
    outer.addWidget(body)

    return container, body_layout, hbox  # also return hbox so caller can add right-side widgets


# ---------------------------------------------------------------------------
# Tool
# ---------------------------------------------------------------------------

class ArnoldMaterialCreator:
    """Arnold PBR Material Creator — production tool for Maya 2025."""

    VERSION = "1.0.6"
    _instance = None

    def __new__(cls):
        from PySide6 import QtWidgets
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
        self.texture_folder = ""
        self.texture_files = []
        self._dialog = None
        self._build_ui()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        from PySide6 import QtWidgets, QtCore, QtGui
        from maya import OpenMayaUI as omui
        import shiboken6

        main_ptr = omui.MQtUtil.mainWindow()
        maya_main = shiboken6.wrapInstance(int(main_ptr), QtWidgets.QWidget)

        dlg = QtWidgets.QDialog(maya_main)
        dlg.setObjectName(WINDOW_OBJECT_NAME)
        dlg.setWindowTitle("Arnold Material Creator v{}".format(self.version))
        dlg.setMinimumWidth(570)
        dlg.setStyleSheet(MAIN_QSS)
        dlg.setAttribute(QtCore.Qt.WA_DeleteOnClose, False)
        self._dialog = dlg

        # Root layout — SetFixedSize makes dialog auto-resize with content
        root_vbox = QtWidgets.QVBoxLayout(dlg)
        root_vbox.setContentsMargins(0, 0, 0, 0)
        root_vbox.setSpacing(0)
        root_vbox.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)

        # ── HEADER ──────────────────────────────────────────────────────
        root_vbox.addWidget(self._build_header())

        # ── CONTENT (no QScrollArea — direct layout) ─────────────────────
        content_widget = QtWidgets.QWidget()
        content_vbox = QtWidgets.QVBoxLayout(content_widget)
        content_vbox.setContentsMargins(15, 10, 15, 10)
        content_vbox.setSpacing(10)

        # ── INSTRUCTIONS (collapsible, starts collapsed) ──────────────────
        instr_sec = CollapsibleSection("Instructions", parent=content_widget)
        instr_sec.set_collapsed(True)
        instr_sec.add_widget(QtWidgets.QLabel(
            "1. Select the texture folder (Substance Painter export recommended)"
        ))
        instr_sec.add_widget(QtWidgets.QLabel(
            "2. Identifiers are auto-detected — adjust if your naming differs"
        ))
        instr_sec.add_widget(QtWidgets.QLabel(
            "3. Choose textures from the list"
        ))
        instr_sec.add_widget(QtWidgets.QLabel(
            "4. Enable ACES 1.2 if your project uses ACES color management"
        ))
        instr_sec.add_widget(QtWidgets.QLabel(
            "5. Click Create Materials"
        ))
        content_vbox.addWidget(instr_sec.widget)

        # ── TEXTURE LOCATION ─────────────────────────────────────────────
        loc_frame, loc_layout, _loc_hbox = _make_section_frame(
            "Texture Location", parent=content_widget
        )

        lbl_folder = QtWidgets.QLabel("Texture Folder:")
        lbl_folder.setObjectName("ctrlLabel")
        loc_layout.addWidget(lbl_folder)

        folder_row = QtWidgets.QHBoxLayout()
        folder_row.setSpacing(6)
        self._folder_field = QtWidgets.QLineEdit()
        self._folder_field.setReadOnly(True)
        self._folder_field.setPlaceholderText("No folder selected...")
        self._folder_field.setStyleSheet("background: #2a2a2a; color: #b0b0b0;")
        btn_browse = QtWidgets.QPushButton("Select Folder")
        btn_browse.setMinimumWidth(120)
        btn_browse.clicked.connect(self.browse_folder)
        folder_row.addWidget(self._folder_field)
        folder_row.addWidget(btn_browse)
        loc_layout.addLayout(folder_row)

        content_vbox.addWidget(loc_frame)

        # ── TEXTURE IDENTIFIERS ───────────────────────────────────────────
        ident_frame, ident_layout, ident_hbox = _make_section_frame(
            "Texture Identifiers", parent=content_widget
        )

        # Re-detect button in the section header bar
        btn_redetect = QtWidgets.QPushButton("Re-detect")
        btn_redetect.setObjectName("btnSmall")
        btn_redetect.setMinimumWidth(80)
        btn_redetect.clicked.connect(self._redetect)
        ident_hbox.addWidget(btn_redetect)

        desc_lbl = QtWidgets.QLabel(
            "Define texture identifiers matching your naming convention. "
            "Auto-detected from folder on selection."
        )
        desc_lbl.setObjectName("hint")
        desc_lbl.setWordWrap(True)
        ident_layout.addWidget(desc_lbl)

        row1 = QtWidgets.QHBoxLayout()
        row1.setSpacing(8)
        lbl_diff = QtWidgets.QLabel("Diffuse:")
        lbl_diff.setStyleSheet("font-weight: bold;")
        lbl_diff.setFixedWidth(80)
        self._diffuse_suffix_field = QtWidgets.QLineEdit("BaseColor")
        self._diffuse_suffix_field.textChanged.connect(self.update_info_text)
        lbl_rough = QtWidgets.QLabel("Roughness:")
        lbl_rough.setStyleSheet("font-weight: bold;")
        lbl_rough.setFixedWidth(80)
        self._roughness_suffix_field = QtWidgets.QLineEdit("Roughness")
        self._roughness_suffix_field.textChanged.connect(self.update_info_text)
        row1.addWidget(lbl_diff)
        row1.addWidget(self._diffuse_suffix_field)
        row1.addSpacing(10)
        row1.addWidget(lbl_rough)
        row1.addWidget(self._roughness_suffix_field)
        ident_layout.addLayout(row1)

        row2 = QtWidgets.QHBoxLayout()
        row2.setSpacing(8)
        lbl_metal = QtWidgets.QLabel("Metalness:")
        lbl_metal.setStyleSheet("font-weight: bold;")
        lbl_metal.setFixedWidth(80)
        self._metalness_suffix_field = QtWidgets.QLineEdit("Metalness")
        self._metalness_suffix_field.textChanged.connect(self.update_info_text)
        lbl_norm = QtWidgets.QLabel("Normal:")
        lbl_norm.setStyleSheet("font-weight: bold;")
        lbl_norm.setFixedWidth(80)
        self._normal_suffix_field = QtWidgets.QLineEdit("Normal")
        self._normal_suffix_field.textChanged.connect(self.update_info_text)
        row2.addWidget(lbl_metal)
        row2.addWidget(self._metalness_suffix_field)
        row2.addSpacing(10)
        row2.addWidget(lbl_norm)
        row2.addWidget(self._normal_suffix_field)
        ident_layout.addLayout(row2)

        self._aces_checkbox = QtWidgets.QCheckBox(
            "ACES 1.2 (sRGB for color, Raw for scalar)"
        )
        self._aces_checkbox.setChecked(False)
        ident_layout.addWidget(self._aces_checkbox)

        self._colorspace_message = QtWidgets.QLabel("")
        self._colorspace_message.setObjectName("infoLabel")
        self._colorspace_message.setWordWrap(True)
        self._colorspace_message.setVisible(False)
        ident_layout.addWidget(self._colorspace_message)

        # Detection result hint
        self._detect_status_lbl = QtWidgets.QLabel("")
        self._detect_status_lbl.setObjectName("hint")
        self._detect_status_lbl.setWordWrap(True)
        self._detect_status_lbl.setVisible(False)
        ident_layout.addWidget(self._detect_status_lbl)

        content_vbox.addWidget(ident_frame)

        # ── SELECT DIFFUSE TEXTURES ───────────────────────────────────────
        list_frame, list_layout, _list_hbox = _make_section_frame(
            "Select Diffuse Textures", parent=content_widget
        )

        list_row = QtWidgets.QHBoxLayout()
        list_row.setSpacing(6)

        self._textures_list = QtWidgets.QListWidget()
        self._textures_list.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )
        self._textures_list.setMinimumHeight(150)
        list_row.addWidget(self._textures_list)

        btn_col = QtWidgets.QVBoxLayout()
        btn_col.setSpacing(4)
        btn_select_all = QtWidgets.QPushButton("Select All")
        btn_select_all.setMinimumWidth(120)
        btn_select_all.clicked.connect(self.select_all_textures)
        btn_clear = QtWidgets.QPushButton("Clear Selection")
        btn_clear.setMinimumWidth(120)
        btn_clear.clicked.connect(self.clear_selection)
        btn_refresh = QtWidgets.QPushButton("Refresh List")
        btn_refresh.setMinimumWidth(120)
        btn_refresh.clicked.connect(self.refresh_list)
        btn_col.addWidget(btn_select_all)
        btn_col.addWidget(btn_clear)
        btn_col.addWidget(btn_refresh)
        btn_col.addStretch()
        list_row.addLayout(btn_col)
        list_layout.addLayout(list_row)

        content_vbox.addWidget(list_frame)

        # ── OPTIONS ───────────────────────────────────────────────────────
        opts_frame, opts_layout, _opts_hbox = _make_section_frame(
            "Options", parent=content_widget
        )

        cols_row = QtWidgets.QHBoxLayout()
        cols_row.setSpacing(20)
        cols_row.setAlignment(QtCore.Qt.AlignTop)

        left_col = QtWidgets.QVBoxLayout()
        left_col.setSpacing(5)
        self._no_place2d_checkbox = QtWidgets.QCheckBox("Don't create place2D nodes")
        self._no_place2d_checkbox.setChecked(False)
        self._no_place2d_checkbox.stateChanged.connect(self.toggle_place2d_options)
        self._place2d_checkbox = QtWidgets.QCheckBox("Shared place2D")
        self._place2d_checkbox.setChecked(False)
        self._use_prefix_checkbox = QtWidgets.QCheckBox("Use prefix")
        self._use_prefix_checkbox.setChecked(True)
        self._use_prefix_checkbox.stateChanged.connect(self.toggle_prefix_field)
        self._create_bump_checkbox = QtWidgets.QCheckBox("Bump from diffuse")
        self._create_bump_checkbox.setChecked(False)
        self._create_bump_checkbox.stateChanged.connect(self.toggle_bump_field)
        self._udim_checkbox = QtWidgets.QCheckBox("UDIM workflow")
        self._udim_checkbox.setChecked(False)
        self._udim_checkbox.setEnabled(False)
        left_col.addWidget(self._no_place2d_checkbox)
        left_col.addWidget(self._place2d_checkbox)
        left_col.addWidget(self._use_prefix_checkbox)
        left_col.addWidget(self._create_bump_checkbox)
        left_col.addWidget(self._udim_checkbox)
        cols_row.addLayout(left_col)

        right_col = QtWidgets.QVBoxLayout()
        right_col.setSpacing(4)
        lbl_prefix = QtWidgets.QLabel("Prefix:")
        lbl_prefix.setStyleSheet("font-weight: bold;")
        self._prefix_field = QtWidgets.QLineEdit("AI_")
        self._prefix_field.textChanged.connect(self.update_info_text)
        right_col.addWidget(lbl_prefix)
        right_col.addWidget(self._prefix_field)

        right_col.addSpacing(8)
        lbl_bump = QtWidgets.QLabel("Bump Depth:")
        lbl_bump.setStyleSheet("font-weight: bold;")
        self._bump_value_field = QtWidgets.QDoubleSpinBox()
        self._bump_value_field.setDecimals(3)
        self._bump_value_field.setMinimum(0.0)
        self._bump_value_field.setMaximum(10.0)
        self._bump_value_field.setValue(0.1)
        self._bump_value_field.setEnabled(False)
        right_col.addWidget(lbl_bump)
        right_col.addWidget(self._bump_value_field)
        right_col.addStretch()
        cols_row.addLayout(right_col)

        opts_layout.addLayout(cols_row)

        self._udim_note_text = QtWidgets.QLabel("")
        self._udim_note_text.setObjectName("statusOk")
        self._udim_note_text.setVisible(False)
        self._udim_note_text.setWordWrap(True)
        opts_layout.addWidget(self._udim_note_text)

        self._bump_note_text = QtWidgets.QLabel("")
        self._bump_note_text.setObjectName("infoLabel")
        self._bump_note_text.setVisible(False)
        self._bump_note_text.setWordWrap(True)
        opts_layout.addWidget(self._bump_note_text)

        content_vbox.addWidget(opts_frame)

        # ── INFO / STATUS ─────────────────────────────────────────────────
        self._info_text = QtWidgets.QLabel(
            "— Materials will be named: AI_[base_name] (extracted from texture)"
        )
        self._info_text.setObjectName("infoLabel")
        self._info_text.setWordWrap(True)
        content_vbox.addWidget(self._info_text)

        # ── CREATE BUTTON ─────────────────────────────────────────────────
        self._create_button = QtWidgets.QPushButton("Create PBR Materials")
        self._create_button.setObjectName("btnPrimary")
        self._create_button.clicked.connect(self.create_materials)
        content_vbox.addWidget(self._create_button)

        # ── STATUS BAR ────────────────────────────────────────────────────
        self._status_lbl = QtWidgets.QLabel("— Ready to create materials")
        self._status_lbl.setObjectName("statusIdle")
        self._status_lbl.setAlignment(QtCore.Qt.AlignCenter)
        content_vbox.addWidget(self._status_lbl)

        root_vbox.addWidget(content_widget)
        dlg.show()

    # ------------------------------------------------------------------
    # Header builder
    # ------------------------------------------------------------------

    def _build_header(self):
        from PySide6 import QtWidgets, QtGui, QtCore

        icon_path = cmds.internalVar(userPrefDir=True) + "icons/"
        bg = tuple(int(v * 255) for v in _C.HEADER_BG)

        header_widget = QtWidgets.QWidget()
        header_widget.setFixedHeight(106)
        header_widget.setStyleSheet("background-color: rgb({},{},{});".format(*bg))

        root_hbox = QtWidgets.QHBoxLayout(header_widget)
        root_hbox.setContentsMargins(10, 5, 10, 5)
        root_hbox.setSpacing(0)

        left_label = QtWidgets.QLabel()
        left_label.setFixedSize(96, 96)
        left_label.setAlignment(QtCore.Qt.AlignCenter)
        tool_icon = icon_path + "icon_arnold_material.png"
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
            logo_label.setText("PXLmentor")
            logo_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")

        logo_hbox = QtWidgets.QHBoxLayout()
        logo_hbox.setContentsMargins(0, 0, 0, 0)
        logo_hbox.addStretch()
        logo_hbox.addWidget(logo_label)
        logo_hbox.addStretch()

        name_label = QtWidgets.QLabel("Arnold PBR Material Creator")
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
    # Status helper
    # ------------------------------------------------------------------

    def _set_status(self, msg, state="idle"):
        name = {"ok": "statusOk", "err": "statusErr", "idle": "statusIdle"}.get(
            state, "statusIdle"
        )
        self._status_lbl.setObjectName(name)
        self._status_lbl.setText(msg)
        self._status_lbl.setStyle(self._status_lbl.style())

    # ------------------------------------------------------------------
    # UI Event Handlers
    # ------------------------------------------------------------------

    def toggle_place2d_options(self, *args):
        no_place2d = self._no_place2d_checkbox.isChecked()
        self._place2d_checkbox.setEnabled(not no_place2d)
        if no_place2d:
            self._place2d_checkbox.setChecked(False)

    def toggle_prefix_field(self, *args):
        use_prefix = self._use_prefix_checkbox.isChecked()
        self._prefix_field.setEnabled(use_prefix)
        self.update_info_text()

    def toggle_bump_field(self, *args):
        create_bump = self._create_bump_checkbox.isChecked()
        self._bump_value_field.setEnabled(create_bump)

    def update_info_text(self, *args):
        use_prefix = self._use_prefix_checkbox.isChecked()
        if use_prefix:
            prefix = self._prefix_field.text()
            info = "— Materials will be named: {}[base_name] (extracted from texture)".format(prefix)
        else:
            info = "— Materials will be named: [base_name] (extracted from texture)"
        self._info_text.setText(info)

    # ------------------------------------------------------------------
    # Auto-detect identifiers
    # ------------------------------------------------------------------

    def auto_detect_identifiers(self):
        """Scan the selected folder and auto-populate identifier fields from known aliases."""
        if not self.texture_folder or not os.path.isdir(self.texture_folder):
            return

        try:
            all_files = os.listdir(self.texture_folder)
        except Exception:
            return

        image_files = [
            os.path.splitext(f)[0]
            for f in all_files
            if os.path.splitext(f)[1].lower() in _IMAGE_EXTENSIONS
        ]

        if not image_files:
            return

        field_map = {
            'diffuse':   self._diffuse_suffix_field,
            'roughness': self._roughness_suffix_field,
            'metalness': self._metalness_suffix_field,
            'normal':    self._normal_suffix_field,
        }

        detected = {}
        for channel, aliases in _TEXTURE_ALIASES.items():
            for alias in aliases:
                alias_lower = alias.lower()
                if any(alias_lower in stem.lower() for stem in image_files):
                    detected[channel] = alias
                    break

        # Populate fields with detected aliases
        for channel, alias in detected.items():
            field_map[channel].setText(alias)

        # Update detection hint label
        if detected:
            parts = [detected.get(ch, "—") for ch in ('diffuse', 'roughness', 'metalness', 'normal')]
            labels = ["Diffuse: {}".format(parts[0]),
                      "Roughness: {}".format(parts[1]),
                      "Metalness: {}".format(parts[2]),
                      "Normal: {}".format(parts[3])]
            self._detect_status_lbl.setText("Auto-detected \u2014 " + "  \u00b7  ".join(labels))
            self._detect_status_lbl.setVisible(True)
        else:
            self._detect_status_lbl.setText("No known texture patterns detected — check identifiers manually")
            self._detect_status_lbl.setVisible(True)

    def _redetect(self, *args):
        """Re-run auto-detect on the current folder."""
        if not self.texture_folder:
            self._detect_status_lbl.setText("No folder selected")
            self._detect_status_lbl.setVisible(True)
            return
        self.auto_detect_identifiers()

    # ------------------------------------------------------------------
    # Folder / File Operations
    # ------------------------------------------------------------------

    def browse_folder(self, *args):
        """Open folder browser, auto-detect identifiers, then load texture files."""
        folder = cmds.fileDialog2(fileMode=3, caption="Select Texture Folder")
        if folder:
            self.texture_folder = folder[0]
            self._folder_field.setText(self.texture_folder)
            self.auto_detect_identifiers()
            self.load_texture_files()

    def load_texture_files(self):
        """Scan selected folder for diffuse textures and populate the list."""
        self._textures_list.clear()
        self.texture_files = []

        if not os.path.exists(self.texture_folder):
            self.update_status("Invalid folder path", error=True)
            return

        diffuse_identifier = self._diffuse_suffix_field.text()

        try:
            files = os.listdir(self.texture_folder)
        except Exception as e:
            self.update_status("Error reading folder: {}".format(str(e)), error=True)
            return

        has_colorspace_in_names = False
        udim_sets = {}
        non_udim_files = []
        udim_pattern = re.compile(r'\.(\d{4})')

        for file in files:
            name, ext = os.path.splitext(file)
            if ext.lower() in _IMAGE_EXTENSIONS:
                if diffuse_identifier.lower() in name.lower():
                    for indicator in ['ACES', 'ACEScg', 'sRGB', 'Linear', 'Raw']:
                        if indicator in name:
                            has_colorspace_in_names = True
                    udim_match = udim_pattern.search(name)
                    if udim_match:
                        base_name = udim_pattern.sub('', name)
                        udim_number = udim_match.group(1)
                        if base_name not in udim_sets:
                            udim_sets[base_name] = []
                        udim_sets[base_name].append((udim_number, file))
                    else:
                        non_udim_files.append(file)

        for base_name, udim_files in sorted(udim_sets.items()):
            udim_files.sort(key=lambda x: x[0])
            first_udim_file = udim_files[0][1]
            display_name = udim_pattern.sub('.<UDIM>', first_udim_file)
            self.texture_files.append(first_udim_file)
            self._textures_list.addItem(display_name)

        for file in sorted(non_udim_files):
            self.texture_files.append(file)
            self._textures_list.addItem(file)

        if self.texture_files:
            self.update_status("Found {} diffuse texture(s)".format(len(self.texture_files)))
            self.check_normal_availability()
            self.check_udim_availability()
            if has_colorspace_in_names:
                self._aces_checkbox.setChecked(False)
                self._colorspace_message.setText(
                    "Color space detected in filenames — Maya will auto-select. ACES override disabled."
                )
                self._colorspace_message.setVisible(True)
            else:
                self._aces_checkbox.setChecked(True)
                self._colorspace_message.setText(
                    "No color space in filenames — ACES 1.2 workflow recommended and enabled."
                )
                self._colorspace_message.setVisible(True)
        else:
            self.update_status(
                "No textures with identifier '{}' found".format(diffuse_identifier), error=True
            )
            self._colorspace_message.setVisible(False)

    def check_normal_availability(self):
        """Check for normal maps; disable 'bump from diffuse' if normals are present."""
        normal_identifier = self._normal_suffix_field.text()
        has_normal = False
        try:
            all_files = os.listdir(self.texture_folder)
            for file in all_files:
                if normal_identifier.lower() in file.lower():
                    has_normal = True
                    break
        except Exception as e:
            cmds.warning("PXLmentor: Could not check for normal maps — {}".format(e))

        if has_normal:
            self._create_bump_checkbox.setEnabled(False)
            self._create_bump_checkbox.setChecked(False)
            self._bump_value_field.setEnabled(False)
            self._bump_note_text.setText("Note: Bump from diffuse disabled — Normal maps detected")
            self._bump_note_text.setVisible(True)
        else:
            self._create_bump_checkbox.setEnabled(True)
            self._bump_note_text.setVisible(False)

    def check_udim_availability(self):
        """Enable UDIM checkbox and show note if UDIM tiles are detected."""
        udim_pattern = re.compile(r'\.\d{4}\.')
        has_udim = any(udim_pattern.search(f) for f in self.texture_files)
        if has_udim:
            self._udim_checkbox.setEnabled(True)
            self._udim_checkbox.setChecked(True)
            self._udim_note_text.setText(
                "\u2713 UDIM textures detected — UDIM workflow enabled by default."
            )
            self._udim_note_text.setVisible(True)
        else:
            self._udim_checkbox.setEnabled(False)
            self._udim_checkbox.setChecked(False)
            self._udim_note_text.setVisible(False)

    def select_all_textures(self, *args):
        self._textures_list.selectAll()

    def clear_selection(self, *args):
        self._textures_list.clearSelection()

    def refresh_list(self, *args):
        if self.texture_folder:
            self.load_texture_files()
        else:
            self.update_status("No folder selected", error=True)

    # ------------------------------------------------------------------
    # Status Bar
    # ------------------------------------------------------------------

    def update_status(self, message, error=False):
        if error:
            self._set_status("\u2715 " + message, state="err")
        else:
            self._set_status("\u2713 " + message, state="ok")

    # ------------------------------------------------------------------
    # Texture Lookup Helpers
    # ------------------------------------------------------------------

    def find_texture(self, base_name, identifier):
        """Search the texture folder for a file matching base_name and identifier."""
        try:
            all_files = os.listdir(self.texture_folder)
        except Exception:
            return None
        for file in all_files:
            name, ext = os.path.splitext(file)
            if ext.lower() in _IMAGE_EXTENSIONS:
                if identifier.lower() in name.lower() and base_name.lower() in name.lower():
                    return os.path.join(self.texture_folder, file)
        return None

    def extract_base_name(self, texture_file, diffuse_identifier):
        """Extract clean material base name from a texture filename."""
        name_without_ext = os.path.splitext(texture_file)[0]
        udim_pattern = re.compile(r'\.\d{4}')
        name_without_udim = udim_pattern.sub('', name_without_ext)
        identifier_pos = name_without_udim.lower().find(diffuse_identifier.lower())
        if identifier_pos != -1:
            base = name_without_udim[:identifier_pos].rstrip('_-. ')
            for indicator in ['ACES', 'ACEScg', 'sRGB', 'Linear', 'Raw', 'Utility']:
                base = base.replace(indicator, '').replace('  ', ' ')
            base = base.rstrip('_-. ')
            base = re.sub(r'[_\s]+', '_', base)
            base = base.strip('_')
            return base
        return name_without_udim.rstrip('_-. ')

    # ------------------------------------------------------------------
    # Material Creation
    # ------------------------------------------------------------------

    def create_materials(self, *args):
        """Create Arnold aiStandardSurface PBR materials from selected diffuse textures."""
        selected_items = self._textures_list.selectedItems()
        if not selected_items:
            self.update_status("No textures selected", error=True)
            cmds.warning("Please select at least one diffuse texture")
            return

        if not cmds.pluginInfo('mtoa', query=True, loaded=True):
            try:
                cmds.loadPlugin('mtoa')
            except Exception:
                self.update_status("Failed to load Arnold plugin", error=True)
                cmds.warning("Arnold (mtoa) plugin is not available")
                return

        create_place2d = self._place2d_checkbox.isChecked()
        no_place2d = self._no_place2d_checkbox.isChecked()
        use_prefix = self._use_prefix_checkbox.isChecked()
        prefix = self._prefix_field.text() if use_prefix else ""
        create_bump = self._create_bump_checkbox.isChecked()
        bump_value = self._bump_value_field.value()
        use_aces = self._aces_checkbox.isChecked()
        use_udim = self._udim_checkbox.isChecked()

        if no_place2d:
            create_place2d = False

        diffuse_identifier = self._diffuse_suffix_field.text()
        roughness_identifier = self._roughness_suffix_field.text()
        metalness_identifier = self._metalness_suffix_field.text()
        normal_identifier = self._normal_suffix_field.text()

        selected_indices = [
            self._textures_list.row(item) for item in selected_items
        ]

        created_materials = []
        self._create_button.setEnabled(False)

        udim_pattern = re.compile(r'\.\d{4}')

        for idx in selected_indices:
            texture_file = self.texture_files[idx]
            base_name = self.extract_base_name(texture_file, diffuse_identifier)
            material_name = prefix + base_name
            is_udim = bool(udim_pattern.search(texture_file))
            diffuse_path = os.path.join(self.texture_folder, texture_file)
            roughness_path = self.find_texture(base_name, roughness_identifier)
            metalness_path = self.find_texture(base_name, metalness_identifier)
            normal_path = self.find_texture(base_name, normal_identifier)
            colorspace_indicators = ['ACES', 'ACEScg', 'sRGB', 'Linear', 'Raw']
            has_colorspace = any(cs in texture_file for cs in colorspace_indicators)

            try:
                shader = cmds.shadingNode(
                    'aiStandardSurface', asShader=True, name=material_name
                )
                shading_group = cmds.sets(
                    renderable=True, noSurfaceShader=True, empty=True,
                    name="{}_SG".format(material_name)
                )
                cmds.connectAttr(
                    "{}.outColor".format(shader),
                    "{}.surfaceShader".format(shading_group),
                    force=True
                )

                place2d = None
                if create_place2d:
                    place2d = cmds.shadingNode(
                        'place2dTexture', asUtility=True,
                        name="{}_place2d".format(material_name)
                    )

                # Diffuse
                diffuse_file = cmds.shadingNode(
                    'file', asTexture=True, name="{}_diffuse".format(material_name)
                )
                cmds.setAttr(
                    "{}.fileTextureName".format(diffuse_file), diffuse_path, type="string"
                )
                if not has_colorspace:
                    cs = "Utility - sRGB - Texture" if use_aces else "sRGB"
                    cmds.setAttr("{}.colorSpace".format(diffuse_file), cs, type="string")
                if is_udim and use_udim:
                    cmds.setAttr("{}.uvTilingMode".format(diffuse_file), 3)
                if create_place2d:
                    self.connect_place2d(place2d, diffuse_file)
                cmds.connectAttr(
                    "{}.outColor".format(diffuse_file),
                    "{}.baseColor".format(shader),
                    force=True
                )

                # Scalar maps (roughness, metalness)
                for tex_path, tex_attr in [
                    (roughness_path, 'specularRoughness'),
                    (metalness_path, 'metalness'),
                ]:
                    if tex_path:
                        fn = os.path.basename(tex_path)
                        fn_has_cs = any(cs in fn for cs in colorspace_indicators)
                        tex_file = cmds.shadingNode(
                            'file', asTexture=True,
                            name="{}_{}_tex".format(material_name, tex_attr)
                        )
                        cmds.setAttr(
                            "{}.fileTextureName".format(tex_file), tex_path, type="string"
                        )
                        if not fn_has_cs:
                            raw_cs = "Utility - Raw" if use_aces else "Raw"
                            cmds.setAttr(
                                "{}.colorSpace".format(tex_file), raw_cs, type="string"
                            )
                        cmds.setAttr("{}.alphaIsLuminance".format(tex_file), 1)
                        if is_udim and use_udim:
                            cmds.setAttr("{}.uvTilingMode".format(tex_file), 3)
                        if create_place2d:
                            self.connect_place2d(place2d, tex_file)
                        cmds.connectAttr(
                            "{}.outAlpha".format(tex_file),
                            "{}.{}".format(shader, tex_attr),
                            force=True
                        )

                # Normal map or bump fallback
                if normal_path:
                    nfn = os.path.basename(normal_path)
                    nfn_has_cs = any(cs in nfn for cs in colorspace_indicators)
                    normal_file = cmds.shadingNode(
                        'file', asTexture=True, name="{}_normal".format(material_name)
                    )
                    cmds.setAttr(
                        "{}.fileTextureName".format(normal_file), normal_path, type="string"
                    )
                    if not nfn_has_cs:
                        raw_cs = "Utility - Raw" if use_aces else "Raw"
                        cmds.setAttr(
                            "{}.colorSpace".format(normal_file), raw_cs, type="string"
                        )
                    if is_udim and use_udim:
                        cmds.setAttr("{}.uvTilingMode".format(normal_file), 3)
                    if create_place2d:
                        self.connect_place2d(place2d, normal_file)
                    normal_map = cmds.shadingNode(
                        'aiNormalMap', asUtility=True,
                        name="{}_aiNormalMap".format(material_name)
                    )
                    cmds.connectAttr(
                        "{}.outColor".format(normal_file),
                        "{}.input".format(normal_map),
                        force=True
                    )
                    cmds.connectAttr(
                        "{}.outValue".format(normal_map),
                        "{}.normalCamera".format(shader),
                        force=True
                    )
                elif create_bump:
                    bump2d = cmds.shadingNode(
                        'bump2d', asUtility=True, name="{}_bump2d".format(material_name)
                    )
                    cmds.setAttr("{}.bumpDepth".format(bump2d), bump_value)
                    cmds.connectAttr(
                        "{}.outAlpha".format(diffuse_file),
                        "{}.bumpValue".format(bump2d),
                        force=True
                    )
                    cmds.connectAttr(
                        "{}.outNormal".format(bump2d),
                        "{}.normalCamera".format(shader),
                        force=True
                    )

                created_materials.append(material_name)

            except Exception as e:
                cmds.warning("PXLmentor: Failed to create material for '{}' — {}".format(
                    texture_file, str(e)
                ))
                continue

        self._create_button.setEnabled(True)

        if created_materials:
            self.update_status("Created {} PBR material(s)".format(len(created_materials)))
            logger.info(
                "Arnold PBR Material Creator — created %d material(s):", len(created_materials)
            )
            for mat in created_materials:
                logger.info("  %s", mat)
        else:
            self.update_status("Failed to create any materials", error=True)

    # ------------------------------------------------------------------
    # place2dTexture Connections
    # ------------------------------------------------------------------

    def connect_place2d(self, place2d, file_node):
        """Connect all relevant attributes from a place2dTexture node to a file node."""
        connections = [
            ('coverage',        'coverage'),
            ('translateFrame',  'translateFrame'),
            ('rotateFrame',     'rotateFrame'),
            ('mirrorU',         'mirrorU'),
            ('mirrorV',         'mirrorV'),
            ('stagger',         'stagger'),
            ('wrapU',           'wrapU'),
            ('wrapV',           'wrapV'),
            ('repeatUV',        'repeatUV'),
            ('offset',          'offset'),
            ('rotateUV',        'rotateUV'),
            ('noiseUV',         'noiseUV'),
            ('vertexUvOne',     'vertexUvOne'),
            ('vertexUvTwo',     'vertexUvTwo'),
            ('vertexUvThree',   'vertexUvThree'),
            ('vertexCameraOne', 'vertexCameraOne'),
            ('outUV',           'uv'),
            ('outUvFilterSize', 'uvFilterSize'),
        ]
        for src, dst in connections:
            cmds.connectAttr(
                "{}.{}".format(place2d, src),
                "{}.{}".format(file_node, dst),
                force=True
            )


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

def show():
    ArnoldMaterialCreator()

show()
