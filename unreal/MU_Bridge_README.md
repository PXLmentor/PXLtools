# PXLmentor MU Bridge — Unreal Side (v0.1.2-alpha)

Maya → Unreal asset bridge. The Maya side exports `.fbx + .pxlbridge.json`. This side ingests it: FBX as StaticMesh, textures with correct colorspace, MaterialInstances parented to a shared master, ACES (OCIO) color pipeline.

**For installers, follow this doc top-to-bottom.** For day-to-day use after install, see [Day-to-day usage](#day-to-day-usage).

---

## What you need

| Requirement | Why |
|---|---|
| Unreal Engine 5.6.1 | The bridge is built and tested against UE 5.6.1 specifically |
| Python Editor Script Plugin enabled | UE's built-in Python runtime — enabled by default, verify in Edit → Plugins → Scripting |
| OpenColorIO plugin enabled | Required for ACES button. The CONFIGURE ACES button auto-enables it on first run via `.uproject` edit + restart prompt |
| `$OCIO` environment variable set | Points at your `config.ocio` file (e.g. `D:\_OCIO\aces_1.2\config.ocio`). Must be set at the OS level BEFORE launching UE so the editor process inherits it |
| `J:\ClaudeCode\projects\PXLtools\` checked out | The bridge code lives here. Adjust paths in `init_unreal.py` if your clone is elsewhere |

---

## Install (3 one-time steps, ~30 minutes total)

### Step 1 — Install the startup hook (~30 seconds)

UE auto-runs `<Project>/Content/Python/init_unreal.py` on every project open. Copy the staged file:

1. Open your UE project's folder in Windows Explorer.
2. Open or create `Content/Python/` inside it.
3. Copy `J:\ClaudeCode\projects\PXLtools\unreal\python\init_unreal.py` into `<Project>/Content/Python/init_unreal.py`.
4. Restart UE.
5. Verify: `J:\tmp\pxl_install_LATEST.txt` exists and ends with `Toolbar icon SHOULD now be on the Level Editor toolbar.`

> Alternatively, after first install of the toolbar/menu, open MU Bridge → click **INSTALL STARTUP HOOK** (added in v0.1.2 CP005) to do this automatically for the active project.

### Step 2 — Bootstrap the Master Material (~25 minutes)

The master Material `M_PXL_PBR_Master` is the parent of every MaterialInstance the bridge creates. It needs scalar/vector/texture/static-switch parameters at specific names.

Follow [`content/PXLbridge/BOOTSTRAP_MASTER_MATERIAL.md`](content/PXLbridge/BOOTSTRAP_MASTER_MATERIAL.md) end-to-end. The doc has step-by-step instructions for every node, wire, and parameter. After Step 10, the `.uasset` is committed to the staged location and every project gets it automatically.

> **If you skip this step:** the importer auto-creates a minimal fallback with 5 texture pins. Visual output is correct but scalar/color parameter overrides from the manifest are silently ignored. Treat the auto-builder as a "you forgot to bootstrap" diagnostic, not a feature.

### Step 3 — Bootstrap the toolbar icon EUW (~15 minutes)

The Level Editor toolbar icon uses an Editor Utility Widget (`W_MUBridge_Toolbar`) so the icon is the brand `icon_mu_bridge.png` instead of a stock UE icon. Until you do this, the bridge falls back to a stock icon on the toolbar AND a `Tools → MU Bridge ...` menu entry (always present).

Follow [`BOOTSTRAP_EUW_TOOLBAR.md`](BOOTSTRAP_EUW_TOOLBAR.md) end-to-end. After Step 7, restart UE; the branded icon appears on the Level Editor toolbar.

> Optional — if you don't care about the branded icon, the Tools menu entry is always available and skips this step.

---

## Day-to-day usage

### Open MU Bridge

- **Preferred:** click the **MU Bridge** toolbar icon on the Level Editor toolbar (branded after Step 3, stock icon before).
- **Fallback:** **Tools menu → MU Bridge ...** (always present).

### First-run: configure ACES (one button, one click)

Click **`1. CONFIGURE ACES (OCIO ASSET + VIEWPORT)`**:

1. If OpenColorIO plugin is missing → the bridge edits your `.uproject` to enable it and prompts you to restart UE. Restart, reopen the bridge, click the button again.
2. If `$OCIO` is unset or points at a missing file → a dialog tells you exactly what to fix at the OS level; restart UE after fixing.
3. Otherwise:
   - Creates `/Game/OCIO/OCIO_ACES_1_2` OCIOConfiguration asset from `$OCIO`.
   - Populates desired color spaces (`ACES - ACEScg` + `Utility - Linear - sRGB`) and display view (`ACES` / `sRGB`).
   - Attempts to activate viewport OCIO Display Configuration (Phase 2 — probe-stage in v0.1.2, locks in v0.1.3).
4. Full step log → `J:\tmp\pxl_aces_LATEST.txt`. Zero `ERROR:` lines = success.

> This is a one-time per project step. Skip on subsequent imports.

### Day-to-day: import a Maya asset

1. In Maya, run the MU Bridge tool, export a selection → produces `<asset>.fbx + <asset>.pxlbridge.json` in your chosen folder.
2. In UE, open MU Bridge → click **`2. IMPORT .PXLBRIDGE ...`**.
3. Pick the `.pxlbridge.json` manifest. The bridge:
   - Imports the sibling FBX as a StaticMesh at `/Game/PXLbridge/<asset>/`.
   - Imports textures with correct colorspace tags (sRGB / Linear / ACEScg / Raw) and DirectX normal flip (Maya OpenGL → UE DirectX).
   - Builds a `MaterialInstanceConstant` per material, parented to `M_PXL_PBR_Master`.
   - Binds each MI to the matching mesh slot.
4. Full step log → `J:\tmp\pxl_import_LATEST.txt`. Report dialog shows dropped Arnold attributes (subsurface, coat, transmission, sheen — V0.2 work) and any failures.

---

## Status files (your debugging lifeline)

Every action writes a status file to `J:\tmp\` regardless of success or failure. When something goes wrong, paste the file content in a message back.

| File | Written by | Contains |
|---|---|---|
| `J:\tmp\pxl_install_LATEST.txt` | `init_unreal.py` on every project open | Whether the startup hook ran, whether `pxl_mu_bridge` imported |
| `J:\tmp\pxl_toolbar_LATEST.txt` | `pxl_mu_bridge.py` on every UE startup | Toolbar + Tools menu registration attempts, EUW probe result |
| `J:\tmp\pxl_aces_LATEST.txt` | `aces_configurator.py` per CONFIGURE ACES click | 8 step results: plugin check, $OCIO read, asset create, configuration_file set, color spaces, display view, save, viewport apply |
| `J:\tmp\pxl_import_LATEST.txt` | `importer.py` per IMPORT click | Per-asset import report — FBX + textures + materials + dropped warnings |

---

## What v0.1.2 can do

- ✅ Maya → Unreal direction (StaticMesh + materials + textures + colorspace)
- ✅ ACES Phase 1: OCIO Configuration asset created from `$OCIO`
- ✅ ACES Phase 2 (probe-stage): viewport OCIO Display Configuration apply — works on most UE 5.6.1 builds, locks down in v0.1.3
- ✅ Auto-enable OpenColorIO plugin via `.uproject` edit + restart prompt
- ✅ Auto-detect missing Master Material → falls back to minimal auto-builder OR copies staged `.uasset` if present
- ✅ Toolbar icon + Tools menu entry on every UE startup
- ✅ Status file logging for every action

## What v0.1.2 cannot do (planned roadmap)

- ❌ **v0.1.3:** ACES Phase 2 viewport apply lock-down (currently a method-name probe)
- ❌ **v0.1.4:** ACES Phase 3 `DefaultEngine.ini` `WorkingColorSpace` keys
- ❌ **v0.1.5:** Production hardening (pytest suite, central logging config, path normalisation audit)
- ❌ **v0.2.0:** Reverse direction (Unreal → Maya), Arnold utility-node translation (`aiColorCorrect`, `aiMultiply`, `hsvToRgb`), Material Instance browser inside the window, custom Slate icon
- ❌ Animation / SkeletalMesh import (StaticMesh only)
- ❌ Arnold subsurface / coat / transmission / sheen (logged as dropped in the report)

---

## Where everything lives

```
J:\ClaudeCode\projects\PXLtools\unreal\
├── python\
│   ├── init_unreal.py                       # Startup hook (copy to <Project>/Content/Python/)
│   ├── pxl_mu_bridge.py                     # Entry point — toolbar + menu registration
│   └── pxl_mu_bridge_pkg\                   # Logic package
│       ├── ui.py                            # PySide6 QDialog
│       ├── importer.py                      # .pxlbridge.json → StaticMesh + MI
│       ├── material_factory.py              # Master + MI creation
│       ├── texture_setup.py                 # UDIM-aware texture import with colorspace
│       ├── aces_configurator.py             # OCIO Configuration asset + viewport apply
│       └── report.py                        # Import report dialog
├── content\PXLbridge\
│   ├── M_PXL_PBR_Master.uasset              # Staged master (built per BOOTSTRAP_MASTER_MATERIAL.md)
│   └── BOOTSTRAP_MASTER_MATERIAL.md         # Step-by-step authoring guide
├── BOOTSTRAP_EUW_TOOLBAR.md                 # Branded toolbar icon authoring guide
├── MU_Bridge_README.md                      # This file
└── CLAUDE.md                                # Maintainer / AI context
```

---

## Support

If anything fails, paste the relevant status file (`J:\tmp\pxl_*_LATEST.txt`) in a message back. The bridge is built to log every action defensively — the answer is almost always in the status file.
