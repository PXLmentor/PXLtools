# PXLmentor Maya Tool Standard
**Version:** 1.2.0
**Date:** 2026-05-16
**Status:** Canonical — every existing tool conforms (or must be brought into conformance), every new tool MUST follow this spec from CP001.

**Changelog:**
- 1.2.0 (2026-05-16): Added §21 — Specialty Tool exception clause. A tool whose core interaction is fundamentally incompatible with the one-shot QDialog pattern (streaming chat, interactive canvas, etc.) may declare itself a Specialty Tool. PXLmentor AI Assistant is the first specialty tool. Specialty tools follow §1-3 and §15-20 but are exempt from §4-14.
- 1.1.0 (2026-05-16): §5 — drop the 96×96 invisible right spacer. Logo centers in the visible content area (right of the tool icon), not on the dialog geometric midline. The previous rule produced layouts that LOOKED off-balance even though they were mathematically symmetric. Existing tools that still carry the right-spacer pattern (Arnold v1.0.4, TurnTable v1.0.39-beta, GLB Manager v0.1.6-alpha, etc.) need a retrofit pass.
- 1.0.0 (2026-05-16): Initial codification reverse-engineered from the 9 production tools.

This document defines the single shared structure for PXLmentor Maya tools. It supersedes nothing in `J:\ClaudeCode\projects\PXLtools\CLAUDE.md` and `J:\ClaudeCode\projects\PXLtools\maya\CLAUDE.md` — it codifies what those documents already imply by extracting the pattern from the production tools themselves.

**Reverse-engineered from:** the 9 production tools at `J:\ClaudeCode\projects\PXLtools\maya\scripts\`. The reference implementation is `PXLmentor_Arnold_PBR_Material_Creator_v1_0_4.py` for QDialog/PySide6 patterns and `PXLmentor_TurnTable_Builder_v1_0_39_beta.py` for the most polished UI and QSS parity.

**Read order for any new tool:** (1) this doc, (2) `PXLtools/CLAUDE.md` for identity/design system, (3) `maya/CLAUDE.md` for Maya-specific gotchas, (4) Arnold PBR Creator as the reference implementation.

---

## 1. File Header (mandatory)

Every tool file starts with this comment block, in this exact order. No variation.

```python
# Tool Name: <Tool Name in Title Case With Spaces>
# Version: <X.Y.Z-stage>
# Author: PXLmentor AI Pipeline TD
# Description: <One-line summary that fits on one line.>
#              <Continuation indented to align with first line of Description.>
# Changelog:
#   X.Y.Z - Most recent change (one sentence per line).
#   X.Y.Z - Previous change.
```

Rules:
- `Tool Name` must match the title shown in the dialog window title (without the trailing ` v<version>`).
- `Version` in header MUST equal the version in the filename (`PXLmentor_Foo_v1_2_3_alpha.py` → `Version: 1.2.3-alpha`).
- Stage suffix in the version: `-alpha` (0.x.x ranges), `-beta` (0.x.x ranges), no suffix when 1.0.0+.
- Changelog is chronological, newest first. Every version bump adds an entry. Never edit a previous entry.
- Optional: `# Checkpoint: CP###` line after `# Author` when using checkpoint discipline.

## 2. Imports & module-level constants

In this order, always:

```python
import logging
import os
# ... other stdlib (re, json, struct, math, base64, csv, etc.)

import maya.cmds as cmds
import maya.mel as mel
# maya.api.OpenMaya as om2 only if you use the API

from PySide6 import QtCore, QtGui, QtWidgets
# maya.OpenMayaUI + shiboken6 inside the build method, not at module top

logger = logging.getLogger(__name__)

WINDOW_OBJECT_NAME = "PXLmentor<ToolNameCamelCase>_v<XYZ-no-dots>"
```

Rules:
- Logger always `logging.getLogger(__name__)`. NEVER configure handlers in tool code — Maya captures stdout/stderr.
- NEVER `print()` in production. Use `logger.info`, `logger.warning`, `logger.exception`.
- WINDOW_OBJECT_NAME: CamelCase tool name + `_v` + version with dots removed. Examples: `PXLmentorArnoldPBRMaterialCreator_v104`, `PXLmentorMUBridge_v011`.

