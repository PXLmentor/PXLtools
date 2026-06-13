# Tool Name: PXLmentor MU Bridge - Color Space Mapping
# Version: 0.1.0-alpha
# Author: PXLmentor AI Pipeline TD
# Description: Translate Maya/OCIO colorSpace attribute strings to a small set of
#              UE-friendly tags consumed by the Unreal importer:
#                  sRGB    -> Texture2D.srgb = True
#                  Linear  -> srgb = False, TC_Default
#                  ACEScg  -> srgb = False, source_color_settings = TCS_ACES_AP1
#                  Raw     -> srgb = False, TC_Default
#              The Maya OCIO env var is read dynamically by the exporter, never
#              hardcoded (per PXLtools maya/CLAUDE.md technical rule).
# Changelog:
#   0.1.0-alpha - CP001: Initial scaffold.

from __future__ import annotations

import logging
from typing import Dict

logger = logging.getLogger(__name__)


# Direct match table. Keys are the exact values that appear in
# ``cmds.getAttr(file_node + '.colorSpace')`` under the ACES 1.2 OCIO config
# shipped with Maya 2025. Anything outside this table falls back to role-based
# defaults via :func:`ue_role_default`.
_MAYA_TO_UE: Dict[str, str] = {
    # ACES 1.2 / Academy
    "ACES - ACEScg":             "ACEScg",
    "ACES - ACES2065-1":         "ACEScg",
    "Utility - sRGB - Texture":  "sRGB",
    "Utility - Linear - sRGB":   "Linear",
    "Utility - Raw":             "Raw",
    "Raw":                       "Raw",
    # OCIO Studio Config v2 fallbacks (also appears in newer Maya OCIO setups)
    "sRGB":                      "sRGB",
    "sRGB - Texture":            "sRGB",
    "Linear Rec.709 (sRGB)":     "Linear",
    "Linear":                    "Linear",
    "scene-linear Rec.709-sRGB": "Linear",
    "scene-linear Rec.2020":     "Linear",
    "scene-linear DCI-P3":       "Linear",
    "ACEScg":                    "ACEScg",
}


# Per-role fallback when the Maya color space is unrecognised. Role names match
# the texture keys in :class:`MaterialEntry.textures` (base_color, roughness,
# metallic, normal, emissive, opacity).
_ROLE_DEFAULT: Dict[str, str] = {
    "base_color": "sRGB",
    "emissive":   "sRGB",
    "roughness":  "Linear",
    "metallic":   "Linear",
    "normal":     "Linear",
    "opacity":    "Linear",
}


def maya_to_ue(maya_colorspace: str, role: str = "") -> str:
    """Map a Maya color-space string to a UE tag.

    Args:
        maya_colorspace: Value of ``file.colorSpace`` from Maya, may be empty.
        role: Texture role key (``base_color`` / ``roughness`` / etc.); used as
            a fallback when ``maya_colorspace`` is unrecognised.

    Returns:
        One of ``sRGB``, ``Linear``, ``ACEScg``, ``Raw``. Always returns a
        valid tag - never raises on unknown input.
    """
    if maya_colorspace:
        tag = _MAYA_TO_UE.get(maya_colorspace.strip())
        if tag:
            return tag
        logger.warning(
            "Unknown Maya colorSpace '%s' for role '%s' - falling back by role.",
            maya_colorspace, role or "<unspecified>",
        )
    return ue_role_default(role)


def ue_role_default(role: str) -> str:
    """Default UE color-space tag for a texture role when the Maya value is unknown."""
    return _ROLE_DEFAULT.get(role, "Linear")
