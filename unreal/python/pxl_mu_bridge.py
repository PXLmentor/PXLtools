# Tool Name: PXLmentor MU Bridge (Unreal side)
# Version: 0.1.2-alpha
# Author: PXLmentor AI Pipeline TD
# Description: Unreal Engine 5.6 side of the Maya <-> Unreal asset bridge.
#              Entry point: registers TWO entry points on every UE startup so
#              the user always has at least one visible launcher:
#                1. Level Editor Toolbar icon (the preferred UX)
#                2. Main Menu -> Tools -> MU Bridge ... (guaranteed visible
#                   fallback if the toolbar registration silently fails)
#              Both entries open the MU Bridge window (PySide6/PySide2 QDialog
#              with header bar matching the PXLMENTOR_TOOL_STANDARD). The
#              window contains:
#                - IMPORT .PXLBRIDGE ... : ingest a Maya .pxlbridge.json
#                  manifest + sibling FBX + textures + MaterialInstances.
#                - CONFIGURE ACES (OCIO ASSET) : Phase 1 of the ACES setup;
#                  creates an OpenColorIOConfiguration asset from $OCIO
#                  with desired color spaces + display view populated.
# Changelog:
#   0.1.2-alpha - CP008: No behaviour change in this file. Bumped in lockstep
#                 with the refresh_asset_directories AttributeError sweep
#                 across aces_configurator (CP008), material_factory (CP003)
#                 and importer (CP002). UI buttons reordered in ui.py (CP003)
#                 so the one-time CONFIGURE ACES sits above per-asset IMPORT.
#   0.1.2-alpha - CP006: Adds EUW probe step. On every UE startup, checks
#                 whether the user has bootstrapped /Game/PXLbridge/W_MUBridge_Toolbar
#                 (Editor Utility Widget hosting the actual icon_mu_bridge.png).
#                 If absent: logs "EUW not bootstrapped" and points at
#                 BOOTSTRAP_EUW_TOOLBAR.md. If present: dumps the
#                 EditorUtilitySubsystem method surface so the next CP can
#                 register the EUW on the toolbar against confirmed APIs
#                 instead of guessing.
#   0.1.2-alpha - CP005: First CP004 run logged toolbar_ok=True on
#                 LevelEditor.LevelEditorToolBar.User but the user reported
#                 the icon was not visible. The .User section is a legacy
#                 4.x/early-5.x convention that often does not render in the
#                 visible 5.6.1 top toolbar (ends up in an overflow / hidden).
#                 Re-ordered _TOOLBAR_CANDIDATES so AssetsToolBar (the
#                 visible green-Add toolbar section) is tried first.
#                 Re-ordered _ICON_CANDIDATES to put icons that are reliably
#                 present in 5.6.1 first.
#   0.1.2-alpha - CP004: Toolbar registration writes a detailed status file
#                 J:\tmp\pxl_toolbar_LATEST.txt (every attempt + result) so
#                 the user does not have to hunt the Output Log to see why
#                 the icon may not appear. Added Tools > MU Bridge ... menu
#                 entry as a GUARANTEED visible fallback (Tools menu is
#                 always present). Toolbar icon attempts try 3 stock icon
#                 names + 4 toolbar paths defensively. The two entries are
#                 registered independently so partial failure does not
#                 cascade.
#   0.1.2-alpha - CP003: Phase 1 of the real ACES configurator.
#   0.1.1-alpha - CP002: Replaced 'PXL Tools' submenu with single toolbar
#                 icon. Click -> opens one Maya-style window.
#   0.1.0-alpha - CP001: Initial scaffold (PXL Tools sub-menu, two items).

from __future__ import annotations

import logging
import sys
import traceback
from pathlib import Path
from typing import List, Optional

import unreal  # noqa: F401  - injected by the Unreal Editor Python runtime


# ---------------------------------------------------------------------------
# Path setup so the pxl_mu_bridge_pkg package + shared schema resolve.
# ---------------------------------------------------------------------------

try:
    _SCRIPTS_DIR = Path(__file__).resolve().parent
