# Tool Name: PXLmentor MU Bridge - Material Factory (Unreal)
# Version: 0.1.2-alpha
# Author: PXLmentor AI Pipeline TD
# Description: Two responsibilities:
#                1. ensure_master() - guarantee that M_PXL_PBR_Master.uasset
#                   exists in the target project's Content/PXLbridge/ folder.
#                   Falls back in order: load project asset -> copy staged
#                   .uasset -> auto-create programmatically via
#                   MaterialEditingLibrary (the V0.1 'manual bootstrap'
#                   requirement is now optional).
#                2. build_material_instance() - create a MaterialInstanceConstant
#                   parented to the master, set scalar/vector/texture/static
#                   parameters from the .pxlbridge.json MaterialEntry.
# Changelog:
#   0.1.2-alpha - CP004: Auto-create fallback downgraded to a clearly-marked
#                 DIAGNOSTIC path. Warning text rewritten to point at
#                 BOOTSTRAP_MASTER_MATERIAL.md and call out the fact that
#                 scalar/vector parameter overrides in the MI silently no-op
#                 against the minimal auto-built master. The V0.1 canonical
#                 path is now: user authors M_PXL_PBR_Master per the bootstrap
#                 doc once, commits to <PXLtools>/unreal/content/PXLbridge/,
#                 and every UE project copies it automatically on first import.
#                 No behaviour change to the success path (load -> copy staged
#                 -> auto-create); only the warning text and log messages.
#   0.1.1-alpha - CP003: Removed unreal.EditorAssetLibrary.refresh_asset_directories
#                 call from ensure_master() after the staged shutil.copy2
#                 branch. Method does not exist in UE 5.6.1; AssetRegistry
#                 picks up file-system additions on its own.
#   0.1.1-alpha - CP002: ensure_master() falls back to a programmatic
#                 auto-builder when neither the project asset nor the staged
#                 .uasset is found. The auto-built master is minimal:
#                 5 TextureSampleParameter2D nodes (BaseColorTex, MetallicTex,
#                 RoughnessTex, NormalTex, EmissiveTex) wired directly to the
#                 PBR pins. Enough for the import pipeline to produce visible
#                 materials without any manual UE bootstrap. Scalar/vector
#                 params can be added to the master later.
#   0.1.0-alpha - CP001: Initial scaffold (required manual .uasset bootstrap).

from __future__ import annotations

import logging
import shutil
import traceback
from pathlib import Path
from typing import Dict, List, Optional

import unreal  # noqa: F401  - injected by the Unreal Editor Python runtime

from . import MASTER_MATERIAL_GAME_PATH, IMPORT_BASE_GAME_PATH

logger = logging.getLogger(__name__)

# Mapping: manifest scalar key -> master Material scalar parameter name
_SCALAR_PARAM_MAP: Dict[str, str] = {
    "metalness":           "Metallic",
    "specular_roughness":  "Roughness",
    "specular_IOR":        "IOR",
    "emission_weight":     "EmissiveStrength",
    "opacity":             "Opacity",
}

# Mapping: manifest color key -> master Material vector parameter name
_COLOR_PARAM_MAP: Dict[str, str] = {
    "base":     "BaseColorTint",
    "emission": "EmissiveColor",
}

# Mapping: manifest texture role -> (texture param name, companion static-switch name)
_TEXTURE_PARAM_MAP: Dict[str, tuple] = {
    "base_color": ("BaseColorTex", "UseBaseColorTex"),
    "roughness":  ("RoughnessTex", "UseRoughnessTex"),
    "metallic":   ("MetallicTex",  "UseMetallicTex"),
    "normal":     ("NormalTex",    "UseNormalTex"),
    "emissive":   ("EmissiveTex",  "UseEmissiveTex"),
    "opacity":    ("OpacityTex",   "UseOpacityTex"),
}


def _staged_master_uasset_path() -> Path:
    """Resolve the in-repo staged path of M_PXL_PBR_Master.uasset.

    Walks up from this file to find ``<PXLtools>/unreal/content/PXLbridge/``.
    """
    here = Path(__file__).resolve()
    # parents[3] = <PXLtools> in the dev tree
    return here.parents[3] / "unreal" / "content" / "PXLbridge" / "M_PXL_PBR_Master.uasset"