## 3. Color tokens — the `_C` class (canonical 16 entries)

Every tool defines this class verbatim at module level. Tools that need extra colors EXTEND the class — they never substitute or omit the canonical entries.

```python
class _C:
    BG_DARK         = "#333333"
    BG_WINDOW       = "#464646"
    BG_SECTION_HDR  = "#393939"
    BG_SECTION_BOD  = "#4a4a4a"
    BG_INPUT        = "#3a3a3a"
    BG_HEADER       = "#0D1F24"     # Hex form of HEADER_BG tuple
    BORDER          = "#2b2b2b"
    ORANGE          = "#E8820C"
    TEXT_PRIMARY    = "#dcdcdc"
    TEXT_MUTED      = "#b0b0b0"
    STATUS_OK_BG    = "#2a402a"
    STATUS_OK_TEXT  = "#7acc7a"
    STATUS_ERR_BG   = "#4a3030"
    STATUS_ERR_TEXT = "#e07070"
    # 0-1 RGB tuples used by _build_header (scaled to 0-255 at runtime)
    HEADER_BG       = (0.051, 0.122, 0.141)
    BTN_PRIMARY     = (0.910, 0.510, 0.047)
```

When extending: add tool-specific entries AFTER these and prefix with the tool's domain (e.g. GLB Manager adds `BTN_ACTION_BG`, Animatic adds `DESTRUCT_BG`). Never rename or recolor a canonical entry.

## 4. MAIN_QSS — global stylesheet

Every tool defines a module-level string constant `MAIN_QSS` and applies it once via `dlg.setStyleSheet(MAIN_QSS)`. The stylesheet defines a fixed set of reserved object names that the rest of the code attaches to widgets via `setObjectName(...)`.

