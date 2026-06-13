# Tool Name: PXLmentor MU Bridge - Texture Import + Color Space Setup (Unreal)
# Version: 0.1.0-alpha
# Author: PXLmentor AI Pipeline TD
# Description: Per-texture import + post-import configuration. Reads the
#              color_space tag and the texture role from the .pxlbridge.json
#              manifest, imports the source file as an Unreal Texture2D, then
#              sets sRGB/compression/source color settings accordingly. Normal
#              maps always get TC_Normalmap, srgb=False, flip_green_channel=True
#              (Maya OpenGL -> UE DirectX convention swap).
# Changelog:
#   0.1.0-alpha - CP001: Initial scaffold.

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional, Tuple

import unreal  # noqa: F401  - injected by the Unreal Editor Python runtime

logger = logging.getLogger(__name__)


_IMG_EXTENSIONS = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".exr", ".tga", ".bmp")


def _udim_first_tile_path(manifest_path: str, fbx_dir: Path) -> Tuple[Optional[Path], bool]:
    """Resolve a (possibly ``<UDIM>``-tokenised) manifest path to a real file on disk.

    Returns ``(actual_path, is_udim)``. If UDIM, returns the 1001 tile (or the
    first tile that exists on disk); UE auto-detects the rest when
    ``TextureFactory.detect_udim`` is True.
    """
    rel = manifest_path or ""
    abs_path = (fbx_dir / rel).resolve()
    if "<UDIM>" not in rel:
        return (abs_path if abs_path.exists() else None), False

    # Swap <UDIM> for 1001, 1002 ... and pick the first that exists on disk.
    for tile in range(1001, 1101):
        candidate = Path(str(abs_path).replace("<UDIM>", str(tile)))
        if candidate.exists():
            return candidate, True
    logger.warning(
        "UDIM texture '%s' resolved no tiles on disk (tested 1001-1100). "
        "Skipping.", rel,
    )
    return None, True


def _apply_color_space(tex: "unreal.Texture2D", color_space: str, role: str) -> None:
    """Apply the manifest's color-space tag to a Texture2D.

    Tag mapping (per PXLmentor MU Bridge schema v0.1.0):
        sRGB   -> srgb=True,  TC_Default
        Linear -> srgb=False, TC_Default
        ACEScg -> srgb=False, source_color_settings.color_space = ACES AP1
        Raw    -> srgb=False, TC_Default

    Normal maps override everything: TC_Normalmap, srgb=False,
    flip_green_channel=True (Maya OpenGL -> UE DirectX).
    """
    is_normal = (role == "normal")

    if is_normal:
        tex.set_editor_property("srgb", False)
        try:
            tex.set_editor_property(
                "compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP,
            )
        except Exception:
            logger.exception("Failed to set TC_NORMALMAP on %s", tex.get_name())
        # Maya is OpenGL convention, UE is DirectX - invert Green.
        try:
            tex.set_editor_property("flip_green_channel", True)
        except Exception:
            logger.warning(
                "Could not set flip_green_channel on '%s' - manual flip "
                "required (Texture Editor -> Flip Green Channel).",
                tex.get_name(),
            )
        return

    if color_space == "sRGB":
        tex.set_editor_property("srgb", True)
        try:
            tex.set_editor_property(
                "compression_settings", unreal.TextureCompressionSettings.TC_DEFAULT,
            )
        except Exception:
            pass

    elif color_space == "Linear":
        tex.set_editor_property("srgb", False)
        try:
            tex.set_editor_property(
                "compression_settings", unreal.TextureCompressionSettings.TC_DEFAULT,
            )
        except Exception:
            pass

    elif color_space == "ACEScg":
        tex.set_editor_property("srgb", False)
        # UE 5.6 supports per-texture source color space via TextureSourceColorSettings.
        # Defensive: try the enum lookup; if missing, fall back to srgb=False only.
        try:
            settings = unreal.TextureSourceColorSettings()
            # Enum name varies across UE versions; try the most likely first.
            color_enum = (
                getattr(unreal.TextureColorSpace, "TCS_ACES_AP1", None)
                or getattr(unreal.TextureColorSpace, "ACES_AP1", None)
            )
            if color_enum is not None:
                settings.set_editor_property("color_space", color_enum)
                tex.set_editor_property("source_color_settings", settings)
            else:
                logger.warning(
                    "ACEScg color space not found on unreal.TextureColorSpace; "
                    "texture '%s' imported as Linear. Check Texture Editor -> "
                    "Source Color Settings manually.",
                    tex.get_name(),
                )
        except Exception:
            logger.exception(
                "Failed to apply ACEScg source_color_settings on %s", tex.get_name(),
            )

    elif color_space == "Raw":
        tex.set_editor_property("srgb", False)

    else:
        logger.warning(
            "Unknown color_space tag '%s' on texture '%s' - leaving defaults.",
            color_space, tex.get_name(),
        )


def import_texture(
    source_path: Path,
    dest_game_path: str,
    color_space: str,
    role: str,
    udim: bool,
    warnings_out: list,
) -> Optional["unreal.Texture2D"]:
    """Import a single texture and apply role-specific post-import settings.

    Args:
        source_path: Absolute path to the source file on disk.
        dest_game_path: UE game path (e.g. ``/Game/PXLbridge/<asset>/Textures``).
        color_space: One of ``sRGB`` / ``Linear`` / ``ACEScg`` / ``Raw``.
        role: Texture role key (``base_color`` / ``roughness`` / ``metallic``
            / ``normal`` / ``emissive`` / ``opacity``).
        udim: True when the manifest flags this as a UDIM set.
        warnings_out: List the function appends free-text warnings to.

    Returns the imported ``Texture2D`` asset, or None on failure.
    """
    if not source_path or not source_path.exists():
        warnings_out.append(
            "Texture source missing on disk: '{}'".format(source_path)
        )
        return None

    if source_path.suffix.lower() not in _IMG_EXTENSIONS:
        warnings_out.append(
            "Unsupported texture extension '{}' for {} ({}); skipping.".format(
                source_path.suffix, role, source_path.name,
            )
        )
        return None

    factory = unreal.TextureFactory()
    if udim:
        try:
            factory.set_editor_property("detect_udim", True)
        except Exception:
            logger.warning(
                "UE 5.6 TextureFactory missing 'detect_udim' - UDIM '%s' "
                "imported as a single tile only.", source_path.name,
            )

    task = unreal.AssetImportTask()
    task.set_editor_property("filename", str(source_path).replace("\\", "/"))
    task.set_editor_property("destination_path", dest_game_path)
    task.set_editor_property("automated", True)
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("save", False)
    task.set_editor_property("factory", factory)

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    try:
        asset_tools.import_asset_tasks([task])
    except Exception:
        logger.exception("import_asset_tasks failed for %s", source_path)
        warnings_out.append(
            "Texture import failed: {} -> {}".format(source_path.name, dest_game_path)
        )
        return None

    imported_paths = list(task.get_editor_property("imported_object_paths") or [])
    if not imported_paths:
        warnings_out.append(
            "Texture import returned no asset path for '{}'.".format(source_path.name)
        )
        return None

    asset_path = imported_paths[0]
    if "." in asset_path:
        asset_path = asset_path.split(".")[0]
    tex = unreal.EditorAssetLibrary.load_asset(asset_path)
    if tex is None:
        warnings_out.append(
            "Could not load imported texture asset at '{}'.".format(asset_path)
        )
        return None

    _apply_color_space(tex, color_space, role)
    unreal.EditorAssetLibrary.save_loaded_asset(tex)
    return tex