except NameError:
    _SCRIPTS_DIR = Path.cwd()

if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from pxl_mu_bridge_pkg import ui  # noqa: E402

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Status file - so we don't have to hunt the Output Log to see what happened.
# ---------------------------------------------------------------------------

_STATUS_FILE = Path(r"J:\tmp\pxl_toolbar_LATEST.txt")
_LOG_LINES: List[str] = []


def _slog(msg: str = "") -> None:
    line = "[PXL TOOLBAR] {}".format(msg)
    _LOG_LINES.append(line)
    try: unreal.log(line)
    except Exception: pass
    try: print(line)
    except Exception: pass


def _serr(msg: str) -> None:
    line = "[PXL TOOLBAR] ERROR: {}".format(msg)
    _LOG_LINES.append(line)
    try: unreal.log_error(line)
    except Exception: pass
    try: print(line)
    except Exception: pass


def _write_status() -> None:
    try:
        _STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
        _STATUS_FILE.write_text("\n".join(_LOG_LINES), encoding="utf-8")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Action callback - opens the MU Bridge window. Module-level so ToolMenu
# Python commands (executed as fresh strings, no closures) can find it.
# ---------------------------------------------------------------------------

def _open_mu_bridge():
    try:
        ui.show_window()
    except Exception:
        msg = "[PXL MU Bridge] window failed to open:\n" + traceback.format_exc()
        try: unreal.log_error(msg)
        except Exception: pass
        try:
            unreal.EditorDialog.show_message(
                title="MU Bridge - Unexpected Error",
                message="The MU Bridge window failed to open. "
                        "See Output Log for the full traceback.",
                message_type=unreal.AppMsgType.OK,
                default_value=unreal.AppReturnType.OK,
            )
        except Exception:
            pass


# Backward-compat alias (any old menu strings that import the v0.1.1 name).
_on_toolbar_clicked = _open_mu_bridge


# ---------------------------------------------------------------------------
# Registration constants
# ---------------------------------------------------------------------------

_MENU_OWNER     = "PXLmentor.MUBridge"
_SECTION_NAME   = "PXLmentor"
_ENTRY_NAME     = "MUBridge"

# Candidate toolbar menu paths in UE 5.6.1. ORDER MATTERS - we register on
# the first one that resolves, so put visible-by-default sections first.
# AssetsToolBar is the green Add-Object toolbar at the top of the Level Editor
# - guaranteed visible. ModesToolBar is the editor-mode strip on the left.
# .User is a legacy 4.x/early-5.x section that often does not render in
# 5.6.1's top toolbar - moved to LAST as a fallback only.
_TOOLBAR_CANDIDATES = [
    "LevelEditor.LevelEditorToolBar.AssetsToolBar",
    "LevelEditor.LevelEditorToolBar.ModesToolBar",
    "LevelEditor.LevelEditorToolBar.SettingsToolbar",
    "LevelEditor.LevelEditorToolBar.PlayToolBar",
    "LevelEditor.LevelEditorToolBar",
    "LevelEditor.LevelEditorToolBar.User",
]

# Candidate stock icons. set_icon does not raise on a bad name (it just
# renders blank), so the only signal is visual. These are ordered from
# most-likely-to-exist-and-look-reasonable to least.
_ICON_CANDIDATES = [
    ("EditorStyle", "Icons.Plus"),
    ("EditorStyle", "Icons.Import"),
    ("EditorStyle", "ClassIcon.MaterialInstanceConstant"),
    ("EditorStyle", "ClassThumbnail.MaterialInstanceConstant"),
    ("CoreStyle",   "Icons.Plus"),
]

# Guaranteed-visible fallback: Tools menu entry
_TOOLS_MENU_PATH = "LevelEditor.MainMenu.Tools"

# Brand-icon path: the Editor Utility Widget the user creates per
# BOOTSTRAP_EUW_TOOLBAR.md. Until they do, the probe logs "not bootstrapped".
EUW_ASSET_PATH = "/Game/PXLbridge/W_MUBridge_Toolbar"


