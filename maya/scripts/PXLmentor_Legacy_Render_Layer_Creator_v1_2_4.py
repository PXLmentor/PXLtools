"""
Tool Name   : PXLmentor Legacy Render Layer Creator
Version     : 1.2.4
Stage       : Stable
Author      : PXLmentor AI Pipeline TD
Description : Production tool for creating legacy Maya render layers with advanced naming options.

Changelog:
    1.2.4 - PXLtools branding pass: in-tool header logo swapped
                 from PixelMentor_Logo_Long.png to PXLtools_logo.png.
                 Fallback text label changed to "PXLtools".
    1.2.3 - Full PySide6 QDialog migration — same dark theme as TurnTable Builder v1.0.5.
            Replaced cmds.window + all cmds widgets with QDialog + Qt equivalents.
            Singleton pattern added. CollapsibleSection used for Instructions.
            Non-collapsible section frames for Objects, Lights, Camera, Naming Options.
            QScrollArea wraps content. MAIN_QSS applied globally.
    1.2.2 - UI standardization and code quality pass. _C color tokens. UPPERCASE labels.
            boldLabelFont labels. status bar prefix pattern. spacing rhythm.
    1.2.1 - UI standardization. Unified header, icon, branding, instructions tab.
    1.2.0 - Previous stable release.
"""

import logging
import os

import maya.cmds as cmds
import maya.mel as mel

