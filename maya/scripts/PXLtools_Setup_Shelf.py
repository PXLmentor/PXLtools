# Tool Name: PXLtools Setup Shelf
# Version: 1.14.0
# Author: PXLsuite / BlackMamba3D
# Description: Creates the PXLtools Maya shelf — one button per INSTALLED tool
#              (tools whose file is absent are skipped, so a TurnTable-only package
#              shows just that button). No Update button: updates come from the
#              GitHub release flow (re-run the installer).
# Changelog:
#   1.14.0 - Removed the in-shelf "Update" button (updates now come from the GitHub
#             release flow). Shelf now SKIPS tools whose versioned file isn't present
#             so the public TurnTable-only package shows only the TurnTable button.
# Changelog (prior):
#   1.13.0 - Auto-update: new "Update" shelf button (icon_update.png) re-scans the
#             scripts folder, resolves the NEWEST version of each tool by filename
#             (stem_vMAJOR_MINOR_PATCH[_stage]) and rebuilds the shelf + reloads
#             modules. Tool entries now carry a version-less `module` stem that is
#             resolved to the latest file on every build, so future version bumps
#             appear on click with zero shelf edits. TurnTable -> PXLtools_TurnTable_Builder.
#   1.12.0 - PXLtools branding pass: every tool patch-bumped for the in-tool
#             logo swap (PixelMentor_Logo_Long -> PXLtools_logo).
#   1.11.0 - Rebrand pass: SHELF_NAME PXLmentor -> PXLtools.
#   1.10.0 - Phase 1 retrofit to STANDARD v1.1.0 (no-right-spacer header).
#   1.9.0 - MU Bridge -> v0.1.2-alpha (header retrofit to STANDARD v1.1.0).
#   1.8.0 - MU Bridge -> v0.1.1-alpha (PXLMENTOR_TOOL_STANDARD compliance pass).
#   1.7.0 - Added MU Bridge button (Maya -> Unreal asset bridge, V0.1 export-only).
#   1.6.0 - Camera Matchmaker -> v0.2.0-alpha (renamed file, drag-drop fix).
#   1.5.0 - Batch Renamer -> v1.0.6, OBJ Exporter -> v1.0.4 (PySide6 AlignCenter fix).
#   1.4.0 - Updated all tool versions to latest.
#   1.3.0 - Added Camera Matchmaker button, positioned before GLB Manager.
#   1.2.0 - Updated mAIa button to v2.1.0-alpha.
#   1.1.0 - Updated mAIa button to v2.0.0 (Agent Mode + MayaMCP integration).
#   1.0.0 - Initial release.

import os
import re
import sys
import glob

import maya.cmds as cmds
import maya.mel as mel
import maya.utils

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

SHELF_NAME   = "PXLtools"
SHELF_MODULE = "PXLtools_Setup_Shelf"
UPDATE_ICON  = "icon_update.png"

# `module` here is a STEM (no version). The newest matching file in the scripts
# folder is resolved on every build, so a version bump needs no edit here.
TOOLS = [
    {"label": "mAIa",          "icon": "icon_claude_for_maya.png",  "module": "PXLmentor_AI_Assistant",
     "annotation": "Claude for Maya (mAIa)  --  Agent Mode + Quick Prompts"},
    {"label": "Animatic",      "icon": "icon_animatic_builder.png", "module": "PXLmentor_Animatic_Builder",
     "annotation": "Animatic Builder"},
    {"label": "CamMatch",      "icon": "icon_camera_matchmaker.png","module": "PXLmentor_Camera_Matchmaker",
     "annotation": "Camera Matchmaker  --  fSpy-inspired VP camera solve"},
    {"label": "GLB Manager",   "icon": "icon_glb_manager.png",      "module": "PXLtools_GLB_Manager",
     "annotation": "GLB Manager  --  Import + Export unified"},
    {"label": "OBJ Export",    "icon": "icon_obj_exporter.png",     "module": "PXLtools_OBJ_Exporter",
     "annotation": "OBJ Batch Exporter"},
    {"label": "Renamer",       "icon": "icon_batch_renamer.png",    "module": "PXLtools_Batch_Renamer",
     "annotation": "Advanced Batch Renamer"},
    {"label": "Materials",     "icon": "icon_pbr_material.png",     "module": "PXLtools_PBR_Material",
     "annotation": "Arnold PBR Material Creator"},
    {"label": "MU Bridge",     "icon": "icon_mu_bridge.png",        "module": "PXLmentor_MU_Bridge",
     "annotation": "MU Bridge  --  Maya -> Unreal shader-preserving asset export"},
    {"label": "Render Layers", "icon": "icon_render_layer_creator.png", "module": "PXLtools_Render_Layer_Creator",
     "annotation": "Legacy Render Layer Creator"},
    {"label": "TurnTable",     "icon": "icon_turntable_builder.png","module": "PXLtools_TurnTable_Builder",
     "annotation": "PXLtools TurnTable Builder"},
]

# ---------------------------------------------------------------------------
# Version-aware discovery
# ---------------------------------------------------------------------------

def _scripts_dir():
    """Folder that holds this shelf file (and all the tool .py files)."""
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except NameError:
        for p in sys.path:
            if os.path.isfile(os.path.join(p, SHELF_MODULE + ".py")):
                return p
        return cmds.internalVar(userScriptDir=True)


def _version_key(filepath, stem):
    """('<stem>_v1_0_21' -> (1,0,21,3)). Stage rank: alpha<beta<rc<release."""
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
    """Newest '<stem>_v*.py' module name in the scripts folder, or None if the tool
    isn't installed (so the shelf simply omits its button — e.g. the public
    TurnTable-only package ships just the one tool)."""
    best, best_key = None, None
    for f in glob.glob(os.path.join(_scripts_dir(), stem + "_v*.py")):
        k = _version_key(f, stem)
        if k and (best_key is None or k > best_key):
            best_key, best = k, os.path.splitext(os.path.basename(f))[0]
    return best


def _launch_cmd(module_name):
    """Python that reloads (if loaded) or imports the given tool module."""
    return (
        "import importlib, sys\n"
        "mod = '{m}'\n"
        "if mod in sys.modules:\n"
        "    importlib.reload(sys.modules[mod])\n"
        "else:\n"
        "    __import__(mod)\n"
    ).format(m=module_name)


# ---------------------------------------------------------------------------
# Shelf build
# ---------------------------------------------------------------------------

def setup_shelf():
    shelf_top = mel.eval("$_tmp = $gShelfTopLevel")

    if cmds.shelfLayout(SHELF_NAME, exists=True):
        cmds.deleteUI(SHELF_NAME, layout=True)

    shelf = cmds.shelfLayout(SHELF_NAME, parent=shelf_top)

    # One button per INSTALLED tool (newest version). Tools whose file isn't present
    # are skipped — so the public TurnTable-only package shows just that button,
    # while a full local install shows them all. (No Update button — updates come
    # from the GitHub release flow / re-running the installer.)
    loaded = 0
    for tool in TOOLS:
        module = _latest_module(tool["module"])
        if not module:
            continue
        cmds.shelfButton(
            parent=shelf,
            label=tool["label"],
            annotation="{}   [{}]".format(tool["annotation"], module),
            image=tool["icon"],
            command=_launch_cmd(module),
            sourceType="python",
            style="iconOnly",
        )
        loaded += 1

    cmds.shelfTabLayout(shelf_top, edit=True, selectTab=SHELF_NAME)
    cmds.inViewMessage(
        assistMessage="PXLtools shelf ready — {} tool(s).".format(loaded),
        position="midCenter",
        fade=True,
    )


setup_shelf()
