# PXLmentor MU Bridge - Unreal Editor startup hook
#
# WHAT THIS FILE DOES
#   UE 5.6 automatically runs a file named exactly `init_unreal.py` if it is
#   found at  <YourUEProject>/Content/Python/init_unreal.py  every time the
#   editor opens that project. This script:
#     1. Adds the PXLtools Unreal Python folder to sys.path
#     2. Imports `pxl_mu_bridge`, which registers the MU Bridge toolbar icon
#
# HOW TO INSTALL (one-time, ~30 seconds, no Project Settings needed)
#   1. Open your UE 5.6 project's folder in Windows Explorer.
#   2. Open or create the folder `Content/Python/` inside it.
#   3. Copy THIS file into `Content/Python/init_unreal.py`.
#      (Replace any existing init_unreal.py - or merge by adding the two lines
#       under "PXL Tools section" below into your existing one.)
#   4. Restart the UE editor for the project.
#   5. After startup, check the Output Log (Window > Output Log) for lines
#      starting with "[PXL MU Bridge]" - they tell you exactly what happened.
#
# REQUIREMENTS
#   - Edit > Plugins > Scripting > "Python Editor Script Plugin" must be
#     enabled (it is by default in UE 5.6). If MU Bridge does not appear,
#     verify that plugin is enabled and restart.
#
# TROUBLESHOOTING
#   - Open Window > Output Log. Filter by "PXL MU Bridge".
#   - If you see "python dir not found", edit PXL_PYTHON_DIR below to point
#     at your local PXLtools clone.
#   - If you see an ImportError or traceback, copy the FULL traceback into
#     a message back and we will diagnose.
#
# Author: PXLmentor AI Pipeline TD

import sys
import traceback
from pathlib import Path

import unreal

# ---- PXL Tools section (PXLmentor MU Bridge) ------------------------------

PXL_PYTHON_DIR = r"J:\ClaudeCode\projects\PXLtools\unreal\python"

# Bulletproof status file so you do not have to hunt the Output Log to see
# whether the bootstrap actually fired. Re-written every time UE opens the
# project. If this file does not exist after a UE restart, this init_unreal.py
# itself is not being executed by UE (Content/Python placement or filename
# wrong).
_STATUS_FILE = Path(r"J:\tmp\pxl_install_LATEST.txt")


def _write_status(lines):
    try:
        _STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
        _STATUS_FILE.write_text("\n".join(lines), encoding="utf-8")
    except Exception:
        pass


def _bootstrap_pxl_mu_bridge():
    log = []
    def L(msg):
        log.append(msg)
        try: unreal.log("[PXL MU Bridge] " + msg)
        except Exception: pass
        try: print("[PXL MU Bridge] " + msg)
        except Exception: pass

    L("init_unreal.py invoked from: {}".format(Path(__file__).resolve() if "__file__" in globals() else "<unknown>"))
    L("python dir target          : {}".format(PXL_PYTHON_DIR))

    p = Path(PXL_PYTHON_DIR)
    if not p.is_dir():
        L("ERROR: python dir not found.")
        _write_status(log)
        return

    s = str(p)
    if s not in sys.path:
        sys.path.insert(0, s)
        L("sys.path += {}".format(s))
    else:
        L("sys.path already contains the python dir.")

    try:
        import pxl_mu_bridge  # noqa: F401  - registers toolbar button on import
        L("pxl_mu_bridge imported successfully.")
        L("Toolbar icon SHOULD now be on the Level Editor toolbar.")
    except Exception:
        L("ERROR importing pxl_mu_bridge. Full traceback:")
        for line in traceback.format_exc().splitlines():
            L("  " + line)

    L("")
    L("DONE. Status file: {}".format(_STATUS_FILE))
    _write_status(log)


_bootstrap_pxl_mu_bridge()

# ---- End PXL Tools section -----------------------------------------------