# ---------------------------------------------------------------------------
# Toolbar registration (best-effort - logs everything; menu fallback below
# is the guaranteed-visible path).
# ---------------------------------------------------------------------------

def _register_toolbar(menus: "unreal.ToolMenus") -> bool:
    _slog("--- Toolbar entry attempt ---")
    for path in _TOOLBAR_CANDIDATES:
        t = menus.find_menu(path)
        if t is None:
            _slog("  miss : {}".format(path))
            continue
        _slog("  found: {}".format(path))
        toolbar = t
        try:
            try:
                toolbar.remove_section(_SECTION_NAME)
            except Exception:
                pass
            toolbar.add_section(_SECTION_NAME, "PXLmentor")

            entry = unreal.ToolMenuEntry(
                name=_ENTRY_NAME,
                type=unreal.MultiBlockType.TOOL_BAR_BUTTON,
            )
            entry.set_label("MU Bridge")
            entry.set_tool_tip("PXLmentor MU Bridge - Maya <-> Unreal asset bridge")
            # Try icon candidates in order; first one whose set_icon does not
            # raise is good enough. set_icon does not validate the style name
            # at register time, so this is best-effort.
            for style_set, style_name in _ICON_CANDIDATES:
                try:
                    entry.set_icon(style_set, style_name)
                    _slog("    set_icon: {} / {}".format(style_set, style_name))
                    break
                except Exception as exc:
                    _slog("    set_icon FAIL: {} / {} ({})".format(style_set, style_name, exc))
            entry.set_string_command(
                type=unreal.ToolMenuStringCommandType.PYTHON,
                custom_type=unreal.Name(""),
                string="from pxl_mu_bridge import _open_mu_bridge; _open_mu_bridge()",
            )
            toolbar.add_menu_entry(_SECTION_NAME, entry)
            _slog("  registered TOOL_BAR_BUTTON on {} (section={})".format(path, _SECTION_NAME))
            return True
        except Exception:
            _serr("registration on {} crashed:\n{}".format(path, traceback.format_exc()))
    _serr("no toolbar candidate accepted the entry.")
    return False


# ---------------------------------------------------------------------------
# Menu fallback - ALWAYS register, regardless of toolbar result.
# Tools menu is part of the standard Main Menu and always visible.
# ---------------------------------------------------------------------------

def _register_tools_menu(menus: "unreal.ToolMenus") -> bool:
    _slog("--- Tools menu entry attempt (guaranteed visible) ---")
    tools_menu = menus.find_menu(_TOOLS_MENU_PATH)
    if tools_menu is None:
        # Some UE 5.6 builds use a different Tools menu path.
        for alt in [
            "MainFrame.MainMenu.Tools",
            "LevelEditor.MainMenu.Window",   # last-ditch: Window menu
        ]:
            tools_menu = menus.find_menu(alt)
            if tools_menu is not None:
                _slog("  fallback parent: {}".format(alt))
                break
    if tools_menu is None:
        _serr("no Tools / Window menu found - cannot register fallback entry.")
        return False

    try:
        try:
            tools_menu.remove_section(_SECTION_NAME)
        except Exception:
            pass
        tools_menu.add_section(_SECTION_NAME, "PXLmentor")

        entry = unreal.ToolMenuEntry(
            name="MUBridge.Open",
            type=unreal.MultiBlockType.MENU_ENTRY,
        )
        entry.set_label("MU Bridge ...")
        entry.set_tool_tip("Open the PXLmentor MU Bridge window.")
        entry.set_string_command(
            type=unreal.ToolMenuStringCommandType.PYTHON,
            custom_type=unreal.Name(""),
            string="from pxl_mu_bridge import _open_mu_bridge; _open_mu_bridge()",
        )
        tools_menu.add_menu_entry(_SECTION_NAME, entry)
        _slog("  registered MENU_ENTRY under Tools menu (section={})".format(_SECTION_NAME))
        return True
    except Exception:
        _serr("Tools menu registration crashed:\n" + traceback.format_exc())
        return False


