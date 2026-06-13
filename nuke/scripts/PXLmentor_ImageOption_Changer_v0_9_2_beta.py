# ==============================================================================
# Tool Name:   PXLmentor Image Option Changer
# Version:     0.9.2-beta
# Author:      PXLmentor AI Pipeline TD
# Description: Batch-change the colorspace (input option) on selected Nuke
#              Read and/or Write nodes. Reads available colorspaces from the
#              active OCIO config; falls back to a curated ACES 1.2 list if
#              PyOpenColorIO is unavailable.
#
# Platform:    Nuke 15 (Python 3) | PySide2
#
# Usage:
#   From menu.py:
#       import PXLmentor_ImageOption_Changer_v0_9_1_beta as _ioc
#       pxl_menu.addCommand("Image Option Changer", _ioc.launch,
#                           icon="PXLmentor_ImageOption_Changer.png")
#   Direct (Script Editor):
#       import PXLmentor_ImageOption_Changer_v0_9_1_beta as _ioc; _ioc.launch()
#
# CHANGELOG:
#   0.9.1-beta - UI polish + code cleanup pass:
#                Replaced nuke.Panel with full PySide2 QDialog for consistent
#                branded UI (header, orange primary button, dark theme).
#                Applied PXLmentor brand color tokens as module-level constants.
#                Primary action button updated to brand orange #E8820C.
#                Reset/close buttons updated to neutral dark grey #525252.
#                Status area with dynamic background (ok/err/idle states).
#                Status messages prefixed with checkmark/cross/dash.
#                Section headers and field labels set to bold.
#                Removed all print() calls — nuke.warning() / logging only.
#                Removed unused nukescripts import.
#                try/except on all external operations verified throughout.
#                Colorspace read dynamically from OCIO config — unchanged (correct).
#   0.9.0-beta - Formalised into PXLmentor suite: added header, version, and
#                filename versioning. Fixed auto-run on import (removed bare
#                module-level run() call). Fixed bare except: -> except Exception.
#                Moved PyOpenColorIO import to module top with ImportError guard.
#                Added launch() entry point for menu.py compatibility.
#                Corrected filename to all-underscores (Python module importable).
# ==============================================================================

import nuke
import logging

try:
    import PyOpenColorIO as OCIO
    _OCIO_AVAILABLE = True
except ImportError:
    _OCIO_AVAILABLE = False

try:
    from PySide2 import QtWidgets, QtCore, QtGui
    PYSIDE_AVAILABLE = True
except ImportError:
    try:
        from PySide6 import QtWidgets, QtCore, QtGui
        PYSIDE_AVAILABLE = True
    except ImportError:
        PYSIDE_AVAILABLE = False

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("PXLmentor.ImageOptionChanger")

# ---------------------------------------------------------------------------
# Brand color tokens
# ---------------------------------------------------------------------------
BRAND_ORANGE = "#E8820C"
HEADER_BG    = "#0D1F24"
BTN_RESET_BG = "#525252"
STATUS_OK    = "#385838"
STATUS_ERR   = "#803838"
STATUS_IDLE  = "#383838"

VERSION = "0.9.2-beta"

# Curated ACES 1.2 fallback list — used when PyOpenColorIO is not installed
_ACES_FALLBACK_COLORSPACES = [
    "ACES - ACEScg",
    "ACES - ACES2065-1",
    "Input - ADX - ADX10",
    "Input - ADX - ADX16",
    "Input - ARRI - ARRI LogC3 (EI800)",
    "Input - ARRI - ARRI LogC4",
    "Input - Blackmagic - Blackmagic Film",
    "Input - Canon - Canon Log 2 Cinema Gamut",
    "Input - Canon - Canon Log 3 Cinema Gamut",
    "Input - DJI - D-Gamut D-Log",
    "Input - Panasonic - V-Gamut V-Log",
    "Input - RED - REDWideGamutRGB Log3G10",
    "Input - Sony - S-Gamut3 S-Log3",
    "Input - Sony - S-Gamut3.Cine S-Log3",
    "Output - Rec.709",
    "Output - sRGB",
    "Output - P3-D65",
    "Output - Rec.2020",
    "Utility - Linear - sRGB",
    "Utility - Linear - Rec.709",
    "Utility - Linear - Rec.2020",
    "Utility - Raw",
    "Utility - sRGB - Texture",
    "role_scene_linear",
    "default",
]


