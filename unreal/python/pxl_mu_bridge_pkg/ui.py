# Tool Name: PXLmentor MU Bridge - UI Dialog (Unreal)
# Version: 0.1.2-alpha
# Author: PXLmentor AI Pipeline TD
# Description: Single PySide6 QDialog that hosts the V0.1 actions: "Install
#              startup hook" (one-shot per UE project), "Configure ACES (OCIO
#              asset + viewport)" (one-time per project), and "Import .pxlbridge"
#              (per-asset, day-to-day). Mirrors PXLMENTOR_TOOL_STANDARD v1.2.0
#              (106px header bar with tool icon LEFT + center vbox with
#              PixelMentor logo + tool name + version, no right spacer).
#              Falls back to PySide2 when running on an older UE build.
# Changelog:
#   0.1.2-alpha - CP005: Three additions per the v0.1.2 blocker-closure plan
#                 (J:\ClaudeCode\.claude\plans\what-about-the-tool-proud-haven.md):
#                 (a) "0. INSTALL STARTUP HOOK" button - copies the staged
#                     init_unreal.py to the active project's Content/Python/.
#                     Backup-before-overwrite if a file is already there.
#                 (b) EUW first-run banner - if W_MUBridge_Toolbar is missing
#                     from the active project, shows a hint pointing at
#                     BOOTSTRAP_EUW_TOOLBAR.md at window open time.
#                 (c) Standard-reference reconciliation - v1.1.0 -> v1.2.0
#                     across the header docstring and inline comments to
#                     match unreal/CLAUDE.md and the design tokens reference.
#   0.1.2-alpha - CP004: Button order swapped per user feedback - CONFIGURE
#                 ACES is now Step 1 (one-time per project, must run before
#                 importing) and IMPORT .PXLBRIDGE is Step 2 (per-asset,
#                 day-to-day). Buttons numbered '1.' and '2.' so the order
#                 is unambiguous. Intro text + hint labels rewritten to
#                 reinforce the sequence.
#   0.1.2-alpha - CP003: ACES button relabelled CONFIGURE ACES (OCIO ASSET) and
#                 hint text rewritten to describe what the new configurator
#                 creates (an OCIOConfiguration asset from $OCIO, with two
#                 desired color spaces and one display view).
#   0.1.1-alpha - CP002: Initial scaffold. Replaces the v0.1.0 two-line menu
#                 with a single-window UI matching the Maya MU Bridge layout.

from __future__ import annotations

import logging
import os
import shutil
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional

# UE 5.6 ships PySide6; older UE ships PySide2. Try 6 first, fall back to 2.
try:
    from PySide6 import QtCore, QtGui, QtWidgets  # type: ignore
    _PYSIDE_VARIANT = "PySide6"
except ImportError:  # pragma: no cover
    from PySide2 import QtCore, QtGui, QtWidgets  # type: ignore
    _PYSIDE_VARIANT = "PySide2"

import unreal  # noqa: F401  - injected by the Unreal Editor Python runtime

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Design tokens (mirrors PXLMENTOR_TOOL_STANDARD v1.2.0 §3)
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


MAIN_QSS = """
QDialog, QWidget {
    background: #464646;
    color: #dcdcdc;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 12px;
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
QPushButton#btnSecondary {
    background: #2b3a4a; color: #c0d0e0; border: 1px solid #1a2530;
    font-size: 12px; letter-spacing: 1.0px; min-height: 38px;
}
QPushButton#btnSecondary:hover { background: #344b5e; color: #ffffff; }
QLabel#statusOk   { background: #2a402a; color: #7acc7a; border: 1px solid #3a5a3a; border-radius: 2px; padding: 5px 10px; font-size: 11px; }
QLabel#statusIdle { background: #404040; color: #888888; border: 1px solid #333333; border-radius: 2px; padding: 5px 10px; font-size: 11px; }
QLabel#statusErr  { background: #4a3030; color: #e07070; border: 1px solid #6a3a3a; border-radius: 2px; padding: 5px 10px; font-size: 11px; }
QLabel#ctrlLabel  { color: #aaaaaa; font-size: 11px; font-weight: bold; letter-spacing: 1.5px; }
QLabel#hint       { color: #888888; font-size: 11px; }
"""