def _project_content_pxlbridge_dir() -> Path:
    """Return the absolute target dir inside the open UE project for M_PXL_PBR_Master."""
    project_content = Path(
        unreal.SystemLibrary.get_project_content_directory()
    ).resolve()
    return project_content / "PXLbridge"


def _auto_create_master_material(warnings_out: List[str]) -> bool:
    """Build M_PXL_PBR_Master programmatically when no .uasset exists.

    Minimal master: 5 TextureSampleParameter2D nodes (one per PBR channel)
    wired directly to the Material's output pins. The MaterialInstance built
    by build_material_instance() overrides each texture parameter with the
    imported textures from the .pxlbridge.json manifest. Scalar/vector
    parameter sets on the MI no-op until those params are added to this
    master in a future revision.
    """
    base_path, name = MASTER_MATERIAL_GAME_PATH.rsplit("/", 1)
    logger.info("Auto-creating master Material at %s", MASTER_MATERIAL_GAME_PATH)

    factory = unreal.MaterialFactoryNew()
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    try:
        mat = asset_tools.create_asset(
            asset_name=name,
            package_path=base_path,
            asset_class=unreal.Material,
            factory=factory,
        )
    except Exception:
        msg = "auto_create_master: AssetTools.create_asset raised"
        warnings_out.append(msg)
        logger.exception(msg)
        return False
    if mat is None:
        warnings_out.append("auto_create_master: AssetTools.create_asset returned None")
        return False

    MEL = unreal.MaterialEditingLibrary

    def add_tex_param(param_name, x, y, normal=False):
        expr_cls = unreal.MaterialExpressionTextureSampleParameter2D
        try:
            expr = MEL.create_material_expression(mat, expr_cls, x, y)
        except Exception:
            msg = "auto_create_master: create_material_expression failed for {}".format(param_name)
            warnings_out.append(msg)
            logger.exception(msg)
            return None
        try:
            expr.set_editor_property("parameter_name", param_name)
            if normal:
                expr.set_editor_property(
                    "sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL,
                )
        except Exception:
            warnings_out.append(
                "auto_create_master: set_editor_property failed for {}".format(param_name)
            )
        return expr

    pin_specs = [
        # (param_name, x, y, normal, source_pin, dest_property)
        ("BaseColorTex", -400, -300, False, "RGB", unreal.MaterialProperty.MP_BASE_COLOR),
        ("MetallicTex",  -400, -100, False, "R",   unreal.MaterialProperty.MP_METALLIC),
        ("RoughnessTex", -400,  100, False, "R",   unreal.MaterialProperty.MP_ROUGHNESS),
        ("NormalTex",    -400,  300, True,  "RGB", unreal.MaterialProperty.MP_NORMAL),
        ("EmissiveTex",  -400,  500, False, "RGB", unreal.MaterialProperty.MP_EMISSIVE_COLOR),
    ]
    built = 0
    for param_name, x, y, normal, src_pin, dest in pin_specs:
        expr = add_tex_param(param_name, x, y, normal=normal)
        if expr is None:
            continue
        try:
            MEL.connect_material_property(expr, src_pin, dest)
            built += 1
        except Exception:
            warnings_out.append(
                "auto_create_master: connect_material_property failed for {}".format(param_name)
            )
            logger.exception("connect_material_property failed for %s", param_name)

    # Compile + save
    try:
        MEL.recompile_material(mat)
    except Exception:
        logger.warning("recompile_material failed (non-fatal):\n%s", traceback.format_exc())
    try:
        unreal.EditorAssetLibrary.save_loaded_asset(mat)
    except Exception:
        logger.warning("save_loaded_asset failed for auto-created master")

    logger.info(
        "Auto-master built with %d/5 texture pins wired at %s.",
        built, MASTER_MATERIAL_GAME_PATH,
    )
    return unreal.EditorAssetLibrary.does_asset_exist(MASTER_MATERIAL_GAME_PATH)


