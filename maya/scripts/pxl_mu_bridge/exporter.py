# Tool Name: PXLmentor MU Bridge - Export Orchestrator (Maya side)
# Version: 0.1.0-alpha
# Author: PXLmentor AI Pipeline TD
# Description: Top-level Maya export pipeline. Walks the current selection,
#              translates each aiStandardSurface, writes FBX + .pxlbridge.json,
#              returns the manifest path and an ExportReport for UI display.
# Changelog:
#   0.1.0-alpha - CP001: Initial scaffold.

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Dict, List, Tuple

import maya.cmds as cmds

from pxl_mu_bridge_schema import (
    SCHEMA_VERSION,
    BridgeManifest,
    ExportReport,
    MaterialEntry,
    MeshAssignment,
    write_manifest,
)

from .fbx_preset import export_selection_to_fbx
from .shader_reader import read_ai_standard_surface

logger = logging.getLogger(__name__)


def _maya_units() -> str:
    try:
        return str(cmds.currentUnit(query=True, linear=True) or "cm")
    except Exception:
        return "cm"


def _ocio_config() -> str:
    return os.environ.get("OCIO", "<not set>")


def _collect_shaders_from_transform(transform: str) -> List[Tuple[str, int]]:
    """Return [(aiStandardSurface_node, slot_index), ...] for a mesh transform.

    Slot index follows the order shadingEngines are encountered on the shape.
    Non-aiStandardSurface shaders are skipped with a log; the orchestrator
    surfaces them as warnings on the ExportReport.
    """
    shapes = cmds.listRelatives(transform, shapes=True, fullPath=True) or []
    if not shapes:
        return []
    pairs: List[Tuple[str, int]] = []
    seen_sg: Dict[str, int] = {}
    for shape in shapes:
        sgs = cmds.listConnections(shape, type="shadingEngine") or []
        for sg in sgs:
            if sg in seen_sg:
                continue
            slot = len(seen_sg)
            seen_sg[sg] = slot
            shaders = cmds.listConnections(
                sg + ".surfaceShader", source=True, destination=False,
            ) or []
            for sh in shaders:
                if cmds.nodeType(sh) == "aiStandardSurface":
                    pairs.append((sh, slot))
    return pairs


def _non_arnold_shader_warnings(transform: str) -> List[str]:
    """Return warning strings for any non-aiStandardSurface shaders on ``transform``."""
    warnings: List[str] = []
    shapes = cmds.listRelatives(transform, shapes=True, fullPath=True) or []
    for shape in shapes:
        sgs = cmds.listConnections(shape, type="shadingEngine") or []
        for sg in sgs:
            shaders = cmds.listConnections(
                sg + ".surfaceShader", source=True, destination=False,
            ) or []
            for sh in shaders:
                t = cmds.nodeType(sh)
                if t != "aiStandardSurface":
                    warnings.append(
                        "Skipped non-aiStandardSurface shader '{}' (type={}) on '{}'. "
                        "V0.1 only handles aiStandardSurface.".format(sh, t, transform)
                    )
    return warnings


def export_selection(
    out_dir: Path,
    asset_name: str,
) -> Tuple[Path, ExportReport]:
    """Export the current Maya selection as ``<asset_name>.fbx`` + ``.pxlbridge.json``.

    Args:
        out_dir: Output directory. Created if missing.
        asset_name: Stem used for the FBX and the manifest sidecar.

    Returns:
        ``(manifest_path, report)``. The FBX is at the same directory with the
        same stem.

    Raises:
        ValueError: when nothing is selected or no aiStandardSurface materials
            are found in the selection.
    """
    selection = cmds.ls(selection=True, long=True, type="transform") or []
    if not selection:
        raise ValueError("Nothing selected. Select one or more transform nodes.")

    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    fbx_path = out_dir / "{}.fbx".format(asset_name)
    json_path = out_dir / "{}.pxlbridge.json".format(asset_name)

    report = ExportReport()
    materials: Dict[str, MaterialEntry] = {}
    mesh_assignments: List[MeshAssignment] = []

    for transform in selection:
        report.warnings.extend(_non_arnold_shader_warnings(transform))
        pairs = _collect_shaders_from_transform(transform)
        if not pairs:
            report.warnings.append(
                "No aiStandardSurface found on '{}' - mesh will export with default material slot."
                .format(transform)
            )
            continue
        for shader, slot in pairs:
            mesh_name = transform.split("|")[-1]
            mesh_assignments.append(MeshAssignment(
                mesh_name=mesh_name,
                slot_index=slot,
                material_name=shader,
            ))
            if shader not in materials:
                entry, w = read_ai_standard_surface(shader, out_dir)
                materials[shader] = entry
                report.warnings.extend(w)
                for u in entry.unmapped_params:
                    if u["attr"] not in report.dropped_params:
                        report.dropped_params.append(u["attr"])

    if not materials:
        msg = ("No aiStandardSurface materials found in selection. "
               "V0.1 requires at least one Arnold material to export.")
        report.validation_errors.append(msg)
        raise ValueError(msg)

    export_selection_to_fbx(fbx_path, selection)

    manifest = BridgeManifest(
        schema_version=SCHEMA_VERSION,
        source_dcc="Maya 2025",
        ocio_config=_ocio_config(),
        asset_name=asset_name,
        fbx_path=fbx_path.name,
        units=_maya_units(),
        materials=list(materials.values()),
        mesh_assignments=mesh_assignments,
        report=report,
    )
    write_manifest(manifest, json_path)
    logger.info(
        "Export complete: %d material(s), %d mesh assignment(s), "
        "%d warning(s), %d dropped param(s).",
        len(materials), len(mesh_assignments),
        len(report.warnings), len(report.dropped_params),
    )
    return json_path, report
