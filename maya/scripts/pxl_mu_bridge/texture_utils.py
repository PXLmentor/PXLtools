# Tool Name: PXLmentor MU Bridge - Texture Path Utilities (Maya side)
# Version: 0.1.0-alpha
# Author: PXLmentor AI Pipeline TD
# Description: UDIM detection and POSIX-relative path normalization for textures
#              referenced in the exported manifest.
# Changelog:
#   0.1.0-alpha - CP001: Initial scaffold.

from __future__ import annotations

import logging
import os
import re
from pathlib import Path

import maya.cmds as cmds

logger = logging.getLogger(__name__)


# UDIM tile-token detectors. Order matters: more specific patterns first.
_UDIM_PATTERNS = (
    re.compile(r"\.<udim>(?=\.[a-zA-Z0-9]+$)", re.IGNORECASE),
    re.compile(r"<udim>", re.IGNORECASE),
    re.compile(r"\.(\d{4})(?=\.[a-zA-Z0-9]+$)"),
    re.compile(r"_(\d{4})(?=\.[a-zA-Z0-9]+$)"),
)


def detect_udim_from_file_node(file_node: str) -> bool:
    """Return True when the Maya file node is configured as a UDIM tile set.

    ``file.uvTilingMode`` enum: 0=Off, 1=ZBrush, 2=Mudbox, 3=UDIM (Mari),
    4=Explicit. Anything non-zero is treated as UDIM for V0.1.
    """
    try:
        mode = cmds.getAttr("{}.uvTilingMode".format(file_node))
    except Exception:
        return False
    return int(mode) != 0


def udim_token_normalize(path: str) -> str:
    """Rewrite any UDIM tile token in ``path`` to a literal ``<UDIM>`` placeholder.

    Idempotent. Leaves non-UDIM paths untouched.
    """
    if not path:
        return path
    out = path
    for pattern in _UDIM_PATTERNS:
        out = pattern.sub("<UDIM>", out)
    return out


def normalize_to_posix_relative(abs_path: str, fbx_dir: Path) -> str:
    """Make ``abs_path`` POSIX-relative to ``fbx_dir``.

    If the path is on a different drive or cannot be made relative, returns
    the original POSIX-ified absolute path so the manifest still parses. The
    Unreal importer treats absolute paths as a hint to copy textures into the
    project; the export log surfaces the situation as a warning.
    """
    if not abs_path:
        return ""
    fbx_dir = Path(fbx_dir).resolve()
    try:
        rel = os.path.relpath(abs_path, fbx_dir)
    except ValueError:
        logger.warning(
            "Texture '%s' is on a different drive than the FBX output dir '%s' - "
            "writing absolute path. Consider copying textures alongside the FBX.",
            abs_path, fbx_dir,
        )
        rel = str(Path(abs_path))
    return rel.replace("\\", "/")