# ---------------------------------------------------------------------------
# EUW probe - runs on every startup. Before bootstrap: logs "not bootstrapped"
# + points at the bootstrap doc. After bootstrap: dumps available registration
# APIs so the next CP can register against confirmed names instead of guessing.
# ---------------------------------------------------------------------------

def _probe_euw():
    _slog("")
    _slog("--- EUW (PXLmentor branded icon) probe ---")
    if not unreal.EditorAssetLibrary.does_asset_exist(EUW_ASSET_PATH):
        _slog("EUW not bootstrapped at {} - falling back to stock toolbar".format(
            EUW_ASSET_PATH))
        _slog("To get the PXLmentor branded icon on the toolbar, follow:")
        _slog("  J:\\ClaudeCode\\projects\\PXLtools\\unreal\\BOOTSTRAP_EUW_TOOLBAR.md")
        _slog("Estimated time: ~15 min of manual UE work, once per UE project.")
        return False

    _slog("found: {} - probing registration APIs".format(EUW_ASSET_PATH))

    # Try loading the EUW class
    try:
        euw_obj = unreal.load_object(None, EUW_ASSET_PATH)
        _slog("load_object result: {} (type {})".format(
            euw_obj, type(euw_obj).__name__))
    except Exception:
        _serr("load_object failed:\n" + traceback.format_exc())

    # Probe the EditorUtilitySubsystem - the most likely registration entry point
    eus_cls = getattr(unreal, "EditorUtilitySubsystem", None)
    if eus_cls is None:
        _serr("unreal.EditorUtilitySubsystem missing - cannot register EUW on toolbar.")
        return False

    _slog("EditorUtilitySubsystem methods (filtered for register/toolbar/widget):")
    for m in sorted(set(dir(eus_cls))):
        if m.startswith("_"):
            continue
        ml = m.lower()
        if any(t in ml for t in ("register", "toolbar", "widget", "tab", "spawn")):
            _slog("  fn  {}".format(m))

    try:
        eus = unreal.get_editor_subsystem(eus_cls)
        _slog("subsystem instance: {}".format(eus))
    except Exception:
        _serr("get_editor_subsystem failed:\n" + traceback.format_exc())

    # Also probe Blutility-related classes that may be relevant
    for cls_name in ("EditorUtilityWidget", "EditorUtilityWidgetBlueprint",
                     "EditorUtilityToolMenuEntry", "EditorUtilityToolMenuEntryScript"):
        c = getattr(unreal, cls_name, None)
        if c is not None:
            _slog("unreal.{} PRESENT".format(cls_name))
        else:
            _slog("unreal.{} missing".format(cls_name))

    _slog("EUW probe done. Send this log section back so the next CP can")
    _slog("register the EUW against confirmed APIs.")
    return True


# ---------------------------------------------------------------------------
# Top-level register
# ---------------------------------------------------------------------------

def _register_all():
    _slog("=" * 60)
    _slog("MU Bridge entry registration (CP006)")
    _slog("=" * 60)
    try:
        menus = unreal.ToolMenus.get()
    except Exception:
        _serr("unreal.ToolMenus.get() raised:\n" + traceback.format_exc())
        _write_status()
        return

    tb_ok = False
    menu_ok = False
    try:
        tb_ok = _register_toolbar(menus)
    except Exception:
        _serr("toolbar block crashed:\n" + traceback.format_exc())
    try:
        menu_ok = _register_tools_menu(menus)
    except Exception:
        _serr("menu block crashed:\n" + traceback.format_exc())

    try:
        _probe_euw()
    except Exception:
        _serr("EUW probe crashed:\n" + traceback.format_exc())

    try:
        menus.refresh_all_widgets()
        _slog("refresh_all_widgets() called.")
    except Exception:
        _serr("refresh_all_widgets() failed (non-fatal):\n" + traceback.format_exc())

    _slog("")
    _slog("RESULT: stock_toolbar_ok={} tools_menu_ok={}".format(tb_ok, menu_ok))
    _slog("Status file: {}".format(_STATUS_FILE))
    _write_status()


_register_all()