# ---------------------------------------------------------------------------
# Icon path resolution
# ---------------------------------------------------------------------------

# Three candidate locations for icon_mu_bridge.png + PixelMentor_Logo_Long.png:
#   1. <user>/Documents/maya/2025/prefs/icons (Maya prefs deployment)
#   2. <PXLtools>/maya/scripts/icons (source-of-truth)
#   3. <PXLtools>/shared/utils/icons (future shared)
# We probe each until one resolves the file. This makes the UE side reuse the
# same icon assets the Maya shelf uses, without needing a UE-specific copy.

_ICON_PATH_CANDIDATES = [
    Path(os.environ.get("USERPROFILE", "")) / "Documents" / "maya" / "2025" / "prefs" / "icons",
    Path("J:/ClaudeCode/projects/PXLtools/maya/scripts/icons"),
]


def _resolve_icon(filename: str) -> Optional[Path]:
    for base in _ICON_PATH_CANDIDATES:
        p = base / filename
        if p.exists():
            return p
    return None


# ---------------------------------------------------------------------------
# Startup-hook install (CP005, B4) - copies the staged init_unreal.py into
# the active UE project's Content/Python/ folder so the toolbar/menu entries
# register on every project open.
# ---------------------------------------------------------------------------

# EUW asset path - duplicated from pxl_mu_bridge.py to avoid a circular import
# (the entry-point module imports this UI module).
_EUW_ASSET_PATH = "/Game/PXLbridge/W_MUBridge_Toolbar"


def _resolve_init_unreal_source() -> Path:
    """Source path of the staged init_unreal.py inside the PXLtools clone.

    This file lives at <PXLtools>/unreal/python/pxl_mu_bridge_pkg/ui.py;
    init_unreal.py lives one directory up.
    """
    return Path(__file__).resolve().parent.parent / "init_unreal.py"


def _resolve_init_unreal_target() -> Optional[Path]:
    """Target path inside the active UE project's Content/Python/."""
    try:
        content_dir_str = unreal.SystemLibrary.get_project_content_directory()
    except Exception:
        logger.exception("get_project_content_directory failed")
        return None
    if not content_dir_str:
        return None
    return Path(content_dir_str).resolve() / "Python" / "init_unreal.py"


def _is_euw_bootstrapped() -> bool:
    """Check whether the user has authored W_MUBridge_Toolbar in this project."""
    try:
        return bool(unreal.EditorAssetLibrary.does_asset_exist(_EUW_ASSET_PATH))
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Main dialog
# ---------------------------------------------------------------------------

TOOL_TITLE          = "MU Bridge"
TOOL_NAME_IN_HEADER = "Maya -> Unreal Bridge"
TOOL_VERSION        = "0.1.2-alpha"