# ==============================================================================
# Core logic
# ==============================================================================

def _get_colorspaces() -> list:
    """Return a sorted list of colorspace names from the active OCIO config.
    Falls back to the curated ACES 1.2 list if PyOpenColorIO is unavailable.
    """
    if _OCIO_AVAILABLE:
        try:
            config = OCIO.GetCurrentConfig()
            names  = [cs.getName() for cs in config.getColorSpaces()]
            return sorted(names)
        except Exception as e:
            nuke.warning(
                f"PXLmentor Image Option Changer: OCIO query failed ({e}). "
                "Using fallback list.")
    return sorted(_ACES_FALLBACK_COLORSPACES)


def _apply_colorspace(target_colorspace: str,
                      read_only: bool = True,
                      include_write: bool = False) -> tuple:
    """Apply target_colorspace to the colorspace knob of selected nodes.

    Args:
        target_colorspace: The colorspace name to apply.
        read_only:         When True, only Read nodes are processed.
        include_write:     When True (and read_only is False),
                           Write nodes are also processed.

    Returns:
        (changed_nodes, skipped_nodes) — lists of node name strings.
    """
    selected_nodes = nuke.selectedNodes()
    changed_nodes  = []
    skipped_nodes  = []

    if not selected_nodes:
        return changed_nodes, skipped_nodes

    for node in selected_nodes:
        node_class = node.Class()

        if read_only and node_class != "Read":
            skipped_nodes.append(node.name())
            continue

        colorspace_knob = None
        if node_class == "Read":
            if "colorspace" in node.knobs():
                colorspace_knob = "colorspace"
        elif node_class == "Write" and include_write:
            if "colorspace" in node.knobs():
                colorspace_knob = "colorspace"
        elif not read_only:
            if "colorspace" in node.knobs():
                colorspace_knob = "colorspace"

        if colorspace_knob:
            try:
                node[colorspace_knob].setValue(target_colorspace)
                changed_nodes.append(node.name())
            except Exception as e:
                skipped_nodes.append(f"{node.name()} (error: {e})")
        else:
            skipped_nodes.append(f"{node.name()} (no colorspace knob)")

    return changed_nodes, skipped_nodes


# ==============================================================================
# UI helpers
# ==============================================================================

def _nuke_main_window():
    """Return Nuke's main window widget, or None."""
    app = QtWidgets.QApplication.instance() if PYSIDE_AVAILABLE else None
    if app:
        for w in app.topLevelWidgets():
            if w.objectName() == "Foundry::UI::DockMainWindow":
                return w
    return None


# ==============================================================================
# Main dialog
# ==============================================================================