**Reserved object names (must be present in every tool's MAIN_QSS):**

| Object name | Applies to | Purpose |
|---|---|---|
| `#collapsibleBody` | QFrame | Body container under a CollapsibleSection header |
| `#sectionFrame` | QFrame | Body container under a non-collapsible section header |
| `#statusOk` | QLabel | Status label (success state) |
| `#statusIdle` | QLabel | Status label (neutral state) |
| `#statusErr` | QLabel | Status label (error state) |
| `#btnPrimary` | QPushButton | Primary orange CTA |
| `#btnSmall` | QPushButton | Small (24px) secondary button |
| `#ctrlLabel` | QLabel | Control labels above inputs ("Texture Folder:") |
| `#hint` | QLabel | Descriptive hint text inside a section |
| `#divider` | QFrame | 1px horizontal rule |

**Canonical QSS blocks (copy verbatim into MAIN_QSS):**

```css
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
```

**Important QSS discipline (§08b ports):**
- The checkbox `::indicator` block is mandatory — default Qt checkboxes are invisible on dark backgrounds.
- Never set styles on `#collapsibleBody` or `#sectionFrame` via `setStyleSheet()` inline — that breaks the QSS cascade to child widgets. Always rely on the `setObjectName(...)` route.

## 5. Header bar (`_build_header()`)

Fixed 106px header with two columns: tool icon (left, 96×96), and a centered text stack (PXLmentor logo + tool name + version) that occupies all remaining width. **No right spacer.** The logo centers in the [icon-right-edge .. dialog-right-edge] range, which is the *visible content area* — not the geometric dialog midline. This is what reads as "centered" to the eye, because the left icon is real visual weight and a matching right spacer would only feel balanced on paper, not in viewing.

Background is the `_C.HEADER_BG` tuple scaled to 0-255.

**Verbatim reference implementation (copy and substitute the highlighted lines):**

```python
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

    # LEFT: per-tool icon, 96x96 (same image as the shelf button)
    left_label = QtWidgets.QLabel()
    left_label.setFixedSize(96, 96)
    left_label.setAlignment(QtCore.Qt.AlignCenter)
    tool_icon = icon_path + "icon_<your_tool>.png"   # <-- per-tool icon filename
    if os.path.exists(tool_icon):
        pixmap = QtGui.QPixmap(tool_icon).scaled(
            96, 96, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation,
        )
        left_label.setPixmap(pixmap)
    else:
        left_label.setText("[Icon]")
        left_label.setStyleSheet("background-color: rgb(51,51,51); color: white;")
    root_hbox.addWidget(left_label)

    # CENTER: logo + tool name + version, vertically stacked. Stretches to fill
    # the remaining width. Logo + name + version are centered HORIZONTALLY in
    # this range via the inner addStretch/widget/addStretch pattern below.
    # NOTE: There is no right spacer. The logo will sit at the centre of the
    # visible content area (right of the icon), which reads as visually centred.
    center_vbox = QtWidgets.QVBoxLayout()
    center_vbox.setContentsMargins(0, 0, 0, 0)
    center_vbox.setSpacing(2)
    center_vbox.setAlignment(QtCore.Qt.AlignVCenter)

    logo_label = QtWidgets.QLabel()
    logo_label.setFixedSize(262, 48)
    logo_label.setAlignment(QtCore.Qt.AlignCenter)
    logo_path = icon_path + "PixelMentor_Logo_Long.png"
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

    name_label = QtWidgets.QLabel("<Your Tool Title Case>")   # <-- tool name
    name_label.setAlignment(QtCore.Qt.AlignCenter)
    name_label.setStyleSheet("color: white; font-weight: bold; font-size: 11px;")

    version_label = QtWidgets.QLabel("v{}".format(self.version))
    version_label.setAlignment(QtCore.Qt.AlignCenter)
    version_label.setStyleSheet("color: #aaaaaa; font-size: 9px;")

    center_vbox.addLayout(logo_hbox)
    center_vbox.addWidget(name_label)
    center_vbox.addWidget(version_label)
    root_hbox.addLayout(center_vbox, 1)

    # NO right spacer. The center_vbox stretches all the way to the right margin.

    return header_widget
```

The only two lines you change per tool are the `icon_<your_tool>.png` filename and the `name_label` text. Everything else is fixed.

**Historical note (2026-05-16):** v1.0.0 of this standard prescribed a 96×96 invisible spacer on the right side to make the layout geometrically symmetric. In practice the eye reads the geometric midline as off-balance because the spacer carries no visual weight. The current rule drops the spacer and centers the logo in the visible content area — what reads as "centered" to the user. Existing tools that still carry the v1.0.0 right-spacer pattern (Arnold v1.0.4, TurnTable v1.0.39-beta, etc.) are non-compliant and need a retrofit pass.

## 6. CollapsibleSection class (verbatim — every tool reuses this)

```python
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
```

## 7. Non-collapsible section helper (`_make_section_frame`)

Use when a section is permanent (no toggle). Returns `(container, body_layout, header_hbox)` so the caller can add right-aligned widgets to the header bar (e.g. a "Re-detect" button).

```python
def _make_section_frame(title, parent=None):
    """Return (container_widget, body_layout, header_hbox) for a non-collapsible section."""
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
    body.setObjectName("sectionFrame")
    body_layout = QtWidgets.QVBoxLayout(body)
    body_layout.setContentsMargins(10, 10, 10, 12)
    body_layout.setSpacing(6)
    outer.addWidget(body)

    return container, body_layout, hbox
```

## 8. Instructions panel (mandatory)

Every tool has a CollapsibleSection titled `"Instructions"`, placed as the FIRST section under the header, starting **collapsed**. Each step is one `QLabel` added to the body. Numbering convention: numerals + period prefix.

```python
instr_sec = CollapsibleSection("Instructions", parent=content_widget)
instr_sec.set_collapsed(True)
instr_sec.add_widget(QtWidgets.QLabel("1. First step the user takes."))
instr_sec.add_widget(QtWidgets.QLabel("2. Second step."))
# ... etc
content_vbox.addWidget(instr_sec.widget)
```

A tool with no Instructions section is non-compliant.

## 9. Singleton class pattern (`__new__` guard + Maya parenting)

```python
class MyTool:
    """One-line description, ends with 'production tool for Maya 2025.'"""

    VERSION = "X.Y.Z-stage"
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
        # ... tool-specific state ...
        self._dialog = None
        self._build_ui()

    def _build_ui(self):
        from PySide6 import QtWidgets, QtCore
        from maya import OpenMayaUI as omui
        import shiboken6

        main_ptr = omui.MQtUtil.mainWindow()
        maya_main = shiboken6.wrapInstance(int(main_ptr), QtWidgets.QWidget)

        dlg = QtWidgets.QDialog(maya_main)
        dlg.setObjectName(WINDOW_OBJECT_NAME)
        dlg.setWindowTitle("<Tool Title> v{}".format(self.version))
        dlg.setMinimumWidth(570)   # 550-720 range; pick what fits content
        dlg.setStyleSheet(MAIN_QSS)
        dlg.setAttribute(QtCore.Qt.WA_DeleteOnClose, False)
        self._dialog = dlg

        root_vbox = QtWidgets.QVBoxLayout(dlg)
        root_vbox.setContentsMargins(0, 0, 0, 0)
        root_vbox.setSpacing(0)
        root_vbox.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)  # auto-resize on collapse/expand

        root_vbox.addWidget(self._build_header())

        content_widget = QtWidgets.QWidget()
        content_vbox = QtWidgets.QVBoxLayout(content_widget)
        content_vbox.setContentsMargins(15, 10, 15, 10)
        content_vbox.setSpacing(10)

        # ... build sections, add to content_vbox ...

        root_vbox.addWidget(content_widget)
        dlg.show()
```

Rules:
- `_instance` is a **class attribute**, not instance.
- `__new__` returns the existing instance if its dialog is still visible (focus + raise instead of rebuild).
- `__init__` short-circuits when the dialog is already alive.
- The dialog is parented to Maya's main window via `MQtUtil.mainWindow() → shiboken6.wrapInstance`.
- `WA_DeleteOnClose, False` lets the dialog survive close events; we manually manage lifecycle through `_instance`.
- `root_vbox.setSizeConstraint(SetFixedSize)` is the ONLY sanctioned auto-resize mechanism. `resizeToFitChildren` and `setFixedSize` after the fact are both banned.

## 10. Window sizing rules

- **Width**: fixed via `setMinimumWidth(N)`. Typical N is 550–720 depending on content.
- **Height**: managed by `root_vbox.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)`. The dialog reflows automatically when CollapsibleSections expand/collapse.
- **`resizeToFitChildren` is BANNED** (unreliable in Maya 2025 — causes layout thrashing).
- **`base_height + instructions_height` math is BANNED for new tools** — use `setSizeConstraint(SetFixedSize)` instead. The math pattern exists in older tools (TurnTable, GLB Manager) and is grandfathered, but new tools must not introduce it.

## 11. Status feedback (`_set_status`)

Every tool has one QLabel named `self._status_lbl` placed at the bottom of the main content area, and one helper method:

```python
def _set_status(self, msg, state="idle"):
    name = {"ok": "statusOk", "err": "statusErr", "idle": "statusIdle"}.get(
        state, "statusIdle",
    )
    self._status_lbl.setObjectName(name)
    self._status_lbl.setText(msg)
    self._status_lbl.setStyle(self._status_lbl.style())   # re-polish QSS
```

Initial status label:

```python
self._status_lbl = QtWidgets.QLabel("Ready.")
self._status_lbl.setObjectName("statusIdle")
self._status_lbl.setWordWrap(True)
content_vbox.addWidget(self._status_lbl)
```

Usage convention (prefix the message with an ASCII glyph for quick scanning):
- Success: `self._set_status("- Exported 4 materials to /path/...", "ok")` (em dash or check)
- Error: `self._set_status("X No FBX plugin loaded.", "err")`
- Idle/info: `self._set_status("Working...", "idle")`

Every button click handler MUST end by calling `_set_status` (per §08b rule 4 — no silent success or silent failure).

## 12. Primary action button

```python
self._btn_primary = QtWidgets.QPushButton("EXPORT SELECTED")
self._btn_primary.setObjectName("btnPrimary")
self._btn_primary.clicked.connect(self._on_export_clicked)
content_vbox.addWidget(self._btn_primary)
```

- Label: ALL CAPS, verb-first.
- Object name: `btnPrimary` (orange/large styling driven by QSS).
- Placement: bottom of main content area, above the status label.
- Min height (set by QSS): 42px.

Secondary buttons use no object name (default styling) or `btnSmall` (24px for header-row affordances like "Re-detect").

## 13. Entry point — `show()` at module bottom

```python
# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

def show():
    MyTool()

show()
```

Rules:
- The entry function is named `show()`, not `run()` or `main()`.
- `show()` is called at the bottom of the module unconditionally. Never wrap in `if __name__ == "__main__":` — Maya never sets that.
- The function does nothing but instantiate the tool class (the singleton machinery handles focus-vs-rebuild).
- The shelf launcher in `PXLmentor_Setup_Shelf.py` triggers `show()` via the reload-or-import block — see §17.

## 14. Cross-DCC UI rules ported from PXLtools/CLAUDE.md §08b

Every tool MUST satisfy all five:

1. **Re-scan buttons always re-execute.** A "Re-detect" / "Refresh" button never reads a cache — always fresh scan.
2. **`_block_live` flag during init / prefs restore.** Set `self._block_live = True` before building UI, flip to `False` after all signals are wired. Every signal handler returns early when `_block_live`.
3. **Checkbox indicator QSS is mandatory.** Without the canonical `QCheckBox::indicator` block from §4, checkboxes are invisible on dark backgrounds.
4. **Status feedback on every action.** Every button handler ends with `_set_status(...)`.
5. **Path normalization on every boundary.** Any path crossing into Maya attributes, MEL, or file I/O calls `.replace("\\", "/")` first.

## 15. Error handling

```python
def _on_action_clicked(self):
    try:
        # ... do work ...
        self._set_status("- Done.", "ok")
    except ValueError as exc:
        self._set_status("X {}".format(exc), "err")
    except Exception:
        logger.exception("Unexpected failure in <action>")
        self._set_status("X Unexpected error - see Script Editor.", "err")
```

- Catch specific exception types when actionable; fall through to a general `except Exception` that uses `logger.exception`.
- Never bare `except:`. Never silently swallow.
- Every external operation (file I/O, plugin load, MEL, network) is wrapped.

## 16. Versioning & backup

- Filename pattern: `PXLmentor_<ToolName>_v<X>_<Y>_<Z>_<status>.py` (lowercase `_alpha` / `_beta`, no suffix on 1.0.0+).
- Header `# Version:` line MUST match the filename version exactly.
- Bump version on ANY change to the live file. No exceptions.
- Backup-before-modify (`§07` from PXLtools/CLAUDE.md): copy current file to `maya/scripts/_OLD/<filename>.py` BEFORE creating the new versioned file. Never edit in place.
- When deploying a new version, the previous versioned file is moved to `_OLD/` in BOTH the source dir and the live deploy dir (per global rule §4).

## 17. Shelf integration

Every tool gets an entry in `J:\ClaudeCode\projects\PXLtools\maya\scripts\PXLmentor_Setup_Shelf.py` `TOOLS` list:

```python
{
    "label":      "<Short Label>",          # 6-12 chars, fits the shelf button width
    "annotation": "<Tool Title> v<X.Y.Z>-<stage>  --  <one-line summary>",
    "icon":       "icon_<tool_name_lower_underscore>.png",
    "module":     "<exact filename without .py>",
},
```

When a tool version bumps, the `annotation` and `module` fields update; the `icon` filename stays the same.

## 18. Icon

- 96×96 PNG.
- Naming: `icon_<tool_name_lower_with_underscores>.png`.
- Generated procedurally by `J:\ClaudeCode\projects\PXLtools\shared\utils\generate_icons.py` (see existing per-tool blocks for the design language: rounded dark panel via `base()`, optional letter/glyph/text, optional subtext label in gray).
- The same icon file feeds three places: shelf button, dialog header bar (left 96×96 slot), and any iconography inside the tool.
- Deploys to `C:\Users\Evil Knight\Documents\maya\2025\prefs\icons\` automatically when the generator runs.

## 19. Code structure / modularity

- Default: monolithic single .py file under `maya/scripts/`.
- Split into a sibling package (`maya/scripts/<tool>/...`) only when ONE of:
  - The tool exceeds ~2000 lines.
  - There is non-UI logic that must be importable from another DCC (e.g. MU Bridge's shared schema with the Unreal side).
- When split into a package, the entry .py at `maya/scripts/PXLmentor_<Tool>_v<...>.py` is a thin UI module that imports from the package. The package directory deploys alongside the entry file.

## 20. Documentation footprint

For every new tool:
- Update the tool catalog table in `maya/CLAUDE.md`.
- Add a detailed catalog entry in `maya/CLAUDE.md` describing purpose, files, status, config.
- Update the `PXLmentor_Setup_Shelf.py` TOOLS list (and bump shelf version + changelog).
- If the icon is new, extend `generate_icons.py` and bump its `print("\nAll N icons complete.")` count.
- If the tool introduces a new pattern this standard does not cover, update THIS standard first, get sign-off, then implement.

---

## Compliance audit checklist (run for every tool, new or existing)

- [ ] File header matches §1 exactly.
- [ ] Imports + logger match §2.
- [ ] `WINDOW_OBJECT_NAME` follows §2 convention.
- [ ] `_C` class contains all 16 canonical entries from §3.
- [ ] `MAIN_QSS` contains every block from §4, in order, with all reserved object names.
- [ ] `_build_header()` returns a 106px widget with tool-icon-LEFT / center-VBOX / spacer-RIGHT layout per §5.
- [ ] `CollapsibleSection` class is verbatim §6.
- [ ] `_make_section_frame` helper is verbatim §7 (only required if the tool has non-collapsible sections).
- [ ] First section under the header is an Instructions CollapsibleSection, starts collapsed (§8).
- [ ] Singleton class with `__new__` guard + Maya parenting per §9.
- [ ] Window sizing uses `setSizeConstraint(SetFixedSize)` per §10.
- [ ] `self._status_lbl` + `_set_status()` per §11.
- [ ] Primary action button uses `setObjectName("btnPrimary")` and ALL-CAPS verb label per §12.
- [ ] `show()` function + module-level call per §13.
- [ ] All five §14 rules satisfied.
- [ ] Try/except discipline per §15.
- [ ] Filename + header version + changelog updated per §16.
- [ ] Shelf entry added per §17.
- [ ] Icon present per §18.
- [ ] `maya/CLAUDE.md` updated per §20.

A tool that fails any of these checkboxes is non-compliant and must be fixed before release.

---

## 21. Specialty Tool exception clause (added in standard v1.2.0)

Some PXLmentor tools have a core interaction model that is fundamentally incompatible with the one-shot QDialog pattern this standard prescribes:
- Streaming chat / agent interfaces with long-lived conversation state (e.g. AI Assistant, with its message history, tool-use callbacks, and live token streaming).
- Interactive canvas tools that take over a `QGraphicsView` for direct user manipulation (e.g. Camera Matchmaker drawing vanishing-point lines).
- Tools that must dock into a Maya layout (workspace panel, not a floating dialog).

For these cases a tool may declare itself a **Specialty Tool** at the top of the file:

```python
# Compliance: SPECIALTY (exempt from PXLMENTOR_TOOL_STANDARD §4-§14)
# Rationale: <one-line explanation of why the dialog pattern doesn't fit>
```

Specialty tools MUST still follow:
- §1 File header
- §2 Imports + logger
- §3 WINDOW_OBJECT_NAME convention
- §15 Error handling
- §16 Versioning + backup-before-modify
- §17 Shelf entry
- §18 Icon
- §19 Code structure
- §20 Documentation

Specialty tools are EXEMPT from:
- §4 `_C` canonical 16 entries (may extend or substitute as the interaction model requires)
- §5 MAIN_QSS reserved object names (may use entirely different stylesheet vocabulary)
- §6 `_build_header` 106px no-right-spacer layout (the dialog header pattern may not fit)
- §7 `CollapsibleSection` class (specialty tool may not have collapsible sections at all)
- §8 `_make_section_frame` helper
- §9 Instructions panel as first content section
- §10 `__new__` singleton + Maya parenting (chat tools often need different lifecycle)
- §11 `SetFixedSize` layout (specialty tools may need resizable layouts)
- §12 `_set_status` standard signature
- §13 Primary CTA via `btnPrimary` (specialty tools may have no primary action)
- §14 `show()` entry point convention (specialty tools may use different entry conventions if documented)

**Current specialty tools:**
- `PXLmentor_AI_Assistant_v2_1_0_alpha.py` — Anthropic streaming chat panel.

When auditing or extending the family, treat Specialty Tools as a separate category. They are NOT non-compliant by default — they are compliant against a narrower contract. If a new specialty tool is added, update this section's list.
