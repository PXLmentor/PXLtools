# Tool Name: PXLmentor MU Bridge - Maya Logic Package
# Version: 0.1.0-alpha
# Author: PXLmentor AI Pipeline TD
# Description: Maya-side logic for the PXLmentor Maya<->Unreal asset bridge.
#              Adds the cross-DCC shared schema directory to sys.path so the
#              dataclasses there can be imported by both Maya and Unreal.
# Changelog:
#   0.1.0-alpha - CP001: Initial scaffold.

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

_HERE = Path(__file__).resolve()

# In the dev tree the package lives at
#   <PXLtools>/maya/scripts/pxl_mu_bridge/__init__.py
# and the schema is a sibling under <PXLtools>/shared. When the package is
# deployed to the user's Maya scripts dir, _HERE.parents[3] is no longer
# PXLtools - fall back to the PXLTOOLS_ROOT env var with a documented default.
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
    logger.debug("MU Bridge: prepended shared schema path: %s", _SHARED_PATH)
