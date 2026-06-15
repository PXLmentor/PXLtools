"""
PBR Material v1.1.0-stable

Purpose:    Create Arnold aiStandardSurface PBR materials from Substance Painter texture sets.
Author:     Cristian Spagnuolo
Date:       2026-06-15
Stack:      Maya 2025
Python:     3.11
Depends:    PySide6, shiboken6, maya.cmds, mtoa, pxl_ui (shared kit)

Description:
    Create Arnold aiStandardSurface PBR materials from Substance Painter texture
    sets. Supports UDIM, ACES 1.2, custom texture identifiers, shared
    place2dTexture, and bump-from-diffuse fallback. Migrated to the shared
    PXLtools pxl_ui UI/UX standard (one shared stylesheet + AppHeader + shared
    collapsible sections); 100% of the tool logic is unchanged from v1.0.6 — only
    the UI chrome was migrated.

Changelog:
    1.1.0 - Migrated the UI to the shared PXLtools pxl_ui kit, EXACTLY mirroring
            the gold-standard PXLtools TurnTable Builder:
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
                QComboBox styling (there are no combos in this tool);
              - inline browse/action buttons and their paired fields share one
                height and are vertically centred;
              - auto-update wired on launch via pxl_update.check (deferred, once/day).
            File renamed PXLmentor_Arnold_PBR_Material_Creator_v1_0_6.py ->
            PXLtools_PBR_Material_v1_1_0.py; window title -> "PBR Material".
    1.0.6 - PXLtools branding pass: in-tool header logo swapped
                  from PixelMentor_Logo_Long.png to PXLtools_logo.png.
                  Fallback text label changed to "PXLtools".
    1.0.5 - Conform to PXLMENTOR_TOOL_STANDARD v1.1.0 - removed the 96x96
            right-spacer from _build_header so the PXLmentor logo centers in
            the visible content area (right of the tool icon) rather than on
            the dialog geometric midline. The previous symmetric layout looked
            off-balance because the spacer carried no visual weight.
    1.0.4 - Section reorder: Texture Location first, then Texture Identifiers.
            Renamed "Texture Folder" -> "Texture Location".
            Auto-detect identifier logic: scans folder on selection, matches known aliases
            (BaseColor/Diff/Diffuse/Albedo, Roughness/Rough/Rgh, Metalness/Metallic/Met/Mtl,
            Normal/Norm/Nrm) case-insensitively, populates fields automatically.
            Detection result shown in hint label; Re-detect button available.
            Window expansion fix: removed QScrollArea, content layout directly in dialog root.
            root_vbox.setSizeConstraint(SetFixedSize) - dialog auto-resizes on section toggle.
            QSS cascade fix: CollapsibleSection body uses setObjectName("collapsibleBody")
            instead of inline setStyleSheet (was breaking child-widget cascade).
            _make_section_frame body uses setObjectName("sectionFrame") - same fix.
            Full TurnTable v1.0.17 QSS parity: added #collapsibleBody, #sectionFrame,
            checkbox hover states, ctrlLabel, hint label styles.
            Button text visibility: setMinimumWidth(120) on all sidebar/browse buttons.
    1.0.3 - Full PySide6 QDialog migration - same dark theme as TurnTable Builder v1.0.5.
            Replaced cmds.window + all cmds widgets with QDialog + Qt equivalents.
            Singleton pattern added. CollapsibleSection used for Instructions.
            Non-collapsible section frames for Texture Identifiers, Texture Folder,
            Select Diffuse Textures, Options. QScrollArea wraps content.
            MAIN_QSS applied globally.
    1.0.2 - UI polish + code cleanup pass
    1.0.1 - UI standardization. Unified header, icon, branding, instructions tab.
    1.0.0 - Initial stable release

Usage:
    Paste this script into the Maya Script Editor (Python tab) and press Ctrl+Enter,
    or launch it from the PXLtools shelf.
"""

import logging
import os
import re
import sys

import maya.cmds as cmds

logger = logging.getLogger(__name__)

TOOL_NAME = "PBR Material"
VERSION = "1.1.0"
WINDOW_OBJECT_NAME = "PXLtoolsPBRMaterial_v110"
ICON_NAME = "icon_arnold_material.png"

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
# Global QSS — shared single-source stylesheet (icon tokens substituted at build)
# ---------------------------------------------------------------------------

