# Tool Name: PXLmentor MU Bridge - aiStandardSurface Graph Reader
# Version: 0.1.0-alpha
# Author: PXLmentor AI Pipeline TD
# Description: Translate a single Maya aiStandardSurface shading network into a
#              MaterialEntry. Handles scalar/color attrs, the 2-hop file-node
#              resolver for textures (via aiNormalMap / bump2d / aiColorCorrect),
#              and unmapped-param drop tracking.
# Changelog:
#   0.1.0-alpha - CP001: Initial scaffold.

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import maya.cmds as cmds

from pxl_mu_bridge_schema import MaterialEntry, TextureRef, maya_to_ue

from .texture_utils import (
    detect_udim_from_file_node,
    normalize_to_posix_relative,
    udim_token_normalize,
)

logger = logging.getLogger(__name__)


# Defaults used to suppress no-op "unmapped" warnings - we only flag attrs
# whose value deviates from the Arnold default.
_AI_STANDARD_SURFACE_DEFAULTS: Dict[str, Any] = {
    "subsurface": 0.0,
    "subsurfaceScale": 1.0,
    "coat": 0.0,
    "coatRoughness": 0.1,
    "coatIOR": 1.5,
    "transmission": 0.0,
    "transmissionDepth": 0.0,
    "sheen": 0.0,
    "sheenRoughness": 0.3,
    "thinWalled": False,
    "coatAffectColor": 0.0,
    "coatAffectRoughness": 0.0,
}

# Maya attr -> (manifest scalar key, Arnold default)
_SCALAR_MAP: Dict[str, Tuple[str, float]] = {
    "base":              ("base_weight",        1.0),
    "metalness":         ("metalness",          0.0),
    "specularRoughness": ("specular_roughness", 0.5),
    "specularIOR":       ("specular_IOR",       1.5),
    "emission":          ("emission_weight",    0.0),
}

# Maya color attr -> manifest color key (linear 0-1 RGB triplet)
_COLOR_MAP: Dict[str, str] = {
    "baseColor":     "base",
    "emissionColor": "emission",
}

# Maya plug -> manifest texture role. opacity is RGB on aiStandardSurface;
# the texture connection is typically on opacity (whole compound), so the
# orchestrator tries the compound first then opacityR as a fallback.
_TEXTURE_ATTR_MAP: Dict[str, str] = {
    "baseColor":         "base_color",
    "specularRoughness": "roughness",
    "metalness":         "metallic",
    "normalCamera":      "normal",
    "emissionColor":     "emissive",
    "opacity":           "opacity",
}


def _read_scalar(shader: str, attr: str) -> Optional[float]:
    try:
        return float(cmds.getAttr("{}.{}".format(shader, attr)))
    except Exception:
        return None


def _read_color_rgb(shader: str, attr: str) -> Optional[List[float]]:
    try:
        v = cmds.getAttr("{}.{}".format(shader, attr))
    except Exception:
        return None
    if isinstance(v, list) and v and isinstance(v[0], (list, tuple)):
        return [float(c) for c in v[0]]
    if isinstance(v, (list, tuple)):
        return [float(c) for c in v]
    return None


def _upstream_files(node: str, plug: Optional[str] = None) -> List[str]:
    """Return upstream file nodes connected to ``node[.plug]`` (one hop)."""
    target = "{}.{}".format(node, plug) if plug else node
    try:
        conns = cmds.listConnections(
            target, source=True, destination=False, plugs=False,
        ) or []
    except Exception:
        return []
    return [c for c in conns if cmds.nodeType(c) == "file"]


