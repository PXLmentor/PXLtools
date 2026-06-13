# Tool Name: PXLmentor MU Bridge - Import Report Dialog (Unreal)
# Version: 0.1.1-alpha
# Author: PXLmentor AI Pipeline TD
# Description: Post-import summary - shows an unreal.EditorDialog AND tees
#              the full report to J:\tmp\pxl_import_LATEST.txt so the user
#              does not have to read the popup carefully or hunt the Output
#              Log to diagnose why materials may have been skipped.
# Changelog:
#   0.1.1-alpha - CP002: Added status-file tee to J:\tmp\pxl_import_LATEST.txt
#                 (matches the install / probe / aces / toolbar pattern). The
#                 popup now also points at this file for full detail.
#   0.1.0-alpha - CP001: Initial scaffold (popup only, no status file).

from __future__ import annotations

import logging
from pathlib import Path
from typing import List

import unreal  # noqa: F401  - injected by the Unreal Editor Python runtime

logger = logging.getLogger(__name__)

_STATUS_FILE = Path(r"J:\tmp\pxl_import_LATEST.txt")


def _section(title: str, body_lines: List[str]) -> List[str]:
    if not body_lines:
        return []
    out = [title, "-" * len(title)]
    out.extend(body_lines)
    out.append("")
    return out


def show_import_report(
    manifest_path: Path,
    asset_name: str,
    materials_count: int,
    textures_count: int,
    mesh_count: int,
    warnings: List[str],
    dropped_params: List[str],
    validation_errors: List[str],
) -> None:
    """Render and display the post-import report via unreal.EditorDialog."""
    has_errors = bool(validation_errors)

    title = "MU Bridge Import {}".format("FAILED" if has_errors else "OK")
    header = [
        "Asset       : {}".format(asset_name),
        "Manifest    : {}".format(Path(manifest_path).as_posix()),
        "Imported    : {} mesh(es), {} material(s), {} texture(s)".format(
            mesh_count, materials_count, textures_count,
        ),
        "",
    ]

    body: List[str] = []
    body.extend(_section("VALIDATION ERRORS ({})".format(len(validation_errors)),
                         validation_errors))
    body.extend(_section("WARNINGS ({})".format(len(warnings)), warnings))
    if dropped_params:
        body.extend(_section(
            "DROPPED ATTRIBUTES ({})".format(len(dropped_params)),
            ["- {}".format(p) for p in dropped_params],
        ))

    if not body:
        body = ["Clean import - no warnings, no dropped attributes."]

    message_for_file = "\n".join(header + body)
    message_for_dialog = (
        message_for_file
        + "\n\nFull report also written to:\n  " + str(_STATUS_FILE)
    )
    logger.info("[MU Bridge Import Report]\n%s", message_for_file)

    # Tee to status file so the user does not have to read the popup carefully.
    try:
        _STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
        _STATUS_FILE.write_text(message_for_file, encoding="utf-8")
    except Exception:
        logger.exception("Could not write import status file %s", _STATUS_FILE)

    try:
        unreal.EditorDialog.show_message(
            title=title,
            message=message_for_dialog,
            message_type=unreal.AppMsgType.OK,
            default_value=unreal.AppReturnType.OK,
        )
    except Exception:
        logger.exception(
            "Could not show EditorDialog import report - see status file or Output Log.",
        )