def ensure_master(warnings_out: List[str]) -> bool:
    """Guarantee the master Material exists at ``/Game/PXLbridge/M_PXL_PBR_Master``.

    Resolution order:
      1. If the asset already exists in the project -> done.
      2. Copy the staged ``.uasset`` from ``<PXLtools>/unreal/content/PXLbridge/``.
      3. Auto-create a minimal master programmatically (CP002 fallback).

    Returns True if any of the three paths succeeded.
    """
    if unreal.EditorAssetLibrary.does_asset_exist(MASTER_MATERIAL_GAME_PATH):
        return True

    staged = _staged_master_uasset_path()
    if staged.exists():
        target_dir = _project_content_pxlbridge_dir()
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / "M_PXL_PBR_Master.uasset"
        try:
            shutil.copy2(str(staged), str(target))
        except Exception as exc:
            warnings_out.append(
                "Failed to copy staged master Material to project: {}".format(exc)
            )
            logger.exception("master copy failed")
            # Fall through to auto-create
        else:
            # CP003: refresh_asset_directories() does not exist on
            # EditorAssetLibrary in UE 5.6.1 - removed. AssetRegistry picks
            # up file-system copies on its periodic scan automatically.
            if unreal.EditorAssetLibrary.does_asset_exist(MASTER_MATERIAL_GAME_PATH):
                logger.info("Bootstrapped staged master into project (%s).", target.as_posix())
                return True
            warnings_out.append(
                "Staged master copied but UE Content Browser does not see it yet. "
                "Falling back to programmatic auto-create."
            )

    # Last resort: programmatic auto-create (DIAGNOSTIC FALLBACK).
    # CP004: this path now exists strictly so a first-time user sees something
    # in the viewport instead of a black mesh. The minimal master has 5 texture
    # pins wired directly to PBR outputs - it has NO ScalarParameter,
    # VectorParameter, or StaticSwitchParameter nodes. That means every
    # scalar (Metallic, Roughness, IOR, EmissiveStrength, Opacity) and every
    # color (BaseColorTint, EmissiveColor) override that build_material_instance()
    # sets on the MI is silently dropped. Treat this code path as a
    # "you forgot to bootstrap" diagnostic, not a feature.
    logger.warning(
        "Master Material missing at both project and staged paths; falling back "
        "to the minimal AUTO-BUILT master. Scalar/vector parameter overrides "
        "will be silently dropped. Author the real master per "
        "BOOTSTRAP_MASTER_MATERIAL.md to fix."
    )
    if _auto_create_master_material(warnings_out):
        warnings_out.append(
            "DIAGNOSTIC FALLBACK: Master Material was auto-created with the "
            "minimal 5-texture-pin variant. Scalar/vector parameter overrides "
            "set on Material Instances will be silently dropped against this "
            "master. To get the full PBR parameter surface (Metallic/Roughness/"
            "IOR/EmissiveStrength/Opacity scalars + BaseColorTint/EmissiveColor "
            "vectors + Use*Tex/bMasked static switches), follow:\n"
            "  <PXLtools>/unreal/content/PXLbridge/BOOTSTRAP_MASTER_MATERIAL.md\n"
            "Then copy your .uasset to "
            "<PXLtools>/unreal/content/PXLbridge/M_PXL_PBR_Master.uasset and "
            "re-run the import. The staged .uasset takes precedence over this "
            "auto-built fallback on every subsequent import in any UE project."
        )
        return True

    warnings_out.append(
        "Master Material is missing AND auto-create failed. Material Instances "
        "will not be built. Bootstrap the master per "
        "<PXLtools>/unreal/content/PXLbridge/BOOTSTRAP_MASTER_MATERIAL.md, "
        "OR check J:\\tmp\\pxl_import_LATEST.txt for the create_asset failure "
        "trace."
    )
    return False


