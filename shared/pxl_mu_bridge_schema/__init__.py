# Tool Name: PXLmentor MU Bridge - Shared Schema Package
# Version: 0.1.0-alpha
# Author: PXLmentor AI Pipeline TD
# Description: Cross-DCC data contract for Maya <-> Unreal asset bridge. Importable
#              from both Maya 2025 (PySide6) and Unreal 5.6 Python. Standard library only.
# Changelog:
#   0.1.0-alpha - CP001: Initial scaffold (schema, texture aliases, colorspace map).

from .schema import (
    SCHEMA_VERSION,
    SCHEMA_EXAMPLE,
    TextureRef,
    MaterialEntry,
    MeshAssignment,
    ExportReport,
    BridgeManifest,
    write_manifest,
    read_manifest,
    is_schema_compatible,
)
from .colorspace_map import maya_to_ue, ue_role_default
from .texture_aliases import TEXTURE_ALIASES, match_role_from_filename

__all__ = [
    "SCHEMA_VERSION",
    "SCHEMA_EXAMPLE",
    "TextureRef",
    "MaterialEntry",
    "MeshAssignment",
    "ExportReport",
    "BridgeManifest",
    "write_manifest",
    "read_manifest",
    "is_schema_compatible",
    "maya_to_ue",
    "ue_role_default",
    "TEXTURE_ALIASES",
    "match_role_from_filename",
]
