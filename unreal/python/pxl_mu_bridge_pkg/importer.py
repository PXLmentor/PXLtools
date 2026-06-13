# Tool Name: PXLmentor MU Bridge - Import Orchestrator (Unreal)
# Version: 0.1.1-alpha
# Author: PXLmentor AI Pipeline TD
# Description: Top-level Unreal import pipeline. Reads a .pxlbridge.json
#              manifest, imports the sibling FBX as a StaticMesh, then per
#              material in the manifest: imports the referenced textures
#              with correct color-space settings, builds a
#              MaterialInstanceConstant parented to M_PXL_PBR_Master, and
#              binds the MI to the matching mesh slot.
# Changelog:
#   0.1.1-alpha - CP002: Removed unreal.EditorAssetLibrary.refresh_asset_directories
#                 call at end of import_manifest. Method does not exist in
#                 UE 5.6.1; save_loaded_asset calls during the import trigger
#                 Content Browser refresh on their own.
#   0.1.0-alpha - CP001: Initial scaffold.

from __future__ import annotations

import logging
import os
import tkinter
import tkinter.filedialog
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import unreal  # noqa: F401  - injected by the Unreal Editor Python runtime

from pxl_mu_bridge_schema import (
    BridgeManifest,
    is_schema_compatible,
    read_manifest,
)

from . import IMPORT_BASE_GAME_PATH
from .material_factory import build_material_instance, ensure_master
from .report import show_import_report
from .texture_setup import _udim_first_tile_path, import_texture

logger = logging.getLogger(__name__)


def pick_manifest_path() -> Optional[Path]:
    """Open a Tk file dialog to choose a .pxlbridge.json manifest."""
    root = tkinter.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        chosen = tkinter.filedialog.askopenfilename(
            parent=root,
            title="Choose MU Bridge manifest (.pxlbridge.json)",
            filetypes=[("MU Bridge manifest", "*.pxlbridge.json"), ("All files", "*.*")],
        )
    finally:
        root.destroy()
    if not chosen:
        return None
    return Path(chosen).resolve()


def _import_fbx_static_mesh(
    fbx_path: Path,
    dest_game_path: str,
    warnings_out: List[str],
) -> Optional["unreal.StaticMesh"]:
    """Import the FBX as a StaticMesh; return the loaded asset or None on failure.

    V0.1 only handles StaticMesh; SkeletalMesh and animation are deferred.
    """
    if not fbx_path.exists():
        warnings_out.append("FBX missing on disk: {}".format(fbx_path))
        return None

    options = unreal.FbxImportUI()
    options.set_editor_property("import_mesh", True)
    options.set_editor_property("import_materials", False)
    options.set_editor_property("import_textures", False)
    options.set_editor_property("import_animations", False)
    options.set_editor_property("import_as_skeletal", False)
    # Static mesh defaults
    try:
        options.static_mesh_import_data.set_editor_property("combine_meshes", False)
    except Exception:
        pass

    task = unreal.AssetImportTask()
    task.set_editor_property("filename", str(fbx_path).replace("\\", "/"))
    task.set_editor_property("destination_path", dest_game_path)
    task.set_editor_property("automated", True)
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("save", False)
    task.set_editor_property("options", options)

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    try:
        asset_tools.import_asset_tasks([task])
    except Exception:
        logger.exception("FBX import failed for %s", fbx_path)
        warnings_out.append("FBX import failed: {}".format(fbx_path.name))
        return None

    imported_paths = list(task.get_editor_property("imported_object_paths") or [])
    if not imported_paths:
        warnings_out.append(
            "FBX import returned no asset paths for '{}'.".format(fbx_path.name)
        )
        return None

    # Prefer the StaticMesh asset; the imported_paths list may include sub-objects.
    for asset_path in imported_paths:
        if "." in asset_path:
            asset_path = asset_path.split(".")[0]
        candidate = unreal.EditorAssetLibrary.load_asset(asset_path)
        if isinstance(candidate, unreal.StaticMesh):
            unreal.EditorAssetLibrary.save_loaded_asset(candidate)
            return candidate

    warnings_out.append(
        "FBX imported but no StaticMesh found in '{}' - V0.1 is static-only.".format(
            fbx_path.name,
        )
    )
    return None


def _bind_materials_to_mesh(
    mesh: "unreal.StaticMesh",
    mesh_assignments,
    material_instances: Dict[str, "unreal.MaterialInstanceConstant"],
    warnings_out: List[str],
) -> int:
    """Assign each MI to the named mesh slot. Returns the number of bound slots."""
    bound = 0
    static_materials = list(mesh.get_editor_property("static_materials") or [])
    slot_names = [str(s.material_slot_name) for s in static_materials]

    for ma in mesh_assignments:
        mi = material_instances.get(ma.material_name)
        if mi is None:
            warnings_out.append(
                "Mesh '{}' slot {}: no MI built for material '{}'.".format(
                    ma.mesh_name, ma.slot_index, ma.material_name,
                )
            )
            continue
        # Prefer index, but fall back to slot-name match if index is out of range.
        idx = ma.slot_index
        if idx < 0 or idx >= len(static_materials):
            # Try slot-name match
            for k, name in enumerate(slot_names):
                if name and (name == ma.material_name or name == "MI_" + ma.material_name):
                    idx = k
                    break
            else:
                warnings_out.append(
                    "Mesh '{}' slot index {} out of range (mesh has {} slots).".format(
                        ma.mesh_name, ma.slot_index, len(static_materials),
                    )
                )
                continue
        try:
            mesh.set_material(idx, mi)
            bound += 1
        except Exception:
            warnings_out.append(
                "Failed to bind '{}' to mesh '{}' slot {}.".format(
                    mi.get_name(), ma.mesh_name, idx,
                )
            )
    unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    return bound