class ImageOptionChangerDialog(QtWidgets.QDialog):
    """Branded PySide2 QDialog for the Image Option Changer."""

    BODY_BG = "#2b2b2b"

    _BTN = (
        f"QPushButton{{background:{BRAND_ORANGE};color:#fff;border:none;"
        "padding:6px 16px;font-size:11px;border-radius:3px;font-weight:bold;}}"
        "QPushButton:hover{background:#f09020;}"
        "QPushButton:pressed{background:#c06a00;}"
    )
    _BTN2 = (
        f"QPushButton{{background:{BTN_RESET_BG};color:#ccc;"
        "border:1px solid #686868;padding:5px 14px;font-size:11px;border-radius:3px;}}"
        "QPushButton:hover{background:#686868;}"
    )
    _COMBO = (
        "QComboBox{background:#1e1e1e;color:#d4d4d4;"
        "border:1px solid #444;padding:4px;font-size:11px;border-radius:2px;}"
        "QComboBox::drop-down{border:none;}"
        "QComboBox QAbstractItemView{background:#1e1e1e;color:#d4d4d4;}"
    )
    _LBL  = "QLabel{color:#cccccc;font-size:11px;font-weight:bold;background:transparent;}"
    _CHK  = ("QCheckBox{color:#cccccc;font-size:11px;background:transparent;}"
             "QCheckBox::indicator{width:14px;height:14px;}")
    _SECT = ("QLabel{color:#e0e0e0;font-size:12px;font-weight:bold;"
             f"border-bottom:1px solid {BRAND_ORANGE};padding-bottom:3px;"
             "background:transparent;}")

    def __init__(self, colorspaces: list, parent=None):
        super().__init__(parent or _nuke_main_window())
        self._colorspaces = colorspaces

        self.setWindowTitle(f"PXLmentor Image Option Changer  v{VERSION}")
        self.setMinimumSize(520, 380)
        self.resize(540, 420)
        self.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.WindowCloseButtonHint
        )
        self.setStyleSheet(f"QDialog{{background:{self.BODY_BG};}}")

        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())
        root.addLayout(self._build_body(), 1)
        root.addWidget(self._build_button_bar())

    # ── HEADER ────────────────────────────────────────────────────────────
    def _build_header(self):
        from os.path import join, exists, expanduser
        icon_dir = join(expanduser("~"), ".nuke", "PXLmentorToolbox", "icons")

        hdr = QtWidgets.QWidget()
        hdr.setFixedHeight(90)
        hdr.setStyleSheet(f"background:{HEADER_BG};")
        hl = QtWidgets.QHBoxLayout(hdr)
        hl.setContentsMargins(12, 8, 12, 8)
        hl.setSpacing(0)

        # Left — tool icon
        lbl_icon = QtWidgets.QLabel()
        lbl_icon.setFixedSize(72, 72)
        lbl_icon.setAlignment(QtCore.Qt.AlignCenter)
        lbl_icon.setStyleSheet(f"background:{HEADER_BG};")
        icon_file = join(icon_dir, "PXLmentor_ImageOption_Changer.png").replace("\\", "/")
        if exists(icon_file):
            lbl_icon.setPixmap(QtGui.QPixmap(icon_file).scaled(
                72, 72, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        else:
            lbl_icon.setText("[ icon ]")
            lbl_icon.setStyleSheet("color:#555;font-size:10px;border:1px solid #444;")
        hl.addWidget(lbl_icon)

        # Center — logo + name + version
        col = QtWidgets.QVBoxLayout()
        col.setAlignment(QtCore.Qt.AlignCenter)
        col.setSpacing(2)

        lbl_logo = QtWidgets.QLabel()
        lbl_logo.setAlignment(QtCore.Qt.AlignCenter)
        lbl_logo.setStyleSheet(f"background:{HEADER_BG};")
        logo_file = join(icon_dir, "PXLtools_logo.png").replace("\\", "/")
        if exists(logo_file):
            lbl_logo.setPixmap(QtGui.QPixmap(logo_file).scaled(
                200, 46, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        else:
            lbl_logo.setText("PXLtools")
            lbl_logo.setStyleSheet(
                "color:#fff;font-size:20px;font-weight:bold;letter-spacing:3px;")
        col.addWidget(lbl_logo)

        lbl_name = QtWidgets.QLabel("Image Option Changer")
        lbl_name.setAlignment(QtCore.Qt.AlignCenter)
        lbl_name.setStyleSheet(
            f"color:#e0e0e0;font-size:12px;font-weight:bold;background:{HEADER_BG};")
        col.addWidget(lbl_name)

        lbl_ver = QtWidgets.QLabel(f"v{VERSION}")
        lbl_ver.setAlignment(QtCore.Qt.AlignCenter)
        lbl_ver.setStyleSheet(f"color:#778899;font-size:10px;background:{HEADER_BG};")
        col.addWidget(lbl_ver)

        hl.addLayout(col, 1)

        # Right spacer
        sp = QtWidgets.QWidget()
        sp.setFixedSize(72, 72)
        sp.setStyleSheet(f"background:{HEADER_BG};")
        hl.addWidget(sp)

        return hdr

    # ── BODY ──────────────────────────────────────────────────────────────
    def _build_body(self):
        outer = QtWidgets.QVBoxLayout()
        outer.setContentsMargins(20, 16, 20, 16)
        outer.setSpacing(16)

        # Section: target colorspace
        sec_lbl = QtWidgets.QLabel("━━  TARGET COLORSPACE")
        sec_lbl.setStyleSheet(self._SECT)
        outer.addWidget(sec_lbl)

        row1 = QtWidgets.QHBoxLayout()
        row1.setSpacing(10)
        cs_lbl = QtWidgets.QLabel("Colorspace")
        cs_lbl.setStyleSheet(self._LBL)
        cs_lbl.setFixedWidth(130)
        self.combo_cs = QtWidgets.QComboBox()
        self.combo_cs.addItems(self._colorspaces)
        self.combo_cs.setStyleSheet(self._COMBO)
        row1.addWidget(cs_lbl)
        row1.addWidget(self.combo_cs, 1)
        outer.addLayout(row1)

        # Section: node filter
        sec_lbl2 = QtWidgets.QLabel("━━  NODE FILTER")
        sec_lbl2.setStyleSheet(self._SECT)
        outer.addWidget(sec_lbl2)

        self.chk_read = QtWidgets.QCheckBox("Read nodes")
        self.chk_read.setChecked(True)
        self.chk_read.setStyleSheet(self._CHK)
        self.chk_write = QtWidgets.QCheckBox("Write nodes")
        self.chk_write.setChecked(False)
        self.chk_write.setStyleSheet(self._CHK)
        outer.addWidget(self.chk_read)
        outer.addWidget(self.chk_write)

        # Status area
        self.lbl_status = QtWidgets.QLabel("— Select nodes in Nuke then click Apply.")
        self.lbl_status.setWordWrap(True)
        self._set_status("Select nodes in Nuke, then click Apply.", "idle")
        outer.addWidget(self.lbl_status)

        outer.addStretch()
        return outer

    # ── BUTTON BAR ────────────────────────────────────────────────────────
    def _build_button_bar(self):
        bar = QtWidgets.QWidget()
        bar.setStyleSheet("background:#222222; border-top:1px solid #3a3a3a;")
        bar.setFixedHeight(50)
        hl = QtWidgets.QHBoxLayout(bar)
        hl.setContentsMargins(16, 8, 16, 8)
        hl.setSpacing(8)
        hl.addStretch()

        self.btn_apply = QtWidgets.QPushButton("Apply")
        self.btn_apply.setFixedWidth(90)
        self.btn_apply.setStyleSheet(self._BTN)

        btn_close = QtWidgets.QPushButton("Close")
        btn_close.setFixedWidth(90)
        btn_close.setStyleSheet(self._BTN2)

        hl.addWidget(self.btn_apply)
        hl.addWidget(btn_close)

        self.btn_apply.clicked.connect(self._do_apply)
        btn_close.clicked.connect(self.reject)
        return bar

    # ── HELPERS ───────────────────────────────────────────────────────────
    def _set_status(self, text: str, state: str = "idle"):
        """Update status label text and background.

        Args:
            text:  Message to display.
            state: 'ok' | 'err' | 'idle'
        """
        prefix = {"ok": "✓ ", "err": "✕ ", "idle": "— "}.get(state, "— ")
        bg     = {"ok": STATUS_OK, "err": STATUS_ERR, "idle": STATUS_IDLE}.get(state, STATUS_IDLE)
        self.lbl_status.setText(prefix + text)
        self.lbl_status.setStyleSheet(
            f"QLabel{{color:#cccccc;font-size:10px;"
            f"background:{bg};border:1px solid #4a4a4a;padding:6px;"
            "border-radius:2px;word-wrap:true;}"
        )

    # ── SLOT ──────────────────────────────────────────────────────────────
    def _do_apply(self):
        target     = self.combo_cs.currentText()
        read_only  = self.chk_read.isChecked() and not self.chk_write.isChecked()
        inc_write  = self.chk_write.isChecked()

        selected = nuke.selectedNodes()
        if not selected:
            self._set_status("No nodes selected. Please select nodes in Nuke first.", "err")
            return

        changed, skipped = _apply_colorspace(target, read_only, inc_write)

        lines = [f"Target: {target}",
                 f"Changed: {len(changed)} node(s)"]
        if changed:
            lines += [f"  {n}" for n in changed[:10]]
            if len(changed) > 10:
                lines.append(f"  … and {len(changed) - 10} more")
        if skipped:
            lines.append(f"Skipped: {len(skipped)} node(s)")
            lines += [f"  {n}" for n in skipped[:10]]
            if len(skipped) > 10:
                lines.append(f"  … and {len(skipped) - 10} more")

        summary = "\n".join(lines)

        if changed:
            self._set_status(
                f"Changed {len(changed)} node(s) to '{target}'."
                + (f"  Skipped {len(skipped)}." if skipped else ""),
                "ok")
        else:
            self._set_status(
                f"No nodes changed. Skipped {len(skipped)} node(s).",
                "err")

        log.info("ImageOptionChanger: %s", summary)


# ==============================================================================
# Fallback (no PySide)
# ==============================================================================

class _FallbackChanger:
    """nuke.Panel fallback when PySide is unavailable."""

    def __init__(self):
        self.colorspaces = _get_colorspaces()

    def run(self):
        p = nuke.Panel("Batch Change Input Colorspace")
        p.addEnumerationPulldown("Target Colorspace", " ".join(self.colorspaces))
        p.addBooleanCheckBox("Read nodes only", True)
        p.addBooleanCheckBox("Include Write nodes", False)

        if not p.show():
            return

        target_cs     = p.value("Target Colorspace")
        read_only     = p.value("Read nodes only")
        include_write = p.value("Include Write nodes")

        selected = nuke.selectedNodes()
        if not selected:
            nuke.message("No nodes selected.")
            return

        changed, skipped = _apply_colorspace(target_cs, read_only, include_write)

        lines = [
            f"Colorspace Change Complete\n",
            f"Target: {target_cs}\n",
            f"Changed {len(changed)} node(s):",
        ]
        if changed:
            lines += [f"  {n}" for n in changed[:10]]
            if len(changed) > 10:
                lines.append(f"  ... and {len(changed) - 10} more")
        if skipped:
            lines.append(f"\nSkipped {len(skipped)} node(s):")
            lines += [f"  {n}" for n in skipped[:10]]
            if len(skipped) > 10:
                lines.append(f"  ... and {len(skipped) - 10} more")

        nuke.message("\n".join(lines))


# ==============================================================================
# Entry points
# ==============================================================================

def launch():
    """Primary entry point — called by menu.py."""
    colorspaces = _get_colorspaces()

    if PYSIDE_AVAILABLE:
        dlg = ImageOptionChangerDialog(colorspaces)
        dlg.exec_()
    else:
        nuke.warning(
            "PXLmentor Image Option Changer: PySide2/6 not available. "
            "Falling back to nuke.Panel.")
        _FallbackChanger().run()


# Keep run() as a legacy alias so any existing shelf buttons still work
run = launch


if __name__ == "__main__":
    launch()
