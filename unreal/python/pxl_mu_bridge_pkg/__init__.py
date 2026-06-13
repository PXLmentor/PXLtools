# Tool Name: PXLmentor MU Bridge - Unreal Logic Package
# Version: 0.1.0-alpha
# Author: PXLmentor AI Pipeline TD
# Description: Unreal-side logic for the PXLmentor Maya <-> Unreal asset bridge.
#              Adds the cross-DCC shared schema directory to sys.path so the
#              .pxlbridge.json manifest dataclasses can be imported here.
# Changelog:
#   0.1.0-alpha - CP001: Initial scaffold (importer + material factory + ACES
#                 configurator + texture setup + report dialog).

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

_HERE = Path(__file__).resolve()

# Dev tree: <PXLtools>/unreal/python/pxl_mu_bridge_pkg/__init__.py
# parents[3] = <PXLtools>; shared schema lives at <PXLtools>/shared
_DEV_GUESS = _HERE.parents[3] / "shared"
if _DEV_GUESS.exists():
    _SHARED_PATH = _DEV_GUESS
else:
    _PXLTOOLS_ROOT = Path(os.environ.get(
        "PXLTOOLS_ROOT",
        "J:/ClaudeCode/projects/PXLtools",
    ))
    _SHARED_PATH = _PXLTOOLS_ROOT / "shared"

if str(_SHARED_PATH) not in sys.path:
    sys.path.insert(0, str(_SHARED_PATH))
    logger.debug("MU Bridge (Unreal): prepended shared schema path: %s", _SHARED_PATH)


# Master Material settings - referenced by material_factory + importer
MASTER_MATERIAL_GAME_PATH = "/Game/PXLbridge/M_PXL_PBR_Master"
IMPORT_BASE_GAME_PATH = "/Game/PXLbridge"