class MUBridgeWindow(QtWidgets.QDialog):
    """Single PySide dialog hosting all V0.1 MU Bridge actions in Unreal."""

    _instance: Optional["MUBridgeWindow"] = None

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("PXLmentorMUBridge_UE_v012")
        self.setWindowTitle("{} v{}".format(TOOL_TITLE, TOOL_VERSION))
        self.setMinimumWidth(620)
        self.setStyleSheet(MAIN_QSS)
        self.setWindowFlags(
            self.windowFlags()
            | QtCore.Qt.WindowMinMaxButtonsHint
            | QtCore.Qt.Window  # standalone window, not a dialog modal
        )

        root_vbox = QtWidgets.QVBoxLayout(self)
        root_vbox.setContentsMargins(0, 0, 0, 0)
        root_vbox.setSpacing(0)
        root_vbox.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)

        root_vbox.addWidget(self._build_header())

        content = QtWidgets.QWidget()
        cv = QtWidgets.QVBoxLayout(content)
        cv.setContentsMargins(16, 14, 16, 14)
        cv.setSpacing(10)

        intro = QtWidgets.QLabel(
            "First-run: configure ACES so the project renders in ACEScg. "
            "Then import Maya MU Bridge assets into the configured project."
        )
        intro.setObjectName("hint")
        intro.setWordWrap(True)
        cv.addWidget(intro)

        # Optional first-run banner: EUW not bootstrapped yet -> branded
        # toolbar icon is not in place. The Tools-menu fallback is always
        # available, so this is informational only.
        if not _is_euw_bootstrapped():
            euw_banner = QtWidgets.QLabel(
                "Branded toolbar icon not bootstrapped yet (stock icon + Tools "
                "menu fallback are in use). Follow BOOTSTRAP_EUW_TOOLBAR.md "
                "(~15 min, one-time per UE project) to install the branded icon."
            )
            euw_banner.setObjectName("statusIdle")
            euw_banner.setWordWrap(True)
            cv.addWidget(euw_banner)

        # Step 0: Install startup hook into the active project (one-shot per project)
        # ----------------------------------------------------------------
        # Copies <PXLtools>/unreal/python/init_unreal.py to the active
        # project's Content/Python/init_unreal.py so the toolbar + menu entries
        # register on every project open. Backup-before-overwrite if a file
        # already exists at the target.
        self._btn_install_hook = QtWidgets.QPushButton("0.  INSTALL STARTUP HOOK INTO ACTIVE PROJECT")
        self._btn_install_hook.setObjectName("btnSecondary")
        self._btn_install_hook.clicked.connect(self._on_install_hook_clicked)
        cv.addWidget(self._btn_install_hook)

        install_note = QtWidgets.QLabel(
            "One-shot per UE project. Copies init_unreal.py to "
            "<Project>/Content/Python/ so MU Bridge registers on every project "
            "open. Skip if you have already done this manually or via a "
            "previous run."
        )
        install_note.setObjectName("hint")
        install_note.setWordWrap(True)
        cv.addWidget(install_note)

        # Step 1: Configure ACES (do this once per project, before importing)
        # ----------------------------------------------------------------
        # Creates an OpenColorIOConfiguration asset at /Game/OCIO/OCIO_ACES_1_2
        # from $OCIO with desired color spaces (ACES - ACEScg + Utility -
        # Linear - sRGB) and display view (ACES / sRGB), then activates the
        # viewport OCIO display configuration. Full step log -> J:\tmp\pxl_aces_LATEST.txt
        self._btn_aces = QtWidgets.QPushButton("1.  CONFIGURE ACES (OCIO ASSET + VIEWPORT)")
        self._btn_aces.setObjectName("btnSecondary")
        self._btn_aces.clicked.connect(self._on_configure_acescg_clicked)
        cv.addWidget(self._btn_aces)

        aces_note = QtWidgets.QLabel(
            "One-time per project. Creates /Game/OCIO/OCIO_ACES_1_2 from your "
            "$OCIO env var, populates desired color spaces + display view, and "
            "activates the viewport OCIO display configuration "
            "(View Mode -> OCIO Display)."
        )
        aces_note.setObjectName("hint")
        aces_note.setWordWrap(True)
        cv.addWidget(aces_note)

        # Step 2: Import Maya asset (per-asset, day-to-day action)
        # ----------------------------------------------------------------
        self._btn_import = QtWidgets.QPushButton("2.  IMPORT .PXLBRIDGE ...")
        self._btn_import.setObjectName("btnPrimary")
        self._btn_import.clicked.connect(self._on_import_clicked)
        cv.addWidget(self._btn_import)

        import_note = QtWidgets.QLabel(
            "Pick a .pxlbridge.json manifest from the Maya MU Bridge tool. "
            "Imports FBX + textures (color-space tagged per the manifest), "
            "auto-creates M_PXL_PBR_Master if missing, builds a "
            "MaterialInstanceConstant per material and binds to mesh slots. "
            "Step log -> J:\\tmp\\pxl_import_LATEST.txt"
        )
        import_note.setObjectName("hint")
        import_note.setWordWrap(True)
        cv.addWidget(import_note)

        # Future-section hint
        future_hint = QtWidgets.QLabel(
            "Coming next: Phase 2 viewport OCIO Display Configuration, "
            "Phase 3 WorkingColorSpace INI keys, Phase 4 Post Process Volume "
            "tonemapping. Reverse direction (Unreal -> Maya) and utility-node "
            "translation in V0.2."
        )
        future_hint.setObjectName("hint")
        future_hint.setWordWrap(True)
        cv.addWidget(future_hint)

        self._status_lbl = QtWidgets.QLabel("Ready.")
        self._status_lbl.setObjectName("statusIdle")
        self._status_lbl.setWordWrap(True)
        cv.addWidget(self._status_lbl)

        root_vbox.addWidget(content)

    # ----- header (PXLMENTOR_TOOL_STANDARD §5, v1.2.0 - NO right spacer) ----

    def _build_header(self) -> QtWidgets.QWidget:
        bg = tuple(int(v * 255) for v in _C.HEADER_BG)

        header = QtWidgets.QWidget()
        header.setFixedHeight(106)
        header.setStyleSheet("background-color: rgb({},{},{});".format(*bg))

        root = QtWidgets.QHBoxLayout(header)
        root.setContentsMargins(10, 5, 10, 5)
        root.setSpacing(0)

        # LEFT: tool icon 96x96 (same image used on the Maya shelf)
        left_label = QtWidgets.QLabel()
        left_label.setFixedSize(96, 96)
        left_label.setAlignment(QtCore.Qt.AlignCenter)
        tool_icon = _resolve_icon("icon_mu_bridge.png")
        if tool_icon:
            pixmap = QtGui.QPixmap(str(tool_icon)).scaled(
                96, 96,
                QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation,
            )
            left_label.setPixmap(pixmap)
        else:
            left_label.setText("[Icon]")
            left_label.setStyleSheet("background-color: rgb(51,51,51); color: white;")
        root.addWidget(left_label)

        # CENTER: PixelMentor logo + tool name + version, vertically stacked
        center = QtWidgets.QVBoxLayout()
        center.setContentsMargins(0, 0, 0, 0)
        center.setSpacing(2)
        center.setAlignment(QtCore.Qt.AlignVCenter)

        logo_label = QtWidgets.QLabel()
        logo_label.setFixedSize(262, 48)
        logo_label.setAlignment(QtCore.Qt.AlignCenter)
        logo = _resolve_icon("PixelMentor_Logo_Long.png")
        if logo:
            logo_pixmap = QtGui.QPixmap(str(logo)).scaled(
                262, 48,
                QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation,
            )
            logo_label.setPixmap(logo_pixmap)
        else:
            logo_label.setText("PXLmentor")
            logo_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")

        logo_row = QtWidgets.QHBoxLayout()
        logo_row.setContentsMargins(0, 0, 0, 0)
        logo_row.addStretch()
        logo_row.addWidget(logo_label)
        logo_row.addStretch()

        name_label = QtWidgets.QLabel(TOOL_NAME_IN_HEADER)
        name_label.setAlignment(QtCore.Qt.AlignCenter)
        name_label.setStyleSheet("color: white; font-weight: bold; font-size: 11px;")

        ver_label = QtWidgets.QLabel("v{}".format(TOOL_VERSION))
        ver_label.setAlignment(QtCore.Qt.AlignCenter)
        ver_label.setStyleSheet("color: #aaaaaa; font-size: 9px;")

        center.addLayout(logo_row)
        center.addWidget(name_label)
        center.addWidget(ver_label)
        root.addLayout(center, 1)

        # NO right spacer per PXLMENTOR_TOOL_STANDARD v1.2.0 - logo centers in
        # the visible content area (right of the tool icon).

        return header

    # ----- actions ---------------------------------------------------------

    def _on_install_hook_clicked(self) -> None:
        """CP005: copy the staged init_unreal.py into the active project."""
        self._set_status("Installing startup hook...", "idle")
        QtWidgets.QApplication.processEvents()

        source = _resolve_init_unreal_source()
        target = _resolve_init_unreal_target()

        if not source.is_file():
            self._set_status(
                "X Could not locate staged init_unreal.py at: {}".format(source),
                "err",
            )
            return
        if target is None:
            self._set_status(
                "X Could not resolve the active UE project's Content/Python/ path.",
                "err",
            )
            return

        try:
            target.parent.mkdir(parents=True, exist_ok=True)

            backup_msg = ""
            if target.exists():
                ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
                backup = target.with_suffix(".py.pxl_bak_{}".format(ts))
                shutil.copy2(str(target), str(backup))
                backup_msg = " (existing file backed up to {})".format(backup.name)

            shutil.copy2(str(source), str(target))
        except Exception as exc:
            logger.exception("Startup hook install failed")
            self._set_status(
                "X Install failed: {}".format(exc),
                "err",
            )
            return

        try:
            unreal.EditorDialog.show_message(
                title="MU Bridge - Startup hook installed",
                message=(
                    "init_unreal.py copied to:\n  {}\n\n"
                    "Restart Unreal Editor for this project so the bridge "
                    "registers on the toolbar + Tools menu automatically.\n\n"
                    "Source: {}{}"
                ).format(target, source, backup_msg),
                message_type=unreal.AppMsgType.OK,
                default_value=unreal.AppReturnType.OK,
            )
        except Exception:
            logger.warning("install dialog failed (non-fatal):\n%s", traceback.format_exc())

        self._set_status(
            "- Startup hook installed at {}. Restart UE to activate.{}".format(
                target, backup_msg,
            ),
            "ok",
        )

    def _on_import_clicked(self) -> None:
        from . import importer
        self._set_status("Picking manifest...", "idle")
        QtWidgets.QApplication.processEvents()
        try:
            ok = importer.import_via_picker()
        except Exception as exc:
            logger.exception("Import errored at top level")
            self._set_status("X Import error: {}".format(exc), "err")
            return
        if ok:
            self._set_status("- Import complete. See report dialog for details.", "ok")
        else:
            self._set_status("Import cancelled or failed - see report dialog.", "idle")

    def _on_configure_acescg_clicked(self) -> None:
        from . import aces_configurator
        self._set_status("Opening ACEScg configurator...", "idle")
        QtWidgets.QApplication.processEvents()
        try:
            aces_configurator.configure_acescg_interactive()
            self._set_status("- ACEScg configurator closed.", "ok")
        except Exception as exc:
            logger.exception("ACEScg configurator errored")
            self._set_status("X ACEScg error: {}".format(exc), "err")

    # ----- status helper (per PXLMENTOR_TOOL_STANDARD §11) -----------------

    def _set_status(self, msg: str, state: str = "idle") -> None:
        name = {"ok": "statusOk", "err": "statusErr", "idle": "statusIdle"}.get(
            state, "statusIdle",
        )
        self._status_lbl.setObjectName(name)
        self._status_lbl.setText(msg)
        self._status_lbl.setStyle(self._status_lbl.style())

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        type(self)._instance = None
        super().closeEvent(event)


def show_window() -> MUBridgeWindow:
    """Singleton entry: open the MU Bridge window or focus the existing one."""
    existing = MUBridgeWindow._instance
    if existing is not None:
        try:
            existing.raise_()
            existing.activateWindow()
            return existing
        except Exception:
            MUBridgeWindow._instance = None

    # Ensure a QApplication exists (UE has one but we guard anyway).
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])

    dlg = MUBridgeWindow()
    MUBridgeWindow._instance = dlg
    dlg.show()
    logger.info("MU Bridge UE window opened (%s).", _PYSIDE_VARIANT)
    return dlg