MAIN_QSS = pxlt.tool_qss() if _PXLUI else ""


# ---------------------------------------------------------------------------
# Flat-text proxy style — kills the host's etched/drop-shadow disabled-text
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
# Section-frame helper — non-collapsible section using the shared look.
# Mirrors the shared CollapsibleSection header (3px accent bar + icon + title)
# but stays always-open. Body uses objectName "sectionFrame" so tool_qss styles
# it. Returns (container, body_layout, header_hbox) so callers can add a
# right-aligned action button into the header bar (e.g. Re-detect).
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
# Tool
# ---------------------------------------------------------------------------

class PBRMaterialCreator:
    """Arnold PBR Material Creator — production tool for Maya 2025 (pxl_ui)."""

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
        self.texture_folder = ""
        self.texture_files = []
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
                # Spin-box / combo arrows — real PNG chevrons (PySide6 does NOT
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
                # RING on hover — drawn to PNG so it stays perfectly round.
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
        from PySide6 import QtWidgets, QtCore, QtGui
        from maya import OpenMayaUI as omui
        import shiboken6

        main_ptr = omui.MQtUtil.mainWindow()
        maya_main = shiboken6.wrapInstance(int(main_ptr), QtWidgets.QWidget)

        dlg = QtWidgets.QDialog(maya_main)
        dlg.setObjectName(self.WINDOW_OBJECT_NAME)
        dlg.setWindowTitle("{} v{}".format(self.TOOL_NAME, self.version))
        dlg.setProperty("pxlPBRVersion", self.VERSION)
        dlg.setMinimumWidth(570)
        dlg.setStyleSheet(self._resolved_qss())
        dlg.setAttribute(QtCore.Qt.WA_DeleteOnClose, False)
        # Remove Qt's etched disabled-text emboss (matches the reference tool).
        try:
            dlg.setStyle(_FlatTextStyle(dlg.style()))
        except Exception:
            pass
        self._dialog = dlg

        # Root layout — SetFixedSize makes dialog auto-resize with content
        root_vbox = QtWidgets.QVBoxLayout(dlg)
        root_vbox.setContentsMargins(0, 0, 0, 0)
        root_vbox.setSpacing(0)
        root_vbox.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)

        # ── HEADER ──────────────────────────────────────────────────────
        self._build_header(root_vbox)

        # ── CONTENT (no QScrollArea — direct layout) ─────────────────────
        content_widget = QtWidgets.QWidget()
        content_vbox = QtWidgets.QVBoxLayout(content_widget)
        content_vbox.setContentsMargins(15, 10, 15, 10)
        content_vbox.setSpacing(10)

        # ── INSTRUCTIONS (collapsible, starts collapsed) ──────────────────
        instr_sec = pxlw.CollapsibleSection(
            "INSTRUCTIONS", icon_name="info", accent="#46C2D6",
            collapsed=True, parent=content_widget,
        )
        for line in [
            "1. Select the texture folder (Substance Painter export recommended)",
            "2. Identifiers are auto-detected — adjust if your naming differs",
            "3. Choose textures from the list",
            "4. Enable ACES 1.2 if your project uses ACES color management",
            "5. Click Create Materials",
        ]:
            lbl = QtWidgets.QLabel(line)
            lbl.setObjectName("hint")
            lbl.setWordWrap(True)
            instr_sec.add_widget(lbl)
        content_vbox.addWidget(instr_sec)

        # ── TEXTURE LOCATION ─────────────────────────────────────────────
        loc_frame, loc_layout, _loc_hbox = _make_section_frame(
            "TEXTURE LOCATION", icon_name="folder", accent="#E8820C",
            parent=content_widget,
        )

        lbl_folder = QtWidgets.QLabel("Texture Folder:")
        lbl_folder.setObjectName("ctrlLabel")
        loc_layout.addWidget(lbl_folder)

        folder_row = QtWidgets.QHBoxLayout()
        folder_row.setSpacing(6)
        self._folder_field = QtWidgets.QLineEdit()
        self._folder_field.setReadOnly(True)
        self._folder_field.setPlaceholderText("No folder selected...")
        self._folder_field.setMinimumHeight(32)
        btn_browse = QtWidgets.QPushButton("Select Folder")
        btn_browse.setObjectName("btnApply")
        btn_browse.setMinimumHeight(32)
        btn_browse.setMinimumWidth(120)
        btn_browse.clicked.connect(self.browse_folder)
        folder_row.addWidget(self._folder_field, 1)
        folder_row.addWidget(btn_browse)
        loc_layout.addLayout(folder_row)

        content_vbox.addWidget(loc_frame)

        # ── TEXTURE IDENTIFIERS ───────────────────────────────────────────
        ident_frame, ident_layout, ident_hbox = _make_section_frame(
            "TEXTURE IDENTIFIERS", icon_name="aces", accent="#9B7EDE",
            parent=content_widget,
        )

        # Re-detect button in the section header bar
        btn_redetect = QtWidgets.QPushButton("Re-detect")
        btn_redetect.setObjectName("btnAction")
        btn_redetect.setMinimumWidth(90)
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
        self._colorspace_message.setObjectName("statusOk")
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
            "SELECT DIFFUSE TEXTURES", icon_name="image", accent="#4F9DE0",
            parent=content_widget,
        )

        list_row = QtWidgets.QHBoxLayout()
        list_row.setSpacing(6)

        self._textures_list = QtWidgets.QListWidget()
        self._textures_list.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )
        self._textures_list.setMinimumHeight(150)
        self._textures_list.setStyleSheet(
            "QListWidget { background: #2c2c2c; color: #E6E6E6; "
            "border: 1px solid #262626; border-radius: 4px; font-size: 12px; }"
            "QListWidget::item:selected { background: #E8820C; color: #241606; }"
        )
        list_row.addWidget(self._textures_list)

        btn_col = QtWidgets.QVBoxLayout()
        btn_col.setSpacing(4)
        btn_select_all = QtWidgets.QPushButton("Select All")
        btn_select_all.setObjectName("btnApply")
        btn_select_all.setMinimumWidth(120)
        btn_select_all.clicked.connect(self.select_all_textures)
        btn_clear = QtWidgets.QPushButton("Clear Selection")
        btn_clear.setObjectName("btnApply")
        btn_clear.setMinimumWidth(120)
        btn_clear.clicked.connect(self.clear_selection)
        btn_refresh = QtWidgets.QPushButton("Refresh List")
        btn_refresh.setObjectName("btnApply")
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
            "OPTIONS", icon_name="utilities", accent="#34B3A0",
            parent=content_widget,
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
        self._bump_note_text.setObjectName("statusIdle")
        self._bump_note_text.setVisible(False)
        self._bump_note_text.setWordWrap(True)
        opts_layout.addWidget(self._bump_note_text)

        content_vbox.addWidget(opts_frame)

        # ── INFO / STATUS ─────────────────────────────────────────────────
        self._info_text = QtWidgets.QLabel(
            "— Materials will be named: AI_[base_name] (extracted from texture)"
        )
        self._info_text.setObjectName("statusIdle")
        self._info_text.setWordWrap(True)
        content_vbox.addWidget(self._info_text)

        # ── CREATE BUTTON ─────────────────────────────────────────────────
        self._create_button = QtWidgets.QPushButton("Create PBR Materials")
        self._create_button.setObjectName("btnPrimary")
        self._create_button.setMinimumHeight(42)
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
            self._detect_status_lbl.setText("Auto-detected — " + "  ·  ".join(labels))
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
            cmds.warning("PXLtools: Could not check for normal maps — {}".format(e))

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
                "✓ UDIM textures detected — UDIM workflow enabled by default."
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
            self._set_status("✕ " + message, state="err")
        else:
            self._set_status("✓ " + message, state="ok")

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
                cmds.warning("PXLtools: Failed to create material for '{}' — {}".format(
                    texture_file, str(e)
                ))
                continue

        self._create_button.setEnabled(True)

        if created_materials:
            self.update_status("Created {} PBR material(s)".format(len(created_materials)))
            logger.info(
                "PBR Material — created %d material(s):", len(created_materials)
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
# Run / entry point
# ---------------------------------------------------------------------------

def run():
    """Launch the PXLtools PBR Material creator."""
    PBRMaterialCreator()
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