logger = logging.getLogger(__name__)


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
    DESTRUCT_BG     = "#4a3030"
    DESTRUCT_TEXT   = "#e07070"
    DESTRUCT_BDR    = "#6a3a3a"
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
QScrollArea { border: none; background: #464646; }
QScrollBar:vertical { background: #3a3a3a; width: 8px; }
QScrollBar::handle:vertical { background: #606060; border-radius: 4px; }
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
QPushButton#btnDestruct {
    background: #4a3030; color: #e07070; border: 1px solid #6a3a3a;
    min-height: 42px;
}
QPushButton#btnDestruct:hover { background: #5a3a3a; color: #f08080; }
QLabel#previewLabel {
    background: #404040; color: #888888;
    border: 1px solid #333333; border-radius: 2px;
    padding: 5px 10px; font-size: 11px; font-style: italic;
}
QLineEdit {
    background: #3a3a3a; color: #dcdcdc;
    border: 1px solid #2b2b2b; border-radius: 2px;
    padding: 4px 8px; font-size: 12px;
}
QListWidget {
    background: #3a3a3a; color: #dcdcdc;
    border: 1px solid #2b2b2b; border-radius: 2px;
    font-size: 12px;
}
QListWidget::item:selected { background: #E8820C; color: white; }
QCheckBox { color: #dcdcdc; font-size: 12px; spacing: 8px; }
QCheckBox::indicator {
    width: 16px; height: 16px;
    border-radius: 2px; background: #3a3a3a; border: 1px solid #2b2b2b;
}
QCheckBox::indicator:checked { background: #E8820C; border: 1px solid #c06000; }
QCheckBox:disabled { color: #686868; }
QCheckBox::indicator:disabled { background: #404040; border-color: #333333; }
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
            num_lbl.setStyleSheet("color: #aaaaaa; font-size: 12px; font-family: 'Courier New'; background: transparent;")
            hbox.addWidget(num_lbl)
        title_lbl = QtWidgets.QLabel(title.upper())
        title_lbl.setStyleSheet("color: #dcdcdc; font-weight: bold; font-size: 12px; letter-spacing: 1px; background: transparent;")
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
    def widget(self): return self._container
    @property
    def body_layout(self): return self._body_layout
    def add_widget(self, w): self._body_layout.addWidget(w)
    def add_layout(self, lay): self._body_layout.addLayout(lay)
    def add_spacing(self, n): self._body_layout.addSpacing(n)

    def set_collapsed(self, collapsed):
        self._collapsed = collapsed
        self._body.setVisible(not collapsed)
        self._arrow.setText("▸" if collapsed else "▾")
        if collapsed:
            self._header.setStyleSheet("QFrame { background: #3a3a3a; border: 1px solid #2b2b2b; border-radius: 3px; }")
            self._arrow.setStyleSheet("color: #888888; font-size: 16px; background: transparent;")
        else:
            self._header.setStyleSheet("QFrame { background: #393939; border: 1px solid #2b2b2b; border-bottom: none; border-radius: 3px 3px 0 0; }")
            self._arrow.setStyleSheet("color: #E8820C; font-size: 16px; background: transparent;")
        self._container.updateGeometry()


# ── Helper: non-collapsible section ───────────────────────────────────────────

def _make_section(title, parent_layout):
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
    lbl.setStyleSheet("color: #dcdcdc; font-weight: bold; font-size: 12px; letter-spacing: 1px; background: transparent;")
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

class RenderLayerCreator:
    """PXLmentor Legacy Render Layer Creator — v1.2.3."""

    VERSION            = "1.2.4"
    TOOL_NAME          = "Legacy Render Layer Creator"
    ICON_NAME          = "icon_render_layers.png"
    WINDOW_OBJECT_NAME = "PXLmentorLegacyRenderLayerCreator_v124"

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

    def create_ui(self):
        self._build_window()

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
        self._window.setMinimumHeight(600)
        self._window.setAttribute(QtCore.Qt.WA_DeleteOnClose, False)
        self._window.setStyleSheet(MAIN_QSS)

        root = QtWidgets.QVBoxLayout(self._window)
        root.setContentsMargins(0, 0, 0, 10)
        root.setSpacing(0)

        root.addWidget(self._build_header())

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        content = QtWidgets.QWidget()
        cl = QtWidgets.QVBoxLayout(content)
        cl.setContentsMargins(10, 8, 10, 8)
        cl.setSpacing(6)
        scroll.setWidget(content)
        root.addWidget(scroll)

        # Instructions (collapsible, collapsed by default)
        instr = CollapsibleSection("Instructions")
        instr.set_collapsed(True)
        for line in [
            "1. Select object(s)/group(s) in viewport → Add Selected (Objects section)",
            "2. Select light(s)/light group(s) in viewport → Add Selected (Lights section)",
            "3. Select a camera in viewport → Set Camera",
            "4. Configure naming options",
            "5. Click Create Render Layers",
        ]:
            lbl = QtWidgets.QLabel(line)
            lbl.setStyleSheet("color: #b0b0b0; font-size: 11px;")
            instr.add_widget(lbl)
        cl.addWidget(instr.widget)

        # Objects section
        obj_layout = _make_section("Objects / Groups to Render", cl)
        obj_lbl = QtWidgets.QLabel("Objects / Groups:")
        obj_lbl.setStyleSheet("color: #b0b0b0; font-size: 11px; font-weight: bold;")
        obj_layout.addWidget(obj_lbl)
        obj_row = QtWidgets.QHBoxLayout()
        self._objects_list_widget = QtWidgets.QListWidget()
        self._objects_list_widget.setFixedHeight(80)
        self._objects_list_widget.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        obj_row.addWidget(self._objects_list_widget)
        obj_btns = QtWidgets.QVBoxLayout()
        obj_btns.setSpacing(4)
        add_obj_btn = QtWidgets.QPushButton("Add Selected")
        add_obj_btn.setObjectName("btnPrimary")
        add_obj_btn.setMinimumHeight(30)
        add_obj_btn.clicked.connect(self.add_objects)
        obj_btns.addWidget(add_obj_btn)
        clr_obj_btn = QtWidgets.QPushButton("Clear")
        clr_obj_btn.setFixedHeight(30)
        clr_obj_btn.clicked.connect(self.clear_objects)
        obj_btns.addWidget(clr_obj_btn)
        obj_btns.addStretch()
        obj_row.addLayout(obj_btns)
        obj_layout.addLayout(obj_row)

        # Lights section
        lgt_layout = _make_section("Lights / Light Groups", cl)
        lgt_lbl = QtWidgets.QLabel("Lights / Light Groups:")
        lgt_lbl.setStyleSheet("color: #b0b0b0; font-size: 11px; font-weight: bold;")
        lgt_layout.addWidget(lgt_lbl)
        lgt_row = QtWidgets.QHBoxLayout()
        self._lights_list_widget = QtWidgets.QListWidget()
        self._lights_list_widget.setFixedHeight(60)
        self._lights_list_widget.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        lgt_row.addWidget(self._lights_list_widget)
        lgt_btns = QtWidgets.QVBoxLayout()
        lgt_btns.setSpacing(4)
        add_lgt_btn = QtWidgets.QPushButton("Add Selected")
        add_lgt_btn.setObjectName("btnPrimary")
        add_lgt_btn.setMinimumHeight(30)
        add_lgt_btn.clicked.connect(self.add_lights)
        lgt_btns.addWidget(add_lgt_btn)
        clr_lgt_btn = QtWidgets.QPushButton("Clear")
        clr_lgt_btn.setFixedHeight(30)
        clr_lgt_btn.clicked.connect(self.clear_lights)
        lgt_btns.addWidget(clr_lgt_btn)
        lgt_btns.addStretch()
        lgt_row.addLayout(lgt_btns)
        lgt_layout.addLayout(lgt_row)

        # Camera section
        cam_layout = _make_section("Camera", cl)
        cam_lbl = QtWidgets.QLabel("Render Camera:")
        cam_lbl.setStyleSheet("color: #b0b0b0; font-size: 11px; font-weight: bold;")
        cam_layout.addWidget(cam_lbl)
        cam_row = QtWidgets.QHBoxLayout()
        self._camera_field = QtWidgets.QLineEdit()
        self._camera_field.setReadOnly(True)
        cam_row.addWidget(self._camera_field)
        set_cam_btn = QtWidgets.QPushButton("Set Camera")
        set_cam_btn.setObjectName("btnPrimary")
        set_cam_btn.setFixedSize(100, 30)
        set_cam_btn.clicked.connect(self.set_camera)
        cam_row.addWidget(set_cam_btn)
        cam_layout.addLayout(cam_row)

        # Naming Options section
        naming_layout = _make_section("Naming Options", cl)

        prefix_suffix_row = QtWidgets.QHBoxLayout()
        prefix_suffix_row.setSpacing(10)
        left_col = QtWidgets.QVBoxLayout()
        left_col.setSpacing(4)
        pfx_lbl = QtWidgets.QLabel("Prefix:")
        pfx_lbl.setStyleSheet("color: #b0b0b0; font-size: 11px; font-weight: bold;")
        left_col.addWidget(pfx_lbl)
        self._prefix_field = QtWidgets.QLineEdit()
        self._prefix_field.textChanged.connect(self.update_naming_preview)
        left_col.addWidget(self._prefix_field)
        right_col = QtWidgets.QVBoxLayout()
        right_col.setSpacing(4)
        sfx_lbl = QtWidgets.QLabel("Suffix:")
        sfx_lbl.setStyleSheet("color: #b0b0b0; font-size: 11px; font-weight: bold;")
        right_col.addWidget(sfx_lbl)
        self._suffix_field = QtWidgets.QLineEdit()
        self._suffix_field.textChanged.connect(self.update_naming_preview)
        right_col.addWidget(self._suffix_field)
        prefix_suffix_row.addLayout(left_col)
        prefix_suffix_row.addLayout(right_col)
        naming_layout.addLayout(prefix_suffix_row)

        naming_layout.addSpacing(4)
        self._use_object_name_check = QtWidgets.QCheckBox("Use object name in layer name")
        self._use_object_name_check.setChecked(True)
        self._use_object_name_check.stateChanged.connect(self.update_naming_preview)
        naming_layout.addWidget(self._use_object_name_check)

        self._use_camera_name_check = QtWidgets.QCheckBox("Use camera name in layer name")
        self._use_camera_name_check.setChecked(False)
        self._use_camera_name_check.stateChanged.connect(self.update_naming_preview)
        naming_layout.addWidget(self._use_camera_name_check)

        div = QtWidgets.QFrame()
        div.setObjectName("divider")
        div.setFrameShape(QtWidgets.QFrame.HLine)
        naming_layout.addWidget(div)

        multi_lbl = QtWidgets.QLabel("Multi-Light Options:")
        multi_lbl.setStyleSheet("color: #b0b0b0; font-size: 11px; font-weight: bold;")
        naming_layout.addWidget(multi_lbl)

        self._layer_per_light_check = QtWidgets.QCheckBox("Create separate render layer per light")
        self._layer_per_light_check.setChecked(False)
        self._layer_per_light_check.stateChanged.connect(self.toggle_light_naming)
        naming_layout.addWidget(self._layer_per_light_check)

        light_pos_row = QtWidgets.QHBoxLayout()
        light_pos_row.setSpacing(20)
        lpos_lbl = QtWidgets.QLabel("Light name position:")
        lpos_lbl.setStyleSheet("color: #b0b0b0; font-size: 11px; font-weight: bold;")
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
        naming_layout.addLayout(light_pos_row)

        div2 = QtWidgets.QFrame()
        div2.setObjectName("divider")
        div2.setFrameShape(QtWidgets.QFrame.HLine)
        naming_layout.addWidget(div2)

        self._naming_preview = QtWidgets.QLabel("— Layer name preview: [object]")
        self._naming_preview.setObjectName("previewLabel")
        naming_layout.addWidget(self._naming_preview)

        # Action buttons
        action_row = QtWidgets.QHBoxLayout()
        action_row.setSpacing(8)
        create_btn = QtWidgets.QPushButton("Create Render Layers")
        create_btn.setObjectName("btnPrimary")
        create_btn.clicked.connect(self.create_render_layers)
        action_row.addWidget(create_btn)
        delete_btn = QtWidgets.QPushButton("Delete All Render Layers")
        delete_btn.setObjectName("btnDestruct")
        delete_btn.clicked.connect(self.delete_all_layers)
        action_row.addWidget(delete_btn)
        cl.addLayout(action_row)

        cl.addStretch()

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

    # ── Logic (unchanged from v1.2.2) ─────────────────────────────────────────

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
            cmds.warning("No objects in list — please add objects before creating layers")
            return
        if not self.lights_list:
            cmds.warning("No lights in list — please add lights before creating layers")
            return
        if not self.camera:
            cmds.warning("No camera set — please set a camera before creating layers")
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
            title='✓ Success',
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
            cmds.confirmDialog(title='— Info', message='No render layers to delete.', button=['OK'])
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
                    cmds.warning("Could not delete layer: {} — {}".format(layer, e))
            cmds.confirmDialog(
                title='✓ Success',
                message='Deleted {} render layer(s).'.format(deleted),
                button=['OK']
            )


# ── Entry point ───────────────────────────────────────────────────────────────

def run():
    creator = RenderLayerCreator()
    creator.create_ui()


run()