def _resolve_to_file_node(
    shader: str,
    attr: str,
    warnings: List[str],
) -> Optional[str]:
    """Walk shader.attr upstream and return the source ``file`` node, or None.

    Recognised intermediates:
        - aiNormalMap   -> .input upstream file
        - bump2d        -> .bumpValue upstream file (warns: bump-not-normal)
        - aiColorCorrect-> .input upstream file (warns: CC params discarded)
    Anything else attempts one generic one-hop fallback and warns.
    """
    try:
        conns = cmds.listConnections(
            "{}.{}".format(shader, attr),
            source=True, destination=False, plugs=False,
        ) or []
    except Exception:
        return None

    for c in conns:
        node_type = cmds.nodeType(c)
        if node_type == "file":
            return c
        if node_type == "aiNormalMap":
            files = _upstream_files(c, "input")
            if files:
                return files[0]
        elif node_type == "bump2d":
            files = _upstream_files(c, "bumpValue")
            if files:
                warnings.append(
                    "bump2d '{}' on {}.{} - exporting source file as normal map. "
                    "UE master expects tangent-space normal; verify visually.".format(
                        c, shader, attr,
                    )
                )
                return files[0]
        elif node_type == "aiColorCorrect":
            files = _upstream_files(c, "input")
            if files:
                warnings.append(
                    "aiColorCorrect '{}' on {}.{} - parameters discarded in V0.1; "
                    "only the upstream texture was exported.".format(c, shader, attr)
                )
                return files[0]
        else:
            files = _upstream_files(c)
            if files:
                warnings.append(
                    "Unhandled intermediate '{}' (type {}) on {}.{} - exported "
                    "source texture, ignored intermediate.".format(
                        c, node_type, shader, attr,
                    )
                )
                return files[0]
    return None


def _build_texture_ref(file_node: str, role: str, fbx_dir: Path) -> TextureRef:
    raw_path = cmds.getAttr("{}.fileTextureName".format(file_node)) or ""
    is_udim = detect_udim_from_file_node(file_node)
    if is_udim:
        try:
            pattern = cmds.getAttr(
                "{}.computedFileTextureNamePattern".format(file_node)
            )
            if pattern:
                raw_path = pattern
        except Exception:
            pass
    normalized = udim_token_normalize(raw_path) if is_udim else raw_path
    rel = normalize_to_posix_relative(normalized, fbx_dir)
    try:
        maya_cs = cmds.getAttr("{}.colorSpace".format(file_node)) or ""
    except Exception:
        maya_cs = ""
    ue_cs = maya_to_ue(maya_cs, role)
    return TextureRef(
        path=rel,
        color_space=ue_cs,
        udim=is_udim,
        original_color_space_in_maya=maya_cs,
    )


def read_ai_standard_surface(
    shader: str,
    fbx_dir: Path,
) -> Tuple[MaterialEntry, List[str]]:
    """Translate one ``aiStandardSurface`` node into a ``MaterialEntry``.

    Returns (entry, warnings). Warnings are merged into ``ExportReport`` by
    the orchestrator. Raises ``ValueError`` if ``shader`` is not an
    aiStandardSurface.
    """
    if cmds.nodeType(shader) != "aiStandardSurface":
        raise ValueError(
            "Expected aiStandardSurface, got '{}' on node '{}'".format(
                cmds.nodeType(shader), shader,
            )
        )

    warnings: List[str] = []
    scalars: Dict[str, float] = {}
    colors: Dict[str, List[float]] = {}
    textures: Dict[str, TextureRef] = {}
    unmapped: List[Dict[str, Any]] = []

    for maya_attr, (manifest_key, _default) in _SCALAR_MAP.items():
        val = _read_scalar(shader, maya_attr)
        if val is not None:
            scalars[manifest_key] = val

    op_rgb = _read_color_rgb(shader, "opacity")
    if op_rgb:
        scalars["opacity"] = float(op_rgb[0])

    for maya_attr, manifest_key in _COLOR_MAP.items():
        rgb = _read_color_rgb(shader, maya_attr)
        if rgb:
            colors[manifest_key] = rgb[:3]

    for maya_attr, role in _TEXTURE_ATTR_MAP.items():
        file_node = _resolve_to_file_node(shader, maya_attr, warnings)
        if not file_node and maya_attr == "opacity":
            file_node = _resolve_to_file_node(shader, "opacityR", warnings)
        if file_node:
            textures[role] = _build_texture_ref(file_node, role, fbx_dir)

    for maya_attr, default in _AI_STANDARD_SURFACE_DEFAULTS.items():
        try:
            cur = cmds.getAttr("{}.{}".format(shader, maya_attr))
        except Exception:
            continue
        if isinstance(cur, list) and cur and isinstance(cur[0], (list, tuple)):
            cur = list(cur[0])
        if cur != default:
            unmapped.append({
                "attr": maya_attr,
                "value": cur,
                "reason": "v0.1 drop (not supported by M_PXL_PBR_Master)",
            })

    entry = MaterialEntry(
        name=shader,
        source_shader_type="aiStandardSurface",
        scalars=scalars,
        colors=colors,
        textures=textures,
        unmapped_params=unmapped,
    )
    return entry, warnings
