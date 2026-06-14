# ==============================================================================
# Tool Name:   PXLtools — Nuke menu.py
# Version:     3.4.0
# Changelog (3.3.0): removed the "↻ Update PXLtools" command (updates come from the
#   GitHub release flow); the menu now SKIPS tools whose versioned file isn't present
#   so the public TurnTable-only package shows only the TurnTable Comp Setup command.
# Author:      PXLsuite / BlackMamba3D
# Description: Registers PXLtools tools into Nuke's toolbar, with an
#              "Update PXLtools" command that re-scans the scripts folder for the
#              newest version of each tool and rebuilds the menu — no Nuke restart.
#
# Location:    C:\Users\Evil Knight\.nuke\menu.py
#
# IMPORTANT — Icon resolution:
#   Nuke resolves icons by FILENAME ONLY via nuke.pluginPath().
#   The icons directory must be registered in init.py:
#     toolbox = os.path.join(os.path.expanduser("~"), ".nuke", "PXLtools")
#     nuke.pluginAddPath(os.path.join(toolbox, "scripts"))
#     nuke.pluginAddPath(os.path.join(toolbox, "icons"))
#   Do NOT pass full paths — Nuke will silently ignore them.
#
# CHANGELOG:
#   3.4.0  - Auto-update on launch: checks GitHub for a newer STABLE release
#            (once/day) via pxl_ui.pxl_update and offers a one-click update.
#   3.2.0  - Auto-update: new "↻ Update PXLtools" menu command (icon_update.png)
#            re-scans the scripts folder, resolves the NEWEST version of each tool
#            by filename and rebuilds the menu + reloads modules. Tool table now
#            uses version-less stems resolved to the latest file on every build.
#   3.1.0  - All Nuke tools patch-bumped for the PXLtools in-tool logo swap.
#   3.0.1  - Parent icon swap -> PXLtools_favicon.png (icon-only P+T mark).
#   3.0.0  - Rebrand pass: parent menu "PXLmentor" -> "PXLtools".
#   (earlier history trimmed — see _OLD backups.)
# ==============================================================================

import os
import sys
import glob
import importlib

import nuke

MENU_NAME    = "PXLtools"
MENU_ICON    = "PXLtools_favicon.png"
UPDATE_ICON  = "icon_update.png"
_SCRIPTS_DIR = os.path.join(os.path.expanduser("~"), ".nuke", "PXLtools", "scripts")

# `stem` is version-less. The newest matching file is resolved on every build,
# so a version bump appears on "Update" with zero edits here.
TOOLS = [
    {"label": "Contact Sheet Generator", "stem": "PXLmentor_ContactSheet_Generator",
     "icon": "PXLmentor_ContactSheet_Generator.png"},
    {"label": "Image Option Changer",    "stem": "PXLmentor_ImageOption_Changer",
     "icon": "PXLmentor_ImageOption_Changer.png"},
    {"label": "TurnTable Comp Setup",    "stem": "PXLtools_TurnTable_Comp_Setup",
     "icon": "icon_turntable_builder.png"},
]


# ---------------------------------------------------------------------------
# Version-aware discovery
# ---------------------------------------------------------------------------

def _version_key(filepath, stem):
    base = os.path.splitext(os.path.basename(filepath))[0]
    if not base.startswith(stem + "_v"):
        return None
    nums, stage = [], 3
    for part in base[len(stem) + 2:].split("_"):
        if part.isdigit():
            nums.append(int(part))
        else:
            stage = {"alpha": 0, "beta": 1, "rc": 2}.get(part.lower(), stage)
    nums = (nums + [0, 0, 0])[:3]
    return (nums[0], nums[1], nums[2], stage)


def _latest_module(stem):
    """Newest '<stem>_v*.py' module name in the scripts folder, or None."""
    best, best_key = None, None
    for f in glob.glob(os.path.join(_SCRIPTS_DIR, stem + "_v*.py")):
        k = _version_key(f, stem)
        if k and (best_key is None or k > best_key):
            best_key, best = k, os.path.splitext(os.path.basename(f))[0]
    return best


def _import_latest(stem):
    """Import (or reload) the newest version of the tool; return the module."""
    name = _latest_module(stem)
    if not name:
        raise ImportError("no versioned file for stem '{}' in {}".format(stem, _SCRIPTS_DIR))
    if name in sys.modules:
        return importlib.reload(sys.modules[name])
    return importlib.import_module(name)


# ---------------------------------------------------------------------------
# Menu build / update
# ---------------------------------------------------------------------------

def build_menu():
    """(Re)build the PXLtools toolbar menu from the newest tool versions on disk."""
    toolbar = nuke.toolbar("Nodes")
    try:
        toolbar.removeItem(MENU_NAME)        # clean rebuild (idempotent)
    except Exception:
        pass

    menu = toolbar.addMenu(MENU_NAME, icon=MENU_ICON)

    # One command per INSTALLED tool. Tools whose file isn't present are skipped
    # silently (so the public TurnTable-only package shows just that command).
    # No Update command — updates come from the GitHub release flow.
    for tool in TOOLS:
        if not _latest_module(tool["stem"]):
            continue
        try:
            mod = _import_latest(tool["stem"])
            menu.addCommand(tool["label"], mod.launch, icon=tool["icon"])
        except Exception as e:
            nuke.warning("PXLtools: could not load {} — {}".format(tool["label"], e))


build_menu()

# Auto-update on launch: check GitHub for a newer STABLE release (throttled once/day),
# offer a one-click update. Safe — never breaks menu loading.
try:
    from pxl_ui import pxl_update
    pxl_update.check(channel="stable", dcc="nuke")
except Exception:
    pass
