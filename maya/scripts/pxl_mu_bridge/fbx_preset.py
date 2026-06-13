# Tool Name: PXLmentor MU Bridge - FBX Export Preset (Maya side)
# Version: 0.1.0-alpha
# Author: PXLmentor AI Pipeline TD
# Description: Configures Maya's FBX exporter for Unreal Engine 5.6 ingest and
#              writes the current selection to disk. Loose textures only -
#              UE applies our colorspace tags from the .pxlbridge.json sidecar.
# Changelog:
#   0.1.0-alpha - CP001: Initial scaffold.

from __future__ import annotations

import logging
from pathlib import Path
from typing import List

import maya.cmds as cmds
import maya.mel as mel

logger = logging.getLogger(__name__)


_PRESET_MEL: List[str] = [
    "FBXResetExport;",
    "FBXExportFileVersion -v FBX202000;",
    "FBXExportInAscii -v false;",
    "FBXExportSmoothingGroups -v true;",
    "FBXExportSmoothMesh -v true;",
    "FBXExportTangents -v true;",
    "FBXExportTriangulate -v false;",
    "FBXExportHardEdges -v false;",
    "FBXExportInstances -v false;",
    "FBXExportReferencedAssetsContent -v true;",
    "FBXExportSkeletonDefinitions -v false;",
    "FBXExportInputConnections -v false;",
    "FBXExportEmbeddedTextures -v false;",
    "FBXExportApplyConstantKeyReducer -v false;",
    "FBXExportConstraints -v false;",
    "FBXExportCameras -v false;",
    "FBXExportLights -v false;",
    "FBXExportShapes -v true;",
    "FBXExportUpAxis y;",
    "FBXExportScaleFactor 1.0;",
]


def apply_ue_fbx_preset() -> None:
    """Apply FBX export options tuned for Unreal Engine 5.6 ingest.

    All settings are session-scoped on the FBX exporter; user prefs in the
    Export FBX UI may show stale state until the dialog is reopened.
    """
    if not cmds.pluginInfo("fbxmaya", query=True, loaded=True):
        cmds.loadPlugin("fbxmaya", quiet=True)
    for line in _PRESET_MEL:
        try:
            mel.eval(line)
        except Exception:
            logger.warning("FBX preset MEL line failed: %s", line)


def export_selection_to_fbx(out_path: Path, selection_long_names: List[str]) -> Path:
    """Export the given Maya nodes to ``out_path`` as binary FBX 2020.

    Overwrites any existing target file. Returns the resolved output path.
    """
    if not selection_long_names:
        raise ValueError("export_selection_to_fbx called with empty selection")

    out_path = Path(out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    apply_ue_fbx_preset()
    cmds.select(selection_long_names, replace=True)
    cmds.file(
        str(out_path).replace("\\", "/"),
        force=True,
        options="v=0;",
        type="FBX export",
        preserveReferences=True,
        exportSelected=True,
    )
    logger.info("FBX exported: %s", out_path.as_posix())
    return out_path