def import_manifest(manifest_path: Path) -> bool:
    """Run the full import pipeline for a single .pxlbridge.json manifest.

    Returns True if the import completed (with or without warnings); False
    only on a fatal validation error before any UE assets were touched.
    """
    warnings: List[str] = []
    validation_errors: List[str] = []
    dropped_params: List[str] = []

    try:
        manifest = read_manifest(manifest_path)
    except Exception as exc:
        msg = "Manifest read failed: {}".format(exc)
        logger.exception(msg)
        show_import_report(
            manifest_path, asset_name="<unknown>",
            materials_count=0, textures_count=0, mesh_count=0,
            warnings=[], dropped_params=[],
            validation_errors=[msg],
        )
        return False

    if not is_schema_compatible(manifest.schema_version):
        msg = "Incompatible schema '{}' - V0.1 importer only accepts 0.1.x.".format(
            manifest.schema_version,
        )
        validation_errors.append(msg)
        show_import_report(
            manifest_path, asset_name=manifest.asset_name,
            materials_count=0, textures_count=0, mesh_count=0,
            warnings=[], dropped_params=[],
            validation_errors=validation_errors,
        )
        return False

    asset_name = manifest.asset_name
    asset_root = "{}/{}".format(IMPORT_BASE_GAME_PATH, asset_name)
    textures_dir = "{}/Textures".format(asset_root)
    materials_dir = "{}/Materials".format(asset_root)
    fbx_dir = manifest_path.parent

    # 1. Ensure master Material exists. Continue on failure to surface report.
    master_ok = ensure_master(warnings)

    # 2. Import FBX (StaticMesh).
    fbx_path = (fbx_dir / manifest.fbx_path).resolve()
    mesh = _import_fbx_static_mesh(fbx_path, asset_root, warnings)
    mesh_count = 1 if mesh is not None else 0

    if mesh is None:
        validation_errors.append("FBX import failed; aborting material build.")
        show_import_report(
            manifest_path, asset_name=asset_name,
            materials_count=0, textures_count=0, mesh_count=0,
            warnings=warnings, dropped_params=dropped_params,
            validation_errors=validation_errors,
        )
        return False

    # 3. For each MaterialEntry: import textures + build MI.
    material_instances: Dict[str, "unreal.MaterialInstanceConstant"] = {}
    textures_total = 0

    for mat in manifest.materials:
        # Surface any dropped params from the export side
        for u in mat.unmapped_params:
            attr = u.get("attr") if isinstance(u, dict) else None
            if attr and attr not in dropped_params:
                dropped_params.append(attr)

        per_material_textures: Dict[str, "unreal.Texture2D"] = {}
        for role, tex_ref in mat.textures.items():
            tile_path, _is_udim = _udim_first_tile_path(tex_ref.path, fbx_dir)
            if tile_path is None:
                # _udim_first_tile_path already logged; record a warning per-tex
                warnings.append(
                    "Material '{}': texture '{}' (role={}) missing on disk.".format(
                        mat.name, tex_ref.path, role,
                    )
                )
                continue
            tex_asset = import_texture(
                source_path=tile_path,
                dest_game_path=textures_dir,
                color_space=tex_ref.color_space,
                role=role,
                udim=tex_ref.udim,
                warnings_out=warnings,
            )
            if tex_asset is not None:
                per_material_textures[role] = tex_asset
                textures_total += 1

        # Build the MI only if the master is present; otherwise log + skip.
        if not master_ok:
            warnings.append(
                "Material '{}': skipped MI build because master Material is missing.".format(
                    mat.name,
                )
            )
            continue

        mi = build_material_instance(
            material_entry=mat,
            materials_game_path=materials_dir,
            texture_assets=per_material_textures,
            warnings_out=warnings,
        )
        if mi is not None:
            material_instances[mat.name] = mi

    # 4. Bind MIs to mesh slots.
    if material_instances:
        _bind_materials_to_mesh(mesh, manifest.mesh_assignments, material_instances, warnings)

    # CP002: refresh_asset_directories() does not exist on EditorAssetLibrary
    # in UE 5.6.1 - removed. Save calls during import trigger Content Browser
    # refresh on their own; no explicit call is needed.

    show_import_report(
        manifest_path, asset_name=asset_name,
        materials_count=len(material_instances),
        textures_count=textures_total,
        mesh_count=mesh_count,
        warnings=warnings,
        dropped_params=dropped_params,
        validation_errors=validation_errors,
    )
    return True


def import_via_picker() -> bool:
    """Top-level UI entry: file picker -> import_manifest()."""
    chosen = pick_manifest_path()
    if chosen is None:
        logger.info("MU Bridge import cancelled (no file chosen).")
        return False
    return import_manifest(chosen)