def build_material_instance(
    material_entry,
    materials_game_path: str,
    texture_assets: Dict[str, "unreal.Texture2D"],
    warnings_out: List[str],
) -> Optional["unreal.MaterialInstanceConstant"]:
    """Create a MaterialInstanceConstant for one MaterialEntry.

    Args:
        material_entry: MaterialEntry dataclass from the manifest.
        materials_game_path: UE folder (e.g.
            ``/Game/PXLbridge/<asset>/Materials``) for the new MI asset.
        texture_assets: dict {role -> Texture2D asset} of already-imported textures.
        warnings_out: list to append warnings to.

    Returns the MI asset, or None on failure.
    """
    master = unreal.EditorAssetLibrary.load_asset(MASTER_MATERIAL_GAME_PATH)
    if master is None:
        warnings_out.append(
            "Master Material missing at '{}' - cannot create MI for '{}'.".format(
                MASTER_MATERIAL_GAME_PATH, material_entry.name,
            )
        )
        return None

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    factory = unreal.MaterialInstanceConstantFactoryNew()
    factory.set_editor_property("initial_parent", master)

    mi_name = "MI_{}".format(material_entry.name)
    try:
        mi = asset_tools.create_asset(
            asset_name=mi_name,
            package_path=materials_game_path,
            asset_class=unreal.MaterialInstanceConstant,
            factory=factory,
        )
    except Exception:
        logger.exception("Failed to create MaterialInstanceConstant '%s'", mi_name)
        warnings_out.append(
            "Could not create MaterialInstanceConstant '{}' at '{}'.".format(
                mi_name, materials_game_path,
            )
        )
        return None
    if mi is None:
        warnings_out.append(
            "AssetTools returned None creating MI '{}'.".format(mi_name)
        )
        return None

    # Make absolutely sure the parent is set (create_asset doesn't always honor
    # factory.initial_parent on every UE 5.6 build).
    try:
        unreal.MaterialEditingLibrary.set_material_instance_parent(mi, master)
    except Exception:
        try:
            mi.set_editor_property("parent", master)
        except Exception:
            logger.exception("Could not assign parent on MI '%s'.", mi_name)

    # Scalars
    for manifest_key, ue_param in _SCALAR_PARAM_MAP.items():
        if manifest_key in material_entry.scalars:
            value = float(material_entry.scalars[manifest_key])
            try:
                unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(
                    mi, ue_param, value,
                )
            except Exception:
                warnings_out.append(
                    "MI '{}': failed to set scalar '{}' = {}.".format(
                        mi_name, ue_param, value,
                    )
                )

    # Vectors (colors)
    for manifest_key, ue_param in _COLOR_PARAM_MAP.items():
        if manifest_key in material_entry.colors:
            rgb = material_entry.colors[manifest_key]
            r = float(rgb[0]) if len(rgb) > 0 else 0.0
            g = float(rgb[1]) if len(rgb) > 1 else 0.0
            b = float(rgb[2]) if len(rgb) > 2 else 0.0
            try:
                unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(
                    mi, ue_param, unreal.LinearColor(r, g, b, 1.0),
                )
            except Exception:
                warnings_out.append(
                    "MI '{}': failed to set vector '{}'.".format(mi_name, ue_param)
                )

    # Textures + companion static-switch
    for role, (tex_param, switch_param) in _TEXTURE_PARAM_MAP.items():
        if role not in texture_assets:
            continue
        tex_asset = texture_assets[role]
        if tex_asset is None:
            continue
        try:
            unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(
                mi, tex_param, tex_asset,
            )
        except Exception:
            warnings_out.append(
                "MI '{}': failed to set texture '{}'.".format(mi_name, tex_param)
            )
            continue
        try:
            unreal.MaterialEditingLibrary.set_material_instance_static_switch_parameter_value(
                mi, switch_param, True,
            )
        except Exception:
            # Some UE 5.6 builds expose static-switch set under a different
            # name; fall back to setting the override via editor property.
            logger.debug(
                "static_switch helper missing for '%s' - relying on master "
                "default until UE Materials API stabilises.", switch_param,
            )

    # Opacity -> bMasked if opacity texture present OR scalar opacity < 1.0
    needs_mask = "opacity" in texture_assets
    if not needs_mask:
        op = material_entry.scalars.get("opacity")
        if op is not None and float(op) < 1.0:
            needs_mask = True
    if needs_mask:
        try:
            unreal.MaterialEditingLibrary.set_material_instance_static_switch_parameter_value(
                mi, "bMasked", True,
            )
        except Exception:
            logger.debug("Could not set bMasked static switch on '%s'.", mi_name)

    unreal.EditorAssetLibrary.save_loaded_asset(mi)
    return mi
