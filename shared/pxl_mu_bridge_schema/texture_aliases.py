# Tool Name: PXLmentor MU Bridge - Texture Filename Aliases
# Version: 0.1.0-alpha
# Author: PXLmentor AI Pipeline TD
# Description: Case-insensitive filename token lookup that maps Substance Painter
#              / common PBR naming conventions to V0.1 texture role keys.
#              Ported from PXLmentor_Arnold_PBR_Material_Creator_v1_0_4.py and
#              extended for emissive + opacity roles.
#
#              V0.1 NOTE: The Maya exporter walks the shader graph directly so
#              role identification is driven by aiStandardSurface attribute
#              names, not filenames. This module is kept here for V0.2+ where
#              the Unreal side may need to identify orphan texture sets without
#              a manifest, and for the texture-from-folder import flow.
# Changelog:
#   0.1.0-alpha - CP001: Initial scaffold.

from __future__ import annotations

import logging
import os
import re
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


TEXTURE_ALIASES: Dict[str, List[str]] = {
    "base_color": ["BaseColor", "Base_Color", "Albedo", "Diffuse", "Diff", "Dif"],
    "roughness":  ["Roughness", "Rough", "Rgh"],
    "metallic":   ["Metalness", "Metallic", "Metal", "Met", "Mtl"],
    "normal":     ["Normal", "Norm", "Nrm"],
    "emissive":   ["Emissive", "Emission", "Emit", "Emi"],
    "opacity":    ["Opacity", "Alpha", "Mask"],
}

IMAGE_EXTENSIONS = frozenset({
    ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".exr", ".tga", ".bmp",
})


def match_role_from_filename(filename: str) -> Optional[str]:
    """Return the texture role for ``filename`` or None if no token matches.

    Matching is case-insensitive and prefers longer aliases (so ``BaseColor``
    wins over ``Diff`` when both could match a file like ``BaseColor_diff.png``).
    """
    stem, ext = os.path.splitext(os.path.basename(filename))
    if ext.lower() not in IMAGE_EXTENSIONS:
        return None
    haystack = stem.lower()

    candidates: List[tuple] = []
    for role, aliases in TEXTURE_ALIASES.items():
        for alias in aliases:
            if re.search(r"(^|[_\-\.\s])" + re.escape(alias.lower()) + r"($|[_\-\.\s\d])", haystack):
                candidates.append((len(alias), role))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][1]
