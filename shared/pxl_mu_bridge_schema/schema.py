# Tool Name: PXLmentor MU Bridge - Manifest Schema
# Version: 0.1.0-alpha
# Author: PXLmentor AI Pipeline TD
# Description: Dataclass definitions for the .pxlbridge.json transport format.
#              Written by Maya export side; read by Unreal import side.
#              Standard library only (dataclasses + json) so it loads cleanly in
#              both mayapy (Python 3.11) and Unreal 5.6 embedded Python.
# Changelog:
#   0.1.0-alpha - CP001: Initial scaffold.

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

SCHEMA_VERSION: str = "0.1.0"


@dataclass
class TextureRef:
    """Single texture reference in the manifest.

    Attributes:
        path: POSIX-style path relative to the FBX file. Forward slashes only.
              May contain a literal ``<UDIM>`` token for UDIM sets.
        color_space: UE-friendly tag. One of: ``sRGB``, ``Linear``, ``ACEScg``, ``Raw``.
        udim: True when the texture is a UDIM set.
        original_color_space_in_maya: Raw value of the Maya ``file.colorSpace`` attr,
            preserved verbatim for debugging and future round-trip work.
    """
    path: str
    color_space: str
    udim: bool
    original_color_space_in_maya: str


@dataclass
class MaterialEntry:
    """One material translated from the Maya shading network.

    V0.1 only handles ``aiStandardSurface``. Future shader types will declare a
    different ``source_shader_type`` and a matching parameter map on the UE side.

    The ``unmapped_params`` list captures every Arnold attribute whose value
    deviates from its default but has no destination in V0.1 (e.g. ``subsurface``,
    ``coat_weight``, ``transmission``). The Unreal importer surfaces these in the
    import report so artists know what was dropped.
    """
    name: str
    source_shader_type: str
    scalars: Dict[str, float] = field(default_factory=dict)
    colors: Dict[str, List[float]] = field(default_factory=dict)
    textures: Dict[str, "TextureRef"] = field(default_factory=dict)
    unmapped_params: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class MeshAssignment:
    """Per-mesh material slot binding.

    ``mesh_name`` is the FBX node name (post-export); ``slot_index`` is the
    material slot index in the imported StaticMesh; ``material_name`` matches a
    ``MaterialEntry.name`` in the same manifest.
    """
    mesh_name: str
    slot_index: int
    material_name: str


@dataclass
class ExportReport:
    """Diagnostics collected during Maya export."""
    warnings: List[str] = field(default_factory=list)
    dropped_params: List[str] = field(default_factory=list)
    validation_errors: List[str] = field(default_factory=list)


@dataclass
class BridgeManifest:
    """Top-level manifest written next to the FBX as ``<asset_name>.pxlbridge.json``."""
    schema_version: str
    source_dcc: str
    ocio_config: str
    asset_name: str
    fbx_path: str
    units: str
    materials: List[MaterialEntry] = field(default_factory=list)
    mesh_assignments: List[MeshAssignment] = field(default_factory=list)
    report: ExportReport = field(default_factory=ExportReport)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BridgeManifest":
        materials = [
            MaterialEntry(
                name=m["name"],
                source_shader_type=m["source_shader_type"],
                scalars=dict(m.get("scalars", {})),
                colors={k: list(v) for k, v in m.get("colors", {}).items()},
                textures={
                    k: TextureRef(**v) for k, v in m.get("textures", {}).items()
                },
                unmapped_params=list(m.get("unmapped_params", [])),
            )
            for m in data.get("materials", [])
        ]
        mesh_assignments = [
            MeshAssignment(**ma) for ma in data.get("mesh_assignments", [])
        ]
        report_data = data.get("report", {}) or {}
        report = ExportReport(
            warnings=list(report_data.get("warnings", [])),
            dropped_params=list(report_data.get("dropped_params", [])),
            validation_errors=list(report_data.get("validation_errors", [])),
        )
        return cls(
            schema_version=data["schema_version"],
            source_dcc=data["source_dcc"],
            ocio_config=data.get("ocio_config", "<not set>"),
            asset_name=data["asset_name"],
            fbx_path=data["fbx_path"],
            units=data.get("units", "cm"),
            materials=materials,
            mesh_assignments=mesh_assignments,
            report=report,
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def is_schema_compatible(version: str) -> bool:
    """V0.1 readers accept any ``0.1.x``. Reject everything else."""
    parts = version.split(".")
    if len(parts) < 2:
        return False
    return parts[0] == "0" and parts[1] == "1"


def write_manifest(manifest: BridgeManifest, out_path: Path) -> Path:
    """Serialize ``manifest`` to ``out_path`` as pretty-printed JSON. Returns the path."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(manifest.to_dict(), f, indent=2)
    logger.info("Wrote manifest: %s", out_path.as_posix())
    return out_path


def read_manifest(in_path: Path) -> BridgeManifest:
    """Parse a ``.pxlbridge.json`` from disk. Raises if schema is incompatible."""
    in_path = Path(in_path)
    with in_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    version = data.get("schema_version", "<missing>")
    if not is_schema_compatible(version):
        raise ValueError(
            "Incompatible manifest schema: expected 0.1.x, got '{}'".format(version)
        )
    return BridgeManifest.from_dict(data)


SCHEMA_EXAMPLE: Dict[str, Any] = {
    "schema_version": SCHEMA_VERSION,
    "source_dcc": "Maya 2025",
    "ocio_config": "ACES 1.2 (Academy)",
    "asset_name": "hero_prop_A",
    "fbx_path": "hero_prop_A.fbx",
    "units": "cm",
    "materials": [
        {
            "name": "M_HeroPropBody",
            "source_shader_type": "aiStandardSurface",
            "scalars": {
                "base_weight": 1.0,
                "metalness": 0.0,
                "specular_roughness": 0.45,
                "specular_IOR": 1.5,
                "emission_weight": 0.0,
                "opacity": 1.0,
            },
            "colors": {
                "base": [0.82, 0.78, 0.74],
                "emission": [0.0, 0.0, 0.0],
            },
            "textures": {
                "base_color": {
                    "path": "textures/HeroProp_BaseColor.<UDIM>.exr",
                    "color_space": "ACEScg",
                    "udim": True,
                    "original_color_space_in_maya": "ACES - ACEScg",
                },
                "roughness": {
                    "path": "textures/HeroProp_Roughness.<UDIM>.exr",
                    "color_space": "Linear",
                    "udim": True,
                    "original_color_space_in_maya": "Utility - Raw",
                },
                "normal": {
                    "path": "textures/HeroProp_Normal.<UDIM>.exr",
                    "color_space": "Linear",
                    "udim": True,
                    "original_color_space_in_maya": "Utility - Raw",
                },
            },
            "unmapped_params": [
                {"attr": "subsurface", "value": 0.0, "reason": "v0.1 drop (SSS not in master)"}
            ],
        }
    ],
    "mesh_assignments": [
        {"mesh_name": "hero_prop_body_GEO", "slot_index": 0, "material_name": "M_HeroPropBody"}
    ],
    "report": {
        "warnings": ["coat_weight=0.2 on M_HeroPropBody - dropped"],
        "dropped_params": ["coat_weight", "sheen_weight"],
        "validation_errors": [],
    },
}
